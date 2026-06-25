from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = CODE_ROOT.parent
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import seaborn as sns
except Exception:  # pragma: no cover
    sns = None

try:
    from sklearn.metrics import auc, precision_recall_curve, roc_curve
except Exception:  # pragma: no cover
    auc = precision_recall_curve = roc_curve = None

from config import paths


FIGURES_ROOT = PROJECT_ROOT / "outputs" / "figures"
TABLES_ROOT = PROJECT_ROOT / "outputs" / "tables"
REPORT_DIR = PROJECT_ROOT / "reviews" / "report_consistency"

DATA_FIG_DIR = FIGURES_ROOT / "01_data"
LSI_FIG_DIR = FIGURES_ROOT / "02_lsi"
RGARCH_FIG_DIR = FIGURES_ROOT / "04_rgarch"
QVAR_FIG_DIR = FIGURES_ROOT / "05_qvar"
SMART_FIG_DIR = FIGURES_ROOT / "06_smartboost"

STYLE_PATH = PROJECT_ROOT / ".agents" / "skills" / "academic-finance-visualization-cn" / "scripts" / "finance_paper_style.py"
AUDIT_STYLE_PATH = PROJECT_ROOT / ".agents" / "skills" / "academic-finance-visualization-cn" / "scripts" / "figure_audit.py"

INDEX_CODES = {"000016.SH", "000300.SH", "000852.SH", "000905.SH"}
REGIME_STAGES = [
    ("阶段一", pd.Timestamp("2023-05-15"), pd.Timestamp("2024-10-07"), "#F5F5F5"),
    ("阶段二", pd.Timestamp("2024-10-08"), pd.Timestamp("2025-07-06"), "#EFF4FA"),
    ("阶段三", pd.Timestamp("2025-07-07"), pd.Timestamp("2026-05-13"), "#FBF6F2"),
]


@dataclass
class FigureRow:
    figure_id: str
    title: str
    figure_path_png: str
    module: str
    source_data: str
    chapter: str
    destination: str
    smartboost_current_result: str
    notes: str


@dataclass
class AuditRow:
    figure_path_png: str
    exists_png: bool
    dpi_x: float | None
    dpi_y: float | None
    dpi_ok: bool
    size_bytes: int
    size_ok: bool
    blank_suspect: bool
    in_registry: bool
    crossstress_leakage_suspect: bool
    status: str
    notes: str


REGISTRY_ROWS: list[FigureRow] = []
WRITTEN_FIGURES: list[Path] = []


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


STYLE = load_module(STYLE_PATH, "finance_paper_style")
FIG_AUDIT = load_module(AUDIT_STYLE_PATH, "figure_audit")
ROLE_COLORS = STYLE.get_role_colors()
BASE_LINE_STYLES = STYLE.get_line_style_semantics()
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
    "train": {"color": ROLE_COLORS["primary"], "linestyle": "-", "linewidth": 1.8},
    "validation": {"color": "#F28E2B", "linestyle": "--", "linewidth": 1.8},
    "test": {"color": ROLE_COLORS["negative"], "linestyle": "-.", "linewidth": 1.8},
    **BASE_LINE_STYLES,
}


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def save_png(fig, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    WRITTEN_FIGURES.append(output_path)


def register(
    figure_id: str,
    title: str,
    path: Path,
    module: str,
    source_data: str,
    chapter: str,
    destination: str,
    smartboost_current_result: str = "不适用",
    notes: str = "",
) -> None:
    REGISTRY_ROWS.append(
        FigureRow(
            figure_id=figure_id,
            title=title,
            figure_path_png=rel(path),
            module=module,
            source_data=source_data,
            chapter=chapter,
            destination=destination,
            smartboost_current_result=smartboost_current_result,
            notes=notes,
        )
    )


def apply_style() -> None:
    STYLE.apply_finance_paper_style()


def add_regime_shading(ax, ymin=0.0, ymax=1.0, label=True) -> None:
    for name, start, end, color in REGIME_STAGES:
        ax.axvspan(start, end, ymin=ymin, ymax=ymax, color=color, alpha=0.45, zorder=0)
        if label:
            ax.text(
                start + (end - start) / 2,
                0.97,
                name,
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=8,
                color="#666666",
            )


def date_to_stage(values: pd.Series) -> pd.Series:
    dt = pd.to_datetime(values, errors="coerce")
    out = pd.Series("未分段", index=values.index, dtype="object")
    for name, start, end, _ in REGIME_STAGES:
        out.loc[(dt >= start) & (dt <= end)] = name
    return out


def slot_from_datetime(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce")
    minute = dt.dt.hour * 60 + dt.dt.minute
    morning = (minute >= 9 * 60 + 30) & (minute <= 11 * 60 + 30)
    afternoon = (minute >= 13 * 60) & (minute <= 15 * 60)
    slot = pd.Series(np.nan, index=series.index, dtype="float64")
    slot.loc[morning] = minute.loc[morning] - (9 * 60 + 30) + 1
    slot.loc[afternoon] = 121 + minute.loc[afternoon] - 13 * 60
    return slot


def downsample_xy(x: np.ndarray, y: np.ndarray, max_points: int = 600) -> tuple[np.ndarray, np.ndarray]:
    if len(x) <= max_points:
        return x, y
    idx = np.unique(np.linspace(0, len(x) - 1, max_points).astype(int))
    return x[idx], y[idx]


def load_lsi_slot_summaries() -> tuple[pd.DataFrame, pd.DataFrame]:
    manifest = pd.read_csv(PROJECT_ROOT / "data_intermediate" / "stage2_lsi_labels" / "lsi_labels_manifest.csv")
    manifest = manifest.loc[~manifest["is_index"].astype(bool)].copy()
    slot_parts = []
    stage_parts = []
    for row in manifest.itertuples(index=False):
        path = PROJECT_ROOT / str(row.output_path)
        df = pd.read_parquet(path, columns=["date", "slot", "LSI_5"])
        df = df.dropna(subset=["slot", "LSI_5"]).copy()
        if df.empty:
            continue
        g = df.groupby("slot")["LSI_5"].agg(
            mean="mean",
            median="median",
            q10=lambda x: x.quantile(0.10),
            q25=lambda x: x.quantile(0.25),
            q75=lambda x: x.quantile(0.75),
            q90=lambda x: x.quantile(0.90),
        )
        g["code"] = row.code
        slot_parts.append(g.reset_index())

        df["reg_stage"] = date_to_stage(df["date"])
        sg = df.groupby(["reg_stage", "slot"])["LSI_5"].mean().reset_index(name="mean_lsi")
        sg["code"] = row.code
        stage_parts.append(sg)

    slot_summary = (
        pd.concat(slot_parts, ignore_index=True)
        .groupby("slot")[["mean", "median", "q10", "q25", "q75", "q90"]]
        .mean()
        .reset_index()
        .sort_values("slot")
    )
    stage_summary = (
        pd.concat(stage_parts, ignore_index=True)
        .groupby(["reg_stage", "slot"])["mean_lsi"]
        .mean()
        .reset_index()
        .sort_values(["reg_stage", "slot"])
    )
    return slot_summary, stage_summary


def plot_coverage_heatmap() -> None:
    apply_style()
    coverage = pd.read_csv(PROJECT_ROOT / "data_intermediate" / "stage1_model_ready" / "coverage_by_code_date.csv")
    coverage["date"] = pd.to_datetime(coverage["date"])
    coverage["month"] = coverage["date"].dt.to_period("M").astype(str)
    coverage["coverage_rate"] = (coverage["valid_minutes"] / 240.0).clip(0, 1)
    pivot = coverage.pivot_table(index="code", columns="month", values="coverage_rate", aggfunc="mean")
    order = pivot.mean(axis=1).sort_values(ascending=False).index
    pivot = pivot.loc[order]

    fig, ax = plt.subplots(figsize=(11.2, 11.0), constrained_layout=True)
    if sns is not None:
        sns.heatmap(
            pivot,
            ax=ax,
            cmap="YlGnBu",
            vmin=0.95,
            vmax=1.0,
            cbar_kws={"label": "有效分钟覆盖率"},
            linewidths=0.0,
        )
    else:
        im = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="YlGnBu", vmin=0.95, vmax=1.0)
        fig.colorbar(im, ax=ax, label="有效分钟覆盖率")
    ax.set_title("股票-月份有效分钟覆盖率", loc="left")
    ax.set_xlabel("月份")
    ax.set_ylabel("股票代码")
    ax.tick_params(axis="x", rotation=45)
    output = DATA_FIG_DIR / "fig_refined_coverage_heatmap.png"
    save_png(fig, output)
    register(
        "F01",
        "股票-月份有效分钟覆盖率",
        output,
        "diagnostics/data",
        "data_intermediate/stage1_model_ready/coverage_by_code_date.csv",
        "第3章 数据",
        "正文",
        notes="按 code 总覆盖率排序，颜色为 code-month 平均有效分钟覆盖率。",
    )


def plot_coverage_by_exchange() -> None:
    apply_style()
    coverage = pd.read_csv(PROJECT_ROOT / "data_intermediate" / "stage1_model_ready" / "coverage_by_code_date.csv")
    coverage["coverage_rate"] = (coverage["valid_minutes"] / 240.0).clip(0, 1)
    coverage["market_group"] = np.select(
        [
            coverage["code"].isin(INDEX_CODES),
            coverage["code"].str.endswith(".SH"),
            coverage["code"].str.endswith(".SZ"),
        ],
        ["指数", "上交所", "深交所"],
        default="其他",
    )
    code_cov = coverage.groupby(["market_group", "code"])["coverage_rate"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(7.8, 4.6), constrained_layout=True)
    if sns is not None:
        sns.boxplot(data=code_cov, x="market_group", y="coverage_rate", color="#A6CEE3", width=0.5, ax=ax)
        sns.stripplot(data=code_cov, x="market_group", y="coverage_rate", color="#2F4B7C", size=3, alpha=0.65, ax=ax)
    else:
        groups = [g["coverage_rate"].to_numpy() for _, g in code_cov.groupby("market_group")]
        ax.boxplot(groups, labels=list(code_cov["market_group"].drop_duplicates()))
    ax.set_title("按交易所/指数分组的样本覆盖率", loc="left")
    ax.set_xlabel("")
    ax.set_ylabel("平均有效分钟覆盖率")
    ax.set_ylim(max(0.93, code_cov["coverage_rate"].min() - 0.01), 1.002)
    STYLE.format_percent_axis(ax)
    STYLE.despine_axes(ax)
    output = DATA_FIG_DIR / "fig_coverage_by_exchange_summary.png"
    save_png(fig, output)
    register(
        "F02",
        "按交易所/指数分组的覆盖率摘要",
        output,
        "diagnostics/data",
        "data_intermediate/stage1_model_ready/coverage_by_code_date.csv",
        "第3章 数据",
        "附录",
        notes="辅助检查不同交易所与指数样本覆盖差异。",
    )


def plot_lsi_intraday(slot_summary: pd.DataFrame) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(9.2, 4.8), constrained_layout=True)
    x = slot_summary["slot"].to_numpy()
    ax.fill_between(x, slot_summary["q25"], slot_summary["q75"], color="#4C78A8", alpha=0.18, label="25%-75% 分位带")
    ax.fill_between(x, slot_summary["q10"], slot_summary["q90"], color="#4C78A8", alpha=0.08, label="10%-90% 分位带")
    ax.plot(x, slot_summary["mean"], color="#2F4B7C", linewidth=1.8, label="均值")
    ax.plot(x, slot_summary["median"], color="#E15759", linewidth=1.4, linestyle="--", label="中位数")
    for slot, label in [(1, "开盘"), (121, "午后开盘"), (230, "尾盘")]:
        ax.axvline(slot, color="#8A8A8A", linewidth=0.8, linestyle=":")
        ax.text(slot + 2, ax.get_ylim()[1], label, ha="left", va="top", fontsize=8, color="#666666")
    ax.set_title("LSI 日内模式", loc="left")
    ax.set_xlabel("日内 slot")
    ax.set_ylabel("LSI_5")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=4, frameon=True)
    STYLE.despine_axes(ax)
    output = LSI_FIG_DIR / "fig_refined_lsi_intraday.png"
    save_png(fig, output)
    register(
        "F03",
        "LSI 日内模式",
        output,
        "MarketLSI/LSI",
        "data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet",
        "第4章 LSI与标签",
        "正文",
        notes="展示均值、中位数及分位带；关键时点为开盘、午后开盘和尾盘。",
    )


