from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path("data/processed/onset_model_panel.parquet")
MANIFEST = Path("data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv")

IDENTITY_COLUMNS = ["code", "stock_code", "symbol", "is_index", "date", "datetime", "timestamp", "slot"]
CORE_COLUMNS = [
    "LSI_5",
    "LSI5",
    "LSI_10",
    "LSI_20",
    "MarketLSI",
    "IndexRet",
    "IndexRV",
    "MarketRelAmt",
    "Stress_H5",
    "Stress_H10",
]
ALLOWED_PREFIXES = (
    "ILLIQ_",
    "Range_",
    "RV_",
    "RelAmt_",
    "z_ILLIQ_",
    "z_Range_",
    "z_RV_",
    "z_RelAmt_",
    "LSI_",
    "Market",
    "Index",
    "xsec_",
    "breadth",
)
FORBIDDEN_PARTS = (
    "future",
    "lead",
    "target",
    "label",
    "max_future",
    "forward",
    "FutureMax",
    "CrossStress",
    "Y_onset",
)

LOCAL_HEAVY_REFUSAL = (
    "本地电脑已设置为轻量模式。当前命令属于重计算任务，已拒绝在本地运行。\n"
    "请在 GitHub Codespaces 或 GitHub Actions 中运行该任务。\n"
    "如确认是在云端环境，请设置环境变量 CLOUD_RUN=1。"
)


def project_path(path: Path | str) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def cloud_run_enabled() -> bool:
    return (
        os.environ.get("CLOUD_RUN") == "1"
        or os.environ.get("CODESPACES", "").lower() == "true"
        or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
    )


def local_windows_light_mode() -> bool:
    return sys.platform.startswith("win") and not cloud_run_enabled()


def local_heavy_override_confirmed(allow_local_heavy: bool) -> bool:
    if not allow_local_heavy:
        return False
    print("WARNING: --allow-local-heavy was requested on a local Windows machine.")
    print("This may crash or restart the local computer. Prefer Codespaces or GitHub Actions.")
    if not sys.stdin.isatty():
        print("Refusing override because no interactive confirmation is available.")
        return False
    reply = input("Type ALLOW_LOCAL_HEAVY to continue: ").strip()
    return reply == "ALLOW_LOCAL_HEAVY"


def same_project_path(left: Path, right: Path) -> bool:
    try:
        return project_path(left).resolve() == project_path(right).resolve()
    except OSError:
        return project_path(left).absolute() == project_path(right).absolute()


def local_heavy_reasons(output: Path, max_stock_codes: int | None, dry_run: bool) -> list[str]:
    if dry_run:
        return []
    reasons: list[str] = []
    output_text = str(output).replace("\\", "/").lower()
    if "full80" in output_text:
        reasons.append("output file name contains full80")
    if same_project_path(output, DEFAULT_OUTPUT):
        reasons.append("output path is data/processed/onset_model_panel.parquet")
    if max_stock_codes is None:
        reasons.append("output parquet would be generated from all eligible stock shards")
    elif int(max_stock_codes) > 5:
        reasons.append(f"--max-stock-codes {max_stock_codes} > 5")
    return reasons


def enforce_local_light_mode(output: Path, max_stock_codes: int | None, dry_run: bool, allow_local_heavy: bool) -> bool:
    if not local_windows_light_mode():
        return True
    reasons = local_heavy_reasons(output, max_stock_codes, dry_run)
    if not reasons:
        return True
    if local_heavy_override_confirmed(allow_local_heavy):
        print("WARNING: local heavy-run guard overridden after explicit confirmation.")
        return True
    print(LOCAL_HEAVY_REFUSAL)
    print("Refusal reasons:")
    for reason in reasons:
        print(f"- {reason}")
    return False


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None or pd.isna(value):
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def parquet_columns(path: Path) -> list[str]:
    import pyarrow.parquet as pq

    return list(pq.ParquetFile(path).schema.names)


def is_forbidden(col: str) -> bool:
    if col in {"Stress_H5", "Stress_H10"}:
        return False
    lower = col.lower()
    return any(part.lower() in lower for part in FORBIDDEN_PARTS)


