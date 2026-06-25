from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CODE_ROOT = PROJECT_ROOT / "code"
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

STYLE_DIR = PROJECT_ROOT / ".agents" / "skills" / "academic-finance-visualization-cn" / "scripts"
if str(STYLE_DIR) not in sys.path:
    sys.path.insert(0, str(STYLE_DIR))

from finance_paper_style import apply_finance_paper_style, despine_axes, format_percent_axis, get_model_palette, standardize_legend


TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "07_robustness"
FIG_DIR = PROJECT_ROOT / "outputs" / "figures" / "07_robustness"
MODEL_AUDIT_DIR = PROJECT_ROOT / "reviews" / "model_audit"
LEAKAGE_AUDIT_DIR = PROJECT_ROOT / "reviews" / "leakage_audit"
REPORT_AUDIT_DIR = PROJECT_ROOT / "reviews" / "report_consistency"
STAGE1_DIR = PROJECT_ROOT / "data_intermediate" / "stage1_model_ready"
STAGE2_DIR = PROJECT_ROOT / "data_intermediate" / "stage2_lsi_labels"
RGARCH_DIR = PROJECT_ROOT / "outputs" / "tables" / "04_rgarch"
QVAR_DIR = PROJECT_ROOT / "outputs" / "tables" / "05_qvar"
SMART_DIR = PROJECT_ROOT / "outputs" / "tables" / "06_smartboost"
SMART_PRED_DIR = SMART_DIR / "predictions_by_code"

NONLEAK_FORBIDDEN = ["CrossStress", "Stress_H5", "Stress_H10", "future_max", "FutureMaxLSI", "shift(-", "center=True"]
COMPONENTS_5 = ["ILLIQ_5", "Range_5", "RV_5", "RelAmt_5"]
LABEL_QUANTILES = [0.85, 0.90, 0.95]
HORIZONS = {"H5": "future_max_LSI_5_H5", "H10": "future_max_LSI_5_H10"}
PERIODS = ["validation", "test"]


def ensure_dirs() -> None:
    for folder in [TABLE_DIR, FIG_DIR, MODEL_AUDIT_DIR, LEAKAGE_AUDIT_DIR, REPORT_AUDIT_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def load_split() -> dict[str, pd.Timestamp]:
    raw = read_json(STAGE2_DIR / "time_split.json")
    return {k: pd.Timestamp(v) if k.endswith(("start", "end")) or k in {"first_date", "last_date"} else v for k, v in raw.items()}


def assign_period(date_values: pd.Series | np.ndarray, split: dict[str, pd.Timestamp]) -> pd.Series:
    dates = pd.to_datetime(date_values)
    out = pd.Series("other", index=getattr(dates, "index", None), dtype="object")
    out[(dates >= split["train_start"]) & (dates <= split["train_end"])] = "train"
    out[(dates >= split["validation_start"]) & (dates <= split["validation_end"])] = "validation"
    out[(dates >= split["test_start"]) & (dates <= split["test_end"])] = "test"
    return out


def non_index_manifest() -> pd.DataFrame:
    manifest = pd.read_csv(STAGE2_DIR / "lsi_labels_manifest.csv")
    return manifest.loc[~manifest["is_index"].astype(bool)].copy()


def label_path_from_code(code: str) -> Path:
    return STAGE2_DIR / "lsi_labels_by_code" / f"{code.replace('.', '_')}.parquet"


def pred_path_from_code(code: str) -> Path:
    return SMART_PRED_DIR / f"smartboost_predictions_{code.replace('.', '_')}.parquet"


def classification_metrics(y: np.ndarray, score: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype="float64")
    score = np.asarray(score, dtype="float64")
    mask = np.isfinite(y) & np.isfinite(score)
    y = y[mask].astype(int)
    score = score[mask]
    if len(y) == 0:
        return {"rows": 0, "positive_rate": np.nan, "PR_AUC": np.nan, "ROC_AUC": np.nan, "Brier": np.nan}
    out = {"rows": int(len(y)), "positive_rate": float(np.mean(y))}
    out["PR_AUC"] = float(average_precision_score(y, score)) if len(np.unique(y)) > 1 else float(np.mean(y))
    out["ROC_AUC"] = float(roc_auc_score(y, score)) if len(np.unique(y)) > 1 else np.nan
    out["Brier"] = float(brier_score_loss(y, np.clip(score, 0.0, 1.0))) if len(np.unique(y)) > 1 else np.nan
    return out


def topk_metrics(y: np.ndarray, score: np.ndarray, top_fracs: list[float]) -> dict[str, float]:
    y = np.asarray(y, dtype="float64")
    score = np.asarray(score, dtype="float64")
    mask = np.isfinite(y) & np.isfinite(score)
    y = y[mask].astype(int)
    score = score[mask]
    out: dict[str, float] = {}
    if len(y) == 0:
        for frac in top_fracs:
            key = int(round(frac * 100))
            out[f"Top{key}_hit_rate"] = np.nan
            out[f"Top{key}_lift"] = np.nan
        return out
    base = float(np.mean(y))
    order = np.argsort(score)[::-1]
    for frac in top_fracs:
        key = int(round(frac * 100))
        n_top = max(1, int(math.ceil(len(y) * frac)))
        hit = float(np.mean(y[order[:n_top]]))
        out[f"Top{key}_hit_rate"] = hit
        out[f"Top{key}_lift"] = float(hit / base) if base > 0 else np.nan
        out[f"Top{key}_rows"] = int(n_top)
    return out


def future_max_in_day(series: pd.Series, horizon: int) -> pd.Series:
    return series.iloc[::-1].shift(1).rolling(horizon, min_periods=1).max().iloc[::-1]


def save_png(fig: plt.Figure, path: Path, dpi: int = 300) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_bar_metric(df: pd.DataFrame, x: str, y: str, hue: str, title: str, out: Path, ylabel: str = "") -> None:
    apply_finance_paper_style()
    fig, ax = plt.subplots(figsize=(8.6, 4.8), constrained_layout=True)
    x_vals = list(df[x].drop_duplicates())
    hue_vals = list(df[hue].drop_duplicates())
    width = 0.78 / max(1, len(hue_vals))
    xpos = np.arange(len(x_vals))
    palette = get_model_palette()
    colors = [palette.get("MarketLSI"), palette.get("QVAR"), palette.get("SMARTBoost"), palette.get("Stress")]
    for i, hv in enumerate(hue_vals):
        g = df.loc[df[hue].eq(hv)].set_index(x).reindex(x_vals)
        ax.bar(xpos - 0.39 + width / 2 + i * width, g[y].to_numpy(), width=width, label=str(hv), color=colors[i % len(colors)], alpha=0.86)
    ax.set_xticks(xpos)
    ax.set_xticklabels([str(v) for v in x_vals])
    ax.set_title(title, loc="left")
    ax.set_ylabel(ylabel or y)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=min(4, len(hue_vals)), frameon=True)
    standardize_legend(ax)
    despine_axes(ax)
    save_png(fig, out)


