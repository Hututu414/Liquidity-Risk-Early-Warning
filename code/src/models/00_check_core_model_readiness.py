from __future__ import annotations

import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import pandas as pd

from config import paths
from src.models.model_data import MARKET_VARIABLES, load_label_thresholds, load_market_context, load_time_split, write_markdown


STAGE = "core_model_readiness"


def _check_exists(relative: str, failures: list[str]) -> None:
    path = paths.PROJECT_ROOT / relative
    if not path.exists():
        failures.append(f"Missing required path: {relative}")


def run() -> None:
    paths.ensure_runtime_dirs()
    paths.RGARCH_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    paths.RGARCH_FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    paths.QVAR_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    paths.QVAR_FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    paths.REVIEWS_DIR.joinpath("model_audit").mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    checks: list[str] = []
    for relative in [
        "data_intermediate/stage2_lsi_labels/market_context.parquet",
        "data_intermediate/stage2_lsi_labels/time_split.json",
        "data_intermediate/stage2_lsi_labels/label_thresholds_train.json",
        "data_intermediate/stage2_lsi_labels/standardization_params_train_code_slot.parquet",
        "data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv",
        "reviews/leakage_audit/no_lookahead_audit.md",
    ]:
        _check_exists(relative, failures)

    if not failures:
        market = load_market_context()
        split = load_time_split()
        thresholds = load_label_thresholds()
        missing = [col for col in MARKET_VARIABLES if col not in market.columns]
        if missing:
            failures.append(f"market_context missing variables: {missing}")
        if market.empty:
            failures.append("market_context is empty")
        if set(thresholds) != {"H5", "H10"}:
            failures.append(f"unexpected label threshold keys: {sorted(thresholds)}")
        train = market.loc[
            (market["datetime"] >= pd.Timestamp(split["train_start"]))
            & (market["datetime"] <= pd.Timestamp(split["train_end"]) + pd.Timedelta(days=1))
        ]
        if train[MARKET_VARIABLES].dropna().shape[0] < 1000:
            failures.append("insufficient non-null training rows for market model variables")
        checks.extend(
            [
                f"market_context_rows={len(market):,}",
                f"market_context_complete_rows={market[MARKET_VARIABLES].dropna().shape[0]:,}",
                f"train_complete_rows={train[MARKET_VARIABLES].dropna().shape[0]:,}",
                f"split={split}",
                f"thresholds={thresholds}",
            ]
        )

    if failures:
        text = "\n".join(
            [
                "# Core Model Blocker",
                "",
                "鏍稿績妯″瀷闃舵琚樆鏂紝鍘熷洜濡備笅锛?,
                "",
                *(f"- {item}" for item in failures),
                "",
                "鍦ㄤ慨澶嶅墠涓嶅簲杩愯 RGARCH-CARR-SK銆丵VAR 鎴?SMARTboost 瀹炶瘉闃舵銆?,
                "",
            ]
        )
        write_markdown(paths.REVIEWS_DIR / "model_audit" / "core_model_blocker.md", text)
        raise RuntimeError("; ".join(failures))

    text = "\n".join(
        [
            "# Core Model Readiness Check",
            "",
            "- 鐘舵€侊細PASS",
            "- 缁撹锛歴tage0-stage3 浜х墿瓒充互杩涘叆 RGARCH-CARR-SK 绠€鍖栭闄╄矾寰勪笌 QVAR 鍒嗕綅绯荤粺闃舵銆?,
            "- 缂哄彛锛歚reviews/model_audit/deepseek_stage3_readiness_review.md` 鏈湪鏈湴鍙戠幇锛屽凡浣滀负浜ゆ帴瀹¤缂哄彛璁板綍锛屼笉闃绘柇寤烘ā銆?,
            "",
            "## 妫€鏌ユ憳瑕?,
            "",
            *(f"- {item}" for item in checks),
            "",
        ]
    )
    write_markdown(paths.REVIEWS_DIR / "model_audit" / "core_model_readiness_check.md", text)
    print("core model readiness PASS")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"{STAGE} failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