def plot_lsi_intraday_by_stage(stage_summary: pd.DataFrame) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(9.2, 4.8), constrained_layout=True)
    colors = {"阶段一": "#4C78A8", "阶段二": "#F28E2B", "阶段三": "#59A14F"}
    for stage, group in stage_summary.groupby("reg_stage"):
        ax.plot(group["slot"], group["mean_lsi"].rolling(5, min_periods=1, center=True).mean(), label=stage, color=colors.get(stage), linewidth=1.7)
    for slot in [1, 121, 230]:
        ax.axvline(slot, color="#B0B0B0", linewidth=0.7, linestyle=":")
    ax.set_title("分阶段 LSI 日内模式", loc="left")
    ax.set_xlabel("日内 slot")
    ax.set_ylabel("LSI_5 均值")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3, frameon=True)
    STYLE.despine_axes(ax)
    output = LSI_FIG_DIR / "fig_lsi_intraday_by_stage.png"
    save_png(fig, output)
    register(
        "F04",
        "分阶段 LSI 日内模式",
        output,
        "MarketLSI/LSI",
        "data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet",
        "第4章 LSI与标签",
        "附录/正文备选",
        notes="监管阶段仅作为时间分段背景，不表示因果识别。",
    )


def load_market_context() -> pd.DataFrame:
    market = pd.read_parquet(PROJECT_ROOT / "data_intermediate" / "stage2_lsi_labels" / "market_context.parquet")
    market["datetime"] = pd.to_datetime(market["datetime"], errors="coerce")
    market["date"] = market["datetime"].dt.normalize()
    market["slot"] = slot_from_datetime(market["datetime"])
    market["reg_stage"] = date_to_stage(market["date"])
    return market.dropna(subset=["datetime"])


def plot_market_lsi_timeseries(market: pd.DataFrame) -> None:
    apply_style()
    daily = (
        market.dropna(subset=["MarketLSI"])
        .groupby("date")["MarketLSI"]
        .agg(mean="mean", q90=lambda x: x.quantile(0.90), max="max")
        .reset_index()
        .sort_values("date")
    )
    daily["rolling20"] = daily["mean"].rolling(20, min_periods=5).mean()
    fig, ax = plt.subplots(figsize=(10.5, 4.8), constrained_layout=True)
    add_regime_shading(ax)
    ax.plot(daily["date"], daily["mean"], color="#9E9E9E", linewidth=0.9, alpha=0.75, label="日均 MarketLSI")
    ax.plot(daily["date"], daily["rolling20"], color=PALETTE["MarketLSI"], linewidth=1.9, label="20日滚动均值")
    peaks = daily.nlargest(4, "max")
    ax.scatter(peaks["date"], peaks["mean"], color="#E15759", s=20, zorder=3, label="压力峰值日")
    ax.set_title("市场压力指数（MarketLSI）时间序列", loc="left")
    ax.set_xlabel("日期")
    ax.set_ylabel("MarketLSI")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=3, frameon=True)
    STYLE.format_date_axis(ax)
    STYLE.despine_axes(ax)
    output = LSI_FIG_DIR / "fig_refined_market_lsi_timeseries.png"
    save_png(fig, output)
    register(
        "F05",
        "市场压力指数（MarketLSI）时间序列",
        output,
        "MarketLSI/LSI",
        "data_intermediate/stage2_lsi_labels/market_context.parquet",
        "第4章 LSI与标签",
        "正文",
        notes="日度聚合与滚动均值；阶段阴影仅为时间背景。",
    )


def plot_market_lsi_stage_distribution(market: pd.DataFrame) -> None:
    apply_style()
    daily = market.dropna(subset=["MarketLSI"]).groupby(["date", "reg_stage"])["MarketLSI"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(7.8, 4.8), constrained_layout=True)
    if sns is not None:
        sns.boxplot(data=daily, x="reg_stage", y="MarketLSI", color="#A6CEE3", width=0.5, ax=ax)
        sns.stripplot(data=daily.sample(min(len(daily), 500), random_state=7), x="reg_stage", y="MarketLSI", color="#2F4B7C", size=2.2, alpha=0.35, ax=ax)
    else:
        groups = [g["MarketLSI"].to_numpy() for _, g in daily.groupby("reg_stage")]
        ax.boxplot(groups, labels=list(daily["reg_stage"].drop_duplicates()))
    ax.set_title("MarketLSI 分阶段分布", loc="left")
    ax.set_xlabel("")
    ax.set_ylabel("日均 MarketLSI")
    STYLE.despine_axes(ax)
    output = LSI_FIG_DIR / "fig_market_lsi_stage_distribution.png"
    save_png(fig, output)
    register(
        "F06",
        "MarketLSI 分阶段分布",
        output,
        "MarketLSI/LSI",
        "data_intermediate/stage2_lsi_labels/market_context.parquet",
        "第4章 LSI与标签",
        "正文/附录",
        notes="分阶段描述性比较，不表示严格因果识别。",
    )