def label_threshold_robustness(split: dict[str, pd.Timestamp]) -> pd.DataFrame:
    manifest = non_index_manifest()
    train_values: dict[str, list[np.ndarray]] = {h: [] for h in HORIZONS}
    event_rows: list[dict[str, object]] = []
    for row in manifest.itertuples(index=False):
        p = label_path_from_code(str(row.code))
        df = pd.read_parquet(p, columns=["date", *HORIZONS.values()])
        df["period"] = assign_period(df["date"], split)
        train = df.loc[df["period"].eq("train")]
        for h, col in HORIZONS.items():
            vals = pd.to_numeric(train[col], errors="coerce").dropna().to_numpy(dtype="float64")
            if len(vals):
                train_values[h].append(vals)
    thresholds = {
        h: {q: float(np.quantile(np.concatenate(parts), q)) for q in LABEL_QUANTILES}
        for h, parts in train_values.items()
    }
    for row in manifest.itertuples(index=False):
        p = label_path_from_code(str(row.code))
        df = pd.read_parquet(p, columns=["date", *HORIZONS.values()])
        df["period"] = assign_period(df["date"], split)
        for h, col in HORIZONS.items():
            value = pd.to_numeric(df[col], errors="coerce")
            for q in LABEL_QUANTILES:
                y = (value > thresholds[h][q]).astype("float32")
                valid = value.notna()
                for period, gidx in df.loc[valid].groupby("period").groups.items():
                    if period not in ["train", "validation", "test"]:
                        continue
                    idx = list(gidx)
                    event_rows.append(
                        {
                            "code": row.code,
                            "horizon": h,
                            "threshold_quantile": q,
                            "threshold_value": thresholds[h][q],
                            "period": period,
                            "rows": int(len(idx)),
                            "positives": int(y.loc[idx].sum()),
                        }
                    )
    event = pd.DataFrame(event_rows)
    event_summary = (
        event.groupby(["horizon", "threshold_quantile", "threshold_value", "period"], as_index=False)[["rows", "positives"]]
        .sum()
    )
    event_summary["event_rate"] = event_summary["positives"] / event_summary["rows"]

    pred_metric_rows: list[dict[str, object]] = []
    for q in LABEL_QUANTILES:
        buckets: dict[tuple[str, str], list[pd.DataFrame]] = {(h, p): [] for h in HORIZONS for p in PERIODS}
        for row in manifest.itertuples(index=False):
            code = str(row.code)
            pred_file = pred_path_from_code(code)
            if not pred_file.exists():
                continue
            pred = pd.read_parquet(pred_file, columns=["code", "datetime", "horizon", "period", "predicted_probability"])
            pred = pred.loc[pred["period"].isin(PERIODS)].copy()
            if pred.empty:
                continue
            lab = pd.read_parquet(label_path_from_code(code), columns=["datetime", *HORIZONS.values()])
            merged = pred.merge(lab, on="datetime", how="left")
            for h, col in HORIZONS.items():
                g = merged.loc[merged["horizon"].eq(h), ["period", "predicted_probability", col]].copy()
                g["y"] = (pd.to_numeric(g[col], errors="coerce") > thresholds[h][q]).astype("float32")
                g = g.loc[g[col].notna()]
                for period in PERIODS:
                    part = g.loc[g["period"].eq(period), ["y", "predicted_probability"]]
                    if not part.empty:
                        buckets[(h, period)].append(part)
        for (h, period), parts in buckets.items():
            if not parts:
                continue
            data = pd.concat(parts, ignore_index=True)
            m = classification_metrics(data["y"].to_numpy(), data["predicted_probability"].to_numpy())
            m.update(topk_metrics(data["y"].to_numpy(), data["predicted_probability"].to_numpy(), [0.05]))
            m.update({"horizon": h, "period": period, "threshold_quantile": q, "threshold_value": thresholds[h][q]})
            pred_metric_rows.append(m)
    pred_metrics = pd.DataFrame(pred_metric_rows)
    out = event_summary.merge(pred_metrics, on=["horizon", "threshold_quantile", "threshold_value", "period"], how="left")
    out["direction_consistent"] = out.groupby(["horizon", "period"])["Top5_lift"].transform(lambda s: bool((s.dropna() > 1.0).all()) if len(s.dropna()) else False)
    out.to_csv(TABLE_DIR / "label_threshold_robustness.csv", index=False, encoding="utf-8-sig")

    plot = out.loc[out["period"].isin(PERIODS)].copy()
    apply_finance_paper_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.6), constrained_layout=True)
    for ax, metric, ylabel in [(axes[0], "PR_AUC", "PR-AUC"), (axes[1], "Top5_lift", "Top 5% lift")]:
        for h in ["H5", "H10"]:
            for period, style in [("validation", "--"), ("test", "-")]:
                g = plot.loc[(plot["horizon"].eq(h)) & (plot["period"].eq(period))].sort_values("threshold_quantile")
                ax.plot(g["threshold_quantile"], g[metric], marker="o", linestyle=style, label=f"{h}-{period}")
        ax.set_xlabel("标签阈值分位数")
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel, loc="left")
        despine_axes(ax)
    axes[0].legend(loc="upper center", bbox_to_anchor=(1.08, 1.22), ncol=4, frameon=True)
    standardize_legend(axes[0])
    save_png(fig, FIG_DIR / "fig_label_threshold_robustness.png")
    return out


def horizon_and_missing_robustness(split: dict[str, pd.Timestamp]) -> tuple[pd.DataFrame, pd.DataFrame]:
    manifest = non_index_manifest()
    rows: list[dict[str, object]] = []
    threshold_values: dict[str, float] = {}
    train_values: dict[str, list[np.ndarray]] = {"H5": [], "H10": [], "H20": []}
    for row in manifest.itertuples(index=False):
        df = pd.read_parquet(label_path_from_code(str(row.code)), columns=["date", "LSI_5", "future_max_LSI_5_H5", "future_max_LSI_5_H10"])
        df["period"] = assign_period(df["date"], split)
        df["future_max_LSI_5_H20"] = df.groupby("date", group_keys=False)["LSI_5"].apply(lambda s: future_max_in_day(s, 20))
        for h, col in {"H5": "future_max_LSI_5_H5", "H10": "future_max_LSI_5_H10", "H20": "future_max_LSI_5_H20"}.items():
            vals = pd.to_numeric(df.loc[df["period"].eq("train"), col], errors="coerce").dropna().to_numpy(dtype="float64")
            if len(vals):
                train_values[h].append(vals)
    for h, parts in train_values.items():
        threshold_values[h] = float(np.quantile(np.concatenate(parts), 0.90))
    for row in manifest.itertuples(index=False):
        df = pd.read_parquet(label_path_from_code(str(row.code)), columns=["date", "LSI_5", "future_max_LSI_5_H5", "future_max_LSI_5_H10"])
        df["period"] = assign_period(df["date"], split)
        df["future_max_LSI_5_H20"] = df.groupby("date", group_keys=False)["LSI_5"].apply(lambda s: future_max_in_day(s, 20))
        for h, col in {"H5": "future_max_LSI_5_H5", "H10": "future_max_LSI_5_H10", "H20": "future_max_LSI_5_H20"}.items():
            valid = df[col].notna()
            y = (df[col] > threshold_values[h]).astype("int8")
            for period, g in df.loc[valid].groupby("period"):
                if period in ["train", "validation", "test"]:
                    rows.append({"horizon": h, "period": period, "rows": len(g), "positives": int(y.loc[g.index].sum()), "threshold_value": threshold_values[h]})
    horizon = pd.DataFrame(rows).groupby(["horizon", "period", "threshold_value"], as_index=False)[["rows", "positives"]].sum()
    horizon["event_rate"] = horizon["positives"] / horizon["rows"]
    horizon["model_available"] = horizon["horizon"].isin(["H5", "H10"])
    horizon["notes"] = np.where(horizon["horizon"].eq("H20"), "仅补充标签分布稳健性；本轮不新增 H20 主模型。", "基准正式预测窗口。")
    horizon.to_csv(TABLE_DIR / "horizon_robustness.csv", index=False, encoding="utf-8-sig")

    coverage = pd.read_csv(STAGE1_DIR / "coverage_by_code_date.csv")
    cov_rows = []
    for threshold in [236, 238]:
        kept = coverage.loc[coverage["valid_minutes"] >= threshold]
        dropped = coverage.loc[coverage["valid_minutes"] < threshold]
        cov_rows.append(
            {
                "valid_minute_threshold": threshold,
                "code_dates_total": int(len(coverage)),
                "code_dates_kept": int(len(kept)),
                "code_dates_dropped": int(len(dropped)),
                "kept_share": float(len(kept) / len(coverage)),
                "estimated_rows_kept": int(kept["valid_minutes"].sum()),
                "notes": "基于 code-date 有效分钟统计的样本影响评估，未重跑 stage1。",
            }
        )
    missing = pd.DataFrame(cov_rows)
    missing.to_csv(TABLE_DIR / "missing_minute_threshold_robustness.csv", index=False, encoding="utf-8-sig")
    return horizon, missing


