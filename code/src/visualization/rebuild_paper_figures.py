from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Callable

CODE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = CODE_ROOT.parent
STYLE_PATH = PROJECT_ROOT / ".agents" / "skills" / "academic-finance-visualization-cn" / "scripts" / "finance_paper_style.py"

sys.dont_write_bytecode = True
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import precision_recall_curve, roc_curve


def load_style_module():
    spec = importlib.util.spec_from_file_location("finance_paper_style", STYLE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load finance paper style helper: {STYLE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


style = load_style_module()
style.apply_finance_paper_style()
ROLE_COLORS = style.get_role_colors()
BASE_LINE_STYLES = style.get_line_style_semantics()
PALETTE = {
    "MarketLSI": ROLE_COLORS["primary"],
    "Stress": ROLE_COLORS["negative"],
    "RGARCH-CARR-SK": ROLE_COLORS["primary"],
    "QVAR": ROLE_COLORS["primary"],
    "SMARTBoost": ROLE_COLORS["primary"],
    "Validation": "#F28E2B",
    "Test": ROLE_COLORS["negative"],
    "H5": ROLE_COLORS["primary"],
    "H10": ROLE_COLORS["negative"],
}
LINE_STYLES = {
    "q0.10": {"color": "#9E9E9E", "linestyle": ":", "linewidth": 1.8},
    "q0.50": {"color": ROLE_COLORS["primary"], "linestyle": "-", "linewidth": 1.8},
    "q0.90": {"color": "#F28E2B", "linestyle": "--", "linewidth": 1.8},
    "q0.95": {"color": ROLE_COLORS["negative"], "linestyle": "-.", "linewidth": 1.8},
    "H5": {"color": ROLE_COLORS["primary"], "linestyle": "-", "linewidth": 1.8},
    "H10": {"color": ROLE_COLORS["negative"], "linestyle": "-.", "linewidth": 1.8},
    "validation": {"color": "#F28E2B", "linestyle": "--", "linewidth": 1.8},
    "test": {"color": ROLE_COLORS["negative"], "linestyle": "-.", "linewidth": 1.8},
    **BASE_LINE_STYLES,
}

STAGE2_DIR = PROJECT_ROOT / "data_intermediate" / "stage2_lsi_labels"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"
OUT_DIR = PROJECT_ROOT / "outputs" / "figures" / "99_paper_ready"
SMARTBOOST_TABLE_DIR = TABLE_DIR / "06_smartboost"
RGARCH_TABLE_DIR = TABLE_DIR / "04_rgarch"
QVAR_TABLE_DIR = TABLE_DIR / "05_qvar"

REG_STAGES = [
    ("2023-05-15", "2024-10-07", "阶段一"),
    ("2024-10-08", "2025-07-06", "阶段二"),
    ("2025-07-07", "2026-05-13", "阶段三"),
]

MANIFEST_ROWS: list[dict[str, str]] = []
WARNINGS: list[str] = []


def relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def save_paper_figure(
    fig,
    figure_id: str,
    title: str,
    section: str,
    source_table: str,
    destination: str,
    uses_current_smartboost: str = "no",
    contains_crossstress: str = "no",
    notes: str = "",
) -> None:
    png = OUT_DIR / f"{figure_id}.png"
    pdf = OUT_DIR / f"{figure_id}.pdf"
    style.save_figure_dual_format(fig, png, pdf, dpi=300)
    MANIFEST_ROWS.append(
        {
            "figure_id": figure_id,
            "title": title,
            "figure_path_png": relative(png),
            "figure_path_pdf": relative(pdf),
            "source_table": source_table,
            "section": section,
            "destination": destination,
            "uses_current_smartboost": uses_current_smartboost,
            "contains_crossstress": contains_crossstress,
            "notes": notes,
        }
    )
    plt.close(fig)


def add_stage_spans(ax) -> None:
    colors = ["#F2F2F2", "#EAEFF6", "#F4EEE8"]
    for idx, (start, end, label) in enumerate(REG_STAGES):
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color=colors[idx], alpha=0.45, zorder=0)
        mid = pd.Timestamp(start) + (pd.Timestamp(end) - pd.Timestamp(start)) / 2
        ax.text(mid, 0.98, label, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=8, color="#666666")


def get_lsi_manifest() -> pd.DataFrame:
    manifest = pd.read_csv(STAGE2_DIR / "lsi_labels_manifest.csv")
    manifest = manifest.loc[(~manifest["is_index"].astype(bool)) & (manifest["rows"].fillna(0).astype(int) > 0)].copy()
    return manifest


def ensure_current_smartboost() -> None:
    metadata = json.loads((SMARTBOOST_TABLE_DIR / "smartboost_model_metadata.json").read_text(encoding="utf-8"))
    features = metadata.get("feature_columns", [])
    leaked = [feature for feature in features if "CrossStress" in feature]
    if leaked:
        raise RuntimeError(f"SMARTBoost metadata contains leaked CrossStress features: {leaked}")
    partial = pd.read_csv(SMARTBOOST_TABLE_DIR / "smartboost_partial_effects.csv")
    if partial["feature"].astype(str).str.contains("CrossStress", case=False, na=False).any():
        raise RuntimeError("SMARTBoost partial effects contain CrossStress")


def plot_coverage_heatmap() -> None:
    manifest = get_lsi_manifest()
    rows = []
    for item in manifest.itertuples(index=False):
        df = pd.read_parquet(PROJECT_ROOT / item.output_path, columns=["code", "date", "valid_minutes"])
        daily = df.drop_duplicates(["code", "date"])[["code", "date", "valid_minutes"]].copy()
        daily["date"] = pd.to_datetime(daily["date"])
        daily["month"] = daily["date"].dt.to_period("M").astype(str)
        daily["coverage"] = pd.to_numeric(daily["valid_minutes"], errors="coerce") / 240.0
        rows.append(daily.groupby(["code", "month"], as_index=False)["coverage"].mean())
    cov = pd.concat(rows, ignore_index=True)
    pivot = cov.pivot(index="code", columns="month", values="coverage")
    order = pivot.mean(axis=1).sort_values(ascending=False).index
    pivot = pivot.loc[order]
    heat_vmin = max(0.97, float(np.nanpercentile(pivot.to_numpy(), 2)))
    if heat_vmin >= 0.999:
        heat_vmin = 0.97

    fig, ax = plt.subplots(figsize=(12.0, 11.5), constrained_layout=True)
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="YlGnBu",
        vmin=heat_vmin,
        vmax=1.0,
        cbar_kws={"label": "有效分钟覆盖率"},
        xticklabels=True,
        yticklabels=True,
    )
    ax.set_title("股票-月份有效分钟覆盖率", loc="left", pad=10)
    ax.set_xlabel("月份")
    ax.set_ylabel("股票代码")
    ax.tick_params(axis="x", rotation=45)
    if len(pivot.index) > 45:
        for idx, label in enumerate(ax.get_yticklabels()):
            if idx % 3 != 0:
                label.set_visible(False)
    save_paper_figure(
        fig,
        "fig_01_coverage_heatmap",
        "股票-月份有效分钟覆盖率",
        "第3章 数据",
        "data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet",
        "正文",
        notes="按 code-month 聚合 valid_minutes/240；不读取原始预处理数据。",
    )