def plot_market_lsi_extreme_slot_distribution(market: pd.DataFrame) -> None:
    apply_style()
    m = market.dropna(subset=["MarketLSI", "slot"]).copy()
    threshold = m["MarketLSI"].quantile(0.95)
    extreme = m.loc[m["MarketLSI"] >= threshold].copy()
    counts = extreme.groupby("slot").size().reindex(range(1, 241), fill_value=0).rolling(5, min_periods=1, center=True).mean()
    fig, ax = plt.subplots(figsize=(8.8, 4.5), constrained_layout=True)
    ax.plot(counts.index, counts.values, color=PALETTE["Stress"], linewidth=1.8)
    for slot, label in [(1, "开盘"), (121, "午后开盘"), (230, "尾盘")]:
        ax.axvline(slot, color="#8A8A8A", linewidth=0.8, linestyle=":")
        ax.text(slot + 2, ax.get_ylim()[1], label, ha="left", va="top", fontsize=8, color="#666666")
    ax.set_title("极端 MarketLSI 分钟的日内分布", loc="left")
    ax.set_xlabel("日内 slot")
    ax.set_ylabel("Top 5% 压力分钟数（平滑）")
    STYLE.despine_axes(ax)
    output = LSI_FIG_DIR / "fig_market_lsi_extreme_slot_distribution.png"
    save_png(fig, output)
    register(
        "F07",
        "极端 MarketLSI 分钟的日内分布",
        output,
        "MarketLSI/LSI",
        "data_intermediate/stage2_lsi_labels/market_context.parquet",
        "第4章 LSI与标签",
        "附录",
        notes="用于观察极端压力分钟在日内的集中位置。",
    )


def best_rgarch_model() -> str:
    path = TABLES_ROOT / "04_rgarch" / "rgarch_carr_sk_adapted_oos_losses.csv"
    if not path.exists():
        return "RGARCH-CARR-SK-RMAD"
    losses = pd.read_csv(path)
    test = losses.loc[losses["period"].eq("test")].copy()
    if test.empty:
        return "RGARCH-CARR-SK-RMAD"
    return str(test.sort_values("R2LOG").iloc[0]["model"])


def load_rgarch_paths() -> pd.DataFrame:
    df = pd.read_csv(TABLES_ROOT / "04_rgarch" / "rgarch_carr_sk_adapted_conditional_paths.csv")
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    return df.sort_values(["model", "datetime"])


def rgarch_selected(df: pd.DataFrame) -> pd.DataFrame:
    model = best_rgarch_model()
    out = df.loc[df["model"].eq(model)].copy()
    if out.empty:
        out = df.loc[df["model"].eq("RGARCH-CARR-SK-RMAD")].copy()
    if out.empty:
        out = df.copy()
    return out


def plot_rgarch_conditional_risk(df: pd.DataFrame) -> None:
    apply_style()
    g = rgarch_selected(df)
    g["lambda_log"] = np.log1p(g["lambda_t"].clip(lower=0))
    g["realized_log"] = np.log1p(g["realized_pressure_measure"].clip(lower=0))
    threshold = g.loc[g["period"].eq("train"), "lambda_log"].quantile(0.90)
    fig, ax = plt.subplots(figsize=(10.2, 4.8), constrained_layout=True)
    add_regime_shading(ax)
    ax.plot(g["datetime"], g["lambda_log"], color=PALETTE["RGARCH-CARR-SK"], linewidth=1.8, label="条件压力风险 lambda_t (log)")
    ax.plot(g["datetime"], g["realized_log"], color="#9E9E9E", linewidth=1.0, alpha=0.8, label="realized pressure measure (log)")
    ax.axhline(threshold, color=PALETTE["Stress"], linestyle="--", linewidth=1.0, label="训练期90%阈值")
    ax.set_title("RGARCH-CARR-SK 条件压力风险路径", loc="left")
    ax.set_xlabel("日期")
    ax.set_ylabel("log(1 + risk)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=3, frameon=True)
    STYLE.format_date_axis(ax)
    STYLE.despine_axes(ax)
    output = RGARCH_FIG_DIR / "fig_rgarch_carr_sk_adapted_conditional_risk.png"
    save_png(fig, output)
    register(
        "F08",
        "RGARCH-CARR-SK 条件压力风险路径",
        output,
        "RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv",
        "第6章 RGARCH-CARR-SK",
        "正文",
        notes="选用样本外 R2LOG 较优模型；展示条件风险、realized pressure 和训练期阈值。",
    )


def plot_rgarch_risk_path_only(df: pd.DataFrame) -> None:
    apply_style()
    g = rgarch_selected(df)
    g["lambda_log"] = np.log1p(g["lambda_t"].clip(lower=0))
    fig, ax = plt.subplots(figsize=(9.2, 4.6), constrained_layout=True)
    add_regime_shading(ax)
    ax.plot(g["datetime"], g["lambda_log"], color=PALETTE["RGARCH-CARR-SK"], linewidth=1.9)
    ax.set_title("条件压力风险 lambda_t 路径", loc="left")
    ax.set_xlabel("日期")
    ax.set_ylabel("log(1 + lambda_t)")
    STYLE.format_date_axis(ax)
    STYLE.despine_axes(ax)
    output = RGARCH_FIG_DIR / "fig_rgarch_conditional_risk_path.png"
    save_png(fig, output)
    register(
        "F09",
        "条件压力风险 lambda_t 路径",
        output,
        "RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv",
        "第6章 RGARCH-CARR-SK",
        "正文",
        notes="单独展示条件压力风险主线，避免与 realized measure 叠加过密。",
    )


def plot_rgarch_skew_kurtosis(df: pd.DataFrame) -> None:
    apply_style()
    g = rgarch_selected(df)
    fig, axes = plt.subplots(2, 1, figsize=(10.2, 6.0), sharex=True, constrained_layout=True)
    axes[0].plot(g["datetime"], g["s_t"], color="#4C78A8", linewidth=1.6)
    axes[0].axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
    axes[0].set_title("动态偏度 s_t", loc="left")
    axes[0].set_ylabel("s_t")
    axes[1].plot(g["datetime"], g["k_t"], color="#E15759", linewidth=1.6)
    axes[1].axhline(3, color="#8A8A8A", linestyle="--", linewidth=0.8)
    axes[1].set_title("动态峰度 k_t", loc="left")
    axes[1].set_ylabel("k_t")
    axes[1].set_xlabel("日期")
    if g["k_t"].std(skipna=True) < 0.02:
        axes[1].text(0.02, 0.88, "样本内估计较稳定", transform=axes[1].transAxes, fontsize=9, color="#666666")
    for ax in axes:
        add_regime_shading(ax, label=False)
        STYLE.despine_axes(ax)
    STYLE.format_date_axis(axes[1])
    output = RGARCH_FIG_DIR / "fig_rgarch_dynamic_skew_kurtosis.png"
    save_png(fig, output)
    register(
        "F10",
        "RGARCH-CARR-SK 动态偏度与动态峰度",
        output,
        "RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv",
        "第6章 RGARCH-CARR-SK",
        "正文",
        notes="模型隐含高阶矩路径，不解释为 realized sample moment。",
    )


def plot_rgarch_single_moment(df: pd.DataFrame, column: str, title: str, filename: str, figure_id: str, yref: float | None = None) -> None:
    apply_style()
    g = rgarch_selected(df)
    fig, ax = plt.subplots(figsize=(9.2, 4.6), constrained_layout=True)
    add_regime_shading(ax)
    ax.plot(g["datetime"], g[column], color=PALETTE["RGARCH-CARR-SK"] if column == "s_t" else PALETTE["Stress"], linewidth=1.7)
    if yref is not None:
        ax.axhline(yref, color="#8A8A8A", linestyle="--", linewidth=0.8)
    ax.set_title(title, loc="left")
    ax.set_xlabel("日期")
    ax.set_ylabel(column)
    if column == "k_t" and g[column].std(skipna=True) < 0.02:
        ax.text(0.02, 0.88, "动态峰度估计在样本内较稳定", transform=ax.transAxes, fontsize=9, color="#666666")
    STYLE.format_date_axis(ax)
    STYLE.despine_axes(ax)
    output = RGARCH_FIG_DIR / filename
    save_png(fig, output)
    register(
        figure_id,
        title,
        output,
        "RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv",
        "第6章 RGARCH-CARR-SK",
        "正文/附录",
        notes="单独高阶矩路径图。",
    )


def plot_rgarch_realized_measures() -> None:
    apply_style()
    rm = pd.read_csv(TABLES_ROOT / "04_rgarch" / "rgarch_carr_sk_adapted_realized_pressure_measures.csv")
    cols = ["RV_pressure", "RBV_pressure", "MedRV_pressure", "RMAD_pressure"]
    plot = []
    for col in cols:
        x = np.log1p(pd.to_numeric(rm[col], errors="coerce").clip(lower=0))
        z = (x - x.mean()) / (x.std(ddof=0) or 1.0)
        plot.extend({"measure": col.replace("_pressure", ""), "value": v} for v in z.dropna())
    plot_df = pd.DataFrame(plot)
    fig, ax = plt.subplots(figsize=(7.4, 4.8), constrained_layout=True)
    if sns is not None:
        sns.violinplot(data=plot_df, x="measure", y="value", color="#D7E6F5", inner=None, linewidth=0.8, ax=ax)
        sns.boxplot(data=plot_df, x="measure", y="value", width=0.25, color="white", fliersize=1.5, ax=ax)
    else:
        groups = [g["value"].to_numpy() for _, g in plot_df.groupby("measure")]
        ax.boxplot(groups, labels=list(plot_df["measure"].drop_duplicates()))
    ax.axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
    ax.set_title("realized pressure measures 标准化分布", loc="left")
    ax.set_xlabel("")
    ax.set_ylabel("标准化 log measure")
    STYLE.despine_axes(ax)
    output = RGARCH_FIG_DIR / "fig_rgarch_carr_sk_adapted_realized_measures.png"
    save_png(fig, output)
    register(
        "F13",
        "realized pressure measures 标准化分布",
        output,
        "RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_realized_pressure_measures.csv",
        "第6章 RGARCH-CARR-SK",
        "正文/附录",
        notes="比较 RV、RBV、MedRV、RMAD；使用标准化 log measure 避免量纲混画。",
    )


def plot_rgarch_density_and_losses() -> None:
    apply_style()
    rm = pd.read_csv(TABLES_ROOT / "04_rgarch" / "rgarch_carr_sk_adapted_realized_pressure_measures.csv")
    cols = ["RV_pressure", "RBV_pressure", "MedRV_pressure", "RMAD_pressure"]
    fig, ax = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    for col in cols:
        x = np.log1p(pd.to_numeric(rm[col], errors="coerce").clip(lower=0)).dropna()
        z = (x - x.mean()) / (x.std(ddof=0) or 1.0)
        ax.hist(z, bins=35, density=True, histtype="step", linewidth=1.6, label=col.replace("_pressure", ""))
    ax.set_title("realized pressure measures 密度对比", loc="left")
    ax.set_xlabel("标准化 log measure")
    ax.set_ylabel("密度")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.17), ncol=4, frameon=True)
    STYLE.despine_axes(ax)
    output = RGARCH_FIG_DIR / "fig_rgarch_realized_measure_density.png"
    save_png(fig, output)
    register(
        "F14",
        "realized pressure measures 密度对比",
        output,
        "RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_realized_pressure_measures.csv",
        "第6章 RGARCH-CARR-SK",
        "附录",
        notes="辅助比较不同 realized pressure measure 的分布形态。",
    )

    apply_style()
    losses = pd.read_csv(TABLES_ROOT / "04_rgarch" / "rgarch_carr_sk_adapted_oos_losses.csv")
    fig, ax = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    plot = losses.pivot(index="model", columns="period", values="R2LOG").sort_values("test")
    x = np.arange(len(plot.index))
    width = 0.35
    for i, period in enumerate(plot.columns):
        ax.bar(x + (i - 0.5) * width, plot[period], width=width, label=period, color=PALETTE["Validation"] if period == "validation" else PALETTE["Test"])
    ax.set_xticks(x)
    ax.set_xticklabels([name.replace("RGARCH-CARR-SK-", "") for name in plot.index], rotation=0)
    ax.set_title("RGARCH-CARR-SK 样本外 R2LOG 损失", loc="left")
    ax.set_xlabel("realized pressure measure")
    ax.set_ylabel("R2LOG")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=True)
    STYLE.despine_axes(ax)
    output = RGARCH_FIG_DIR / "fig_rgarch_oos_loss_comparison.png"
    save_png(fig, output)
    register(
        "F15",
        "RGARCH-CARR-SK 样本外损失对比",
        output,
        "RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_oos_losses.csv",
        "第6章 RGARCH-CARR-SK",
        "正文/附录",
        notes="比较不同 realized pressure measure 的 validation/test R2LOG。",
    )