def choose_columns(columns: list[str]) -> tuple[list[str], list[str]]:
    keep: list[str] = []
    excluded: list[str] = []
    for col in columns:
        if is_forbidden(col):
            excluded.append(col)
            continue
        if col in IDENTITY_COLUMNS or col in CORE_COLUMNS or col.startswith(ALLOWED_PREFIXES):
            keep.append(col)
    if "code" not in keep:
        if "stock_code" in keep:
            keep.append("code")
        elif "symbol" in keep:
            keep.append("code")
    return sorted(dict.fromkeys(keep)), excluded


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    if "stock_code" in df.columns and "code" not in df.columns:
        rename["stock_code"] = "code"
    if "symbol" in df.columns and "code" not in df.columns:
        rename["symbol"] = "code"
    if "timestamp" in df.columns and "datetime" not in df.columns:
        rename["timestamp"] = "datetime"
    if "LSI5" in df.columns and "LSI_5" not in df.columns:
        rename["LSI5"] = "LSI_5"
    if rename:
        df = df.rename(columns=rename)
    if "stock_code" not in df.columns and "code" in df.columns:
        df["stock_code"] = df["code"]
    if "symbol" not in df.columns and "code" in df.columns:
        df["symbol"] = df["code"]
    if "is_index" not in df.columns:
        df["is_index"] = False
    return df


def contract_missing(columns: list[str]) -> list[str]:
    available = set(columns)
    groups = {
        "code/stock_code/symbol": {"code", "stock_code", "symbol"},
        "date": {"date"},
        "datetime/timestamp": {"datetime", "timestamp"},
        "LSI_5/LSI5": {"LSI_5", "LSI5"},
        "MarketLSI": {"MarketLSI"},
        "IndexRet": {"IndexRet"},
        "IndexRV": {"IndexRV"},
        "MarketRelAmt": {"MarketRelAmt"},
    }
    return [name for name, aliases in groups.items() if available.isdisjoint(aliases)]


def candidate_records() -> list[dict[str, Any]]:
    manifest_path = ROOT / MANIFEST
    if manifest_path.exists():
        manifest = pd.read_csv(manifest_path)
        records: list[dict[str, Any]] = []
        for _, row in manifest.iterrows():
            raw = row.get("output_path")
            if pd.isna(raw):
                continue
            path = project_path(raw)
            if path.exists() and path.suffix.lower() == ".parquet":
                records.append(
                    {
                        "path": path,
                        "code": str(row.get("code", "")),
                        "is_index": parse_bool(row.get("is_index", False)),
                    }
                )
        preferred = [r for r in records if "lsi_labels_by_code" in str(r["path"])]
        if preferred:
            return preferred
        return records
    roots = [ROOT / "data_intermediate", ROOT / "data_inbox", ROOT / "outputs", ROOT / "experiments"]
    records = []
    for base in roots:
        if base.exists():
            records.extend({"path": path, "code": "", "is_index": False} for path in base.rglob("*.parquet"))
    return sorted(records, key=lambda r: str(r["path"]))


def candidate_files() -> list[Path]:
    return [record["path"] for record in candidate_records()]


def inspect_candidates(limit: int = 80) -> list[dict[str, Any]]:
    rows = []
    for path in candidate_files()[:limit]:
        try:
            columns = parquet_columns(path)
            missing = contract_missing(columns)
            rows.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
                    "columns": len(columns),
                    "missing": missing,
                    "satisfies_contract": not missing,
                }
            )
        except Exception as exc:
            rows.append({"path": str(path), "error": str(exc), "satisfies_contract": False})
    return rows


