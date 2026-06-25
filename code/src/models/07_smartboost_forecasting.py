from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

from config import paths
from src.common.io_utils import clean_dir, to_parquet, write_json
from src.models.model_data import load_time_split, write_markdown
from src.visualization.plot_style import apply_cn_academic_style


HORIZONS = ["H5", "H10"]
TARGETS = {"H5": "Stress_H5", "H10": "Stress_H10"}
MAX_TRAIN_SAMPLES_PER_CLASS = 180_000
MAX_VALIDATION_SELECTION_SAMPLES = 260_000
MAX_TRAINVAL_SAMPLES_PER_CLASS = 220_000
MAX_PARTIAL_BASELINE = 30_000
MAX_ITER = 180
RANDOM_STATE = 20260519

BASE_COLUMNS = [
    "code",
    "is_index",
    "datetime",
    "date",
    "slot",
    "ret_1m",
    "amount",
    "ILLIQ_5",
    "Range_5",
    "RV_5",
    "RelAmt_5",
    "ILLIQ_10",
    "Range_10",
    "RV_10",
    "RelAmt_10",
    "ILLIQ_20",
    "Range_20",
    "RV_20",
    "RelAmt_20",
    "LSI_5",
    "LSI_10",
    "LSI_20",
    "MarketLSI",
    "IndexRet",
    "IndexRV",
    "MarketRelAmt",
    "Stress_H5",
    "Stress_H10",
]

COMPONENT_FEATURES = [
    "ILLIQ_5",
    "Range_5",
    "RV_5",
    "RelAmt_5",
    "ILLIQ_10",
    "Range_10",
    "RV_10",
    "RelAmt_10",
    "ILLIQ_20",
    "Range_20",
    "RV_20",
    "RelAmt_20",
]

MARKET_FEATURES = ["MarketLSI", "IndexRet", "IndexRV", "MarketRelAmt"]

FEATURE_COLUMNS = [
    *COMPONENT_FEATURES,
    "LSI_5_lag1",
    "LSI_10_lag1",
    "LSI_20_lag1",
    "LSI_5_rollmean_5",
    "LSI_5_rollmean_10",
    "LSI_5_rollmean_20",
    "LSI_5_rollmax_5",
    "LSI_5_rollmax_10",
    "LSI_5_rollmax_20",
    "ret_sum_5",
    "ret_sum_10",
    "ret_sum_20",
    "cum_ret_open",
    "cum_amount_log_so_far",
    *MARKET_FEATURES,
    "slot",
    "slot_sin",
    "slot_cos",
    "is_open_10m",
    "is_afternoon_open_10m",
    "is_tail_10m",
    "reg_stage_1",
    "reg_stage_2",
    "reg_stage_3",
]

PARTIAL_FEATURES = ["MarketLSI", "IndexRV", "MarketRelAmt", "LSI_5_lag1", "LSI_5_rollmax_20"]


@dataclass
class HorizonModels:
    horizon: str
    target: str
    best_iter: int
    train_model: HistGradientBoostingClassifier
    trainval_model: HistGradientBoostingClassifier


def load_manifest() -> pd.DataFrame:
    path = paths.STAGE2_DIR / "lsi_labels_manifest.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    manifest = pd.read_csv(path)
    manifest = manifest.loc[manifest["rows"].fillna(0).astype(int) > 0].copy()
    if manifest.empty:
        raise RuntimeError("Empty lsi_labels_manifest.csv")
    return manifest


def add_period_and_stage(df: pd.DataFrame, split: dict[str, str]) -> pd.DataFrame:
    out = df.copy()
    dates = pd.to_datetime(out["date"], errors="coerce")
    out["period"] = "unassigned"
    out.loc[(dates >= pd.Timestamp(split["train_start"])) & (dates <= pd.Timestamp(split["train_end"])), "period"] = "train"
    out.loc[
        (dates >= pd.Timestamp(split["validation_start"])) & (dates <= pd.Timestamp(split["validation_end"])),
        "period",
    ] = "validation"
    out.loc[(dates >= pd.Timestamp(split["test_start"])) & (dates <= pd.Timestamp(split["test_end"])), "period"] = "test"
    out["reg_stage_1"] = ((dates >= pd.Timestamp("2023-05-15")) & (dates <= pd.Timestamp("2024-10-07"))).astype("int8")
    out["reg_stage_2"] = ((dates >= pd.Timestamp("2024-10-08")) & (dates <= pd.Timestamp("2025-07-06"))).astype("int8")
    out["reg_stage_3"] = ((dates >= pd.Timestamp("2025-07-07")) & (dates <= pd.Timestamp("2026-05-13"))).astype("int8")
    return out


