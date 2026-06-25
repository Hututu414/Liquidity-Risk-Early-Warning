from __future__ import annotations

import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from config import paths
from src.common.config_loader import load_project_config
from src.common.features import add_minute_returns
from src.common.io_utils import clean_dir, sanitize_code, to_parquet, write_json, write_markdown
from src.common.logging_utils import setup_logger, write_failure
from src.common.time_utils import build_slot_map, filter_and_add_slot


STAGE = "stage1_make_model_ready_panel"
RAW_COLUMNS = [
    "code",
    "is_index",
    "datetime",
    "date",
    "time",
    "year",
    "month",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
]


def _discover_codes() -> list[str]:
    security_list = paths.PREPROCESSED_QUALITY_DIR / "preprocessed_security_list.csv"
    if security_list.exists():
        securities = pd.read_csv(security_list)
        if "included" in securities.columns:
            securities = securities.loc[securities["included"].astype(str).str.lower().eq("true")]
        return sorted(securities["code"].dropna().astype(str).unique())

    pf = pq.ParquetFile(paths.RAW_PANEL_PATH)
    code_idx = pf.schema_arrow.names.index("code")
    codes: set[str] = set()
    for idx in range(pf.num_row_groups):
        stats = pf.metadata.row_group(idx).column(code_idx).statistics
        if stats and stats.min == stats.max:
            codes.add(str(stats.min))
    if not codes:
        raise RuntimeError("Unable to discover codes from security list or parquet row group stats.")
    return sorted(codes)


def _read_code_frame(code: str) -> pd.DataFrame:
    return pd.read_parquet(
        paths.RAW_PANEL_PATH,
        columns=RAW_COLUMNS,
        filters=[("code", "=", code)],
        engine="pyarrow",
    )