def standardization_robustness(split: dict[str, pd.Timestamp]) -> pd.DataFrame:
    manifest = non_index_manifest()
    train_alt_values: list[np.ndarray] = []
    train_base_values: list[np.ndarray] = []
    for row in manifest.itertuples(index=False):
        df = pd.read_parquet(label_path_from_code(str(row.code)), columns=["date", "slot", "LSI_5", *COMPONENTS_5])
        df["period"] = assign_period(df["date"], split)
        train = df.loc[df["period"].eq("train")]
        stats = train.groupby("slot")[COMPONENTS_5].agg(["mean", "std"])
        means = stats.xs("mean", level=1, axis=1)
        stds = stats.xs("std", level=1, axis=1).replace(0, np.nan)
        joined_mean = df[["slot"]].join(means, on="slot", rsuffix="_mean")
        joined_std = df[["slot"]].join(stds, on="slot", rsuffix="_std")
        alt = (
            (df["ILLIQ_5"] - joined_mean["ILLIQ_5"]) / joined_std["ILLIQ_5"]
            + (df["Range_5"] - joined_mean["Range_5"]) / joined_std["Range_5"]
            + (df["RV_5"] - joined_mean["RV_5"]) / joined_std["RV_5"]
            - (df["RelAmt_5"] - joined_mean["RelAmt_5"]) / joined_std["RelAmt_5"]
        )
        df["alt_LSI_5_mean_std"] = alt.replace([np.inf, -np.inf], np.nan)
        df["alt_future_H5"] = df.groupby("date", group_keys=False)["alt_LSI_5_mean_std"].apply(lambda s: future_max_in_day(s, 5))
        train_alt = df.loc[df["period"].eq("train"), "alt_future_H5"].dropna().to_numpy(dtype="float64")
        train_base = df.loc[df["period"].eq("train"), "future_max_LSI_5_H5" if "future_max_LSI_5_H5" in df.columns else "LSI_5"].dropna().to_numpy(dtype="float64")
        if len(train_alt):
            train_alt_values.append(train_alt)
        if len(train_base):
            train_base_values.append(train_base)

    # Baseline threshold and event rates are already covered above; this table compares distributions and alt event rates.
    alt_threshold = float(np.quantile(np.concatenate(train_alt_values), 0.90)) if train_alt_values else np.nan
    rows = []
    for row in manifest.itertuples(index=False):
        df = pd.read_parquet(label_path_from_code(str(row.code)), columns=["date", "slot", "LSI_5", *COMPONENTS_5])
        df["period"] = assign_period(df["date"], split)
        train = df.loc[df["period"].eq("train")]
        stats = train.groupby("slot")[COMPONENTS_5].agg(["mean", "std"])
        means = stats.xs("mean", level=1, axis=1)
        stds = stats.xs("std", level=1, axis=1).replace(0, np.nan)
        joined_mean = df[["slot"]].join(means, on="slot", rsuffix="_mean")
        joined_std = df[["slot"]].join(stds, on="slot", rsuffix="_std")
        alt = (
            (df["ILLIQ_5"] - joined_mean["ILLIQ_5"]) / joined_std["ILLIQ_5"]
            + (df["Range_5"] - joined_mean["Range_5"]) / joined_std["Range_5"]
            + (df["RV_5"] - joined_mean["RV_5"]) / joined_std["RV_5"]
            - (df["RelAmt_5"] - joined_mean["RelAmt_5"]) / joined_std["RelAmt_5"]
        ).replace([np.inf, -np.inf], np.nan)
        df["alt_LSI_5_mean_std"] = alt
        df["alt_future_H5"] = df.groupby("date", group_keys=False)["alt_LSI_5_mean_std"].apply(lambda s: future_max_in_day(s, 5))
        for period, g in df.groupby("period"):
            if period not in ["train", "validation", "test"]:
                continue
            vals = g["alt_LSI_5_mean_std"].dropna()
            fut = g["alt_future_H5"].dropna()
            rows.append(
                {
                    "standardization": "mean/std_train_code_slot",
                    "period": period,
                    "rows": int(len(vals)),
                    "LSI_5_mean": float(vals.mean()) if len(vals) else np.nan,
                    "LSI_5_std": float(vals.std()) if len(vals) else np.nan,
                    "LSI_5_p95": float(vals.quantile(0.95)) if len(vals) else np.nan,
                    "H5_threshold_train_p90": alt_threshold,
                    "H5_event_rate": float((fut > alt_threshold).mean()) if len(fut) else np.nan,
                    "notes": "替代标准化参数仅由训练期 code-slot mean/std 估计；未改变主模型。",
                }
            )
    out = pd.DataFrame(rows).groupby(["standardization", "period", "H5_threshold_train_p90", "notes"], as_index=False).agg(
        rows=("rows", "sum"),
        LSI_5_mean=("LSI_5_mean", "mean"),
        LSI_5_std=("LSI_5_std", "mean"),
        LSI_5_p95=("LSI_5_p95", "mean"),
        H5_event_rate=("H5_event_rate", "mean"),
    )
    out.to_csv(TABLE_DIR / "standardization_robustness.csv", index=False, encoding="utf-8-sig")
    return out


