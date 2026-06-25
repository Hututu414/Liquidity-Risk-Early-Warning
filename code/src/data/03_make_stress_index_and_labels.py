from __future__ import annotations

import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import numpy as np
import pandas as pd

from config import paths
from src.common.config_loader import load_project_config
from src.common.features import (
    add_future_lsi_targets,
    add_lsi_columns,
    apply_robust_standardization,
    assign_stress_labels,
)
from src.common.io_utils import clean_dir, sanitize_code, to_parquet, write_json, write_markdown
from src.common.logging_utils import setup_logger, write_failure
from src.common.splits import period_mask


STAGE = "stage2b_make_stress_index_and_labels"


def _read_raw_manifest() -> pd.DataFrame:
    path = paths.STAGE2_DIR / "stress_components_raw_manifest.csv"
    if not path.exists():
        raise FileNotFoundError(f"Stage2a raw component manifest is missing: {path}")
    manifest = pd.read_csv(path)
    if manifest.empty:
        raise RuntimeError("Raw component manifest is empty.")
    return manifest


def _read_component_columns() -> list[str]:
    metadata_path = paths.STAGE2_DIR / "component_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Component metadata is missing: {metadata_path}")
    import json

    with metadata_path.open("r", encoding="utf-8") as handle:
        return list(json.load(handle)["component_columns"])


def _market_add(left: pd.DataFrame | None, right: pd.DataFrame) -> pd.DataFrame:
    if left is None:
        return right.copy()
    return left.add(right, fill_value=0)


def _aggregate_market_part(df: pd.DataFrame, primary_index_code: str) -> tuple[pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None]:
    stock = df.loc[~df["is_index"].astype(bool)].copy()
    stock_agg = None
    if not stock.empty:
        stock_agg = stock.groupby("datetime").agg(
            market_lsi_sum=("LSI_5", "sum"),
            market_lsi_count=("LSI_5", "count"),
            cross_stress_sum=("Stress_H5", "sum"),
            cross_stress_count=("Stress_H5", "count"),
            cross_stress_h10_sum=("Stress_H10", "sum"),
            cross_stress_h10_count=("Stress_H10", "count"),
            market_relamt_sum=("RelAmt_5", "sum"),
            market_relamt_count=("RelAmt_5", "count"),
        )

    index_context = None
    if (df["code"] == primary_index_code).any():
        primary = df.loc[df["code"] == primary_index_code, ["datetime", "ret_1m", "RV_5"]].drop_duplicates("datetime")
        index_context = primary.rename(columns={"ret_1m": "IndexRet", "RV_5": "IndexRV"}).set_index("datetime")

    index_fallback = None
    index_rows = df.loc[df["is_index"].astype(bool)].copy()
    if not index_rows.empty:
        index_fallback = index_rows.groupby("datetime").agg(
            index_ret_sum=("ret_1m", "sum"),
            index_ret_count=("ret_1m", "count"),
            index_rv_sum=("RV_5", "sum"),
            index_rv_count=("RV_5", "count"),
        )
    return stock_agg, index_context, index_fallback


def _finalize_market_context(
    stock_agg: pd.DataFrame,
    primary_index_context: pd.DataFrame | None,
    index_fallback_agg: pd.DataFrame | None,
) -> pd.DataFrame:
    market = pd.DataFrame(index=stock_agg.index)
    market["MarketLSI"] = stock_agg["market_lsi_sum"] / stock_agg["market_lsi_count"].replace(0, np.nan)
    market["CrossStress"] = stock_agg["cross_stress_sum"] / stock_agg["cross_stress_count"].replace(0, np.nan)
    market["CrossStress_H10"] = stock_agg["cross_stress_h10_sum"] / stock_agg["cross_stress_h10_count"].replace(0, np.nan)
    market["MarketRelAmt"] = stock_agg["market_relamt_sum"] / stock_agg["market_relamt_count"].replace(0, np.nan)

    if primary_index_context is not None and not primary_index_context.empty:
        market = market.join(primary_index_context[["IndexRet", "IndexRV"]], how="left")
    elif index_fallback_agg is not None and not index_fallback_agg.empty:
        fallback = pd.DataFrame(index=index_fallback_agg.index)
        fallback["IndexRet"] = index_fallback_agg["index_ret_sum"] / index_fallback_agg["index_ret_count"].replace(0, np.nan)
        fallback["IndexRV"] = index_fallback_agg["index_rv_sum"] / index_fallback_agg["index_rv_count"].replace(0, np.nan)
        market = market.join(fallback, how="left")
    else:
        market["IndexRet"] = np.nan
        market["IndexRV"] = np.nan

    market = market.reset_index().rename(columns={"index": "datetime"})
    return market