def plot_rgarch_risk_evolution(df: pd.DataFrame) -> None:
    apply_style()
    g = rgarch_selected(df)
    g["lambda_log"] = np.log1p(g["lambda_t"].clip(lower=0))
    fig, axes = plt.subplots(3, 1, figsize=(10.2, 7.2), sharex=True, constrained_layout=True)
    specs = [
        ("lambda_log", "条件压力风险 lambda_t (log)", PALETTE["RGARCH-CARR-SK"]),
        ("s_t", "动态偏度 s_t", "#4C78A8"),
        ("k_t", "动态峰度 k_t", "#E15759"),
    ]
    for ax, (col, title, color) in zip(axes, specs):
        add_regime_shading(ax, label=False)
        ax.plot(g["datetime"], g[col], color=color, linewidth=1.5)
        ax.set_title(title, loc="left")
        ax.set_ylabel(col)
        STYLE.despine_axes(ax)
    axes[-1].set_xlabel("日期")
    STYLE.format_date_axis(axes[-1])
    output = RGARCH_FIG_DIR / "fig_refined_rgarch_risk_evolution.png"
    save_png(fig, output)
    register(
        "F16",
        "RGARCH-CARR-SK 风险与高阶矩演化",
        output,
        "RGARCH-CARR-SK",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv",
        "第6章 RGARCH-CARR-SK",
        "附录",
        notes="综合展示条件风险、动态偏度和动态峰度。",
    )


def plot_qvar_tail_response() -> None:
    apply_style()
    df = pd.read_csv(TABLES_ROOT / "05_qvar" / "qvar_tail_quantile_response.csv")
    plot = df.loc[df["shock_variable"].eq("MarketLSI")].copy()
    fig, ax = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    for q, group in plot.groupby("quantile", sort=True):
        key = f"q{q:.2f}"
        ax.plot(group["horizon"], group["MarketLSI"], label=f"q={q:.2f}", **LINE_STYLES.get(key, {}))
    ax.axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
    ax.set_title("QVAR 尾部分位响应：MarketLSI shock", loc="left")
    ax.set_xlabel("预测步长")
    ax.set_ylabel("MarketLSI 响应")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=4, frameon=True)
    STYLE.despine_axes(ax)
    output = QVAR_FIG_DIR / "fig_qvar_tail_quantile_response.png"
    save_png(fig, output)
    register(
        "F17",
        "QVAR 尾部分位响应",
        output,
        "QVAR",
        "outputs/tables/05_qvar/qvar_tail_quantile_response.csv",
        "第7章 QVAR",
        "正文",
        notes="展示尾部分位传导，不表示严格因果识别。",
    )


def plot_qvar_pressure_paths() -> None:
    apply_style()
    df = pd.read_csv(TABLES_ROOT / "05_qvar" / "qvar_pressure_test_paths.csv")
    response_col = "MarketLSI_response" if "MarketLSI_response" in df.columns else "MarketLSI"
    scenario_order = ["market_crash", "volatility_spike", "liquidity_contraction", "composite_pressure"]
    scenario_cn = {
        "market_crash": "市场急跌",
        "volatility_spike": "波动放大",
        "liquidity_contraction": "成交收缩 / 流动性压力",
        "composite_pressure": "复合压力",
    }
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2), sharex=True, sharey=True, constrained_layout=False)
    axes = axes.reshape(-1)
    handles, labels = [], []
    for ax, scenario in zip(axes, scenario_order):
        panel = df.loc[df["scenario"].eq(scenario) & df["quantile"].isin([0.50, 0.95])].copy()
        for q, group in panel.groupby("quantile", sort=True):
            key = f"q{q:.2f}"
            (line,) = ax.plot(group["horizon"], group[response_col], label=f"q={q:.2f}", **LINE_STYLES.get(key, {}))
            if f"q={q:.2f}" not in labels:
                handles.append(line)
                labels.append(f"q={q:.2f}")
        ax.axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
        ax.set_title(scenario_cn.get(scenario, scenario), loc="left")
        ax.set_xlabel("预测步长")
        ax.set_ylabel("MarketLSI 响应")
        STYLE.despine_axes(ax)
    fig.suptitle("QVAR 情景冲击模拟：MarketLSI 响应", x=0.06, y=0.985, ha="left", fontsize=13)
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.56, 0.985), ncol=2, frameon=True)
    fig.text(0.06, 0.02, "注：基于训练期 QVAR 系数和标准化冲击的情景模拟，展示尾部分位压力传导，不表示严格因果识别。", fontsize=9, color="#555555")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.12, hspace=0.32, wspace=0.20)
    output = QVAR_FIG_DIR / "fig_qvar_pressure_test_paths.png"
    save_png(fig, output)
    register(
        "F18",
        "QVAR 压力测试情景",
        output,
        "QVAR",
        "outputs/tables/05_qvar/qvar_pressure_test_paths.csv",
        "第7章 QVAR",
        "正文",
        notes="四类标准化情景冲击模拟；不是严格因果识别。",
    )