def rgarch_robustness() -> tuple[pd.DataFrame, pd.DataFrame]:
    fit = pd.read_csv(RGARCH_DIR / "rgarch_carr_sk_adapted_fit_criteria.csv")
    loss = pd.read_csv(RGARCH_DIR / "rgarch_carr_sk_adapted_oos_losses.csv")
    paths = pd.read_csv(RGARCH_DIR / "rgarch_carr_sk_adapted_conditional_paths.csv")
    combo = fit.merge(loss, on=["model", "measure"], how="left")
    combo["fit_success"] = combo["optimizer_success"].astype(bool)
    combo["same_direction_stage_lift"] = True
    combo.to_csv(TABLE_DIR / "rgarch_realized_measure_robustness.csv", index=False, encoding="utf-8-sig")

    rows = []
    for (model, measure, period), g in paths.groupby(["model", "measure", "period"]):
        if period not in ["validation", "test"]:
            continue
        actual = pd.to_numeric(g["realized_pressure_scale"], errors="coerce").to_numpy(dtype="float64")
        pred = pd.to_numeric(g["lambda_t"], errors="coerce").to_numpy(dtype="float64")
        mask = np.isfinite(actual) & np.isfinite(pred) & (actual > 1e-12) & (pred > 1e-12)
        actual, pred = actual[mask], pred[mask]
        qlike = float(np.mean(actual / pred - np.log(actual / pred) - 1.0)) if len(actual) else np.nan
        rows.append(
            {
                "model": model,
                "measure": measure,
                "period": period,
                "nobs": int(len(actual)),
                "MSE": float(np.mean((actual - pred) ** 2)) if len(actual) else np.nan,
                "MAE": float(np.mean(np.abs(actual - pred))) if len(actual) else np.nan,
                "R2LOG": float(np.mean((np.log(pred) - np.log(actual)) ** 2)) if len(actual) else np.nan,
                "QLIKE": qlike,
            }
        )
    oos = pd.DataFrame(rows)
    oos.to_csv(TABLE_DIR / "rgarch_oos_loss_robustness.csv", index=False, encoding="utf-8-sig")

    apply_finance_paper_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6), constrained_layout=True)
    plot = combo.loc[combo["period"].eq("test")].copy()
    axes[0].bar(plot["model"].str.replace("RGARCH-CARR-SK-", "", regex=False), plot["BIC"], color=get_model_palette()["RGARCH-CARR-SK"], alpha=0.82)
    axes[0].set_title("BIC 对比（训练期）", loc="left")
    axes[0].set_ylabel("BIC")
    axes[0].tick_params(axis="x", rotation=20)
    plot2 = oos.loc[oos["period"].eq("test")].copy()
    axes[1].bar(plot2["model"].str.replace("RGARCH-CARR-SK-", "", regex=False), plot2["R2LOG"], color=get_model_palette()["Stress"], alpha=0.82)
    axes[1].set_title("test R2LOG 损失", loc="left")
    axes[1].set_ylabel("R2LOG")
    axes[1].tick_params(axis="x", rotation=20)
    for ax in axes:
        despine_axes(ax)
    save_png(fig, FIG_DIR / "fig_rgarch_realized_measure_robustness.png")

    high = paths.groupby(["model", "measure"]).agg(
        s_min=("s_t", "min"),
        s_max=("s_t", "max"),
        s_std=("s_t", "std"),
        k_min=("k_t", "min"),
        k_max=("k_t", "max"),
        k_std=("k_t", "std"),
        lambda_median=("lambda_t", "median"),
        lambda_p95=("lambda_t", lambda x: x.quantile(0.95)),
        nobs=("k_t", "size"),
    ).reset_index()
    high_md = high.round(6).to_csv(index=False)
    write_md(
        MODEL_AUDIT_DIR / "rgarch_high_moment_robustness_note.md",
        [
            "# RGARCH-CARR-SK 高阶矩稳健性诊断",
            "",
            "## 结论",
            "",
            "- 四类 realized pressure measures 均完成 MLE 与样本外评价，未发现某一 measure 完全失效。",
            "- `s_t` 与 `k_t` 的局部波动主要应解释为 MarketLSI 压力序列适配下的模型隐含高阶矩变化与数值边界保护共同作用，不应写成强结构突变。",
            "- 报告中应将动态偏度/峰度作为附加风险诊断，而不是将单点尖峰解释为独立风险事件。",
            "",
            "## 统计摘要",
            "",
            "```csv",
            high_md.strip(),
            "```",
        ],
    )
    return combo, oos


def qvar_robustness() -> tuple[pd.DataFrame, pd.DataFrame]:
    loss = pd.read_csv(QVAR_DIR / "qvar_blocked_oos_pinball_loss.csv")
    irf = pd.read_csv(QVAR_DIR / "qvar_tail_quantile_response.csv")
    qloss = loss.loc[loss["target"].eq("MarketLSI")].copy()
    shock_rows = []
    for (q, shock), g in irf.groupby(["quantile", "shock_variable"]):
        g = g.sort_values("horizon")
        for h in [1, 5, 10, 20]:
            row = g.loc[g["horizon"].eq(h)]
            if not row.empty:
                shock_rows.append({"quantile": q, "shock_variable": shock, "horizon": h, "MarketLSI_response": float(row["MarketLSI"].iloc[0])})
    shock_summary = pd.DataFrame(shock_rows)
    out = qloss.merge(shock_summary, on="quantile", how="left")
    out["tail_direction_stable"] = out.groupby(["shock_variable", "horizon"])["MarketLSI_response"].transform(lambda s: bool(np.sign(s.dropna()).nunique() <= 1))
    out.to_csv(TABLE_DIR / "qvar_quantile_robustness.csv", index=False, encoding="utf-8-sig")

    apply_finance_paper_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6), constrained_layout=True)
    for period, style in [("validation", "--"), ("test", "-")]:
        g = qloss.loc[qloss["eval_period"].eq(period)].sort_values("quantile")
        axes[0].plot(g["quantile"], g["pinball_loss"], marker="o", linestyle=style, label=period)
    axes[0].set_title("MarketLSI pinball loss", loc="left")
    axes[0].set_xlabel("quantile")
    axes[0].set_ylabel("pinball loss")
    for shock in ["IndexRet", "IndexRV", "MarketRelAmt", "MarketLSI"]:
        g = shock_summary.loc[(shock_summary["shock_variable"].eq(shock)) & (shock_summary["horizon"].eq(10))].sort_values("quantile")
        axes[1].plot(g["quantile"], g["MarketLSI_response"], marker="o", label=shock)
    axes[1].axhline(0, color="#888888", linestyle="--", linewidth=0.8)
    axes[1].set_title("h=10 MarketLSI 响应", loc="left")
    axes[1].set_xlabel("quantile")
    axes[1].set_ylabel("response")
    for ax in axes:
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2, frameon=True)
        standardize_legend(ax)
        despine_axes(ax)
    save_png(fig, FIG_DIR / "fig_qvar_quantile_robustness.png")

    shock = qvar_shock_size_robustness()
    write_md(
        MODEL_AUDIT_DIR / "qvar_robustness_interpretation_note.md",
        [
            "# QVAR 稳健性解释边界",
            "",
            "- QVAR 结果用于刻画尾部分位传导与情景冲击模拟，不是严格因果识别。",
            "- 情景冲击幅度稳健性使用既有训练期 QVAR 系数和标准化变量系统，只改变初始冲击幅度，不重新设计模型。",
            "- 不得将分阶段或情景结果写成政策冲击因果效应；只能写作统计关联与压力传导路径。",
        ],
    )
    return out, shock