def plot_lsi_intraday() -> None:
    manifest = get_lsi_manifest()
    sums = []
    samples = []
    for item in manifest.itertuples(index=False):
        df = pd.read_parquet(PROJECT_ROOT / item.output_path, columns=["slot", "LSI_5"])
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        g = df.groupby("slot")["LSI_5"].agg(["sum", "count"]).reset_index()
        sums.append(g)
        step = max(1, len(df) // 5_000)
        samples.append(df.iloc[::step].head(5_000))
    agg = pd.concat(sums, ignore_index=True).groupby("slot").sum(numeric_only=True).reset_index()
    agg["mean"] = agg["sum"] / agg["count"].replace(0, np.nan)
    sample = pd.concat(samples, ignore_index=True)
    q = sample.groupby("slot")["LSI_5"].quantile([0.25, 0.75]).unstack()
    q.columns = ["q25", "q75"]
    plot = agg.merge(q.reset_index(), on="slot", how="left").sort_values("slot")

    fig, ax = plt.subplots(figsize=(9.0, 4.8), constrained_layout=True)
    ax.fill_between(plot["slot"], plot["q25"], plot["q75"], color=PALETTE["MarketLSI"], alpha=0.18, label="25%-75% 分位带")
    ax.plot(plot["slot"], plot["mean"], color=PALETTE["MarketLSI"], linewidth=1.9, label="均值 LSI_5")
    for slot, label in [(1, "开盘"), (122, "午后开盘"), (230, "尾盘")]:
        ax.axvline(slot, color="#777777", linestyle="--", linewidth=0.9)
        ax.text(slot + 1, 0.98, label, transform=ax.get_xaxis_transform(), va="top", fontsize=8, color="#555555")
    ax.set_title("LSI 日内模式", loc="left")
    ax.set_xlabel("日内 slot")
    ax.set_ylabel("LSI_5")
    ax.set_xlim(1, 240)
    style.standardize_legend(ax)
    style.despine_axes(ax)
    save_paper_figure(
        fig,
        "fig_02_lsi_intraday_pattern",
        "LSI 日内模式",
        "第4章 LSI与标签",
        "data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet",
        "正文",
        notes="分位带来自每只股票确定性抽样；均值为 slot 聚合。",
    )


def plot_market_lsi_time_series() -> None:
    market = pd.read_parquet(STAGE2_DIR / "market_context.parquet", columns=["datetime", "MarketLSI"])
    market["datetime"] = pd.to_datetime(market["datetime"])
    market = market.dropna(subset=["MarketLSI"]).copy()
    daily = market.set_index("datetime")["MarketLSI"].resample("1D").mean().dropna().to_frame("MarketLSI")
    daily["rolling_20d"] = daily["MarketLSI"].rolling(20, min_periods=5).mean()

    fig, ax = plt.subplots(figsize=(10.5, 4.8), constrained_layout=True)
    add_stage_spans(ax)
    ax.plot(daily.index, daily["MarketLSI"], color=PALETTE["MarketLSI"], linewidth=0.8, alpha=0.35, label="日度 MarketLSI")
    ax.plot(daily.index, daily["rolling_20d"], color="#2F4B7C", linewidth=2.0, label="20日滚动均值")
    peak = daily["rolling_20d"].idxmax()
    if pd.notna(peak):
        ax.scatter([peak], [daily.loc[peak, "rolling_20d"]], color=PALETTE["Stress"], s=24, zorder=5)
    ax.set_title("市场压力指数（MarketLSI）时间序列", loc="left")
    ax.set_ylabel("MarketLSI")
    ax.set_xlabel("日期")
    style.format_date_axis(ax)
    style.standardize_legend(ax)
    style.despine_axes(ax)
    save_paper_figure(
        fig,
        "fig_03_market_lsi_time_series",
        "市场压力指数（MarketLSI）时间序列",
        "第4章 LSI与标签",
        "data_intermediate/stage2_lsi_labels/market_context.parquet",
        "正文",
        notes="监管阶段仅作为时间分段背景，不表示因果识别。",
    )


def select_rgarch_model(paths: pd.DataFrame) -> pd.DataFrame:
    model = "RGARCH-CARR-SK-RMAD" if "RGARCH-CARR-SK-RMAD" in set(paths["model"]) else str(paths["model"].iloc[0])
    return paths.loc[paths["model"].eq(model)].copy()


def plot_rgarch_conditional_risk() -> None:
    paths = pd.read_csv(RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_conditional_paths.csv")
    df = select_rgarch_model(paths)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["lambda_log"] = np.log1p(pd.to_numeric(df["lambda_t"], errors="coerce").clip(lower=0))
    df["realized_log"] = np.log1p(pd.to_numeric(df["realized_pressure_measure"], errors="coerce").clip(lower=0))
    weekly = df.set_index("datetime")[["lambda_log", "realized_log"]].resample("W-FRI").mean().dropna()
    threshold = float(np.nanquantile(df.loc[df["period"].eq("train"), "lambda_log"], 0.90))

    fig, ax = plt.subplots(figsize=(10.2, 4.8), constrained_layout=True)
    add_stage_spans(ax)
    ax.plot(weekly.index, weekly["lambda_log"], color=PALETTE["RGARCH-CARR-SK"], linewidth=1.9, label=r"条件压力风险 $\lambda_t$（log）")
    ax.plot(weekly.index, weekly["realized_log"], color="#8A8A8A", linewidth=1.2, alpha=0.85, label="realized pressure measure（log）")
    ax.axhline(threshold, color=PALETTE["Stress"], linestyle="--", linewidth=1.0, label="训练期90%风险阈值")
    ax.set_title("RGARCH-CARR-SK 条件压力风险路径", loc="left")
    ax.set_xlabel("日期")
    ax.set_ylabel("log(1 + risk)")
    style.format_date_axis(ax)
    style.standardize_legend(ax)
    style.despine_axes(ax)
    save_paper_figure(
        fig,
        "fig_04_rgarch_conditional_pressure_risk",
        "RGARCH-CARR-SK 条件压力风险路径",
        "第6章 RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv",
        "正文",
        notes="使用 RMAD 版本；周度均值避免过密路径。",
    )


def plot_rgarch_skew_kurtosis() -> None:
    paths = pd.read_csv(RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_conditional_paths.csv")
    df = select_rgarch_model(paths)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df["s_roll"] = df["s_t"].rolling(10, min_periods=3).mean()
    df["k_roll"] = df["k_t"].rolling(10, min_periods=3).mean()

    fig, axes = plt.subplots(2, 1, figsize=(10.2, 6.0), sharex=True, constrained_layout=True)
    axes[0].plot(df["datetime"], df["s_roll"], color=PALETTE["RGARCH-CARR-SK"], linewidth=1.6)
    axes[0].axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
    axes[0].set_title("(a) 动态偏度 s_t", loc="left")
    axes[0].set_ylabel("s_t")
    axes[1].plot(df["datetime"], df["k_roll"], color=PALETTE["Stress"], linewidth=1.6)
    axes[1].set_title("(b) 动态峰度 k_t", loc="left")
    axes[1].set_ylabel("k_t")
    axes[1].set_xlabel("日期")
    k_range = float(np.nanmax(df["k_t"]) - np.nanmin(df["k_t"]))
    if k_range < 0.25:
        axes[1].text(0.01, 0.92, "动态峰度估计在样本内较稳定", transform=axes[1].transAxes, fontsize=9, color="#555555")
    for ax in axes:
        add_stage_spans(ax)
        style.format_date_axis(ax)
        style.despine_axes(ax)
    save_paper_figure(
        fig,
        "fig_05_rgarch_dynamic_skew_kurtosis",
        "RGARCH-CARR-SK 动态偏度与动态峰度",
        "第6章 RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv",
        "正文",
        notes="10日滚动均值；动态高阶矩为模型隐含路径。",
    )


def plot_rgarch_realized_measures() -> None:
    df = pd.read_csv(RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_realized_pressure_measures.csv")
    measures = ["RV_pressure", "RBV_pressure", "MedRV_pressure", "RMAD_pressure"]
    data = []
    labels = ["RV", "RBV", "MedRV", "RMAD"]
    for measure in measures:
        values = np.log1p(pd.to_numeric(df[measure], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna())
        z = (values - values.mean()) / values.std(ddof=0)
        data.append(z.to_numpy())
    fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    box = ax.boxplot(data, tick_labels=labels, showfliers=False, patch_artist=True, widths=0.55)
    colors = ["#4C78A8", "#59A14F", "#F28E2B", "#B07AA1"]
    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.65)
    ax.axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
    ax.set_title("realized pressure measures 对比", loc="left")
    ax.set_ylabel("标准化 log(1 + measure)")
    style.despine_axes(ax)
    save_paper_figure(
        fig,
        "fig_06_rgarch_realized_pressure_measures",
        "realized pressure measures 对比",
        "第6章 RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_realized_pressure_measures.csv",
        "正文/附录",
        notes="使用标准化 log measure 避免不同量纲混画。",
    )


def plot_qvar_tail_response() -> None:
    df = pd.read_csv(QVAR_TABLE_DIR / "qvar_tail_quantile_response.csv")
    plot = df.loc[df["shock_variable"].eq("MarketLSI")].copy()
    fig, ax = plt.subplots(figsize=(8.0, 4.8), constrained_layout=True)
    for quantile, g in plot.groupby("quantile", sort=True):
        key = f"q{quantile:.2f}"
        ls = LINE_STYLES.get(key, {})
        ax.plot(g["horizon"], g["MarketLSI"], label=f"q={quantile:.2f}", **ls)
    ax.axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
    ax.set_title("QVAR 尾部分位响应：MarketLSI shock", loc="left")
    ax.set_xlabel("预测步长")
    ax.set_ylabel("MarketLSI 响应")
    style.standardize_legend(ax)
    style.despine_axes(ax)
    save_paper_figure(
        fig,
        "fig_07_qvar_tail_quantile_response",
        "QVAR 尾部分位响应（标准化 MarketLSI shock）",
        "第7章 QVAR",
        "outputs/tables/05_qvar/qvar_tail_quantile_response.csv",
        "正文",
        notes=(
            "响应为标准化空间中冲击路径减基准路径之差，不作严格因果解释。"
        ),
    )


def plot_qvar_pressure_scenarios() -> None:
    df = pd.read_csv(QVAR_TABLE_DIR / "qvar_pressure_test_paths.csv")
    scenario_map = {
        "market_crash": "市场急跌",
        "volatility_spike": "波动放大",
        "liquidity_contraction": "成交收缩",
        "composite_pressure": "复合压力",
        "volatility_negative_return": "急跌+波动放大",
        "liquidity_pressure": "流动性压力",
    }
    available = list(df["scenario"].drop_duplicates())
    missing_requested = [s for s in ["market_crash", "volatility_spike", "liquidity_contraction", "composite_pressure"] if s not in available]
    if missing_requested:
        WARNINGS.append("QVAR压力测试表未提供四类指定情景，未伪造缺失情景；仅绘制已有情景：" + ", ".join(available))

    scenarios = available[:4]
    n_cols = 2
    n_rows = math.ceil(len(scenarios) / n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(10.0, 3.8 * n_rows), sharex=True, constrained_layout=True)
    axes = np.asarray(axes).reshape(-1)
    for ax, scenario in zip(axes, scenarios):
        g0 = df.loc[df["scenario"].eq(scenario) & df["quantile"].isin([0.5, 0.95])].copy()
        for quantile, g in g0.groupby("quantile", sort=True):
            key = f"q{quantile:.2f}"
            ls = LINE_STYLES.get(key, {})
            ax.plot(g["horizon"], g["MarketLSI"], label=f"q={quantile:.2f}", **ls)
        ax.axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
        ax.set_title(scenario_map.get(scenario, scenario), loc="left")
        ax.set_ylabel("MarketLSI")
        style.standardize_legend(ax)
        style.despine_axes(ax)
    for ax in axes[len(scenarios) :]:
        ax.set_visible(False)
    for ax in axes[-n_cols:]:
        if ax.get_visible():
            ax.set_xlabel("预测步长")
    save_paper_figure(
        fig,
        "fig_08_qvar_pressure_test_scenarios",
        "QVAR 四类情景 MarketLSI 响应（标准化冲击）",
        "第7章 QVAR",
        "outputs/tables/05_qvar/qvar_pressure_test_paths.csv",
        "正文",
        notes=(
            "MarketLSI_response = 情景路径 - 基准路径（标准化空间）。"
            "响应方向依赖系数符号和递推设定，不作严格因果解释。"
        ),
    )


def load_smartboost_test_predictions() -> pd.DataFrame:
    manifest = pd.read_csv(SMARTBOOST_TABLE_DIR / "smartboost_prediction_manifest.csv")
    parts = []
    for item in manifest.itertuples(index=False):
        df = pd.read_parquet(
            PROJECT_ROOT / item.output_path,
            columns=["horizon", "period", "y_true", "predicted_probability"],
        )
        parts.append(df.loc[df["period"].eq("test")].copy())
    pred = pd.concat(parts, ignore_index=True)
    pred = pred.dropna(subset=["y_true", "predicted_probability"])
    return pred


def thin_curve(x: np.ndarray, y: np.ndarray, max_points: int = 1200) -> tuple[np.ndarray, np.ndarray]:
    if len(x) <= max_points:
        return x, y
    idx = np.unique(np.linspace(0, len(x) - 1, max_points).astype(int))
    return x[idx], y[idx]


def plot_smartboost_pr_roc() -> None:
    ensure_current_smartboost()
    pred = load_smartboost_test_predictions()
    metrics = pd.read_csv(SMARTBOOST_TABLE_DIR / "smartboost_metrics.csv").set_index(["horizon", "period"])

    fig_pr, ax_pr = plt.subplots(figsize=(7.5, 5.0), constrained_layout=True)
    fig_roc, ax_roc = plt.subplots(figsize=(7.5, 5.0), constrained_layout=True)
    for horizon in ["H5", "H10"]:
        g = pred.loc[pred["horizon"].eq(horizon)]
        y = g["y_true"].astype("int8").to_numpy()
        p = g["predicted_probability"].astype("float64").to_numpy()
        precision, recall, _ = precision_recall_curve(y, p)
        fpr, tpr, _ = roc_curve(y, p)
        recall_t, precision_t = thin_curve(recall, precision)
        fpr_t, tpr_t = thin_curve(fpr, tpr)
        ls = LINE_STYLES[horizon]
        pr_auc = float(metrics.loc[(horizon, "test"), "PR_AUC"])
        roc_auc = float(metrics.loc[(horizon, "test"), "ROC_AUC"])
        base = float(metrics.loc[(horizon, "test"), "positive_rate"])
        ax_pr.plot(recall_t, precision_t, label=f"{horizon}-test PR-AUC={pr_auc:.3f}", **ls)
        ax_pr.axhline(base, color=ls["color"], linestyle=":", linewidth=0.9, alpha=0.75, label=f"{horizon} 基准={base:.3f}")
        ax_roc.plot(fpr_t, tpr_t, label=f"{horizon}-test ROC-AUC={roc_auc:.3f}", **ls)
    ax_pr.set_title("SMARTBoost 样本外 PR 曲线", loc="left")
    ax_pr.set_xlabel("Recall")
    ax_pr.set_ylabel("Precision")
    ax_pr.set_xlim(0, 1)
    ax_pr.set_ylim(0, 1.02)
    style.standardize_legend(ax_pr)
    style.despine_axes(ax_pr)
    save_paper_figure(
        fig_pr,
        "fig_09_smartboost_pr_curve",
        "SMARTBoost 样本外 PR 曲线",
        "第8章 SMARTBoost",
        "outputs/tables/06_smartboost/predictions_by_code/*.parquet; smartboost_metrics.csv",
        "正文",
        uses_current_smartboost="yes",
        notes="使用剔除 CrossStress 后的预测概率；基准线为测试期事件率。",
    )

    ax_roc.plot([0, 1], [0, 1], color="#8A8A8A", linestyle="--", linewidth=0.9, label="No skill")
    ax_roc.set_title("SMARTBoost 样本外 ROC 曲线", loc="left")
    ax_roc.set_xlabel("False Positive Rate")
    ax_roc.set_ylabel("True Positive Rate")
    ax_roc.set_xlim(0, 1)
    ax_roc.set_ylim(0, 1.02)
    style.standardize_legend(ax_roc)
    style.despine_axes(ax_roc)
    save_paper_figure(
        fig_roc,
        "fig_10_smartboost_roc_curve",
        "SMARTBoost 样本外 ROC 曲线",
        "第8章 SMARTBoost",
        "outputs/tables/06_smartboost/predictions_by_code/*.parquet; smartboost_metrics.csv",
        "附录",
        uses_current_smartboost="yes",
        notes="ROC 为辅助图，不替代 PR 曲线作为主证据。",
    )


def plot_smartboost_calibration() -> None:
    ensure_current_smartboost()
    cal = pd.read_csv(SMARTBOOST_TABLE_DIR / "smartboost_calibration_table.csv")
    cal = cal.loc[cal["period"].eq("test")].copy()
    fig, ax = plt.subplots(figsize=(6.8, 5.0), constrained_layout=True)
    ax.plot([0, 1], [0, 1], color="#8A8A8A", linestyle="--", linewidth=0.9, label="45度线")
    for horizon, g in cal.groupby("horizon", sort=True):
        ls = LINE_STYLES[horizon]
        ax.plot(
            g["mean_predicted_probability"],
            g["realized_pressure_rate"],
            marker="o",
            markersize=4,
            label=f"{horizon}-test",
            **ls,
        )
    ax.set_title("SMARTBoost Calibration 曲线", loc="left")
    ax.set_xlabel("平均预测概率")
    ax.set_ylabel("真实压力发生率")
    ax.set_xlim(0, max(0.7, cal["mean_predicted_probability"].max() * 1.05))
    ax.set_ylim(0, max(0.7, cal["realized_pressure_rate"].max() * 1.05))
    style.standardize_legend(ax)
    style.despine_axes(ax)
    save_paper_figure(
        fig,
        "fig_11_smartboost_calibration_curve",
        "SMARTBoost Calibration 曲线",
        "第8章 SMARTBoost",
        "outputs/tables/06_smartboost/smartboost_calibration_table.csv",
        "正文/附录",
        uses_current_smartboost="yes",
    )


def plot_smartboost_top5() -> None:
    ensure_current_smartboost()
    df = pd.read_csv(SMARTBOOST_TABLE_DIR / "smartboost_event_rate_and_lift.csv")
    plot = df.loc[df["reg_stage"].eq("ALL")].copy()
    plot["label"] = plot["horizon"] + "-" + plot["period"].replace({"validation": "val", "test": "test"})
    plot = plot.sort_values(["horizon", "period"])
    x = np.arange(len(plot))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8.2, 4.8), constrained_layout=True)
    ax.bar(x - width / 2, plot["positive_rate"], width, color="#8A8A8A", alpha=0.55, label="全样本基准事件率")
    ax.bar(x + width / 2, plot["Precision_Top5pct"], width, color=PALETTE["Top 5%"], alpha=0.82, label="Top 5% 高风险组")
    for xi, rate, lift in zip(x, plot["Precision_Top5pct"], plot["Top5_lift"]):
        ax.text(xi + width / 2, rate + 0.015, f"{rate:.3f}\n{lift:.1f}x", ha="center", va="bottom", fontsize=8, color="#333333")
    ax.set_xticks(x)
    ax.set_xticklabels(plot["label"], rotation=0)
    ax.set_title("SMARTBoost Top 5% 高风险组真实压力发生率", loc="left")
    ax.set_ylabel("真实压力发生率")
    style.format_percent_axis(ax)
    style.standardize_legend(ax)
    style.despine_axes(ax)
    save_paper_figure(
        fig,
        "fig_12_smartboost_top5_event_rate",
        "SMARTBoost Top 5% 高风险组真实压力发生率",
        "第8章 SMARTBoost",
        "outputs/tables/06_smartboost/smartboost_event_rate_and_lift.csv",
        "正文",
        uses_current_smartboost="yes",
        notes="柱上标注 Top 5% 真实压力发生率与 lift。",
    )


def plot_smartboost_partial_effects() -> None:
    ensure_current_smartboost()
    effects = pd.read_csv(SMARTBOOST_TABLE_DIR / "smartboost_partial_effects.csv")
    preferred = ["MarketLSI", "IndexRV", "MarketRelAmt", "LSI_5_rollmax_20"]
    features = [feature for feature in preferred if feature in set(effects["feature"])]
    label_map = {
        "MarketLSI": "市场压力指数（MarketLSI）",
        "IndexRV": "指数波动状态（IndexRV）",
        "MarketRelAmt": "市场相对成交额（MarketRelAmt）",
        "LSI_5_rollmax_20": "过去窗口压力峰值（LSI_5 rollmax 20）",
    }
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 7.0), constrained_layout=True)
    axes = axes.ravel()
    for ax, feature in zip(axes, features):
        g0 = effects.loc[effects["feature"].eq(feature)].copy()
        for horizon, g in g0.groupby("horizon", sort=True):
            ax.plot(g["feature_value"], g["mean_predicted_probability"], marker="o", markersize=3, label=horizon, **LINE_STYLES[horizon])
        ax.set_title(label_map.get(feature, feature), loc="left", fontsize=10)
        ax.set_xlabel("")
        ax.set_ylabel("预测概率的局部响应")
        style.standardize_legend(ax)
        style.despine_axes(ax)
    for ax in axes[len(features) :]:
        ax.set_visible(False)
    save_paper_figure(
        fig,
        "fig_13_smartboost_partial_effects",
        "SMARTBoost Partial Effects",
        "第8章 SMARTBoost",
        "outputs/tables/06_smartboost/smartboost_partial_effects.csv",
        "正文/附录",
        uses_current_smartboost="yes",
        notes="仅保留4个当前无泄漏核心变量；不包含 CrossStress。",
    )