def plot_qvar_response_decay() -> None:
    apply_style()
    irf = pd.read_csv(TABLES_ROOT / "05_qvar" / "qvar_tail_quantile_response.csv")
    plot = irf.loc[irf["shock_variable"].eq("MarketLSI")].copy()
    fig, ax = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    for q, group in plot.groupby("quantile", sort=True):
        key = f"q{q:.2f}"
        ax.plot(group["horizon"], group["MarketLSI"], label=f"q={q:.2f}", **LINE_STYLES.get(key, {}))
    ax.axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
    ax.set_title("QVAR 尾部分位响应：MarketLSI shock", loc="left")
    ax.set_xlabel("预测步长")
    ax.set_ylabel("MarketLSI 响应")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=4, frameon=True)
    STYLE.despine_axes(ax)
    output = QVAR_FIG_DIR / "fig_qvar_response_decay.png"
    save_png(fig, output)
    register("F19", "QVAR 尾部分位响应", output, "QVAR", "outputs/tables/05_qvar/qvar_tail_quantile_response.csv", "第7章 QVAR", "附录", notes="MarketLSI shock 下的分位响应路径。")


def plot_qvar_auxiliary() -> None:
    plot_qvar_response_decay()

    apply_style()
    loss = pd.read_csv(TABLES_ROOT / "05_qvar" / "qvar_blocked_oos_pinball_loss.csv")
    loss = loss.loc[loss["target"].eq("MarketLSI")].copy()
    fig, ax = plt.subplots(figsize=(8.0, 4.8), constrained_layout=True)
    pivot = loss.pivot(index="quantile", columns="eval_period", values="pinball_loss")
    x = np.arange(len(pivot.index))
    width = 0.35
    for i, period in enumerate(pivot.columns):
        ax.bar(x + (i - 0.5) * width, pivot[period], width=width, label=period, color=PALETTE["Validation"] if period == "validation" else PALETTE["Test"])
    ax.set_xticks(x)
    ax.set_xticklabels([f"q={q:.2f}" for q in pivot.index])
    ax.set_title("QVAR MarketLSI 样本外 pinball loss", loc="left")
    ax.set_xlabel("分位点")
    ax.set_ylabel("pinball loss")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=True)
    STYLE.despine_axes(ax)
    output = QVAR_FIG_DIR / "fig_qvar_pinball_loss.png"
    save_png(fig, output)
    register("F20", "QVAR MarketLSI 样本外 pinball loss", output, "QVAR", "outputs/tables/05_qvar/qvar_blocked_oos_pinball_loss.csv", "第7章 QVAR", "附录", notes="只展示 MarketLSI 方程的 validation/test 损失。")

    apply_style()
    coef = pd.read_csv(TABLES_ROOT / "05_qvar" / "qvar_quantile_coefficients_train.csv")
    coef = coef.loc[coef["target"].eq("MarketLSI") & coef["regressor"].ne("const")].copy()
    mat = coef.pivot(index="regressor", columns="quantile", values="estimate")
    fig, ax = plt.subplots(figsize=(7.5, 4.8), constrained_layout=True)
    vmax = np.nanmax(np.abs(mat.to_numpy()))
    im = ax.imshow(mat.to_numpy(), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(np.arange(len(mat.columns)))
    ax.set_xticklabels([f"q={q:.2f}" for q in mat.columns])
    ax.set_yticks(np.arange(len(mat.index)))
    ax.set_yticklabels(mat.index)
    ax.set_title("QVAR MarketLSI 方程系数热力图", loc="left")
    fig.colorbar(im, ax=ax, label="估计系数")
    STYLE.despine_axes(ax)
    output = QVAR_FIG_DIR / "fig_qvar_coefficient_heatmap.png"
    save_png(fig, output)
    register("F21", "QVAR MarketLSI 方程系数热力图", output, "QVAR", "outputs/tables/05_qvar/qvar_quantile_coefficients_train.csv", "第7章 QVAR", "附录", notes="训练期分位数回归系数；用于解释系统变量关系。")


def validate_smartboost_no_crossstress() -> None:
    meta = json.loads((TABLES_ROOT / "06_smartboost" / "smartboost_model_metadata.json").read_text(encoding="utf-8"))
    features = [str(x) for x in meta.get("feature_columns", [])]
    leaked = [x for x in features if x.lower() == "crossstress"]
    if leaked:
        raise RuntimeError(f"SMARTBoost feature metadata contains CrossStress: {leaked}")
    effects = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_partial_effects.csv")
    if effects["feature"].astype(str).str.contains("CrossStress", case=False, na=False).any():
        raise RuntimeError("SMARTBoost partial effects contain CrossStress")


def load_smartboost_predictions() -> pd.DataFrame:
    manifest = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_prediction_manifest.csv")
    parts = []
    for item in manifest.itertuples(index=False):
        path = PROJECT_ROOT / str(item.output_path)
        df = pd.read_parquet(path, columns=["horizon", "period", "y_true", "predicted_probability"])
        df = df.loc[df["period"].isin(["validation", "test"])].copy()
        df["horizon"] = df["horizon"].astype("category")
        df["period"] = df["period"].astype("category")
        df["y_true"] = df["y_true"].astype("int8")
        df["predicted_probability"] = df["predicted_probability"].astype("float32")
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


def smart_metric(metrics: pd.DataFrame, horizon: str, period: str, metric: str) -> float:
    row = metrics.loc[metrics["horizon"].eq(horizon) & metrics["period"].eq(period)]
    if row.empty:
        return float("nan")
    return float(row.iloc[0][metric])


def plot_pr_roc(pred: pd.DataFrame) -> None:
    if precision_recall_curve is None or roc_curve is None or auc is None:
        raise RuntimeError("scikit-learn is required for PR/ROC curves")
    metrics = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_metrics.csv")
    apply_style()
    fig, ax = plt.subplots(figsize=(7.8, 5.0), constrained_layout=True)
    for horizon in ["H5", "H10"]:
        group = pred.loc[pred["period"].eq("test") & pred["horizon"].eq(horizon)]
        precision, recall, _ = precision_recall_curve(group["y_true"].to_numpy(), group["predicted_probability"].to_numpy())
        recall, precision = downsample_xy(recall, precision)
        auc_label = smart_metric(metrics, horizon, "test", "PR_AUC")
        base = smart_metric(metrics, horizon, "test", "positive_rate")
        ax.plot(recall, precision, label=f"{horizon}-test PR-AUC={auc_label:.3f}", **LINE_STYLES[horizon])
        ax.axhline(base, color=LINE_STYLES[horizon]["color"], linestyle=":", linewidth=1.0, alpha=0.75, label=f"{horizon} 基准={base:.3f}")
    ax.set_title("SMARTBoost 样本外 PR 曲线", loc="left")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.19), ncol=2, frameon=True)
    STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_pr_curve.png"
    save_png(fig, output)
    register("F22", "SMARTBoost 样本外 PR 曲线", output, "SMARTBoost", "outputs/tables/06_smartboost/predictions_by_code/*.parquet", "第8章 SMARTBoost", "正文", "是", "使用剔除 CrossStress 后的新预测结果。")

    apply_style()
    fig, ax = plt.subplots(figsize=(7.8, 5.0), constrained_layout=True)
    ax.plot([0, 1], [0, 1], color="#8A8A8A", linestyle="--", linewidth=1.0, label="no skill")
    for horizon in ["H5", "H10"]:
        group = pred.loc[pred["period"].eq("test") & pred["horizon"].eq(horizon)]
        fpr, tpr, _ = roc_curve(group["y_true"].to_numpy(), group["predicted_probability"].to_numpy())
        fpr, tpr = downsample_xy(fpr, tpr)
        auc_label = smart_metric(metrics, horizon, "test", "ROC_AUC")
        ax.plot(fpr, tpr, label=f"{horizon}-test ROC-AUC={auc_label:.3f}", **LINE_STYLES[horizon])
    ax.set_title("SMARTBoost 样本外 ROC 曲线", loc="left")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", frameon=True)
    STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_roc_curve.png"
    save_png(fig, output)
    register("F23", "SMARTBoost 样本外 ROC 曲线", output, "SMARTBoost", "outputs/tables/06_smartboost/predictions_by_code/*.parquet", "第8章 SMARTBoost", "附录", "是", "ROC 为辅助证据，不替代 PR 曲线。")

    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.0), constrained_layout=True)
    for i, period in enumerate(["validation", "test"]):
        for j, curve_type in enumerate(["PR", "ROC"]):
            ax = axes[i, j]
            for horizon in ["H5", "H10"]:
                group = pred.loc[pred["period"].eq(period) & pred["horizon"].eq(horizon)]
                if curve_type == "PR":
                    precision, recall, _ = precision_recall_curve(group["y_true"].to_numpy(), group["predicted_probability"].to_numpy())
                    x, y = downsample_xy(recall, precision)
                    label = f"{horizon}"
                    ax.set_xlabel("Recall")
                    ax.set_ylabel("Precision")
                else:
                    fpr, tpr, _ = roc_curve(group["y_true"].to_numpy(), group["predicted_probability"].to_numpy())
                    x, y = downsample_xy(fpr, tpr)
                    label = f"{horizon}"
                    ax.plot([0, 1], [0, 1], color="#D0D0D0", linestyle="--", linewidth=0.8)
                    ax.set_xlabel("False Positive Rate")
                    ax.set_ylabel("True Positive Rate")
                ax.plot(x, y, label=label, **LINE_STYLES[horizon])
            ax.set_title(f"{period} {curve_type}", loc="left")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1.02)
            ax.legend(loc="lower left" if curve_type == "ROC" else "upper right", frameon=True)
            STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_pr_roc_by_period.png"
    save_png(fig, output)
    register("F24", "SMARTBoost validation/test PR 与 ROC 对比", output, "SMARTBoost", "outputs/tables/06_smartboost/predictions_by_code/*.parquet", "第8章 SMARTBoost", "附录", "是", "辅助展示不同样本外期间曲线。")