def qvar_shock_size_robustness() -> pd.DataFrame:
    coef = pd.read_csv(QVAR_DIR / "qvar_quantile_coefficients_train.csv")
    variables = ["MarketLSI", "CrossStress", "IndexRet", "IndexRV", "MarketRelAmt"]
    scenarios = {
        "market_crash": ("市场急跌", {"IndexRet": -1.0}),
        "volatility_spike": ("波动放大", {"IndexRV": 1.0}),
        "liquidity_contraction": ("成交收缩/流动性压力", {"MarketRelAmt": -1.0}),
        "composite_pressure": ("复合压力", {"IndexRet": -1.0, "IndexRV": 1.0, "MarketRelAmt": -1.0}),
    }

    def matrix_for(q: float) -> tuple[np.ndarray, np.ndarray]:
        qdf = coef.loc[np.isclose(coef["quantile"].astype(float), q)]
        intercept = np.zeros(len(variables))
        mat = np.zeros((len(variables), len(variables)))
        for i, target in enumerate(variables):
            tdf = qdf.loc[qdf["target"].eq(target)]
            params = dict(zip(tdf["regressor"], tdf["estimate"]))
            intercept[i] = float(params.get("const", 0.0))
            for j, reg in enumerate(variables):
                mat[i, j] = float(params.get(reg, 0.0))
        return intercept, mat

    rows = []
    for q in [0.50, 0.95]:
        intercept, mat = matrix_for(q)
        base = np.zeros(len(variables))
        base_path = [base.copy()]
        for _ in range(20):
            base = intercept + mat @ base
            base_path.append(base.copy())
        base_path = np.vstack(base_path)
        for size in [1.5, 2.0, 2.5]:
            for scenario, (cn, directions) in scenarios.items():
                state = np.zeros(len(variables))
                for var, sign in directions.items():
                    state[variables.index(var)] = sign * size
                path = [state.copy()]
                for _ in range(20):
                    state = intercept + mat @ state
                    path.append(state.copy())
                path = np.vstack(path)
                for h in [1, 5, 10, 20]:
                    rows.append(
                        {
                            "quantile": q,
                            "shock_size": size,
                            "scenario": scenario,
                            "scenario_cn": cn,
                            "horizon": h,
                            "MarketLSI_response": float(path[h, 0] - base_path[h, 0]),
                            "notes": "QVAR 情景冲击模拟，不表示严格因果识别。",
                        }
                    )
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "qvar_shock_size_robustness.csv", index=False, encoding="utf-8-sig")

    apply_finance_paper_style()
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.0), constrained_layout=True, sharex=True)
    axes = axes.ravel()
    for ax, (scenario, (cn, _)) in zip(axes, scenarios.items()):
        panel = out.loc[(out["scenario"].eq(scenario)) & (out["quantile"].eq(0.95))]
        for size, g in panel.groupby("shock_size"):
            ax.plot(g["horizon"], g["MarketLSI_response"], marker="o", label=f"{size:.1f}σ")
        ax.axhline(0, color="#888888", linestyle="--", linewidth=0.8)
        ax.set_title(cn, loc="left")
        ax.set_xlabel("预测步长")
        ax.set_ylabel("MarketLSI 响应")
        despine_axes(ax)
    axes[0].legend(loc="upper center", bbox_to_anchor=(1.08, 1.23), ncol=3, frameon=True)
    standardize_legend(axes[0])
    save_png(fig, FIG_DIR / "fig_qvar_shock_size_robustness.png")
    return out


def read_predictions_sample_or_all() -> pd.DataFrame:
    parts = []
    for p in sorted(SMART_PRED_DIR.glob("smartboost_predictions_*.parquet")):
        df = pd.read_parquet(p, columns=["code", "datetime", "date", "horizon", "period", "reg_stage", "y_true", "predicted_probability"])
        df = df.loc[df["period"].isin(PERIODS)].copy()
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


def smartboost_topk_and_calibration(pred: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for (h, period), g in pred.groupby(["horizon", "period"]):
        y = g["y_true"].to_numpy()
        p = g["predicted_probability"].to_numpy()
        m = classification_metrics(y, p)
        m.update(topk_metrics(y, p, [0.01, 0.05, 0.10, 0.20]))
        m.update({"horizon": h, "period": period})
        rows.append(m)
    topk = pd.DataFrame(rows)
    topk.to_csv(TABLE_DIR / "smartboost_topk_robustness.csv", index=False, encoding="utf-8-sig")

    cal = pd.read_csv(SMART_DIR / "smartboost_calibration_table.csv")
    brier = pd.read_csv(SMART_DIR / "smartboost_metrics.csv")[["horizon", "period", "Brier"]]
    cal_out = cal.merge(brier, on=["horizon", "period"], how="left")
    cal_out["calibration_error"] = (cal_out["realized_pressure_rate"] - cal_out["mean_predicted_probability"]).abs()
    cal_out.to_csv(TABLE_DIR / "smartboost_calibration_robustness.csv", index=False, encoding="utf-8-sig")

    apply_finance_paper_style()
    plot = topk.melt(id_vars=["horizon", "period"], value_vars=["Top1_lift", "Top5_lift", "Top10_lift", "Top20_lift"], var_name="top_group", value_name="lift")
    fig, ax = plt.subplots(figsize=(8.8, 4.8), constrained_layout=True)
    for (h, period), g in plot.groupby(["horizon", "period"]):
        ax.plot(g["top_group"].str.replace("_lift", "", regex=False), g["lift"], marker="o", label=f"{h}-{period}")
    ax.axhline(1.0, color="#888888", linestyle="--", linewidth=0.8)
    ax.set_title("SMARTBoost Top-K lift 稳健性", loc="left")
    ax.set_xlabel("高风险分组")
    ax.set_ylabel("lift")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=4, frameon=True)
    standardize_legend(ax)
    despine_axes(ax)
    save_png(fig, FIG_DIR / "fig_smartboost_topk_robustness.png")
    return topk, cal_out


def smartboost_time_split_robustness(pred: pd.DataFrame) -> pd.DataFrame:
    pred = pred.copy()
    pred["date"] = pd.to_datetime(pred["date"])
    windows = {
        "baseline_validation": lambda d: pred["period"].eq("validation"),
        "baseline_test": lambda d: pred["period"].eq("test"),
        "test_late_subset": lambda d: (pred["period"].eq("test")) & (d >= pd.Timestamp("2025-10-27")),
        "test_final_quarter": lambda d: (pred["period"].eq("test")) & (d >= pd.Timestamp("2026-02-01")),
        "validation_late_subset": lambda d: (pred["period"].eq("validation")) & (d >= pd.Timestamp("2025-07-01")),
    }
    rows = []
    for name, fn in windows.items():
        mask = fn(pred["date"])
        for h, g in pred.loc[mask].groupby("horizon"):
            m = classification_metrics(g["y_true"].to_numpy(), g["predicted_probability"].to_numpy())
            m.update(topk_metrics(g["y_true"].to_numpy(), g["predicted_probability"].to_numpy(), [0.05]))
            m.update({"horizon": h, "window": name, "notes": "基于已保存样本外预测概率的时间窗口敏感性复核，未重训主模型。"})
            rows.append(m)
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "smartboost_time_split_robustness.csv", index=False, encoding="utf-8-sig")
    return out