def build_panel(max_stock_codes: int | None) -> tuple[pd.DataFrame, dict[str, Any]]:
    eligible: list[dict[str, Any]] = []
    seen_codes: set[str] = set()
    skipped_index = 0
    for record in candidate_records():
        path = record["path"]
        if contract_missing(parquet_columns(path)):
            continue
        if parse_bool(record.get("is_index", False)):
            skipped_index += 1
            continue
        code = str(record.get("code") or path.stem)
        if code in seen_codes:
            continue
        seen_codes.add(code)
        eligible.append({**record, "code": code})
    files = [record["path"] for record in eligible]
    if max_stock_codes is not None:
        files = files[:max_stock_codes]
        eligible = eligible[:max_stock_codes]
    if not files:
        inspected = inspect_candidates()
        searched = sorted({str(p.parent.relative_to(ROOT)) for p in candidate_files()[:20]})
        raise RuntimeError(
            "No candidate parquet satisfies the onset model-panel data contract. "
            f"Searched directories/files: {searched}. First inspections: {inspected[:5]}"
        )

    first_cols = parquet_columns(files[0])
    keep, excluded = choose_columns(first_cols)
    if "code" in keep and "code" not in first_cols:
        keep.remove("code")
    frames = []
    for path in files:
        cols = [c for c in keep if c in parquet_columns(path)]
        df = pd.read_parquet(path, columns=cols)
        df = normalize_columns(df)
        df = df.loc[~df["is_index"].astype(bool)].copy()
        frames.append(df)
    panel = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    panel = panel.sort_values(["code", "date", "datetime"] if "datetime" in panel else ["code", "date"]).reset_index(drop=True)
    profile = {
        "source_files": [str(p.relative_to(ROOT)) for p in files],
        "source_stock_codes": [str(record["code"]) for record in eligible],
        "source_file_count": len(files),
        "skipped_index_source_files": skipped_index,
        "retained_columns": list(panel.columns),
        "excluded_columns": excluded,
        "rows": int(len(panel)),
        "columns": int(panel.shape[1]),
        "stock_count": int(panel["code"].nunique()) if "code" in panel else None,
        "date_min": str(pd.to_datetime(panel["date"], errors="coerce").min().date()) if "date" in panel and len(panel) else None,
        "date_max": str(pd.to_datetime(panel["date"], errors="coerce").max().date()) if "date" in panel and len(panel) else None,
    }
    return panel, profile


def write_profile(output: Path, profile: dict[str, Any], dry_run: bool) -> None:
    output_abs = project_path(output)
    out_dir = output_abs.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = output_abs.stem
    schema_path = out_dir / f"{stem}_schema.json"
    profile_path = out_dir / f"{stem}_profile.md"
    write_schema = {
        "dry_run": dry_run,
        "output": str(output),
        "retained_columns": profile.get("retained_columns", []),
        "excluded_columns": profile.get("excluded_columns", []),
        "source_files": profile.get("source_files", []),
    }
    schema_path.write_text(json.dumps(write_schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Onset model panel profile",
        "",
        f"- dry_run: {dry_run}",
        f"- output: {output}",
        f"- rows: {profile.get('rows')}",
        f"- columns: {profile.get('columns')}",
        f"- stock_count: {profile.get('stock_count')}",
        f"- date_min: {profile.get('date_min')}",
        f"- date_max: {profile.get('date_max')}",
        f"- source_file_count: {profile.get('source_file_count')}",
        f"- skipped_index_source_files: {profile.get('skipped_index_source_files')}",
        "",
        "## Source Stock Codes",
        "",
        *(f"- {c}" for c in profile.get("source_stock_codes", [])),
        "",
        "## Retained Columns",
        "",
        *(f"- {c}" for c in profile.get("retained_columns", [])),
        "",
        "## Excluded Columns",
        "",
        *(f"- {c}" for c in profile.get("excluded_columns", [])),
    ]
    profile_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a minimal onset model panel from existing intermediate data.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-stock-codes", type=int, default=None)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--allow-local-heavy",
        action="store_true",
        help="Override the local Windows heavy-run guard after an interactive confirmation.",
    )
    args = parser.parse_args()

    output = Path(args.output)
    if not enforce_local_light_mode(output, args.max_stock_codes, args.dry_run, args.allow_local_heavy):
        return 2
    try:
        effective_max = args.max_stock_codes
        if args.dry_run and effective_max is None:
            effective_max = 5
        panel, profile = build_panel(effective_max)
        if not args.dry_run:
            output_abs = project_path(output)
            output_abs.parent.mkdir(parents=True, exist_ok=True)
            panel.to_parquet(output_abs, index=False)
            profile["file_size_mb"] = round(output_abs.stat().st_size / (1024 * 1024), 3)
        write_profile(output, profile, args.dry_run)
        print(json.dumps(profile, ensure_ascii=False, indent=2))
        if args.dry_run:
            print("Dry run only: parquet file was not written.")
        else:
            print(f"Wrote {output}")
        return 0
    except Exception as exc:
        inspections = inspect_candidates()
        print(f"FAILED: {exc}")
        print("Candidate inspection:")
        print(json.dumps(inspections[:20], ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