def write_outputs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = pd.DataFrame(MANIFEST_ROWS)
    manifest.to_csv(OUT_DIR / "paper_figure_registry.csv", index=False, encoding="utf-8-sig")
    lines = ["# Paper Figure Rebuild Log", ""]
    lines.append(f"- generated_figures: {len(MANIFEST_ROWS)}")
    if WARNINGS:
        lines.append("")
        lines.append("## Warnings")
        lines.extend([f"- {warning}" for warning in WARNINGS])
    else:
        lines.append("- warnings: none")
    (OUT_DIR / "paper_figure_rebuild_log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_step(name: str, func: Callable[[], None]) -> None:
    print(f"[paper-figures] {name}")
    try:
        func()
    except FileNotFoundError as exc:
        warning = f"{name} skipped: missing input {exc}"
        WARNINGS.append(warning)
        print(warning)
    except KeyError as exc:
        warning = f"{name} skipped: missing column {exc}"
        WARNINGS.append(warning)
        print(warning)


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    steps: list[tuple[str, Callable[[], None]]] = [
        ("coverage_heatmap", plot_coverage_heatmap),
        ("lsi_intraday", plot_lsi_intraday),
        ("market_lsi_time_series", plot_market_lsi_time_series),
        ("rgarch_conditional_risk", plot_rgarch_conditional_risk),
        ("rgarch_skew_kurtosis", plot_rgarch_skew_kurtosis),
        ("rgarch_realized_measures", plot_rgarch_realized_measures),
        ("qvar_tail_response", plot_qvar_tail_response),
        ("qvar_pressure_scenarios", plot_qvar_pressure_scenarios),
        ("smartboost_pr_roc", plot_smartboost_pr_roc),
        ("smartboost_calibration", plot_smartboost_calibration),
        ("smartboost_top5", plot_smartboost_top5),
        ("smartboost_partial_effects", plot_smartboost_partial_effects),
    ]
    for name, func in steps:
        run_step(name, func)
    write_outputs()
    print(f"[paper-figures] done: {len(MANIFEST_ROWS)} figures")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"paper figure rebuild failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