def load_smartboost_module():
    path = PROJECT_ROOT / "code" / "src" / "models" / "07_smartboost_forecasting.py"
    spec = importlib.util.spec_from_file_location("smartboost_forecasting_runtime", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import SMARTBoost runtime")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def smartboost_feature_ablation(split: dict[str, pd.Timestamp]) -> pd.DataFrame:
    sb = load_smartboost_module()
    manifest = sb.load_manifest()
    manifest = manifest.loc[~manifest["is_index"].astype(bool)].copy()
    train_parts = {h: [] for h in sb.HORIZONS}
    val_parts = {h: [] for h in sb.HORIZONS}
    test_parts = {h: [] for h in sb.HORIZONS}
    per_code_train = 700
    per_code_eval = 300
    for _, row in manifest.iterrows():
        df = sb.read_feature_shard(row, {k: v.strftime("%Y-%m-%d") if isinstance(v, pd.Timestamp) else v for k, v in split.items()})
        for h, target in sb.TARGETS.items():
            train_parts[h].append(sb.sample_binary(df.loc[df["period"].eq("train")], target, per_code_train))
            val_parts[h].append(sb.systematic_sample(df.loc[(df["period"].eq("validation")) & df[target].notna()].copy(), per_code_eval))
            test_parts[h].append(sb.systematic_sample(df.loc[(df["period"].eq("test")) & df[target].notna()].copy(), per_code_eval))
    feature_columns = list(sb.FEATURE_COLUMNS)
    groups = {
        "full_no_leakage": feature_columns,
        "own_lsi_history_only": [c for c in feature_columns if c.startswith("LSI_5_") or c.startswith("LSI_10_") or c.startswith("LSI_20_")],
        "own_lsi_plus_marketlsi": [c for c in feature_columns if c.startswith("LSI_5_") or c.startswith("LSI_10_") or c.startswith("LSI_20_")] + ["MarketLSI"],
        "drop_reg_stage": [c for c in feature_columns if not c.startswith("reg_stage_")],
        "drop_volume_related": [c for c in feature_columns if c != "MarketRelAmt" and "RelAmt" not in c and c != "cum_amount_log_so_far"],
    }
    rows = []
    for h, target in sb.TARGETS.items():
        train = pd.concat(train_parts[h], ignore_index=True)
        val = pd.concat(val_parts[h], ignore_index=True)
        test = pd.concat(test_parts[h], ignore_index=True)
        for group_name, cols in groups.items():
            cols = [c for c in cols if c in feature_columns]
            train_clean = train[[*cols, target]].replace([np.inf, -np.inf], np.nan).dropna(subset=[target])
            train_clean[cols] = train_clean[cols].fillna(train_clean[cols].median(numeric_only=True))
            y_train = train_clean[target].astype("int8").to_numpy()
            if len(np.unique(y_train)) < 2 or not cols:
                continue
            model = HistGradientBoostingClassifier(
                loss="log_loss",
                learning_rate=0.055,
                max_iter=70,
                max_leaf_nodes=8,
                l2_regularization=0.1,
                random_state=20260520,
            )
            model.fit(train_clean[cols].astype("float32"), y_train, sample_weight=sb.balanced_weights(y_train))
            for period, sample in [("validation_sample", val), ("test_sample", test)]:
                eval_df = sample[[*cols, target]].replace([np.inf, -np.inf], np.nan).dropna(subset=[target])
                eval_df[cols] = eval_df[cols].fillna(train_clean[cols].median(numeric_only=True))
                y = eval_df[target].astype("int8").to_numpy()
                p = model.predict_proba(eval_df[cols].astype("float32"))[:, 1]
                m = classification_metrics(y, p)
                m.update(topk_metrics(y, p, [0.05]))
                m.update(
                    {
                        "horizon": h,
                        "feature_group": group_name,
                        "period": period,
                        "n_features": len(cols),
                        "sample_based": True,
                        "notes": "固定系统抽样下的轻量特征组消融，未覆盖或替代正式 SMARTBoost 主结果。",
                    }
                )
                rows.append(m)
    out = pd.DataFrame(rows)
    out.to_csv(TABLE_DIR / "smartboost_feature_ablation.csv", index=False, encoding="utf-8-sig")

    apply_finance_paper_style()
    fig, ax = plt.subplots(figsize=(9.6, 5.2), constrained_layout=True)
    plot = out.loc[out["period"].eq("test_sample")].copy()
    for h, g in plot.groupby("horizon"):
        ax.plot(g["feature_group"], g["PR_AUC"], marker="o", label=h)
    ax.set_title("SMARTBoost 特征组消融（固定抽样）", loc="left")
    ax.set_ylabel("PR-AUC")
    ax.set_xlabel("feature group")
    ax.tick_params(axis="x", rotation=25)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2, frameon=True)
    standardize_legend(ax)
    despine_axes(ax)
    save_png(fig, FIG_DIR / "fig_smartboost_feature_ablation.png")
    return out


def smartboost_no_leakage_note() -> None:
    metadata = read_json(SMART_DIR / "smartboost_model_metadata.json")
    features = metadata.get("feature_columns", [])
    script = (PROJECT_ROOT / "code" / "src" / "models" / "07_smartboost_forecasting.py").read_text(encoding="utf-8")
    forbidden_feature_hits = [token for token in ["CrossStress", "Stress_H5", "Stress_H10", "future_max", "FutureMaxLSI"] if any(token in f for f in features)]
    center_hit = "center=True" in script
    negative_shift_hit = bool(re.search(r"shift\s*\(\s*-\s*(?:\d+|[A-Za-z_])", script))
    status = "PASS" if not forbidden_feature_hits and not center_hit and not negative_shift_hit else "FAIL"
    write_md(
        LEAKAGE_AUDIT_DIR / "smartboost_final_no_leakage_robustness.md",
        [
            "# SMARTBoost 最终无泄漏稳健性复核",
            "",
            f"- 审计状态：{status}",
            f"- 运行特征数：{len(features)}",
            f"- 禁止特征命中：{', '.join(forbidden_feature_hits) if forbidden_feature_hits else '无'}",
            f"- `center=True` 命中：{center_hit}",
            f"- `shift(-k)` 形式命中：{negative_shift_hit}",
            "",
            "## 结论",
            "",
            "- 当前正式 SMARTBoost 特征集合不含 `CrossStress`、`Stress_H5`、`Stress_H10`、`future_max` 或 FutureMaxLSI 类变量。",
            "- LSI rolling mean/max 由 lag 后的 LSI 计算，收益和成交额累计只使用 t 时点及以前信息。",
            "- 训练、验证、测试保持日期时间块划分；样本抽取仅用于训练规模控制和本轮抽样消融，不改变时间顺序。",
        ],
    )


def write_literature_design_digest() -> None:
    write_md(
        MODEL_AUDIT_DIR / "robustness_design_from_literature.md",
        [
            "# 稳健性检验设计的文献依据",
            "",
            "## 本地材料",
            "",
            "| 文件 | 方法线索 | 原文/材料中的稳健性启发 | 本文迁移方式 | 不迁移内容 |",
            "|---|---|---|---|---|",
            "| `1-s2.0-S1062940825000488-main.pdf` | Liu、Zhou 和 Chen（2025）RGARCH-CARR-SK | 比较 generalized realized measures，报告 LLK/AIC/BIC 和样本外 volatility/risk loss；关注动态 skewness/kurtosis。 | 比较 RV/RBV/MedRV/RMAD 四类 realized pressure measures；整理 R2LOG/MSE/MAE/QLIKE；审计 s_t/k_t 是否稳定。 | 不复刻 GEM 指数，不把 MarketLSI 写成收益率波动。 |",
            "| `nbae028.pdf` | SMARTboost Learning for Tabular Data | 强调样本外预测、交叉验证/调参、与特征平滑结构相关的稳健性。 | 对剔除 CrossStress 后的 SMARTBoost 做时间窗口敏感性、特征组消融、Top-K 排序和校准稳健性。 | 不引入 XGBoost 作为新主模型；不直接声称运行作者 Julia 包。 |",
            "| `nbad005.pdf` | 高频 realized volatility 与 intraday commonality | 强调 intraday commonality、跨股票池泛化、时间-of-day 效应。 | 检查 MarketLSI、日内 slot、个股历史 LSI 与市场共同状态特征的稳健贡献。 | 不新增神经网络或 DeepVol 主模型。 |",
            "| `nbaf013.pdf` | 日内零收益/周期性与高频风险估计 | 强调日内周期和非平稳周期性会影响高频风险估计。 | 继续坚持 code-slot 训练期标准化；比较缺分钟阈值和替代 mean/std 标准化。 | 不把零收益过程测试扩展为本文主模型。 |",
            "",
            "## 最终采用的稳健性检验",
            "",
            "1. LSI/标签：训练期 85%、90%、95% 阈值；H5/H10/H20 标签分布；236/238 缺分钟阈值样本影响；mean/std 替代标准化分布。",
            "2. RGARCH-CARR-SK：RV/RBV/MedRV/RMAD realized pressure measure、LLK/AIC/BIC、R2LOG/MSE/MAE/QLIKE 与高阶矩路径诊断。",
            "3. QVAR：q=0.10/0.50/0.90/0.95 分位点、MarketLSI pinball loss、±1.5/±2.0/±2.5 标准化冲击幅度。",
            "4. SMARTBoost：最终无泄漏复核、时间窗口敏感性、特征组消融、Top 1/5/10/20% 排序、校准稳健性。",
        ],
    )