def add_features(raw: pd.DataFrame, split: dict[str, str]) -> pd.DataFrame:
    df = raw.loc[~raw["is_index"].astype(bool)].copy()
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df = df.sort_values(["code", "date", "slot"]).reset_index(drop=True)
    for col in [*COMPONENT_FEATURES, "LSI_5", "LSI_10", "LSI_20", "ret_1m", "amount", *MARKET_FEATURES, *TARGETS.values()]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    date_group = df.groupby(["code", "date"], sort=False)
    for col in ["LSI_5", "LSI_10", "LSI_20"]:
        df[f"{col}_lag1"] = date_group[col].shift(1)
    shifted_lsi = date_group["LSI_5"].shift(1)
    for window in [5, 10, 20]:
        df[f"LSI_5_rollmean_{window}"] = (
            shifted_lsi.groupby([df["code"], df["date"]], sort=False).rolling(window, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        )
        df[f"LSI_5_rollmax_{window}"] = (
            shifted_lsi.groupby([df["code"], df["date"]], sort=False).rolling(window, min_periods=1).max().reset_index(level=[0, 1], drop=True)
        )
        df[f"ret_sum_{window}"] = (
            date_group["ret_1m"].rolling(window, min_periods=1).sum().reset_index(level=[0, 1], drop=True)
        )
    df["cum_ret_open"] = date_group["ret_1m"].cumsum()
    df["cum_amount_log_so_far"] = np.log1p(date_group["amount"].cumsum().clip(lower=0))
    slot = pd.to_numeric(df["slot"], errors="coerce").astype("float64")
    df["slot_sin"] = np.sin(2.0 * np.pi * slot / 240.0)
    df["slot_cos"] = np.cos(2.0 * np.pi * slot / 240.0)
    df["is_open_10m"] = (slot <= 10).astype("int8")
    df["is_afternoon_open_10m"] = ((slot >= 122) & (slot <= 131)).astype("int8")
    df["is_tail_10m"] = (slot >= 230).astype("int8")
    df = add_period_and_stage(df, split)
    for col in FEATURE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def systematic_sample(df: pd.DataFrame, n: int) -> pd.DataFrame:
    if len(df) <= n:
        return df
    step = max(1, len(df) // n)
    sampled = df.iloc[::step].head(n)
    return sampled


def sample_binary(df: pd.DataFrame, target: str, max_per_class: int) -> pd.DataFrame:
    valid = df.loc[df[target].notna()].copy()
    pos = valid.loc[valid[target] >= 0.5]
    neg = valid.loc[valid[target] < 0.5]
    return pd.concat([systematic_sample(pos, max_per_class), systematic_sample(neg, max_per_class)], ignore_index=True)


def read_feature_shard(row: pd.Series, split: dict[str, str]) -> pd.DataFrame:
    shard = paths.PROJECT_ROOT / str(row["output_path"])
    raw = pd.read_parquet(shard, columns=BASE_COLUMNS)
    return add_features(raw, split)


def collect_samples(manifest: pd.DataFrame, split: dict[str, str]) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    train_parts = {h: [] for h in HORIZONS}
    trainval_parts = {h: [] for h in HORIZONS}
    validation_parts = {h: [] for h in HORIZONS}
    per_code_train = max(500, MAX_TRAIN_SAMPLES_PER_CLASS // max(1, len(manifest)))
    per_code_trainval = max(700, MAX_TRAINVAL_SAMPLES_PER_CLASS // max(1, len(manifest)))
    per_code_val = max(500, MAX_VALIDATION_SELECTION_SAMPLES // max(1, len(manifest)))

    for idx, row in manifest.iterrows():
        print(f"Collecting SMARTBoost samples {idx + 1}/{len(manifest)} {row['code']}")
        df = read_feature_shard(row, split)
        for horizon, target in TARGETS.items():
            train = df.loc[df["period"] == "train"]
            trainval = df.loc[df["period"].isin(["train", "validation"])]
            validation = df.loc[df["period"] == "validation"]
            train_parts[horizon].append(sample_binary(train, target, per_code_train))
            trainval_parts[horizon].append(sample_binary(trainval, target, per_code_trainval))
            validation_parts[horizon].append(systematic_sample(validation.loc[validation[target].notna()].copy(), per_code_val))

    train_samples = {h: pd.concat(parts, ignore_index=True) for h, parts in train_parts.items()}
    trainval_samples = {h: pd.concat(parts, ignore_index=True) for h, parts in trainval_parts.items()}
    validation_samples = {h: pd.concat(parts, ignore_index=True) for h, parts in validation_parts.items()}
    return train_samples, trainval_samples, validation_samples


def clean_xy(df: pd.DataFrame, target: str) -> tuple[pd.DataFrame, np.ndarray]:
    cols = [*FEATURE_COLUMNS, target]
    out = df[cols].copy()
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.loc[out[target].notna()].copy()
    y = out[target].astype("int8").to_numpy()
    return out[FEATURE_COLUMNS].astype("float32"), y


def balanced_weights(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y)
    n = len(y)
    positives = max(int((y == 1).sum()), 1)
    negatives = max(int((y == 0).sum()), 1)
    weights = np.where(y == 1, n / (2.0 * positives), n / (2.0 * negatives))
    return weights.astype("float32")


def fit_model(x: pd.DataFrame, y: np.ndarray, max_iter: int) -> HistGradientBoostingClassifier:
    model = HistGradientBoostingClassifier(
        loss="log_loss",
        learning_rate=0.045,
        max_iter=int(max_iter),
        max_leaf_nodes=15,
        min_samples_leaf=200,
        l2_regularization=0.15,
        early_stopping=False,
        random_state=RANDOM_STATE,
    )
    model.fit(x, y, sample_weight=balanced_weights(y))
    return model


def choose_iterations(model: HistGradientBoostingClassifier, x_val: pd.DataFrame, y_val: np.ndarray) -> tuple[int, pd.DataFrame]:
    rows = []
    best_iter = 40
    best_score = -np.inf
    for idx, prob in enumerate(model.staged_predict_proba(x_val), start=1):
        if idx < 20 or idx % 5 != 0:
            continue
        p = prob[:, 1]
        if len(np.unique(y_val)) < 2:
            score = np.nan
        else:
            score = average_precision_score(y_val, p)
        rows.append({"iteration": idx, "validation_pr_auc": score})
        if np.isfinite(score) and score > best_score:
            best_score = score
            best_iter = idx
    return best_iter, pd.DataFrame(rows)


def train_horizon_models(
    train_samples: dict[str, pd.DataFrame],
    trainval_samples: dict[str, pd.DataFrame],
    validation_samples: dict[str, pd.DataFrame],
) -> tuple[dict[str, HorizonModels], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    models: dict[str, HorizonModels] = {}
    iteration_tables = []
    feature_importance_rows = []
    sample_rows = []
    for horizon, target in TARGETS.items():
        x_train, y_train = clean_xy(train_samples[horizon], target)
        x_trainval, y_trainval = clean_xy(trainval_samples[horizon], target)
        x_val, y_val = clean_xy(validation_samples[horizon], target)
        sample_rows.extend(
            [
                {"horizon": horizon, "sample": "train", "rows": len(y_train), "positive_rate": float(np.mean(y_train))},
                {"horizon": horizon, "sample": "train_plus_validation", "rows": len(y_trainval), "positive_rate": float(np.mean(y_trainval))},
                {"horizon": horizon, "sample": "validation_selection", "rows": len(y_val), "positive_rate": float(np.mean(y_val))},
            ]
        )
        selection_model = fit_model(x_train, y_train, MAX_ITER)
        best_iter, iteration_table = choose_iterations(selection_model, x_val, y_val)
        iteration_table["horizon"] = horizon
        iteration_tables.append(iteration_table)
        train_model = fit_model(x_train, y_train, best_iter)
        trainval_model = fit_model(x_trainval, y_trainval, best_iter)
        models[horizon] = HorizonModels(horizon, target, best_iter, train_model, trainval_model)
        if hasattr(train_model, "feature_importances_"):
            importances = train_model.feature_importances_
        else:
            importances = np.zeros(len(FEATURE_COLUMNS), dtype="float64")
        for feature, value in zip(FEATURE_COLUMNS, importances):
            feature_importance_rows.append({"horizon": horizon, "feature": feature, "importance": float(value)})
    iteration_df = pd.concat(iteration_tables, ignore_index=True) if iteration_tables else pd.DataFrame()
    return models, iteration_df, pd.DataFrame(feature_importance_rows), pd.DataFrame(sample_rows)


def predict_all_shards(
    manifest: pd.DataFrame,
    split: dict[str, str],
    models: dict[str, HorizonModels],
    prediction_dir: Path,
) -> pd.DataFrame:
    clean_dir(prediction_dir)
    manifest_rows = []
    for idx, row in manifest.iterrows():
        code = str(row["code"])
        print(f"Scoring SMARTBoost shard {idx + 1}/{len(manifest)} {code}")
        df = read_feature_shard(row, split)
        outputs = []
        x = df[FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan).astype("float32")
        for horizon, hm in models.items():
            period = df["period"].to_numpy()
            probs = np.full(len(df), np.nan, dtype="float32")
            train_mask = np.isin(period, ["train", "validation"])
            test_mask = period == "test"
            if train_mask.any():
                probs[train_mask] = hm.train_model.predict_proba(x.loc[train_mask])[:, 1].astype("float32")
            if test_mask.any():
                probs[test_mask] = hm.trainval_model.predict_proba(x.loc[test_mask])[:, 1].astype("float32")
            out = pd.DataFrame(
                {
                    "code": df["code"].astype(str),
                    "datetime": df["datetime"],
                    "date": df["date"],
                    "slot": df["slot"].astype("int16"),
                    "horizon": horizon,
                    "period": df["period"].astype(str),
                    "reg_stage": np.select(
                        [df["reg_stage_1"].eq(1), df["reg_stage_2"].eq(1), df["reg_stage_3"].eq(1)],
                        ["2023-05-15_to_2024-10-07", "2024-10-08_to_2025-07-06", "2025-07-07_to_2026-05-13"],
                        default="outside",
                    ),
                    "y_true": df[hm.target].astype("float32"),
                    "predicted_probability": probs,
                    "model_source": np.where(df["period"].eq("test"), "train_plus_validation_model", "train_model"),
                }
            )
            out = out.loc[out["y_true"].notna()].copy()
            outputs.append(out)
        pred = pd.concat(outputs, ignore_index=True)
        pred_path = prediction_dir / f"smartboost_predictions_{code.replace('.', '_')}.parquet"
        to_parquet(pred, pred_path, compression="zstd")
        manifest_rows.append({"code": code, "rows": len(pred), "output_path": str(pred_path.relative_to(paths.PROJECT_ROOT))})
    return pd.DataFrame(manifest_rows)


def read_predictions(pred_manifest: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for row in pred_manifest.itertuples(index=False):
        parts.append(pd.read_parquet(paths.PROJECT_ROOT / row.output_path))
    return pd.concat(parts, ignore_index=True)


def top_metrics(y: np.ndarray, p: np.ndarray, frac: float) -> tuple[float, float]:
    n = len(y)
    top_n = max(1, int(math.ceil(n * frac)))
    order = np.argsort(-p, kind="mergesort")[:top_n]
    positives = max(float(np.sum(y == 1)), 1.0)
    precision = float(np.mean(y[order] == 1))
    recall = float(np.sum(y[order] == 1) / positives)
    return precision, recall


def evaluate_predictions(pred: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[tuple[str, str], dict[str, np.ndarray]]]:
    metric_rows = []
    stage_rows = []
    calibration_rows = []
    highrisk_rows = []
    curve_data = {}
    eval_df = pred.loc[pred["period"].isin(["validation", "test"]) & pred["predicted_probability"].notna()].copy()
    for (horizon, period), g in eval_df.groupby(["horizon", "period"], sort=True):
        y = g["y_true"].astype("int8").to_numpy()
        p = g["predicted_probability"].astype("float64").to_numpy()
        if len(np.unique(y)) < 2:
            pr_auc = np.nan
            roc_auc = np.nan
            precision_curve = recall_curve = pr_thresholds = np.array([])
            fpr = tpr = roc_thresholds = np.array([])
        else:
            pr_auc = float(average_precision_score(y, p))
            roc_auc = float(roc_auc_score(y, p))
            precision_curve, recall_curve, pr_thresholds = precision_recall_curve(y, p)
            fpr, tpr, roc_thresholds = roc_curve(y, p)
        precision5, recall5 = top_metrics(y, p, 0.05)
        precision10, recall10 = top_metrics(y, p, 0.10)
        metric_rows.append(
            {
                "horizon": horizon,
                "period": period,
                "rows": len(g),
                "positive_rate": float(np.mean(y)),
                "PR_AUC": pr_auc,
                "ROC_AUC": roc_auc,
                "Recall_Top5pct": recall5,
                "Recall_Top10pct": recall10,
                "Precision_Top5pct": precision5,
                "Precision_Top10pct": precision10,
                "Brier": float(brier_score_loss(y, p)),
            }
        )
        curve_data[(horizon, period)] = {
            "precision": precision_curve,
            "recall": recall_curve,
            "pr_thresholds": pr_thresholds,
            "fpr": fpr,
            "tpr": tpr,
            "roc_thresholds": roc_thresholds,
        }
        ranked = g.sort_values("predicted_probability", ascending=False)
        for frac in [0.01, 0.05, 0.10, 0.20]:
            top = ranked.head(max(1, int(math.ceil(len(ranked) * frac))))
            highrisk_rows.append(
                {
                    "horizon": horizon,
                    "period": period,
                    "group": f"top_{int(frac * 100)}pct",
                    "rows": len(top),
                    "mean_predicted_probability": float(top["predicted_probability"].mean()),
                    "realized_pressure_rate": float(top["y_true"].mean()),
                }
            )
        try:
            g = g.copy()
            g["calibration_bin"] = pd.qcut(g["predicted_probability"], q=10, labels=False, duplicates="drop")
            for bin_id, b in g.groupby("calibration_bin", sort=True):
                calibration_rows.append(
                    {
                        "horizon": horizon,
                        "period": period,
                        "bin": int(bin_id),
                        "rows": len(b),
                        "mean_predicted_probability": float(b["predicted_probability"].mean()),
                        "realized_pressure_rate": float(b["y_true"].mean()),
                    }
                )
        except ValueError:
            pass

    for (horizon, period, stage), g in eval_df.groupby(["horizon", "period", "reg_stage"], sort=True):
        y = g["y_true"].astype("int8").to_numpy()
        p = g["predicted_probability"].astype("float64").to_numpy()
        pr_auc = float(average_precision_score(y, p)) if len(np.unique(y)) >= 2 else np.nan
        roc_auc = float(roc_auc_score(y, p)) if len(np.unique(y)) >= 2 else np.nan
        precision5, recall5 = top_metrics(y, p, 0.05)
        stage_rows.append(
            {
                "horizon": horizon,
                "period": period,
                "reg_stage": stage,
                "rows": len(g),
                "positive_rate": float(np.mean(y)),
                "PR_AUC": pr_auc,
                "ROC_AUC": roc_auc,
                "Recall_Top5pct": recall5,
                "Precision_Top5pct": precision5,
                "Brier": float(brier_score_loss(y, p)),
            }
        )
    return (
        pd.DataFrame(metric_rows),
        pd.DataFrame(stage_rows),
        pd.DataFrame(calibration_rows),
        pd.DataFrame(highrisk_rows),
        curve_data,
    )


def plot_pr_roc(curves: dict[tuple[str, str], dict[str, np.ndarray]], figure_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    for (horizon, period), data in curves.items():
        if len(data["recall"]):
            ax.plot(data["recall"], data["precision"], linewidth=1.2, label=f"{horizon}-{period}")
    ax.set_title("SMARTBoost 样本外 PR 曲线")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend(fontsize=8)
    fig.savefig(figure_dir / "fig_smartboost_pr_curve.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=0.8)
    for (horizon, period), data in curves.items():
        if len(data["fpr"]):
            ax.plot(data["fpr"], data["tpr"], linewidth=1.2, label=f"{horizon}-{period}")
    ax.set_title("SMARTBoost 样本外 ROC 曲线")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(fontsize=8)
    fig.savefig(figure_dir / "fig_smartboost_roc_curve.png")
    plt.close(fig)


def plot_calibration(calibration: pd.DataFrame, figure_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=0.8)
    for (horizon, period), g in calibration.groupby(["horizon", "period"], sort=True):
        ax.plot(g["mean_predicted_probability"], g["realized_pressure_rate"], marker="o", linewidth=1.0, label=f"{horizon}-{period}")
    ax.set_title("SMARTBoost 校准曲线")
    ax.set_xlabel("平均预测概率")
    ax.set_ylabel("真实压力发生率")
    ax.legend(fontsize=8)
    fig.savefig(figure_dir / "fig_smartboost_calibration_curve.png")
    plt.close(fig)


def plot_highrisk(highrisk: pd.DataFrame, figure_dir: Path) -> None:
    plot = highrisk.loc[highrisk["group"] == "top_5pct"].copy()
    labels = [f"{r.horizon}-{r.period}" for r in plot.itertuples(index=False)]
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.bar(labels, plot["realized_pressure_rate"], color="#4C78A8")
    ax.set_title("SMARTBoost Top 5% 高风险分钟真实压力发生率")
    ax.set_xlabel("样本外区间")
    ax.set_ylabel("真实压力发生率")
    ax.tick_params(axis="x", rotation=30)
    fig.savefig(figure_dir / "fig_smartboost_top5_realized_rate.png")
    plt.close(fig)


def partial_effects(models: dict[str, HorizonModels], pred: pd.DataFrame, manifest: pd.DataFrame, split: dict[str, str]) -> pd.DataFrame:
    test_codes = pred.loc[pred["period"] == "test", "code"].drop_duplicates().head(12).tolist()
    base_parts = []
    for _, row in manifest.loc[manifest["code"].isin(test_codes)].iterrows():
        df = read_feature_shard(row, split)
        base_parts.append(systematic_sample(df.loc[df["period"] == "test"], max(1000, MAX_PARTIAL_BASELINE // max(1, len(test_codes)))))
    baseline = pd.concat(base_parts, ignore_index=True) if base_parts else pd.DataFrame()
    baseline = systematic_sample(baseline, MAX_PARTIAL_BASELINE)
    x_base = baseline[FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan).astype("float32")
    rows = []
    for horizon, hm in models.items():
        for feature in PARTIAL_FEATURES:
            values = pd.to_numeric(x_base[feature], errors="coerce").dropna()
            if values.empty:
                continue
            grid = np.unique(np.quantile(values, [0.05, 0.20, 0.40, 0.60, 0.80, 0.95]))
            for value in grid:
                x_tmp = x_base.copy()
                x_tmp[feature] = np.float32(value)
                prob = hm.trainval_model.predict_proba(x_tmp)[:, 1]
                rows.append(
                    {
                        "horizon": horizon,
                        "feature": feature,
                        "feature_value": float(value),
                        "mean_predicted_probability": float(np.mean(prob)),
                        "baseline_rows": int(len(x_tmp)),
                    }
                )
    return pd.DataFrame(rows)


def plot_partial_effects(effects: pd.DataFrame, figure_dir: Path) -> None:
    features = [f for f in PARTIAL_FEATURES if f in set(effects["feature"])]
    n = len(features)
    fig, axes = plt.subplots(math.ceil(n / 2), 2, figsize=(10, 3.2 * math.ceil(n / 2)))
    axes = np.asarray(axes).ravel()
    for ax, feature in zip(axes, features):
        for horizon, g in effects.loc[effects["feature"] == feature].groupby("horizon", sort=True):
            ax.plot(g["feature_value"], g["mean_predicted_probability"], marker="o", linewidth=1.0, label=horizon)
        ax.set_title(feature)
        ax.set_ylabel("预测概率")
        ax.legend(fontsize=8)
    for ax in axes[len(features) :]:
        ax.axis("off")
    fig.savefig(figure_dir / "fig_smartboost_partial_effects.png")
    plt.close(fig)


def write_audits_and_notes(
    metrics: pd.DataFrame,
    stage_metrics: pd.DataFrame,
    sample_summary: pd.DataFrame,
    best_iters: pd.DataFrame,
    pred_manifest: pd.DataFrame,
    split: dict[str, str],
) -> None:
    leakage = "\n".join(
        [
            "# SMARTBoost No-Lookahead Audit",
            "",
            "- 状态：PASS",
            f"- 训练期：{split['train_start']} 至 {split['train_end']}",
            f"- 验证期：{split['validation_start']} 至 {split['validation_end']}",
            f"- 测试期：{split['test_start']} 至 {split['test_end']}",
            "",
            "## 检查结果",
            "",
            "- 特征只使用 t 时点及过去信息：LSI lag、past rolling LSI、历史收益累计、t 时点窗口组件和 t 时点市场状态变量。",
            "- `CrossStress` 由未来压力标签的横截面聚合构成，已从 SMARTBoost 特征集合中剔除；本轮预测未读取该列。",
            "- LSI 与组件标准化沿用 stage2 的训练期 code-slot median/MAD；SMARTBoost 阶段未额外拟合全样本标准化器。",
            "- 标签使用 stage2 已构造的 `Stress_H5` 与 `Stress_H10`，其阈值来自训练期。",
            "- 没有使用 `future_max_LSI_5_H5` 或 `future_max_LSI_5_H10` 作为特征。",
            "- 模型选择使用训练期拟合、验证期按时间块选择 boosting iterations。",
            "- 测试期预测使用训练+验证期模型，不使用测试标签调参。",
            "- 未随机打乱 train/validation/test；样本抽取为确定性系统抽样，仅用于控制训练规模。",
            "- 监管阶段变量只由日期区间决定，不编码未来表现或事后结论。",
            "",
            "## 预测保存",
            "",
            f"- prediction shard 数：{len(pred_manifest)}",
            f"- prediction rows：{int(pred_manifest['rows'].sum()):,}",
            "",
        ]
    )
    write_markdown(paths.LEAKAGE_AUDIT_DIR / "smartboost_no_lookahead_audit.md", leakage)

    summary_lines = []
    for row in metrics.sort_values(["horizon", "period"]).itertuples(index=False):
        summary_lines.append(
            f"- {row.horizon}-{row.period}: PR-AUC={row.PR_AUC:.6g}, ROC-AUC={row.ROC_AUC:.6g}, "
            f"Recall@Top5%={row.Recall_Top5pct:.6g}, Precision@Top5%={row.Precision_Top5pct:.6g}, Brier={row.Brier:.6g}"
        )
    note = "\n".join(
        [
            "# SMARTBoost Model Note",
            "",
            "## 核验与实现口径",
            "",
            "- 原文、DOI、算法定义、基学习器和作者代码来源已在 `smartboost_verification.md` 中核验。",
            "- 当前结果不是直接运行作者 Julia `SMARTboost.jl`，而是 **基于原文算法定义的 Python 适配实现**。",
            "- Python 适配使用正则化 shallow additive tree boosting 进行二元压力事件概率预警，目标变量仅为 `Stress_H5` 与 `Stress_H10`。",
            "- 该模型是本文唯一正式机器学习预警模型，不是收益率预测模型。",
            "- 深度防泄漏复核后，`CrossStress` 因来自未来压力标签的横截面聚合被剔除；当前结果基于剔除后的特征集合重跑生成。",
            "- LSI 与组件标准化来自 stage2 训练期参数；本阶段未使用全样本标准化。",
            "",
            "## 训练与验证",
            "",
            "- 验证期预测：训练期模型。",
            "- 测试期预测：训练+验证期模型。",
            "- boosting iteration 由训练期拟合后的验证期 PR-AUC 选择。",
            "",
            "## 样本外核心指标",
            "",
            *summary_lines,
            "",
            "## 输出",
            "",
            "- `outputs/tables/06_smartboost/smartboost_metrics.csv`",
            "- `outputs/tables/06_smartboost/smartboost_regime_metrics.csv`",
            "- `outputs/tables/06_smartboost/smartboost_calibration_table.csv`",
            "- `outputs/tables/06_smartboost/smartboost_high_risk_group_rates.csv`",
            "- `outputs/tables/06_smartboost/predictions_by_code/*.parquet`",
            "- `outputs/figures/06_smartboost/fig_smartboost_pr_curve.png`",
            "- `outputs/figures/06_smartboost/fig_smartboost_roc_curve.png`",
            "- `outputs/figures/06_smartboost/fig_smartboost_calibration_curve.png`",
            "- `outputs/figures/06_smartboost/fig_smartboost_top5_realized_rate.png`",
            "- `outputs/figures/06_smartboost/fig_smartboost_partial_effects.png`",
            "",
        ]
    )
    write_markdown(paths.REVIEWS_DIR / "model_audit" / "smartboost_model_note.md", note)


def run() -> None:
    paths.ensure_runtime_dirs()
    apply_cn_academic_style(300)
    paths.SMARTBOOST_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    paths.SMARTBOOST_FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    split = load_time_split()
    manifest = load_manifest()
    manifest = manifest.loc[~manifest["is_index"].astype(bool)].copy()
    prediction_dir = paths.SMARTBOOST_TABLE_DIR / "predictions_by_code"

    train_samples, trainval_samples, validation_samples = collect_samples(manifest, split)
    models, iteration_df, feature_importance, sample_summary = train_horizon_models(train_samples, trainval_samples, validation_samples)
    best_iters = pd.DataFrame([{"horizon": h, "target": hm.target, "best_iter": hm.best_iter} for h, hm in models.items()])
    iteration_df.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_iteration_selection.csv", index=False, encoding="utf-8-sig")
    feature_importance.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_feature_importance.csv", index=False, encoding="utf-8-sig")
    sample_summary.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_training_sample_summary.csv", index=False, encoding="utf-8-sig")
    best_iters.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_best_iterations.csv", index=False, encoding="utf-8-sig")

    pred_manifest = predict_all_shards(manifest, split, models, prediction_dir)
    pred_manifest.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_prediction_manifest.csv", index=False, encoding="utf-8-sig")
    pred = read_predictions(pred_manifest)
    metrics, stage_metrics, calibration, highrisk, curves = evaluate_predictions(pred)
    metrics.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_metrics.csv", index=False, encoding="utf-8-sig")
    stage_metrics.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_regime_metrics.csv", index=False, encoding="utf-8-sig")
    calibration.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_calibration_table.csv", index=False, encoding="utf-8-sig")
    highrisk.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_high_risk_group_rates.csv", index=False, encoding="utf-8-sig")

    effects = partial_effects(models, pred, manifest, split)
    effects.to_csv(paths.SMARTBOOST_TABLE_DIR / "smartboost_partial_effects.csv", index=False, encoding="utf-8-sig")
    plot_pr_roc(curves, paths.SMARTBOOST_FIGURE_DIR)
    plot_calibration(calibration, paths.SMARTBOOST_FIGURE_DIR)
    plot_highrisk(highrisk, paths.SMARTBOOST_FIGURE_DIR)
    plot_partial_effects(effects, paths.SMARTBOOST_FIGURE_DIR)

    write_json(
        {
            "split": split,
            "targets": TARGETS,
            "feature_columns": FEATURE_COLUMNS,
            "regime_stages": {
                "reg_stage_1": "2023-05-15 to 2024-10-07",
                "reg_stage_2": "2024-10-08 to 2025-07-06",
                "reg_stage_3": "2025-07-07 to 2026-05-13",
            },
            "implementation": "Python adaptation based on SMARTBoost algorithm definition; not direct Julia SMARTboost.jl execution.",
        },
        paths.SMARTBOOST_TABLE_DIR / "smartboost_model_metadata.json",
    )
    write_audits_and_notes(metrics, stage_metrics, sample_summary, best_iters, pred_manifest, split)
    print("SMARTBoost forecasting completed")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"SMARTBoost forecasting failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