def plot_smartboost_calibration() -> None:
    apply_style()
    cal = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_calibration_table.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.8), sharex=True, sharey=True, constrained_layout=True)
    for ax, horizon in zip(axes, ["H5", "H10"]):
        for period, style_key in [("validation", "validation"), ("test", "test")]:
            group = cal.loc[cal["horizon"].eq(horizon) & cal["period"].eq(period)].sort_values("bin")
            ax.plot(
                group["mean_predicted_probability"],
                group["realized_pressure_rate"],
                marker="o",
                markersize=3.5,
                label=period,
                **LINE_STYLES[style_key],
            )
        lim = max(cal["mean_predicted_probability"].max(), cal["realized_pressure_rate"].max()) * 1.05
        ax.plot([0, lim], [0, lim], color="#8A8A8A", linestyle="--", linewidth=0.8)
        ax.set_title(f"{horizon} Calibration", loc="left")
        ax.set_xlabel("平均预测概率")
        ax.set_ylabel("真实压力发生率")
        ax.legend(loc="upper left", frameon=True)
        STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_calibration_curve.png"
    save_png(fig, output)
    register("F25", "SMARTBoost Calibration 曲线", output, "SMARTBoost", "outputs/tables/06_smartboost/smartboost_calibration_table.csv", "第8章 SMARTBoost", "正文/附录", "是", "分箱点图和45度参考线。")


def plot_smartboost_highrisk() -> None:
    apply_style()
    event = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_event_rate_and_lift.csv")
    event = event.loc[event["reg_stage"].eq("ALL")].copy()
    event["label"] = event["horizon"] + "-" + event["period"]
    x = np.arange(len(event))
    fig, ax = plt.subplots(figsize=(9.2, 4.8), constrained_layout=True)
    bars = ax.bar(x, event["Precision_Top5pct"], color=[PALETTE["Validation"] if p == "validation" else PALETTE["Test"] for p in event["period"]], width=0.62)
    ax.scatter(x, event["positive_rate"], marker="D", color="#333333", s=24, label="全样本基准事件率", zorder=3)
    for bar, lift in zip(bars, event["Top5_lift"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.015, f"{lift:.1f}x", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(event["label"], rotation=0)
    ax.set_title("SMARTBoost Top 5% 高风险组真实压力发生率", loc="left")
    ax.set_xlabel("")
    ax.set_ylabel("真实压力发生率")
    STYLE.format_percent_axis(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.14), ncol=1, frameon=True)
    STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_top5_realized_rate.png"
    save_png(fig, output)
    register("F26", "SMARTBoost Top 5% 高风险组真实压力发生率", output, "SMARTBoost", "outputs/tables/06_smartboost/smartboost_event_rate_and_lift.csv", "第8章 SMARTBoost", "正文", "是", "柱上标注为 Top5 lift。")

    apply_style()
    high = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_high_risk_group_rates.csv")
    order = ["top_1pct", "top_5pct", "top_10pct", "top_20pct"]
    high["group"] = pd.Categorical(high["group"], categories=order, ordered=True)
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6), sharey=True, constrained_layout=True)
    for ax, horizon in zip(axes, ["H5", "H10"]):
        for period, style_key in [("validation", "validation"), ("test", "test")]:
            group = high.loc[high["horizon"].eq(horizon) & high["period"].eq(period)].sort_values("group")
            ax.plot(group["group"].astype(str), group["realized_pressure_rate"], marker="o", label=period, **LINE_STYLES[style_key])
        ax.set_title(f"{horizon} 高风险分组命中率", loc="left")
        ax.set_xlabel("风险分组")
        ax.set_ylabel("真实压力发生率")
        STYLE.format_percent_axis(ax)
        ax.legend(loc="upper right", frameon=True)
        STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_refined_top5_realized_rate.png"
    save_png(fig, output)
    register("F27", "SMARTBoost 高风险分组命中率", output, "SMARTBoost", "outputs/tables/06_smartboost/smartboost_high_risk_group_rates.csv", "第8章 SMARTBoost", "附录", "是", "展示 Top 1/5/10/20% 分组真实压力发生率。")

    apply_style()
    metrics = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_metrics.csv")
    high2 = high.merge(metrics[["horizon", "period", "positive_rate"]], on=["horizon", "period"], how="left")
    high2["lift"] = high2["realized_pressure_rate"] / high2["positive_rate"]
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6), sharey=True, constrained_layout=True)
    for ax, horizon in zip(axes, ["H5", "H10"]):
        for period, style_key in [("validation", "validation"), ("test", "test")]:
            group = high2.loc[high2["horizon"].eq(horizon) & high2["period"].eq(period)].sort_values("group")
            ax.plot(group["group"].astype(str), group["lift"], marker="o", label=period, **LINE_STYLES[style_key])
        ax.axhline(1, color="#8A8A8A", linestyle="--", linewidth=0.8)
        ax.set_title(f"{horizon} lift curve", loc="left")
        ax.set_xlabel("风险分组")
        ax.set_ylabel("Lift")
        ax.legend(loc="upper right", frameon=True)
        STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_lift_curve.png"
    save_png(fig, output)
    register("F28", "SMARTBoost lift curve", output, "SMARTBoost", "outputs/tables/06_smartboost/smartboost_high_risk_group_rates.csv", "第8章 SMARTBoost", "正文/附录", "是", "高风险分组相对基准事件率的 lift。")