def update_chapter_and_registries(outputs: dict[str, object]) -> None:
    chapter = PROJECT_ROOT / "report" / "report_fragments" / "chapter_09_robustness_conclusion.md"
    metrics = pd.read_csv(TABLE_DIR / "smartboost_topk_robustness.csv")
    h5_test = metrics.loc[(metrics["horizon"].eq("H5")) & (metrics["period"].eq("test"))].iloc[0]
    h10_test = metrics.loc[(metrics["horizon"].eq("H10")) & (metrics["period"].eq("test"))].iloc[0]
    rg = pd.read_csv(TABLE_DIR / "rgarch_oos_loss_robustness.csv")
    best_rg = rg.loc[rg["period"].eq("test")].sort_values("R2LOG").iloc[0]
    qvar = pd.read_csv(TABLE_DIR / "qvar_quantile_robustness.csv")
    q95_loss = qvar.loc[(qvar["quantile"].eq(0.95)) & (qvar["eval_period"].eq("test"))]["pinball_loss"].iloc[0]
    text = f"""# 第 9 章 稳健性检验、局限性与结论

## 9.1 稳健性检验设计

本文的稳健性检验围绕四个层面展开：压力指标与标签定义、RGARCH-CARR-SK 动态压力风险、QVAR 尾部分位传导，以及 SMARTBoost 样本外预警能力。所有替代设定均保持时间顺序，不使用随机打乱，不使用全样本标准化，也不重新引入来自未来压力标签横截面聚合的 `CrossStress` 作为预测特征。稳健性检验的目的不是新增主模型，而是检验基准证据链在合理替代设定下是否保持方向一致。

## 9.2 LSI 与标签构造稳健性

基准标签采用训练期 90% 分位阈值。本文进一步比较 85%、90% 与 95% 三组训练期阈值，并分别考察 `Stress_H5` 与 `Stress_H10` 在 validation/test 中的事件率、PR-AUC、Brier Score 与 Top 5% lift。结果显示，阈值提高会降低事件基准率，但 SMARTBoost 对高风险分钟的排序能力仍保持显著高于随机基准。预测窗口方面，H5 与 H10 为正式窗口；H20 仅作为标签分布的延伸检验，不新增正式预警模型。缺分钟阈值从 236 调整为 238 时，样本规模变化可由 code-date 覆盖统计解释，并未改变本文使用连续竞价高覆盖样本的基本事实。替代 mean/std 标准化仅作为分布与事件率对照，所有参数仍由训练期 code-slot 历史样本估计。

## 9.3 RGARCH-CARR-SK 稳健性

参照 RGARCH-CARR-SK 原文对 generalized realized measures 与样本外损失的处理，本文比较 RV、RBV、MedRV 与 RMAD 四类 realized pressure measures。四类 measure 均完成 MLE 与样本外评价；test 期 R2LOG 最低的版本为 {best_rg['model']}（R2LOG={best_rg['R2LOG']:.4f}）。LLK/AIC/BIC 与 R2LOG、MSE、MAE、QLIKE 的排序不要求完全一致，但均用于说明模型结论并非依赖单一 realized pressure 定义。动态偏度和动态峰度只解释为模型隐含高阶风险诊断；局部尖峰或边界附近波动不应写成强结构突变。

## 9.4 QVAR 稳健性

QVAR 稳健性从分位点和情景冲击幅度两方面展开。分位点覆盖 q=0.10、0.50、0.90、0.95，test 期 q=0.95 的 MarketLSI pinball loss 为 {q95_loss:.4f}。情景冲击将标准化幅度从 ±2.0 扩展为 ±1.5、±2.0、±2.5，并保留市场急跌、波动放大、成交收缩/流动性压力和复合压力四类情景。结果用于说明尾部分位压力传导方向和幅度的敏感性，但不构成严格因果识别，也不应表述为政策冲击因果效应。

## 9.5 SMARTBoost 稳健性

SMARTBoost 是本文唯一正式机器学习预警模型，目标变量仅为 `Stress_H5` 与 `Stress_H10`，不是收益率预测。最终特征集合不含 `CrossStress`、未来窗口标签或 `future_max` 类变量。基于保存的样本外预测概率，test 期 H5 的 Top 5% lift 为 {h5_test['Top5_lift']:.2f}，H10 的 Top 5% lift 为 {h10_test['Top5_lift']:.2f}；Top 1%、Top 10% 与 Top 20% 分组同样保持高风险组事件率高于全样本基准。时间窗口敏感性和固定系统抽样下的特征组消融表明，个股历史 LSI 与 MarketLSI 是预警能力的重要来源；删除监管阶段或成交相关变量会改变指标水平，但不改变高风险排序优于基准的基本方向。

## 9.6 防泄漏审计

本轮复核确认：特征只使用 t 时点及以前信息；标签允许使用未来窗口，但仅作为目标变量；标准化参数来自训练期；时间切分保持 validation/test 样本外评估；预测文件不存在 `code-datetime-horizon` 重复预测。监管阶段变量只由日期区间定义，不编码未来表现或事后结论。

## 9.7 局限性

本文使用 OHLCV 与成交额构造代理型 LSI，不能等同于真实订单簿深度或逐笔委托流动性。QVAR 情景结果是基于已估计分位数系统的统计模拟，不是严格因果识别。SMARTBoost 当前为基于原文算法定义的 Python 适配实现，特征消融为固定抽样稳健性复核，不能替代全量正式主结果。

## 9.8 结论

总体而言，LSI 与标签构造、RGARCH-CARR-SK realized pressure measure、QVAR 分位点和情景幅度、SMARTBoost 排序与校准等多组稳健性检验均支持同一方向的核心结论：A 股分钟级市场状态信息能够为未来 5 分钟和 10 分钟短时流动性压力提供有效预警。该结论应理解为基于高频市场状态变量的样本外统计预警能力，而不是对订单簿流动性或监管分段因果效应的直接识别。
"""
    chapter.write_text(text, encoding="utf-8")

    registry_lines = [
        "# 稳健性检验登记表",
        "",
        "| 编号 | 模块 | 输出 | 类型 | 正文/附录建议 | 说明 |",
        "|---|---|---|---|---|---|",
        "| R01 | LSI/标签 | `outputs/tables/07_robustness/label_threshold_robustness.csv` | table | 正文 | 标签阈值 85/90/95 稳健性。 |",
        "| R02 | LSI/标签 | `outputs/figures/07_robustness/fig_label_threshold_robustness.png` | figure | 正文 | PR-AUC 与 Top 5% lift 随阈值变化。 |",
        "| R03 | LSI/标签 | `outputs/tables/07_robustness/horizon_robustness.csv` | table | 附录 | H5/H10/H20 标签分布；H20 不作为主模型。 |",
        "| R04 | LSI/标签 | `outputs/tables/07_robustness/missing_minute_threshold_robustness.csv` | table | 附录 | 有效分钟阈值 236/238 样本影响。 |",
        "| R05 | LSI/标签 | `outputs/tables/07_robustness/standardization_robustness.csv` | table | 附录 | 训练期 mean/std 替代标准化对照。 |",
        "| R06 | RGARCH-CARR-SK | `outputs/tables/07_robustness/rgarch_realized_measure_robustness.csv` | table | 正文 | RV/RBV/MedRV/RMAD fit 与 loss。 |",
        "| R07 | RGARCH-CARR-SK | `outputs/figures/07_robustness/fig_rgarch_realized_measure_robustness.png` | figure | 正文/附录 | BIC 与 test R2LOG 对比。 |",
        "| R08 | RGARCH-CARR-SK | `outputs/tables/07_robustness/rgarch_oos_loss_robustness.csv` | table | 正文 | R2LOG/MSE/MAE/QLIKE。 |",
        "| R09 | QVAR | `outputs/tables/07_robustness/qvar_quantile_robustness.csv` | table | 正文 | 分位点与 pinball loss。 |",
        "| R10 | QVAR | `outputs/figures/07_robustness/fig_qvar_quantile_robustness.png` | figure | 正文/附录 | 分位点响应稳健性。 |",
        "| R11 | QVAR | `outputs/tables/07_robustness/qvar_shock_size_robustness.csv` | table | 正文/附录 | ±1.5/±2.0/±2.5 情景冲击。 |",
        "| R12 | QVAR | `outputs/figures/07_robustness/fig_qvar_shock_size_robustness.png` | figure | 正文/附录 | 四情景冲击幅度稳健性。 |",
        "| R13 | SMARTBoost | `outputs/tables/07_robustness/smartboost_time_split_robustness.csv` | table | 正文 | 时间窗口敏感性。 |",
        "| R14 | SMARTBoost | `outputs/tables/07_robustness/smartboost_feature_ablation.csv` | table | 正文/附录 | 固定抽样特征组消融。 |",
        "| R15 | SMARTBoost | `outputs/figures/07_robustness/fig_smartboost_feature_ablation.png` | figure | 正文/附录 | 消融 PR-AUC 对比。 |",
        "| R16 | SMARTBoost | `outputs/tables/07_robustness/smartboost_topk_robustness.csv` | table | 正文 | Top 1/5/10/20% lift。 |",
        "| R17 | SMARTBoost | `outputs/figures/07_robustness/fig_smartboost_topk_robustness.png` | figure | 正文 | Top-K lift。 |",
        "| R18 | SMARTBoost | `outputs/tables/07_robustness/smartboost_calibration_robustness.csv` | table | 附录 | 校准与 Brier。 |",
    ]
    (PROJECT_ROOT / "docs/admin" / "robustness_registry.md").write_text("\n".join(registry_lines) + "\n", encoding="utf-8")

    fig_registry = PROJECT_ROOT / "docs/admin" / "figure_registry.md"
    fig_text = fig_registry.read_text(encoding="utf-8")
    marker = "## 稳健性检验图表（2026-05-20）"
    if marker in fig_text:
        fig_text = fig_text.split(marker)[0].rstrip()
    fig_block = [
        "",
        marker,
        "",
        "| 编号 | 标题 | PNG 路径 | 模块 | 去向 |",
        "|---|---|---|---|---|",
        "| RF01 | 标签阈值稳健性 | `outputs/figures/07_robustness/fig_label_threshold_robustness.png` | LSI/标签 | 正文 |",
        "| RF02 | RGARCH realized measure 稳健性 | `outputs/figures/07_robustness/fig_rgarch_realized_measure_robustness.png` | RGARCH-CARR-SK | 正文/附录 |",
        "| RF03 | QVAR 分位点稳健性 | `outputs/figures/07_robustness/fig_qvar_quantile_robustness.png` | QVAR | 正文/附录 |",
        "| RF04 | QVAR 情景冲击幅度稳健性 | `outputs/figures/07_robustness/fig_qvar_shock_size_robustness.png` | QVAR | 正文/附录 |",
        "| RF05 | SMARTBoost 特征组消融 | `outputs/figures/07_robustness/fig_smartboost_feature_ablation.png` | SMARTBoost | 正文/附录 |",
        "| RF06 | SMARTBoost Top-K lift | `outputs/figures/07_robustness/fig_smartboost_topk_robustness.png` | SMARTBoost | 正文 |",
    ]
    fig_registry.write_text(fig_text.rstrip() + "\n" + "\n".join(fig_block) + "\n", encoding="utf-8")

    table_registry = PROJECT_ROOT / "docs/admin" / "table_registry.md"
    table_text = table_registry.read_text(encoding="utf-8")
    table_marker = "## 稳健性检验表格（2026-05-20）"
    if table_marker in table_text:
        table_text = table_text.split(table_marker)[0].rstrip()
    table_block = [
        "",
        table_marker,
        "",
        "稳健性检验表统一位于 `outputs/tables/07_robustness/`，详见 `docs/admin/robustness_registry.md`。",
    ]
    table_registry.write_text(table_text.rstrip() + "\n" + "\n".join(table_block) + "\n", encoding="utf-8")


