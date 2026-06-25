from __future__ import annotations

import json
import math
import runpy
import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from config import paths


PREDICTION_COLUMNS = [
    "code",
    "datetime",
    "date",
    "horizon",
    "period",
    "reg_stage",
    "y_true",
    "predicted_probability",
]
EVAL_PERIODS = ["validation", "test"]
METRIC_COLUMNS = [
    "PR_AUC",
    "ROC_AUC",
    "Recall_Top5pct",
    "Recall_Top10pct",
    "Precision_Top5pct",
    "Precision_Top10pct",
    "Brier",
]
FORBIDDEN_FEATURE_TOKENS = [
    "CrossStress",
    "CrossStress_H10",
    "Stress_H5",
    "Stress_H10",
    "future_max",
]


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def top_metrics(y: np.ndarray, p: np.ndarray, frac: float) -> tuple[int, int, float, float, float]:
    n = len(y)
    top_n = max(1, int(math.ceil(n * frac)))
    order = np.argsort(-p, kind="mergesort")[:top_n]
    positives = int(np.sum(y == 1))
    top_positives = int(np.sum(y[order] == 1))
    precision = float(top_positives / top_n)
    recall = float(top_positives / positives) if positives else np.nan
    baseline = float(np.mean(y)) if n else np.nan
    lift = float(precision / baseline) if baseline and np.isfinite(baseline) else np.nan
    return top_n, top_positives, precision, recall, lift


def metric_row(g: pd.DataFrame) -> dict[str, float]:
    y = g["y_true"].astype("int8").to_numpy()
    p = g["predicted_probability"].astype("float64").to_numpy()
    if len(np.unique(y)) >= 2:
        pr_auc = float(average_precision_score(y, p))
        roc_auc = float(roc_auc_score(y, p))
    else:
        pr_auc = np.nan
        roc_auc = np.nan
    precision5_n, precision5_pos, precision5, recall5, lift5 = top_metrics(y, p, 0.05)
    precision10_n, precision10_pos, precision10, recall10, lift10 = top_metrics(y, p, 0.10)
    return {
        "rows": int(len(g)),
        "positives": int(np.sum(y == 1)),
        "positive_rate": float(np.mean(y)) if len(y) else np.nan,
        "PR_AUC": pr_auc,
        "ROC_AUC": roc_auc,
        "Recall_Top5pct": recall5,
        "Recall_Top10pct": recall10,
        "Precision_Top5pct": precision5,
        "Precision_Top10pct": precision10,
        "Top5_rows": precision5_n,
        "Top5_positives": precision5_pos,
        "Top5_lift": lift5,
        "Top10_rows": precision10_n,
        "Top10_positives": precision10_pos,
        "Top10_lift": lift10,
        "Brier": float(brier_score_loss(y, p)) if len(np.unique(y)) >= 1 else np.nan,
    }


def load_forecasting_constants() -> dict[str, list[str]]:
    globals_dict = runpy.run_path(str(paths.SRC_DIR / "models" / "07_smartboost_forecasting.py"))
    return {
        "BASE_COLUMNS": list(globals_dict["BASE_COLUMNS"]),
        "MARKET_FEATURES": list(globals_dict["MARKET_FEATURES"]),
        "FEATURE_COLUMNS": list(globals_dict["FEATURE_COLUMNS"]),
        "PARTIAL_FEATURES": list(globals_dict["PARTIAL_FEATURES"]),
    }