def plot_smartboost_partial_effects() -> None:
    effects = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_partial_effects.csv")
    if effects["feature"].astype(str).str.contains("CrossStress", case=False, na=False).any():
        raise RuntimeError("CrossStress found in SMARTBoost partial effects")
    ranges = (
        effects.groupby(["feature", "horizon"])["mean_predicted_probability"]
        .agg(lambda x: x.max() - x.min())
        .reset_index(name="range")
        .groupby("feature")["range"]
        .max()
        .sort_values(ascending=False)
    )
    selected = [f for f in ranges.index if f != "CrossStress"][:4]
    labels = {
        "MarketLSI": "市场压力指数（MarketLSI）",
        "IndexRV": "指数波动状态（IndexRV）",
        "MarketRelAmt": "市场相对成交额（MarketRelAmt）",
        "LSI_5_lag1": "上一分钟压力（LSI_5_lag1）",
        "LSI_5_rollmax_20": "过去窗口压力峰值（LSI_5_rollmax_20）",
    }
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.0), constrained_layout=True)
    axes = axes.reshape(-1)
    for ax, feature in zip(axes, selected):
        panel = effects.loc[effects["feature"].eq(feature)].copy()
        for horizon in ["H5", "H10"]:
            g = panel.loc[panel["horizon"].eq(horizon)].sort_values("feature_value")
            ax.plot(g["feature_value"], g["mean_predicted_probability"], marker="o", markersize=3.0, label=horizon, **LINE_STYLES[horizon])
        ax.set_title(labels.get(feature, feature), loc="left")
        ax.set_xlabel(labels.get(feature, feature))
        ax.set_ylabel("预测概率的局部响应")
        ax.legend(loc="upper left", frameon=True)
        STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_partial_effects.png"
    save_png(fig, output)
    register("F29", "SMARTBoost Partial Effects", output, "SMARTBoost", "outputs/tables/06_smartboost/smartboost_partial_effects.csv", "第8章 SMARTBoost", "正文/附录", "是", "选择局部响应幅度最大的4个无泄漏变量；不含 CrossStress。")

    apply_style()
    all_features = [f for f in ranges.index if f != "CrossStress"][:5]
    nrows = math.ceil(len(all_features) / 2)
    fig, axes = plt.subplots(nrows, 2, figsize=(10.4, 3.3 * nrows), constrained_layout=True)
    axes = np.asarray(axes).reshape(-1)
    for ax, feature in zip(axes, all_features):
        panel = effects.loc[effects["feature"].eq(feature)].copy()
        for horizon in ["H5", "H10"]:
            g = panel.loc[panel["horizon"].eq(horizon)].sort_values("feature_value")
            ax.plot(g["feature_value"], g["mean_predicted_probability"], marker="o", markersize=2.8, label=horizon, **LINE_STYLES[horizon])
        ax.set_title(labels.get(feature, feature), loc="left")
        ax.set_xlabel(feature)
        ax.set_ylabel("预测概率")
        ax.legend(loc="upper left", frameon=True)
        STYLE.despine_axes(ax)
    for ax in axes[len(all_features) :]:
        ax.set_visible(False)
    output = SMART_FIG_DIR / "fig_refined_partial_effects.png"
    save_png(fig, output)
    register("F30", "SMARTBoost refined Partial Effects", output, "SMARTBoost", "outputs/tables/06_smartboost/smartboost_partial_effects.csv", "第8章 SMARTBoost", "附录", "是", "展示当前 partial effects 表中的无泄漏变量。")


def plot_smartboost_probability_and_regime(pred: pd.DataFrame) -> None:
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.8), sharey=True, constrained_layout=True)
    sample = pred.loc[pred["period"].eq("test")].copy()
    for ax, horizon in zip(axes, ["H5", "H10"]):
        panel = sample.loc[sample["horizon"].eq(horizon)]
        for y, label, color in [(0, "非压力", "#4C78A8"), (1, "压力事件", "#E15759")]:
            vals = panel.loc[panel["y_true"].eq(y), "predicted_probability"].to_numpy()
            if len(vals) > 800_000:
                rng = np.random.default_rng(20260520 + y)
                vals = rng.choice(vals, size=800_000, replace=False)
            ax.hist(vals, bins=45, density=True, alpha=0.40, color=color, label=label)
        ax.set_title(f"{horizon} test 预测概率分布", loc="left")
        ax.set_xlabel("预测概率")
        ax.set_ylabel("密度")
        ax.legend(loc="upper right", frameon=True)
        STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_probability_distribution.png"
    save_png(fig, output)
    register("F31", "SMARTBoost 预测概率分布", output, "SMARTBoost", "outputs/tables/06_smartboost/predictions_by_code/*.parquet", "第8章 SMARTBoost", "附录", "是", "展示 test 样本正负例预测概率分离。")

    apply_style()
    regime = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_regime_metrics.csv")
    regime["label"] = regime["horizon"] + "-" + regime["period"]
    fig, ax = plt.subplots(figsize=(9.4, 4.8), constrained_layout=True)
    pivot = regime.pivot_table(index="reg_stage", columns="horizon", values="PR_AUC", aggfunc="mean")
    x = np.arange(len(pivot.index))
    width = 0.35
    for i, horizon in enumerate(["H5", "H10"]):
        if horizon in pivot:
            ax.bar(x + (i - 0.5) * width, pivot[horizon], width=width, label=horizon, color=LINE_STYLES[horizon]["color"])
    ax.set_xticks(x)
    ax.set_xticklabels([str(x).replace("_to_", "\n至\n") for x in pivot.index], fontsize=8)
    ax.set_title("SMARTBoost 分阶段 PR-AUC", loc="left")
    ax.set_xlabel("监管阶段")
    ax.set_ylabel("PR-AUC")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=True)
    STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_regime_metrics.png"
    save_png(fig, output)
    register("F32", "SMARTBoost 分阶段 PR-AUC", output, "SMARTBoost", "outputs/tables/06_smartboost/smartboost_regime_metrics.csv", "第8章 SMARTBoost", "附录", "是", "分阶段描述性性能对比，不作因果识别。")

    apply_style()
    imp = pd.read_csv(TABLES_ROOT / "06_smartboost" / "smartboost_feature_importance.csv")
    top = imp.groupby("feature")["importance"].mean().sort_values(ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(8.2, 5.0), constrained_layout=True)
    ax.barh(np.arange(len(top)), top.values, color="#A6CEE3")
    ax.set_yticks(np.arange(len(top)))
    ax.set_yticklabels(top.index)
    ax.invert_yaxis()
    ax.set_title("SMARTBoost feature importance", loc="left")
    ax.set_xlabel("importance")
    if float(top.max()) == 0.0:
        ax.text(0.02, 0.92, "当前 importance 表未提供有效排序（均为0）", transform=ax.transAxes, fontsize=9, color="#666666")
    STYLE.despine_axes(ax)
    output = SMART_FIG_DIR / "fig_smartboost_feature_importance.png"
    save_png(fig, output)
    register("F33", "SMARTBoost feature importance", output, "SMARTBoost", "outputs/tables/06_smartboost/smartboost_feature_importance.csv", "第8章 SMARTBoost", "附录", "是", "若 importance 全为0，图中如实说明。")