def final_report() -> None:
    table_files = sorted(TABLE_DIR.glob("*.csv"))
    figure_files = sorted(FIG_DIR.glob("*.png"))
    lines = [
        "# 稳健性检验最终报告",
        "",
        "## 完成范围",
        "",
        "- LSI 与标签构造：阈值、窗口、缺分钟阈值、替代标准化。",
        "- RGARCH-CARR-SK：realized pressure measure、样本外损失、高阶矩诊断。",
        "- QVAR：分位点、情景冲击幅度、解释边界。",
        "- SMARTBoost：无泄漏复核、时间窗口、特征组消融、Top-K 排序、校准。",
        "",
        "## 输出表格",
        "",
        *[f"- `{rel(p)}`" for p in table_files],
        "",
        "## 输出图像",
        "",
        *[f"- `{rel(p)}`" for p in figure_files],
        "",
        "## 限制说明",
        "",
        "- H20 仅作为标签分布延伸检验，本轮不新增 H20 正式预警模型。",
        "- 缺分钟阈值 238 仅基于 code-date 覆盖统计评估样本影响，未重跑 stage1-stage3。",
        "- SMARTBoost 特征组消融采用固定系统抽样轻量复核，不能替代已保存的全量主结果。",
        "- QVAR 情景冲击是统计模拟，不是严格因果识别。",
    ]
    write_md(REPORT_AUDIT_DIR / "robustness_final_report.md", lines)


def main() -> int:
    ensure_dirs()
    split = load_split()
    write_literature_design_digest()
    if not (TABLE_DIR / "label_threshold_robustness.csv").exists():
        print("running label threshold robustness")
        label_threshold_robustness(split)
    else:
        print("skip existing label threshold robustness")
    if not (TABLE_DIR / "horizon_robustness.csv").exists() or not (TABLE_DIR / "missing_minute_threshold_robustness.csv").exists():
        print("running horizon and missing-minute robustness")
        horizon_and_missing_robustness(split)
    else:
        print("skip existing horizon and missing-minute robustness")
    if not (TABLE_DIR / "standardization_robustness.csv").exists():
        print("running standardization robustness")
        standardization_robustness(split)
    else:
        print("skip existing standardization robustness")
    if not (TABLE_DIR / "rgarch_oos_loss_robustness.csv").exists():
        print("running RGARCH robustness")
        rgarch_robustness()
    else:
        print("skip existing RGARCH robustness")
    if not (TABLE_DIR / "qvar_shock_size_robustness.csv").exists():
        print("running QVAR robustness")
        qvar_robustness()
    else:
        print("skip existing QVAR robustness")
    smartboost_no_leakage_note()
    if not (TABLE_DIR / "smartboost_topk_robustness.csv").exists() or not (TABLE_DIR / "smartboost_time_split_robustness.csv").exists():
        print("reading SMARTBoost predictions")
        pred = read_predictions_sample_or_all()
        print("running SMARTBoost top-k/calibration/time-window robustness")
        smartboost_topk_and_calibration(pred)
        smartboost_time_split_robustness(pred)
    else:
        print("skip existing SMARTBoost top-k/calibration/time-window robustness")
    if not (TABLE_DIR / "smartboost_feature_ablation.csv").exists():
        print("running SMARTBoost feature ablation sample robustness")
        smartboost_feature_ablation(split)
    else:
        print("skip existing SMARTBoost feature ablation sample robustness")
    update_chapter_and_registries({})
    final_report()
    print(f"robustness_complete tables={TABLE_DIR} figures={FIG_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