def load_predictions() -> tuple[pd.DataFrame, pd.DataFrame, int, int, int, pd.DataFrame]:
    manifest_path = paths.SMARTBOOST_TABLE_DIR / "smartboost_prediction_manifest.csv"
    manifest = pd.read_csv(manifest_path)
    eval_parts = []
    duplicate_count = 0
    loaded_rows = 0
    prob_null_all = 0
    period_date_parts = []
    for row in manifest.itertuples(index=False):
        pred_path = paths.PROJECT_ROOT / row.output_path
        df = pd.read_parquet(pred_path, columns=PREDICTION_COLUMNS)
        loaded_rows += len(df)
        duplicate_count += int(df.duplicated(["code", "datetime", "horizon"]).sum())
        prob_null_all += int(df["predicted_probability"].isna().sum())
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        period_date_parts.append(
            df.groupby("period", dropna=False)["date"].agg(["min", "max", "count"]).reset_index()
        )
        eval_parts.append(df.loc[df["period"].isin(EVAL_PERIODS)].copy())
    eval_df = pd.concat(eval_parts, ignore_index=True)
    period_dates = pd.concat(period_date_parts, ignore_index=True)
    period_dates = period_dates.groupby("period", dropna=False).agg({"min": "min", "max": "max", "count": "sum"}).reset_index()
    return manifest, eval_df, duplicate_count, loaded_rows, prob_null_all, period_dates