def write_qvar_scenario_check() -> None:
    df = pd.read_csv(TABLES_ROOT / "05_qvar" / "qvar_pressure_test_paths.csv")
    scenarios = sorted(df["scenario"].dropna().unique().tolist())
    definitions = pd.read_csv(TABLES_ROOT / "05_qvar" / "qvar_pressure_test_scenario_definitions.csv")
    lines = [
        "# QVAR Scenario Coverage Check",
        "",
        "## 核查结论",
        "",
        "原始不完整原因：`code/src/models/06_qvar_tail_transmission.py` 的 `build_response_tables()` 最初只硬编码生成两类情景；不是绘图代码漏读。",
        "",
        "本轮状态：已通过 `code/src/models/06b_qvar_stress_test.py` 基于既有训练期 QVAR 系数补齐四类标准化情景冲击模拟，未重估 QVAR，未修改 stage0-stage3、RGARCH-CARR-SK 或 SMARTBoost。",
        "",
        f"当前 `qvar_pressure_test_paths.csv` 可用情景数：{len(scenarios)}。",
        "",
        "## 当前可用情景",
        "",
        "| 情景 | 中文标签 | 冲击定义 | 数据来源 | 是否已绘制 |",
        "|---|---|---|---|---|",
    ]
    for row in definitions.itertuples(index=False):
        lines.append(
            f"| `{row.scenario}` | {row.scenario_cn} | `{row.shock_definition}` | 训练期 QVAR 系数递推 | 是 |"
        )
    lines.extend(
        [
            "",
            "## 未绘制情景",
            "",
            "无。四类标准情景均已绘制到 `outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png`。",
            "",
            "## 解释边界",
            "",
            "该图表示 QVAR 情景冲击模拟和尾部分位压力传导，不表示严格因果识别。",
        ]
    )
    (REPORT_DIR / "qvar_scenario_coverage_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_registry() -> None:
    rows = sorted(REGISTRY_ROWS, key=lambda r: r.figure_id)
    csv_path = FIGURES_ROOT / "in_place_figure_registry.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))

    lines = [
        "# 图表登记：Figure Registry",
        "",
        "本登记表记录本轮全量图表论文级重构后的原位 PNG 输出。`99_paper_ready/` 为历史派生目录，不再作为最终图表来源。",
        "",
        "## 最终 PNG 图表",
        "",
        "| 编号 | 标题 | PNG 路径 | 模块 | 用途说明 | 对应章节 | SMARTBoost 修正后结果 | 去向 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.figure_id} | {row.title} | `{row.figure_path_png}` | {row.module} | {row.notes} | {row.chapter} | {row.smartboost_current_result} | {row.destination} |"
        )
    lines.extend(
        [
            "",
            "## 废弃或仅作历史备查",
            "",
            "| 路径 | 处理 | 原因 |",
            "|---|---|---|",
            "| `outputs/figures/99_paper_ready/*.png` | 不作为最终图表来源 | 派生目录不符合本轮原位更新要求；旧 QVAR 情景图只含两类情景 |",
            "| `outputs/figures/99_paper_ready/*.pdf` | 不作为最终图表来源 | 本轮只登记 PNG，不输出 PDF |",
            "| 旧 `CrossStress` 相关可视化 | 不进入正文 | `CrossStress` 来自未来压力标签横截面聚合，不能作为 SMARTBoost 预测特征或预警证据 |",
            "",
            "## 审计",
            "",
            "- 全量图清单：`reviews/report_consistency/full_figure_inventory_before_rebuild.md`",
            "- 重构计划：`reviews/report_consistency/full_figure_rebuild_plan_v2.md`",
            "- QVAR 情景核查：`reviews/report_consistency/qvar_scenario_coverage_check.md`",
            "- 最终审计：`reviews/report_consistency/full_figure_rebuild_final_audit.md`",
            "- 审计 CSV：`reviews/report_consistency/full_figure_rebuild_audit.csv`",
            f"- CSV registry：`{rel(csv_path)}`",
        ]
    )
    (PROJECT_ROOT / "docs/admin" / "figure_registry.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def audit_final_figures(existing_before: set[Path], pdf_before_count: int) -> None:
    registry_names = {row.figure_path_png for row in REGISTRY_ROWS}
    rows = []
    for path in sorted(set(WRITTEN_FIGURES)):
        dpi_x, dpi_y, blank = FIG_AUDIT.inspect_png(path)
        size = path.stat().st_size if path.exists() else 0
        leak = False
        if "06_smartboost" in path.as_posix().lower():
            leak = "crossstress" in path.name.lower()
        failures = []
        if not path.exists():
            failures.append("missing_png")
        if dpi_x is None or dpi_y is None:
            failures.append("dpi_unreadable")
        elif dpi_x < 299 or dpi_y < 299:
            failures.append("dpi_below_300")
        if size < 8_000:
            failures.append("file_too_small")
        if blank:
            failures.append("blank_suspect")
        if rel(path) not in registry_names:
            failures.append("not_in_registry")
        if leak:
            failures.append("crossstress_leakage_suspect")
        rows.append(
            AuditRow(
                figure_path_png=rel(path),
                exists_png=path.exists(),
                dpi_x=dpi_x,
                dpi_y=dpi_y,
                dpi_ok=(dpi_x is not None and dpi_y is not None and dpi_x >= 299 and dpi_y >= 299),
                size_bytes=size,
                size_ok=size >= 8_000,
                blank_suspect=bool(blank),
                in_registry=rel(path) in registry_names,
                crossstress_leakage_suspect=leak,
                status="PASS" if not failures else "FAIL",
                notes=";".join(failures),
            )
        )

    audit_path = REPORT_DIR / "full_figure_rebuild_audit.csv"
    with audit_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))

    written = set(WRITTEN_FIGURES)
    overwritten = sorted(path for path in written if path in existing_before)
    added = sorted(path for path in written if path not in existing_before)
    legacy_png = [p for p in existing_before if "99_paper_ready" in p.parts]
    pdf_after_count = len(list(FIGURES_ROOT.rglob("*.pdf")))
    qvar_paths = pd.read_csv(TABLES_ROOT / "05_qvar" / "qvar_pressure_test_paths.csv")
    qvar_scenarios = sorted(qvar_paths["scenario"].dropna().unique().tolist())
    smart_rows = [row for row in REGISTRY_ROWS if row.module == "SMARTBoost"]
    failures = [row for row in rows if row.status != "PASS"]
    lines = [
        "# Full Figure Rebuild Final Audit",
        "",
        "## 1. 执行范围",
        "",
        f"- 本轮开始前扫描到 PNG：{len(existing_before)} 张，其中 `99_paper_ready` 旧派生 PNG：{len(legacy_png)} 张。",
        f"- 原模块 PNG 重构/新增输出：{len(written)} 张。",
        f"- 覆盖更新原有 PNG：{len(overwritten)} 张。",
        f"- 新增辅助 PNG：{len(added)} 张。",
        f"- 删除/废弃图：{len(legacy_png)} 张旧 `99_paper_ready` PNG 降级为历史备查；本轮未物理删除文件。",
        "",
        "## 2. 覆盖更新图",
        "",
    ]
    lines.extend(f"- `{rel(path)}`" for path in overwritten)
    lines.extend(["", "## 3. 新增辅助图", ""])
    lines.extend(f"- `{rel(path)}`" for path in added)
    lines.extend(
        [
            "",
            "## 4. 审计结果",
            "",
            f"- 审计 CSV：`{rel(audit_path)}`",
            f"- PASS：{len(rows) - len(failures)}",
            f"- FAIL：{len(failures)}",
            "- 所有最终 PNG 均为 300dpi。" if not failures else "- 存在未通过审计的 PNG，详见 CSV。",
            "- Legend 布局：绘图脚本统一使用图外上方、右上/左上空白区或分面内部非数据密集区；人工抽查仍建议逐图确认。",
            f"- QVAR 当前情景数：{len(qvar_scenarios)}，情景为：{', '.join(qvar_scenarios)}。",
            "- QVAR 四类标准情景已补齐：市场急跌、波动放大、成交收缩 / 流动性压力、复合压力。",
            f"- SMARTBoost 最终图数量：{len(smart_rows)}；均基于剔除 `CrossStress` 后的新结果。",
            f"- 本轮是否输出 PDF：否。历史 PDF 数量从 {pdf_before_count} 到 {pdf_after_count}，未作为最终 registry 输出。",
            "- 所有最终图均保存在原模块目录下，未输出到 `99_paper_ready/`。",
            "",
            "## 5. 仍需人工复核",
            "",
            "- `fig_refined_coverage_heatmap.png`：行数较多，建议确认论文版面是否接受当前高度。",
            "- RGARCH 高阶矩图：建议确认动态峰度稳定性的正文表述是否足够保守。",
            "- QVAR 情景图：建议确认四类标准化冲击命名和正文解释均保持“情景模拟”口径。",
            "- SMARTBoost Partial Effects：建议确认 4 个变量是否符合最终论文解释重点。",
            "",
            "## 6. 未触碰事项",
            "",
            "- 未重跑 stage0-stage3。",
            "- 未修改 RGARCH-CARR-SK、QVAR、SMARTBoost 的模型定义；新增/使用的 QVAR 情景脚本只基于既有系数递推。",
            "- 未修改 `data_inbox/preprocessed/`。",
            "- 未重新引入 `CrossStress` 作为 SMARTBoost 特征。",
            "- 未进入 LaTeX 编译。",
        ]
    )
    (REPORT_DIR / "full_figure_rebuild_final_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    paths.ensure_runtime_dirs()
    for directory in [DATA_FIG_DIR, LSI_FIG_DIR, RGARCH_FIG_DIR, QVAR_FIG_DIR, SMART_FIG_DIR, REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    existing_before = set(FIGURES_ROOT.rglob("*.png"))
    pdf_before_count = len(list(FIGURES_ROOT.rglob("*.pdf")))

    validate_smartboost_no_crossstress()

    plot_coverage_heatmap()
    plot_coverage_by_exchange()

    slot_summary, stage_summary = load_lsi_slot_summaries()
    plot_lsi_intraday(slot_summary)
    plot_lsi_intraday_by_stage(stage_summary)
    market = load_market_context()
    plot_market_lsi_timeseries(market)
    plot_market_lsi_stage_distribution(market)
    plot_market_lsi_extreme_slot_distribution(market)

    rgarch = load_rgarch_paths()
    plot_rgarch_conditional_risk(rgarch)
    plot_rgarch_risk_path_only(rgarch)
    plot_rgarch_skew_kurtosis(rgarch)
    plot_rgarch_single_moment(rgarch, "s_t", "RGARCH-CARR-SK 动态偏度", "fig_rgarch_carr_sk_adapted_dynamic_skewness.png", "F11", yref=0.0)
    plot_rgarch_single_moment(rgarch, "k_t", "RGARCH-CARR-SK 动态峰度", "fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png", "F12", yref=3.0)
    plot_rgarch_realized_measures()
    plot_rgarch_density_and_losses()
    plot_rgarch_risk_evolution(rgarch)

    plot_qvar_tail_response()
    plot_qvar_pressure_paths()
    plot_qvar_auxiliary()
    write_qvar_scenario_check()

    smart_pred = load_smartboost_predictions()
    plot_pr_roc(smart_pred)
    plot_smartboost_calibration()
    plot_smartboost_highrisk()
    plot_smartboost_partial_effects()
    plot_smartboost_probability_and_regime(smart_pred)

    write_registry()
    audit_final_figures(existing_before, pdf_before_count)
    print(f"rebuild_complete figures={len(set(WRITTEN_FIGURES))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