def build_audit_text(split: dict[str, object], thresholds: dict[str, float], final_rows: int) -> str:
    threshold_lines = [f"- {key}: {value:.6g}" for key, value in thresholds.items()]
    return "\n".join(
        [
            "# Stage2b LSI 涓庢爣绛惧璁?,
            "",
            "- 鐘舵€侊細PASS",
            f"- 鏈€缁堝彉閲忎笌鏍囩 shard 鐩綍锛歚{paths.LSI_LABELS_BY_CODE_DIR.relative_to(paths.PROJECT_ROOT)}`",
            f"- 鏈€缁堣鏁帮細{final_rows:,}",
            f"- 璁粌鏈燂細{split['train_start']} 鑷?{split['train_end']}",
            "",
            "## 鏍囩闃堝€?,
            "",
            *threshold_lines,
            "",
            "## 闃叉硠婕忓彛寰?,
            "",
            "- LSI 鏍囧噯鍖栧弬鏁版潵鑷缁冩湡 code-slot median/MAD銆?,
            "- Stress_H5 涓?Stress_H10 闃堝€兼潵鑷缁冩湡鏈潵 LSI 鍒嗗竷銆?,
            "- 鏍囩鏈潵绐楀彛鎸?code-date 鍐呭悜鍓嶇湅锛屼笉璺ㄤ氦鏄撴棩銆?,
            "- 鍚庣画楠岃瘉蹇呴』缁х画浣跨敤鏃堕棿婊氬姩鏍锋湰澶栵紝涓嶈兘闅忔満鎵撲贡銆?,
            "",
        ]
    )