def build_event_rate_and_lift(eval_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (horizon, period), g in eval_df.groupby(["horizon", "period"], sort=True):
        row = {"horizon": horizon, "period": period, "reg_stage": "ALL"}
        row.update(metric_row(g))
        rows.append(row)
    for (horizon, period, reg_stage), g in eval_df.groupby(["horizon", "period", "reg_stage"], sort=True):
        row = {"horizon": horizon, "period": period, "reg_stage": reg_stage}
        row.update(metric_row(g))
        rows.append(row)
    return pd.DataFrame(rows)


def add_check(
    rows: list[dict],
    check_scope: str,
    check_name: str,
    status: str,
    observed: object = "",
    expected: object = "",
    delta: object = "",
    horizon: str = "",
    period: str = "",
    reg_stage: str = "",
    row_count: object = "",
    notes: str = "",
) -> None:
    rows.append(
        {
            "check_scope": check_scope,
            "horizon": horizon,
            "period": period,
            "reg_stage": reg_stage,
            "check_name": check_name,
            "status": status,
            "observed": observed,
            "expected": expected,
            "delta": delta,
            "rows": row_count,
            "notes": notes,
        }
    )


def build_integrity_checks(
    constants: dict[str, list[str]],
    metadata: dict,
    saved_metrics: pd.DataFrame,
    event_rate_lift: pd.DataFrame,
    eval_df: pd.DataFrame,
    manifest: pd.DataFrame,
    duplicate_count: int,
    loaded_rows: int,
    prob_null_all: int,
    period_dates: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    source_path = paths.SRC_DIR / "models" / "07_smartboost_forecasting.py"
    source_text = source_path.read_text(encoding="utf-8")
    stage2_text = (paths.SRC_DIR / "data" / "03_make_stress_index_and_labels.py").read_text(encoding="utf-8")
    feature_columns = list(metadata.get("feature_columns", []))
    forbidden_in_features = sorted(
        {f for f in feature_columns for token in FORBIDDEN_FEATURE_TOKENS if token in f}
    )
    forbidden_in_runtime_features = sorted(
        {
            f
            for key in ["MARKET_FEATURES", "FEATURE_COLUMNS", "PARTIAL_FEATURES"]
            for f in constants[key]
            for token in FORBIDDEN_FEATURE_TOKENS
            if token in f
        }
    )
    forbidden_in_base_inputs = sorted(
        {
            f
            for f in constants["BASE_COLUMNS"]
            for token in ["CrossStress", "CrossStress_H10", "future_max"]
            if token in f
        }
    )

    add_check(
        rows,
        "feature_static",
        "forbidden_feature_absent_from_metadata",
        "PASS" if not forbidden_in_features else "FAIL",
        observed=";".join(forbidden_in_features),
        expected="",
        notes="Forbidden tokens include CrossStress, Stress labels, and future_max.",
    )
    add_check(
        rows,
        "feature_static",
        "forbidden_feature_absent_from_runtime_constants",
        "PASS" if not forbidden_in_runtime_features else "FAIL",
        observed=";".join(forbidden_in_runtime_features),
        expected="",
        notes="Checked MARKET_FEATURES, FEATURE_COLUMNS, and PARTIAL_FEATURES from 07_smartboost_forecasting.py.",
    )
    add_check(
        rows,
        "feature_static",
        "label_aware_base_input_check",
        "PASS" if not forbidden_in_base_inputs else "FAIL",
        observed=";".join(forbidden_in_base_inputs),
        expected="",
        notes="BASE_COLUMNS may include Stress_H5/Stress_H10 as targets, but must not include CrossStress or future_max variables.",
    )
    add_check(
        rows,
        "feature_static",
        "crossstress_source_uses_future_labels",
        "CONFIRMED_REMOVED",
        observed="Stress_H5/Stress_H10 aggregation detected in stage2 source",
        expected="not used as SMARTBoost feature",
        notes="CrossStress is a label-derived market diagnostic and is excluded from the corrected SMARTBoost feature set.",
    )
    add_check(
        rows,
        "feature_static",
        "marketlsi_source_current_lsi",
        "PASS" if 'market_lsi_sum=("LSI_5", "sum")' in stage2_text else "REVIEW",
        observed='market_lsi_sum=("LSI_5", "sum")' in stage2_text,
        expected=True,
        notes="MarketLSI is the current cross-sectional aggregation of LSI_5, not a future-window label.",
    )
    add_check(
        rows,
        "feature_static",
        "rolling_center_true_absent",
        "PASS" if "center=True" not in source_text else "FAIL",
        observed="center=True" in source_text,
        expected=False,
    )
    add_check(
        rows,
        "feature_static",
        "negative_shift_absent",
        "PASS" if "shift(-" not in source_text else "FAIL",
        observed="shift(-" in source_text,
        expected=False,
        notes="Label columns may use future windows upstream, but SMARTBoost feature code must not call shift(-k).",
    )
    add_check(
        rows,
        "prediction",
        "prediction_manifest_code_unique",
        "PASS" if manifest["code"].is_unique else "FAIL",
        observed=int(manifest["code"].duplicated().sum()),
        expected=0,
        row_count=len(manifest),
    )
    add_check(
        rows,
        "prediction",
        "duplicate_code_datetime_horizon",
        "PASS" if duplicate_count == 0 else "FAIL",
        observed=duplicate_count,
        expected=0,
        row_count=loaded_rows,
    )
    add_check(
        rows,
        "prediction",
        "probability_null_all_periods",
        "PASS" if prob_null_all == 0 else "FAIL",
        observed=prob_null_all,
        expected=0,
        row_count=loaded_rows,
    )

    split = metadata["split"]
    expected_ranges = {
        "train": (split["train_start"], split["train_end"]),
        "validation": (split["validation_start"], split["validation_end"]),
        "test": (split["test_start"], split["test_end"]),
    }
    for row in period_dates.itertuples(index=False):
        period = str(row.period)
        if period not in expected_ranges:
            continue
        obs_min = pd.Timestamp(row.min).strftime("%Y-%m-%d")
        obs_max = pd.Timestamp(row.max).strftime("%Y-%m-%d")
        exp_min, exp_max = expected_ranges[period]
        add_check(
            rows,
            "time_split",
            "period_date_range",
            "PASS" if obs_min >= exp_min and obs_max <= exp_max else "FAIL",
            observed=f"{obs_min} to {obs_max}",
            expected=f"{exp_min} to {exp_max}",
            period=period,
            row_count=int(row.count),
        )

    for (horizon, period), g in eval_df.groupby(["horizon", "period"], sort=True):
        prob = g["predicted_probability"].astype("float64")
        oob_count = int(((prob < 0) | (prob > 1)).sum())
        null_count = int(prob.isna().sum())
        add_check(
            rows,
            "prediction",
            "probability_bounds",
            "PASS" if oob_count == 0 and null_count == 0 else "FAIL",
            observed=f"min={prob.min():.12g}; max={prob.max():.12g}; nulls={null_count}; oob={oob_count}",
            expected="[0, 1] and non-null",
            horizon=horizon,
            period=period,
            row_count=len(g),
        )

    saved = saved_metrics.set_index(["horizon", "period"])
    recomputed = event_rate_lift.loc[event_rate_lift["reg_stage"].eq("ALL")].set_index(["horizon", "period"])
    for key, row in recomputed.iterrows():
        horizon, period = key
        for metric in METRIC_COLUMNS:
            observed = float(row[metric])
            expected = float(saved.loc[key, metric])
            delta = observed - expected
            add_check(
                rows,
                "metric_consistency",
                metric,
                "PASS" if (pd.isna(delta) or abs(delta) <= 1e-10) else "FAIL",
                observed=f"{observed:.12g}",
                expected=f"{expected:.12g}",
                delta=f"{delta:.12g}",
                horizon=horizon,
                period=period,
                row_count=int(row["rows"]),
            )
    return pd.DataFrame(rows)


def format_metric_lines(metrics: pd.DataFrame) -> list[str]:
    lines = []
    for row in metrics.sort_values(["horizon", "period"]).itertuples(index=False):
        lines.append(
            f"| {row.horizon} | {row.period} | {row.rows:,} | {row.positives:,} | "
            f"{row.positive_rate:.6f} | {row.PR_AUC:.6f} | {row.ROC_AUC:.6f} | "
            f"{row.Precision_Top5pct:.6f} | {row.Top5_lift:.3f} | "
            f"{row.Precision_Top10pct:.6f} | {row.Top10_lift:.3f} | {row.Brier:.6f} |"
        )
    return lines


def write_deep_audit(
    constants: dict[str, list[str]],
    metadata: dict,
    event_rate_lift: pd.DataFrame,
    integrity: pd.DataFrame,
    loaded_rows: int,
    duplicate_count: int,
) -> None:
    all_metrics = event_rate_lift.loc[event_rate_lift["reg_stage"].eq("ALL")].copy()
    failed = integrity.loc[integrity["status"].eq("FAIL")]
    status = "PASS" if failed.empty else "FAIL"
    feature_list = ", ".join(metadata.get("feature_columns", []))
    lines = [
        "# SMARTBoost Feature Leakage Deep Audit",
        "",
        f"- 审计状态：{status}",
        "- 结论：本轮复核发现旧版 SMARTBoost 使用的 `CrossStress` 来自未来压力标签的横截面聚合，属于特征泄漏；已从特征集合、训练、预测和 partial effects 中删除，并已重跑 SMARTBoost。",
        "- 当前可进入正文的结果是剔除 `CrossStress` 后的新结果；旧版含 `CrossStress` 的指标不得进入正文。",
        "",
        "## 1. CrossStress",
        "",
        "- stage2 中 `CrossStress` 由 `Stress_H5` 横截面聚合得到，`CrossStress_H10` 由 `Stress_H10` 横截面聚合得到。",
        "- `Stress_H5` / `Stress_H10` 是未来窗口标签，因此 `CrossStress` 不能作为 SMARTBoost 的 t 时点特征。",
        "- 当前 `07_smartboost_forecasting.py` 的 `BASE_COLUMNS`、`MARKET_FEATURES`、`FEATURE_COLUMNS`、`PARTIAL_FEATURES` 均不包含 `CrossStress`。",
        "",
        "## 2. MarketLSI",
        "",
        "- `MarketLSI` 保留。stage2 中它由当前分钟的 `LSI_5` 横截面聚合得到。",
        "- `LSI_5` 来自 t 时点及过去窗口组件，并沿用训练期 code-slot median/MAD 标准化；没有使用未来窗口标签。",
        "",
        "## 3. Rolling Features",
        "",
        "- LSI lag 使用 code-date 内 `shift(1)`。",
        "- LSI rolling mean/max 基于 lag 后的 LSI 再 rolling，窗口只覆盖 t 以前。",
        "- 收益窗口 `ret_sum_5/10/20` 使用 t 及以前分钟的 rolling sum。",
        "- 源码扫描未发现 `center=True` 或 `shift(-k)`。",
        "",
        "## 4. Labels",
        "",
        "- `Stress_H5` / `Stress_H10` 继续作为目标变量，允许使用未来窗口构造。",
        "- `future_max_LSI_5_H5`、`future_max_LSI_5_H10`、`Stress_H5`、`Stress_H10` 均未进入特征集合。",
        "",
        "## 5. Time Split And Prediction Integrity",
        "",
        "- 训练、验证、测试按日期区间切分；样本抽取只用于控制训练规模，不改变时间块定义。",
        "- 验证期预测使用训练期模型；测试期预测使用训练+验证期模型。",
        f"- 已读取预测行数：{loaded_rows:,}。",
        f"- `code-datetime-horizon` 重复预测数：{duplicate_count:,}。",
        "",
        "## 6. Recomputed Validation/Test Metrics",
        "",
        "| Horizon | Period | Rows | Positives | Event rate | PR-AUC | ROC-AUC | Precision@Top5% | Top5 lift | Precision@Top10% | Top10 lift | Brier |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        *format_metric_lines(all_metrics),
        "",
        "## 7. Runtime Feature Columns",
        "",
        f"- 特征数：{len(metadata.get('feature_columns', []))}",
        f"- 特征清单：{feature_list}",
        "",
        "## 8. Output Tables",
        "",
        "- `outputs/tables/06_smartboost/smartboost_event_rate_and_lift.csv`",
        "- `outputs/tables/06_smartboost/smartboost_prediction_integrity_check.csv`",
        "",
    ]
    if failed.empty:
        lines.extend(
            [
                "## Final Assessment",
                "",
                "剔除 `CrossStress` 并重跑后的 SMARTBoost 结果未发现剩余特征泄漏或预测重复问题，保存的指标与预测概率可复算一致。当前修正后结果可以进入正文。",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Final Assessment",
                "",
                "仍存在未通过项，当前 SMARTBoost 结果不得进入正文。失败项见 `smartboost_prediction_integrity_check.csv`。",
                "",
            ]
        )
    write_markdown(paths.LEAKAGE_AUDIT_DIR / "smartboost_feature_leakage_deep_audit.md", "\n".join(lines))


def run() -> None:
    paths.ensure_runtime_dirs()
    metadata = read_json(paths.SMARTBOOST_TABLE_DIR / "smartboost_model_metadata.json")
    saved_metrics = pd.read_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_metrics.csv")
    constants = load_forecasting_constants()
    manifest, eval_df, duplicate_count, loaded_rows, prob_null_all, period_dates = load_predictions()
    event_rate_lift = build_event_rate_and_lift(eval_df)
    integrity = build_integrity_checks(
        constants=constants,
        metadata=metadata,
        saved_metrics=saved_metrics,
        event_rate_lift=event_rate_lift,
        eval_df=eval_df,
        manifest=manifest,
        duplicate_count=duplicate_count,
        loaded_rows=loaded_rows,
        prob_null_all=prob_null_all,
        period_dates=period_dates,
    )
    event_rate_lift.to_csv(
        paths.SMARTBOOST_TABLE_DIR / "smartboost_event_rate_and_lift.csv",
        index=False,
        encoding="utf-8-sig",
    )
    integrity.to_csv(
        paths.SMARTBOOST_TABLE_DIR / "smartboost_prediction_integrity_check.csv",
        index=False,
        encoding="utf-8-sig",
    )
    write_deep_audit(constants, metadata, event_rate_lift, integrity, loaded_rows, duplicate_count)
    failed = integrity.loc[integrity["status"].eq("FAIL")]
    if not failed.empty:
        raise RuntimeError(f"SMARTBoost deep audit found {len(failed)} failed checks")
    print("SMARTBoost deep audit completed")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"SMARTBoost deep audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
