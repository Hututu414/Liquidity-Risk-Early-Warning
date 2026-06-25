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
from src.common.features import compute_raw_components, compute_standardization_params
from src.common.io_utils import clean_dir, sanitize_code, to_parquet, write_json, write_markdown
from src.common.logging_utils import setup_logger, write_failure
from src.common.splits import make_time_split, period_mask


STAGE = "stage2a_make_stress_components"


def _read_manifest() -> pd.DataFrame:
    path = paths.STAGE1_DIR / "model_ready_manifest.csv"
    if not path.exists():
        raise FileNotFoundError(f"Stage1 manifest is missing: {path}")
    manifest = pd.read_csv(path)
    manifest = manifest.loc[manifest["model_ready_rows"].fillna(0).astype(int) > 0].copy()
    if manifest.empty:
        raise RuntimeError("Stage1 manifest has no usable model-ready shards.")
    return manifest


def _collect_dates(manifest: pd.DataFrame) -> list[object]:
    dates: set[object] = set()
    for row in manifest.itertuples(index=False):
        shard = paths.PROJECT_ROOT / str(row.output_path)
        df = pd.read_parquet(shard, columns=["date"])
        dates.update(pd.to_datetime(df["date"], errors="coerce").dropna().dt.date)
    return sorted(dates)


def build_audit_text(split: dict[str, object], params_rows: int, raw_rows: int) -> str:
    return "\n".join(
        [
            "# Stage2a 鍘嬪姏缁勪欢瀹¤",
            "",
            "- 鐘舵€侊細PASS",
            f"- 鍘熷缁勪欢 shard 鐩綍锛歚{paths.STRESS_COMPONENTS_RAW_BY_CODE_DIR.relative_to(paths.PROJECT_ROOT)}`",
            f"- 鍘熷缁勪欢琛屾暟锛歿raw_rows:,}",
            f"- 鏍囧噯鍖栧弬鏁拌鏁帮細{params_rows:,}",
            f"- 璁粌鏈燂細{split['train_start']} 鑷?{split['train_end']}",
            "",
            "## 闃叉硠婕忓彛寰?,
            "",
            "- ILLIQ銆丷ange銆丷V銆丷elAmt 鍏堟寜鍗曞彧璇佸埜銆佸崟鏃ュ唴绐楀彛婊氬姩鐢熸垚锛屼笉璺ㄤ氦鏄撴棩銆?,
            "- robust median/MAD 鍙傛暟鍙娇鐢ㄨ缁冩湡鏍锋湰锛屽苟鎸?code-slot 鍒嗙粍淇濆瓨銆?,
            "- 鏈剼鏈笉鐢熸垚姝ｅ紡妯″瀷缁撴灉銆?,
            "",
        ]
    )


def run() -> None:
    logger = setup_logger(STAGE)
    paths.ensure_runtime_dirs()
    config = load_project_config()
    stage2_cfg = config["stage2"]
    windows = [int(x) for x in stage2_cfg["windows"]]
    epsilon = float(stage2_cfg["epsilon"])
    amount_scale = float(stage2_cfg["amount_scale_for_illiq"])
    compression = str(stage2_cfg.get("compression", "zstd"))

    manifest = _read_manifest()
    clean_dir(paths.STRESS_COMPONENTS_RAW_BY_CODE_DIR)

    split = make_time_split(
        _collect_dates(manifest),
        float(stage2_cfg["train_fraction"]),
        float(stage2_cfg["validation_fraction"]),
    )
    write_json(split, paths.STAGE2_DIR / "time_split.json")

    params_parts: list[pd.DataFrame] = []
    raw_manifest: list[dict[str, object]] = []
    component_cols: list[str] | None = None
    raw_rows = 0

    for idx, row in enumerate(manifest.itertuples(index=False), start=1):
        code = str(row.code)
        shard = paths.PROJECT_ROOT / str(row.output_path)
        logger.info("Computing raw components for %s (%d/%d)", code, idx, len(manifest))
        df = pd.read_parquet(shard)
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        df = df.sort_values(["date", "slot", "datetime"]).reset_index(drop=True)

        raw, cols = compute_raw_components(df, windows, amount_scale, epsilon)
        if component_cols is None:
            component_cols = cols
        train_mask = period_mask(raw["date"], str(split["train_start"]), str(split["train_end"]))
        params = compute_standardization_params(raw, cols, train_mask, epsilon)
        params_parts.append(params)

        output_path = paths.STRESS_COMPONENTS_RAW_BY_CODE_DIR / f"{sanitize_code(code)}.parquet"
        to_parquet(raw, output_path, compression=compression)
        raw_rows += int(len(raw))
        raw_manifest.append(
            {
                "code": code,
                "is_index": bool(row.is_index),
                "rows": int(len(raw)),
                "output_path": str(output_path.relative_to(paths.PROJECT_ROOT)),
            }
        )

    if component_cols is None:
        raise RuntimeError("No component columns were generated.")

    params_all = pd.concat(params_parts, ignore_index=True)
    params_path = paths.STAGE2_DIR / "standardization_params_train_code_slot.parquet"
    to_parquet(params_all, params_path, compression=compression)
    pd.DataFrame(raw_manifest).to_csv(paths.STAGE2_DIR / "stress_components_raw_manifest.csv", index=False, encoding="utf-8-sig")
    write_json({"component_columns": component_cols, "windows": windows}, paths.STAGE2_DIR / "component_metadata.json")
    write_markdown(build_audit_text(split, len(params_all), raw_rows), paths.LEAKAGE_AUDIT_DIR / "stage2a_components_audit.md")
    logger.info("Stage2a completed: raw_rows=%s params_rows=%s", f"{raw_rows:,}", f"{len(params_all):,}")


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