def run() -> None:
    logger = setup_logger(STAGE)
    paths.ensure_runtime_dirs()
    config = load_project_config()
    stage2_cfg = config["stage2"]
    windows = [int(x) for x in stage2_cfg["windows"]]
    horizons = [int(x) for x in stage2_cfg["label_horizons"]]
    source_lsi_col = f"LSI_{int(stage2_cfg['label_source_lsi_window'])}"
    mad_scale = float(stage2_cfg["robust_mad_scale"])
    epsilon = float(stage2_cfg["epsilon"])
    compression = str(stage2_cfg.get("compression", "zstd"))
    primary_index_code = str(stage2_cfg["primary_index_code"])

    manifest = _read_raw_manifest()
    component_cols = _read_component_columns()
    params_all = pd.read_parquet(paths.STAGE2_DIR / "standardization_params_train_code_slot.parquet")
    import json

    with (paths.STAGE2_DIR / "time_split.json").open("r", encoding="utf-8") as handle:
        split = json.load(handle)

    clean_dir(paths.LSI_UNLABELED_BY_CODE_DIR)
    clean_dir(paths.LSI_LABELED_NO_MARKET_BY_CODE_DIR)
    clean_dir(paths.LSI_LABELS_BY_CODE_DIR)

    train_future_values: dict[int, list[np.ndarray]] = {h: [] for h in horizons}
    unlabeled_manifest: list[dict[str, object]] = []

    for idx, row in enumerate(manifest.itertuples(index=False), start=1):
        code = str(row.code)
        logger.info("Applying standardization and LSI for %s (%d/%d)", code, idx, len(manifest))
        df = pd.read_parquet(paths.PROJECT_ROOT / str(row.output_path))
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        params = params_all.loc[params_all["code"] == code].copy()
        df = apply_robust_standardization(df, params, component_cols, mad_scale, epsilon)
        df = add_lsi_columns(df, windows)
        df = add_future_lsi_targets(df, source_lsi_col, horizons)

        train_mask = period_mask(df["date"], str(split["train_start"]), str(split["train_end"]))
        stock_mask = ~df["is_index"].astype(bool)
        for horizon in horizons:
            future_col = f"future_max_{source_lsi_col}_H{horizon}"
            values = pd.to_numeric(df.loc[train_mask & stock_mask, future_col], errors="coerce").dropna().to_numpy()
            if values.size:
                train_future_values[horizon].append(values)

        output_path = paths.LSI_UNLABELED_BY_CODE_DIR / f"{sanitize_code(code)}.parquet"
        to_parquet(df, output_path, compression=compression)
        unlabeled_manifest.append(
            {
                "code": code,
                "is_index": bool(row.is_index),
                "rows": int(len(df)),
                "output_path": str(output_path.relative_to(paths.PROJECT_ROOT)),
            }
        )

    thresholds: dict[str, float] = {}
    for horizon, parts in train_future_values.items():
        if not parts:
            raise RuntimeError(f"No train-period future LSI values available for H{horizon}.")
        values = np.concatenate(parts)
        thresholds[f"H{horizon}"] = float(np.nanquantile(values, float(stage2_cfg["label_quantile"])))
    write_json(thresholds, paths.STAGE2_DIR / "label_thresholds_train.json")
    pd.DataFrame(unlabeled_manifest).to_csv(paths.STAGE2_DIR / "lsi_unlabeled_manifest.csv", index=False, encoding="utf-8-sig")

    stock_agg: pd.DataFrame | None = None
    primary_index_context: pd.DataFrame | None = None
    index_fallback_agg: pd.DataFrame | None = None
    labeled_manifest: list[dict[str, object]] = []

    for idx, row in enumerate(pd.DataFrame(unlabeled_manifest).itertuples(index=False), start=1):
        code = str(row.code)
        logger.info("Assigning labels for %s (%d/%d)", code, idx, len(unlabeled_manifest))
        df = pd.read_parquet(paths.PROJECT_ROOT / str(row.output_path))
        df = assign_stress_labels(df, thresholds, source_lsi_col)
        out_path = paths.LSI_LABELED_NO_MARKET_BY_CODE_DIR / f"{sanitize_code(code)}.parquet"
        to_parquet(df, out_path, compression=compression)
        labeled_manifest.append(
            {
                "code": code,
                "is_index": bool(row.is_index),
                "rows": int(len(df)),
                "output_path": str(out_path.relative_to(paths.PROJECT_ROOT)),
            }
        )

        stock_part, index_context_part, index_fallback_part = _aggregate_market_part(df, primary_index_code)
        if stock_part is not None:
            stock_agg = _market_add(stock_agg, stock_part)
        if index_context_part is not None:
            primary_index_context = index_context_part if primary_index_context is None else primary_index_context.combine_first(index_context_part)
        if index_fallback_part is not None:
            index_fallback_agg = _market_add(index_fallback_agg, index_fallback_part)

    if stock_agg is None:
        raise RuntimeError("No stock rows were available for market aggregation.")
    market_context = _finalize_market_context(stock_agg, primary_index_context, index_fallback_agg)
    market_context_path = paths.STAGE2_DIR / "market_context.parquet"
    to_parquet(market_context, market_context_path, compression=compression)

    final_manifest: list[dict[str, object]] = []
    final_rows = 0
    for idx, row in enumerate(pd.DataFrame(labeled_manifest).itertuples(index=False), start=1):
        code = str(row.code)
        logger.info("Joining market context for %s (%d/%d)", code, idx, len(labeled_manifest))
        df = pd.read_parquet(paths.PROJECT_ROOT / str(row.output_path))
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        final = df.merge(market_context, on="datetime", how="left", validate="many_to_one")
        out_path = paths.LSI_LABELS_BY_CODE_DIR / f"{sanitize_code(code)}.parquet"
        to_parquet(final, out_path, compression=compression)
        final_rows += int(len(final))
        final_manifest.append(
            {
                "code": code,
                "is_index": bool(row.is_index),
                "rows": int(len(final)),
                "output_path": str(out_path.relative_to(paths.PROJECT_ROOT)),
            }
        )

    pd.DataFrame(labeled_manifest).to_csv(paths.STAGE2_DIR / "lsi_labeled_no_market_manifest.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(final_manifest).to_csv(paths.STAGE2_DIR / "lsi_labels_manifest.csv", index=False, encoding="utf-8-sig")
    write_markdown(build_audit_text(split, thresholds, final_rows), paths.LEAKAGE_AUDIT_DIR / "no_lookahead_audit.md")
    logger.info("Stage2b completed: final_rows=%s", f"{final_rows:,}")


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