def _normalize_for_stage1(df: pd.DataFrame, slot_map: dict[str, int]) -> pd.DataFrame:
    out = df.copy()
    out["datetime"] = pd.to_datetime(out["datetime"], errors="coerce")
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date
    out = filter_and_add_slot(out, slot_map)
    numeric_cols = ["open", "high", "low", "close", "volume", "amount"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.sort_values(["code", "date", "slot", "datetime"]).reset_index(drop=True)
    return out


def _process_code(
    code: str,
    slot_map: dict[str, int],
    min_minutes: int,
    compression: str,
) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    raw = _read_code_frame(code)
    df = _normalize_for_stage1(raw, slot_map)

    duplicate_mask = df.duplicated(["code", "datetime"], keep=False)
    duplicate_rows = df.loc[duplicate_mask, ["code", "datetime", "date", "time", "open", "high", "low", "close"]].copy()

    counts = df.groupby(["code", "date"], observed=True).size().rename("valid_minutes").reset_index()
    excluded = counts.loc[counts["valid_minutes"] < min_minutes].copy()
    valid_dates = set(counts.loc[counts["valid_minutes"] >= min_minutes, "date"])
    df = df.loc[df["date"].isin(valid_dates)].copy()
    if not df.empty:
        df = df.merge(counts, on=["code", "date"], how="left", validate="many_to_one")
        df = add_minute_returns(df)
        df["ret_1m"] = df["ret_1m"].astype("float64")
        output_path = paths.MODEL_READY_BY_CODE_DIR / f"{sanitize_code(code)}.parquet"
        to_parquet(df, output_path, compression=compression)
    else:
        output_path = None

    manifest_row = {
        "code": code,
        "is_index": bool(raw["is_index"].dropna().iloc[0]) if len(raw) else None,
        "raw_rows": int(len(raw)),
        "session_rows": int(len(_normalize_for_stage1(raw, slot_map))),
        "model_ready_rows": int(len(df)),
        "n_dates_before_threshold": int(counts["date"].nunique()) if len(counts) else 0,
        "n_dates_after_threshold": int(df["date"].nunique()) if len(df) else 0,
        "duplicate_key_rows": int(len(duplicate_rows)),
        "output_path": str(output_path.relative_to(paths.PROJECT_ROOT)) if output_path else "",
    }
    return manifest_row, counts, excluded.assign(code=code), duplicate_rows


def build_audit_text(
    manifest: pd.DataFrame,
    excluded: pd.DataFrame,
    duplicate_rows: pd.DataFrame,
    min_minutes: int,
) -> str:
    total_rows = int(manifest["model_ready_rows"].sum()) if len(manifest) else 0
    return "\n".join(
        [
            "# Stage1 妯″瀷灏辩华闈㈡澘瀹¤",
            "",
            "- 鐘舵€侊細PASS",
            f"- 杈撳嚭鐩綍锛歚{paths.MODEL_READY_BY_CODE_DIR.relative_to(paths.PROJECT_ROOT)}`",
            f"- 杈撳嚭琛屾暟锛歿total_rows:,}",
            f"- 鏈夋晥鍒嗛挓闃堝€硷細{min_minutes}",
            f"- 琚墧闄?code-date 鏁帮細{len(excluded):,}",
            f"- 閲嶅 code-datetime 琛屾暟锛歿len(duplicate_rows):,}",
            "",
            "## 澶勭悊瑙勫垯",
            "",
            "- 鍙繚鐣欓厤缃腑鐨勮繛缁氦鏄撴椂娈?slot锛宻lot 鏁颁负 240銆?,
            "- 鏀剁泭鐜囨寜 code-date 鍐?close 瀵规暟宸垎锛岃法浜ゆ槗鏃ョ涓€鍒嗛挓涓虹己澶便€?,
            "- 鍘熷 `data_inbox/preprocessed/` 鏈淇敼銆?,
            "",
        ]
    )


def run() -> None:
    logger = setup_logger(STAGE)
    paths.ensure_runtime_dirs()
    config = load_project_config()
    slot_map = build_slot_map(config)
    min_minutes = int(config["model_ready"]["min_minutes_per_code_date"])
    compression = str(config["model_ready"].get("compression", "zstd"))
    fail_on_duplicates = bool(config["model_ready"].get("fail_on_duplicate_keys", True))

    if not paths.RAW_PANEL_PATH.exists():
        raise FileNotFoundError(f"Raw panel parquet is missing: {paths.RAW_PANEL_PATH}")

    clean_dir(paths.MODEL_READY_BY_CODE_DIR)
    codes = _discover_codes()
    logger.info("Discovered %d securities.", len(codes))

    manifest_rows: list[dict[str, object]] = []
    coverage_parts: list[pd.DataFrame] = []
    excluded_parts: list[pd.DataFrame] = []
    duplicate_parts: list[pd.DataFrame] = []

    for idx, code in enumerate(codes, start=1):
        logger.info("Processing %s (%d/%d)", code, idx, len(codes))
        manifest_row, counts, excluded, duplicate_rows = _process_code(code, slot_map, min_minutes, compression)
        manifest_rows.append(manifest_row)
        coverage_parts.append(counts)
        if len(excluded):
            excluded_parts.append(excluded)
        if len(duplicate_rows):
            duplicate_parts.append(duplicate_rows)

    manifest = pd.DataFrame(manifest_rows)
    coverage = pd.concat(coverage_parts, ignore_index=True) if coverage_parts else pd.DataFrame()
    excluded = pd.concat(excluded_parts, ignore_index=True) if excluded_parts else pd.DataFrame()
    duplicates = pd.concat(duplicate_parts, ignore_index=True) if duplicate_parts else pd.DataFrame()

    manifest.to_csv(paths.STAGE1_DIR / "model_ready_manifest.csv", index=False, encoding="utf-8-sig")
    coverage.to_csv(paths.STAGE1_DIR / "coverage_by_code_date.csv", index=False, encoding="utf-8-sig")
    excluded.to_csv(paths.STAGE1_DIR / "excluded_code_dates.csv", index=False, encoding="utf-8-sig")
    duplicates.to_csv(paths.STAGE1_DIR / "duplicate_code_datetime_rows.csv", index=False, encoding="utf-8-sig")
    trading_dates = sorted(pd.to_datetime(coverage["date"], errors="coerce").dropna().dt.date.astype(str).unique())
    write_json({"trading_dates": trading_dates, "slot_count": len(slot_map)}, paths.STAGE1_DIR / "stage1_metadata.json")
    write_markdown(build_audit_text(manifest, excluded, duplicates, min_minutes), paths.DATA_AUDIT_DIR / "stage1_model_ready_audit.md")

    if fail_on_duplicates and len(duplicates):
        raise RuntimeError(f"Duplicate code-datetime rows found after session filtering: {len(duplicates)}")
    logger.info("Stage1 completed: model_ready_rows=%s", f"{int(manifest['model_ready_rows'].sum()):,}")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        paths.ensure_runtime_dirs()
        failure_path = write_failure(STAGE, exc, paths.REVIEWS_DIR / "stage_failures")
        print(f"{STAGE} failed. See {failure_path}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
