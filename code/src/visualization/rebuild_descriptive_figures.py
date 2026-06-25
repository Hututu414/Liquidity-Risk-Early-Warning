from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SKILL_SCRIPT_DIR = PROJECT_ROOT / ".agents" / "skills" / "academic-finance-visualization-cn" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPT_DIR))

from finance_paper_style import (  # noqa: E402
    apply_finance_paper_style,
    despine_axes,
    format_date_axis,
    format_percent_axis,
    get_model_palette,
    standardize_legend,
)


import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402


STAGE1_DIR = PROJECT_ROOT / "data_intermediate" / "stage1_model_ready"
STAGE2_DIR = PROJECT_ROOT / "data_intermediate" / "stage2_lsi_labels"
OLD_DESC_TABLE_DIR = PROJECT_ROOT / "outputs" / "descriptive_diagnostics" / "tables"
OUT_FIG_DIR = PROJECT_ROOT / "outputs" / "figures" / "03_descriptive"
OUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "03_descriptive"
AUDIT_DIR = PROJECT_ROOT / "reviews" / "figure_audit"

PALETTE = get_model_palette()
PERIOD_COLORS = {
    "train": "#EAF2F8",
    "validation": "#FFF3E0",
    "test": "#FDEDEC",
}
PERIOD_LABELS = {
    "train": "training",
    "validation": "validation",
    "test": "test",
}


@dataclass
class FigureRecord:
    figure_id: str
    title: str
    path: str
    input_data: str
    destination: str
    notes: str
    overwritten_existing: bool


FIGURES: list[FigureRecord] = []


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def save_png(fig: plt.Figure, path: Path, dpi: int = 300) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return existed


def register(
    figure_id: str,
    title: str,
    path: Path,
    input_data: str,
    destination: str,
    notes: str,
    overwritten_existing: bool,
) -> None:
    FIGURES.append(
        FigureRecord(
            figure_id=figure_id,
            title=title,
            path=rel(path),
            input_data=input_data,
            destination=destination,
            notes=notes,
            overwritten_existing=overwritten_existing,
        )
    )


def load_time_split() -> dict[str, pd.Timestamp]:
    raw = json.loads((STAGE2_DIR / "time_split.json").read_text(encoding="utf-8"))
    return {
        "train_start": pd.Timestamp(raw["train_start"]),
        "train_end": pd.Timestamp(raw["train_end"]),
        "validation_start": pd.Timestamp(raw["validation_start"]),
        "validation_end": pd.Timestamp(raw["validation_end"]),
        "test_start": pd.Timestamp(raw["test_start"]),
        "test_end": pd.Timestamp(raw["test_end"]),
    }


def assign_period(date_series: pd.Series, split: dict[str, pd.Timestamp]) -> pd.Series:
    dates = pd.to_datetime(date_series)
    out = pd.Series("other", index=dates.index, dtype="object")
    out[(dates >= split["train_start"]) & (dates <= split["train_end"])] = "train"
    out[(dates >= split["validation_start"]) & (dates <= split["validation_end"])] = "validation"
    out[(dates >= split["test_start"]) & (dates <= split["test_end"])] = "test"
    return out


def add_period_background(ax: plt.Axes, split: dict[str, pd.Timestamp], label: bool = False) -> None:
    spans = [
        ("train", split["train_start"], split["train_end"]),
        ("validation", split["validation_start"], split["validation_end"]),
        ("test", split["test_start"], split["test_end"]),
    ]
    for period, start, end in spans:
        ax.axvspan(start, end, color=PERIOD_COLORS[period], alpha=0.38, lw=0)
        if label:
            mid = start + (end - start) / 2
            ylim = ax.get_ylim()
            ax.text(
                mid,
                ylim[1],
                PERIOD_LABELS[period],
                ha="center",
                va="top",
                fontsize=9,
                color="#666666",
            )


def load_market_daily(split: dict[str, pd.Timestamp]) -> pd.DataFrame:
    market = pd.read_parquet(STAGE2_DIR / "market_context.parquet")
    market["datetime"] = pd.to_datetime(market["datetime"])
    market["date"] = market["datetime"].dt.normalize()
    daily = (
        market.dropna(subset=["MarketLSI"])
        .groupby("date")
        .agg(
            MarketLSI_mean=("MarketLSI", "mean"),
            MarketLSI_p95=("MarketLSI", lambda x: x.quantile(0.95)),
            MarketLSI_max=("MarketLSI", "max"),
            IndexRet_sum=("IndexRet", "sum"),
            IndexRV_mean=("IndexRV", "mean"),
            MarketRelAmt_mean=("MarketRelAmt", "mean"),
        )
        .reset_index()
    )
    daily["period"] = assign_period(daily["date"], split)
    daily["MarketLSI_20d"] = daily["MarketLSI_mean"].rolling(20, min_periods=5).mean()
    return daily


def plot_coverage_heatmap(split: dict[str, pd.Timestamp]) -> None:
    coverage = pd.read_csv(STAGE1_DIR / "coverage_by_code_date.csv")
    manifest = pd.read_csv(STAGE1_DIR / "model_ready_manifest.csv")[["code", "is_index"]]
    coverage["date"] = pd.to_datetime(coverage["date"])
    coverage["month"] = coverage["date"].dt.to_period("M").astype(str)
    coverage["coverage_rate"] = pd.to_numeric(coverage["valid_minutes"], errors="coerce") / 240.0
    coverage = coverage.merge(manifest, on="code", how="left")
    coverage["exchange"] = np.select(
        [
            coverage["is_index"].fillna(False),
            coverage["code"].str.endswith(".SH", na=False),
            coverage["code"].str.endswith(".SZ", na=False),
        ],
        ["Index", "SH", "SZ"],
        default="Other",
    )
    monthly = (
        coverage.groupby(["code", "exchange", "month"], as_index=False)["coverage_rate"]
        .mean()
        .dropna()
    )
    order = (
        monthly.groupby(["code", "exchange"])["coverage_rate"]
        .mean()
        .reset_index()
        .sort_values(["exchange", "coverage_rate", "code"], ascending=[True, False, True])
    )
    pivot = monthly.pivot(index="code", columns="month", values="coverage_rate")
    pivot = pivot.reindex(order["code"])
    month_labels = list(pivot.columns)

    apply_finance_paper_style()
    fig, ax = plt.subplots(figsize=(11.8, 10.8), constrained_layout=True)
    cmap = LinearSegmentedColormap.from_list("coverage", ["#F7FBFF", "#9ECAE1", "#08519C"])
    image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap=cmap, vmin=0.95, vmax=1.0)
    cbar = fig.colorbar(image, ax=ax, pad=0.012, shrink=0.82)
    cbar.set_label("有效分钟覆盖率")

    ax.set_title("股票-月份有效分钟覆盖率", loc="left", pad=10)
    ax.set_xlabel("月份")
    ax.set_ylabel("样本证券")

    step = 3 if len(month_labels) > 24 else 2
    xticks = np.arange(0, len(month_labels), step)
    ax.set_xticks(xticks)
    ax.set_xticklabels([month_labels[i] for i in xticks], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels([x.replace(".", "") for x in pivot.index], fontsize=7)

    for boundary in ["validation_start", "test_start"]:
        month = split[boundary].to_period("M").strftime("%Y-%m")
        if month in month_labels:
            xpos = month_labels.index(month) - 0.5
            ax.axvline(xpos, color="#333333", linestyle="--", linewidth=0.8)
            ax.text(xpos + 0.2, -1.1, boundary.replace("_start", ""), fontsize=8, color="#333333")

    for spine in ax.spines.values():
        spine.set_visible(False)

    out = OUT_FIG_DIR / "fig_descriptive_01_sample_coverage_heatmap.png"
    existed = save_png(fig, out)
    register(
        "D01",
        "股票-月份有效分钟覆盖率",
        out,
        "data_intermediate/stage1_model_ready/coverage_by_code_date.csv",
        "正文",
        "图一；按月聚合避免逐日热力图过密，按交易所和平均覆盖率排序。",
        existed,
    )


def plot_sample_split_timeline(split: dict[str, pd.Timestamp]) -> None:
    apply_finance_paper_style()
    periods = [
        ("training", split["train_start"], split["train_end"], PALETTE["MarketLSI"]),
        ("validation", split["validation_start"], split["validation_end"], PALETTE["Validation"]),
        ("test", split["test_start"], split["test_end"], PALETTE["Test"]),
    ]
    fig, ax = plt.subplots(figsize=(9.4, 3.4), constrained_layout=True)
    for idx, (label, start, end, color) in enumerate(periods):
        ax.barh(idx, (end - start).days + 1, left=start, height=0.46, color=color, alpha=0.78)
        ax.annotate(
            start.strftime("%Y-%m-%d"),
            xy=(start, idx),
            xytext=(0, -14),
            textcoords="offset points",
            ha="left",
            va="top",
            fontsize=9
        )
        ax.annotate(
            end.strftime("%Y-%m-%d"),
            xy=(end, idx),
            xytext=(0, -14),
            textcoords="offset points",
            ha="right",
            va="top",
            fontsize=9
        )
    ax.set_yticks(range(len(periods)))
    ax.set_yticklabels([p[0] for p in periods], fontsize=10)
    ax.margins(y=0.3)
    ax.set_xlabel("日期", fontsize=10)
    ax.invert_yaxis()
    format_date_axis(ax)
    ax.tick_params(axis='x', labelsize=9)
    despine_axes(ax)
    out = OUT_FIG_DIR / "fig_descriptive_02_sample_split_timeline.png"
    existed = save_png(fig, out)
    register("D02", "样本划分时间轴", out, "data_intermediate/stage2_lsi_labels/time_split.json", "正文", "展示 training / validation / test 的时间区间。", existed)


def plot_market_lsi_timeseries(daily: pd.DataFrame, split: dict[str, pd.Timestamp]) -> None:
    apply_finance_paper_style()
    fig, ax = plt.subplots(figsize=(10.8, 4.8), constrained_layout=True)
    add_period_background(ax, split)
    ax.plot(daily["date"], daily["MarketLSI_mean"], color="#9E9E9E", linewidth=0.8, alpha=0.6, label="日均 MarketLSI")
    ax.plot(daily["date"], daily["MarketLSI_20d"], color=PALETTE["MarketLSI"], linewidth=2.0, label="20日滚动均值")
    top = daily.nlargest(4, "MarketLSI_mean").sort_values("date")
    ax.scatter(top["date"], top["MarketLSI_mean"], s=28, color=PALETTE["Stress"], zorder=4, label="高压力日")
    for _, row in top.iterrows():
        ax.annotate(
            row["date"].strftime("%Y-%m-%d"),
            xy=(row["date"], row["MarketLSI_mean"]),
            xytext=(4, 8),
            textcoords="offset points",
            fontsize=8,
            color="#555555",
        )
    ax.set_title("市场压力指数（MarketLSI）日度演化", loc="left")
    ax.set_ylabel("MarketLSI")
    ax.set_xlabel("日期")
    format_date_axis(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=3, frameon=True)
    standardize_legend(ax)
    despine_axes(ax)
    out = OUT_FIG_DIR / "fig_descriptive_03_marketlsi_timeseries.png"
    existed = save_png(fig, out)
    register("D03", "MarketLSI 日度时间序列", out, "data_intermediate/stage2_lsi_labels/market_context.parquet", "正文", "日均 MarketLSI、20日滚动均值和高压力日标注。", existed)


def plot_event_rate_timeseries(split: dict[str, pd.Timestamp]) -> pd.DataFrame:
    rates = pd.read_csv(OLD_DESC_TABLE_DIR / "stress_rate_by_date.csv")
    rates["date"] = pd.to_datetime(rates["date"])
    rates["period"] = assign_period(rates["date"], split)
    monthly = (
        rates.set_index("date")[["Stress_H5_mean", "Stress_H10_mean"]]
        .resample("ME")
        .mean()
        .dropna()
        .reset_index()
    )
    monthly["period"] = assign_period(monthly["date"], split)

    apply_finance_paper_style()
    fig, ax = plt.subplots(figsize=(10.4, 4.4), constrained_layout=True)
    add_period_background(ax, split)
    ax.plot(monthly["date"], monthly["Stress_H5_mean"], color=PALETTE["Stress"], linewidth=1.8, marker="o", markersize=2.8, label="Stress_H5")
    ax.plot(monthly["date"], monthly["Stress_H10_mean"], color=PALETTE["QVAR"], linewidth=1.8, marker="s", markersize=2.8, label="Stress_H10")
    ax.set_title("H5 / H10 压力事件率（月度）", loc="left")
    ax.set_ylabel("事件率")
    ax.set_xlabel("月份")
    format_percent_axis(ax)
    format_date_axis(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.17), ncol=2, frameon=True)
    standardize_legend(ax)
    despine_axes(ax)
    out = OUT_FIG_DIR / "fig_descriptive_04_event_rate_h5_h10_timeseries.png"
    existed = save_png(fig, out)
    register("D04", "H5 / H10 压力事件率时间图", out, "outputs/descriptive_diagnostics/tables/stress_rate_by_date.csv", "正文", "按月展示 Stress_H5 与 Stress_H10 的时变事件率。", existed)
    monthly.to_csv(OUT_TABLE_DIR / "descriptive_monthly_event_rate.csv", index=False, encoding="utf-8-sig")
    return rates


def plot_intraday_pattern() -> None:
    stats = pd.read_csv(OLD_DESC_TABLE_DIR / "lsi_intraday_stats.csv")
    stats = stats.dropna(subset=["slot", "LSI_5_mean"]).sort_values("slot")
    apply_finance_paper_style()
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(9.8, 8.2),
        sharex=True,
        constrained_layout=False,
        gridspec_kw={"height_ratios": [1.0, 1.35]},
    )

    def draw_panel(ax: plt.Axes) -> None:
        ax.fill_between(
            stats["slot"],
            stats["LSI_5_q25"],
            stats["LSI_5_q75"],
            color=PALETTE["MarketLSI"],
            alpha=0.18,
            label="25%-75% 分位带",
        )
        ax.plot(stats["slot"], stats["LSI_5_mean"], color=PALETTE["MarketLSI"], linewidth=1.8, label="均值 LSI_5")
        ax.plot(stats["slot"], stats["LSI_5_q50"], color="#333333", linewidth=1.1, linestyle="--", label="中位数")
        for x, label in [(6, "开盘"), (121, "午后开盘"), (235, "尾盘")]:
            ax.axvline(x, color="#777777", linestyle=":", linewidth=0.85)
            ax.text(x + 1, 0.98, label, transform=ax.get_xaxis_transform(), ha="left", va="top", fontsize=8, color="#555555")
        ax.set_xlim(1, 240)
        despine_axes(ax)

    draw_panel(axes[0])
    draw_panel(axes[1])
    body_low = min(stats["LSI_5_q25"].quantile(0.02), stats["LSI_5_q50"].quantile(0.02), stats["LSI_5_mean"].quantile(0.02))
    body_high = max(stats["LSI_5_q75"].quantile(0.98), stats["LSI_5_q50"].quantile(0.98), stats["LSI_5_mean"].quantile(0.95))
    pad = max((body_high - body_low) * 0.12, 0.25)
    axes[1].set_ylim(body_low - pad, body_high + pad)
    axes[0].set_title("LSI_5 日内模式：全样本范围", loc="left")
    axes[1].set_title("主体区间放大（尾盘与午后开盘极值见上图）", loc="left", fontsize=10)
    axes[0].set_ylabel("LSI_5")
    axes[1].set_ylabel("LSI_5")
    axes[1].set_xlabel("日内 slot")
    axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.28), ncol=3, frameon=True)
    standardize_legend(axes[0])
    fig.subplots_adjust(left=0.085, right=0.985, top=0.885, bottom=0.105, hspace=0.22)
    out = OUT_FIG_DIR / "fig_descriptive_05_intraday_pattern.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    existed = out.exists()
    fig.savefig(out, dpi=300, facecolor="white", bbox_inches=None)
    plt.close(fig)
    register(
        "D05",
        "LSI_5 日内模式",
        out,
        "outputs/descriptive_diagnostics/tables/lsi_intraday_stats.csv",
        "正文",
        "展示均值、中位数和 IQR 分位带；采用全范围与主体区间放大，避免尾盘极值压扁主体波动。",
        existed,
    )


def build_stage_intraday_from_labels(split: dict[str, pd.Timestamp]) -> pd.DataFrame:
    manifest = pd.read_csv(STAGE2_DIR / "lsi_labels_manifest.csv")
    manifest = manifest.loc[~manifest["is_index"].astype(bool)].copy()
    pieces = []
    for _, row in manifest.iterrows():
        path = PROJECT_ROOT / str(row["output_path"]).replace("\\", "/")
        df = pd.read_parquet(path, columns=["date", "slot", "LSI_5"])
        df = df.dropna(subset=["date", "slot", "LSI_5"])
        df["period"] = assign_period(df["date"], split)
        part = df.loc[df["period"].isin(["train", "validation", "test"])].groupby(["period", "slot"])["LSI_5"].agg(["sum", "count"]).reset_index()
        pieces.append(part)
    agg = pd.concat(pieces, ignore_index=True).groupby(["period", "slot"], as_index=False).sum()
    agg["mean_lsi_5"] = agg["sum"] / agg["count"]
    agg.to_csv(OUT_TABLE_DIR / "descriptive_intraday_lsi_by_period.csv", index=False, encoding="utf-8-sig")
    return agg


def plot_intraday_by_period(split: dict[str, pd.Timestamp]) -> None:
    agg_path = OUT_TABLE_DIR / "descriptive_intraday_lsi_by_period.csv"
    if agg_path.exists():
        agg = pd.read_csv(agg_path)
    else:
        agg = build_stage_intraday_from_labels(split)
    apply_finance_paper_style()
    fig, ax = plt.subplots(figsize=(9.6, 4.6), constrained_layout=True)
    for period, color in [("train", PALETTE["MarketLSI"]), ("validation", PALETTE["Validation"]), ("test", PALETTE["Test"])]:
        g = agg.loc[agg["period"].eq(period)].sort_values("slot")
        ax.plot(g["slot"], g["mean_lsi_5"], linewidth=1.8, color=color, label=PERIOD_LABELS[period])
    for x in [6, 121, 235]:
        ax.axvline(x, color="#999999", linestyle=":", linewidth=0.8)
    ax.set_xlim(1, 240)
    ax.set_title("分样本区间 LSI_5 日内模式", loc="left")
    ax.set_xlabel("日内 slot")
    ax.set_ylabel("平均 LSI_5")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=3, frameon=True)
    standardize_legend(ax)
    despine_axes(ax)
    out = OUT_FIG_DIR / "fig_descriptive_06_intraday_pattern_by_period.png"
    existed = save_png(fig, out)
    register("D06", "分样本区间 LSI_5 日内模式", out, "data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet", "正文/附录", "按 training / validation / test 对比日内模式稳定性。", existed)


def load_lsi_sample(max_per_code: int = 2500) -> pd.DataFrame:
    manifest = pd.read_csv(STAGE2_DIR / "lsi_labels_manifest.csv")
    manifest = manifest.loc[~manifest["is_index"].astype(bool)].copy()
    samples = []
    for _, row in manifest.iterrows():
        path = PROJECT_ROOT / str(row["output_path"]).replace("\\", "/")
        df = pd.read_parquet(path, columns=["LSI_5"])
        df = df.dropna(subset=["LSI_5"])
        if len(df) > max_per_code:
            df = df.sample(max_per_code, random_state=11)
        samples.append(df)
    return pd.concat(samples, ignore_index=True)


def plot_variable_distribution(daily: pd.DataFrame) -> None:
    lsi_sample = load_lsi_sample()
    variables = [
        ("MarketLSI", daily["MarketLSI_mean"].dropna(), "日均 MarketLSI"),
        ("LSI_5", lsi_sample["LSI_5"].dropna(), "个股分钟 LSI_5 抽样"),
        ("IndexRV", daily["IndexRV_mean"].dropna(), "日均 IndexRV"),
        ("MarketRelAmt", daily["MarketRelAmt_mean"].dropna(), "日均 MarketRelAmt"),
    ]
    apply_finance_paper_style()
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 6.8), constrained_layout=True)
    for ax, (name, series, title) in zip(axes.ravel(), variables):
        lo, hi = series.quantile([0.01, 0.99])
        clipped = series.clip(lo, hi)
        ax.hist(clipped, bins=42, color=PALETTE.get(name, PALETTE["MarketLSI"]), alpha=0.78, edgecolor="white", linewidth=0.4)
        ax.axvline(series.median(), color="#333333", linestyle="--", linewidth=0.9, label="中位数")
        ax.set_title(title, loc="left")
        ax.set_ylabel("频数")
        ax.set_xlabel(name)
        despine_axes(ax)
    out = OUT_FIG_DIR / "fig_descriptive_07_core_variable_distribution.png"
    existed = save_png(fig, out)
    register("D07", "核心变量分布", out, "market_context.parquet; lsi_labels_by_code/*.parquet sampled", "正文/附录", "对极端 1% 尾部做 winsorized 展示，仅用于避免主体分布被极值压扁。", existed)


def plot_event_rate_period_comparison(rates: pd.DataFrame, split: dict[str, pd.Timestamp]) -> pd.DataFrame:
    rates = rates.copy()
    rates["period"] = assign_period(rates["date"], split)
    comp = (
        rates.loc[rates["period"].isin(["train", "validation", "test"])]
        .groupby("period")[["Stress_H5_mean", "Stress_H10_mean"]]
        .mean()
        .reindex(["train", "validation", "test"])
        .reset_index()
    )
    comp.to_csv(OUT_TABLE_DIR / "descriptive_event_rate_by_period.csv", index=False, encoding="utf-8-sig")
    x = np.arange(len(comp))
    width = 0.36
    apply_finance_paper_style()
    fig, ax = plt.subplots(figsize=(8.2, 4.4), constrained_layout=True)
    b1 = ax.bar(x - width / 2, comp["Stress_H5_mean"], width, color=PALETTE["Stress"], label="Stress_H5")
    b2 = ax.bar(x + width / 2, comp["Stress_H10_mean"], width, color=PALETTE["QVAR"], label="Stress_H10")
    for bars in [b1, b2]:
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{bar.get_height():.1%}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([PERIOD_LABELS[p] for p in comp["period"]])
    ax.set_title("H5 / H10 事件率分样本区间比较", loc="left")
    ax.set_ylabel("事件率")
    format_percent_axis(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2, frameon=True)
    standardize_legend(ax)
    despine_axes(ax)
    out = OUT_FIG_DIR / "fig_descriptive_08_event_rate_period_comparison.png"
    existed = save_png(fig, out)
    register("D08", "H5 / H10 事件率比较", out, "outputs/descriptive_diagnostics/tables/stress_rate_by_date.csv", "正文", "比较 training / validation / test 中 Stress_H5 与 Stress_H10 的平均事件率。", existed)
    return comp


def plot_correlation_heatmap(daily: pd.DataFrame, rates: pd.DataFrame) -> None:
    rates = rates[["date", "Stress_H5_mean", "Stress_H10_mean"]].copy()
    rates["date"] = pd.to_datetime(rates["date"])
    corr_df = daily.merge(rates, on="date", how="left")
    use = corr_df[
        [
            "MarketLSI_mean",
            "MarketLSI_p95",
            "IndexRet_sum",
            "IndexRV_mean",
            "MarketRelAmt_mean",
            "Stress_H5_mean",
            "Stress_H10_mean",
        ]
    ].rename(
        columns={
            "MarketLSI_mean": "MarketLSI",
            "MarketLSI_p95": "MarketLSI_p95",
            "IndexRet_sum": "IndexRet",
            "IndexRV_mean": "IndexRV",
            "MarketRelAmt_mean": "MarketRelAmt",
            "Stress_H5_mean": "Stress_H5",
            "Stress_H10_mean": "Stress_H10",
        }
    )
    corr = use.corr()
    corr.to_csv(OUT_TABLE_DIR / "descriptive_core_variable_correlation.csv", encoding="utf-8-sig")

    apply_finance_paper_style()
    fig, ax = plt.subplots(figsize=(7.2, 6.0), constrained_layout=True)
    im = ax.imshow(corr.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1)
    fig.colorbar(im, ax=ax, pad=0.012, shrink=0.82, label="Pearson correlation")
    ax.set_xticks(np.arange(len(corr.columns)))
    ax.set_yticks(np.arange(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=35, ha="right")
    ax.set_yticklabels(corr.index)
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            val = corr.iloc[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8, color="white" if abs(val) > 0.55 else "#333333")
    ax.set_title("核心变量相关系数热力图（日度）", loc="left")
    for spine in ax.spines.values():
        spine.set_visible(False)
    out = OUT_FIG_DIR / "fig_descriptive_09_correlation_heatmap.png"
    existed = save_png(fig, out)
    register("D09", "核心变量相关系数热力图", out, "market_context.parquet; stress_rate_by_date.csv", "正文/附录", "只选日度核心变量，不使用 CrossStress 作为预测特征证据。", existed)


def audit_outputs() -> pd.DataFrame:
    from PIL import Image

    rows = []
    for rec in FIGURES:
        path = PROJECT_ROOT / rec.path
        with Image.open(path) as img:
            dpi = img.info.get("dpi", (None, None))
            extrema = img.convert("L").getextrema()
        rows.append(
            {
                **asdict(rec),
                "exists": path.exists(),
                "size_bytes": path.stat().st_size,
                "dpi_x": dpi[0],
                "dpi_y": dpi[1],
                "blank_suspect": extrema[0] == extrema[1],
            }
        )
    audit = pd.DataFrame(rows)
    audit.to_csv(AUDIT_DIR / "descriptive_figures_audit.csv", index=False, encoding="utf-8-sig")
    return audit


def write_audit_md(audit: pd.DataFrame) -> None:
    fig_one = audit.loc[audit["figure_id"].eq("D01")].iloc[0]
    lines = [
        "# 描述性统计图表体系审计",
        "",
        "## 图一识别",
        "",
        "- 图一对应：描述性事实章节 5.1 的“股票-月份有效分钟覆盖率热力图”。",
        "- 反向定位依据：`report/report_fragments/chapter_05_descriptive.md` 将数据覆盖热力图标为图 5.1；`docs/admin/figure_registry.md` 旧 F01 也是覆盖率热力图；早期 `outputs/descriptive_diagnostics/figures/fig_coverage_heatmap.png` 是同类图。",
        "- 最终输出路径：`outputs/figures/03_descriptive/fig_descriptive_01_sample_coverage_heatmap.png`。",
        "- 输入数据：`data_intermediate/stage1_model_ready/coverage_by_code_date.csv`，并用 `model_ready_manifest.csv` 标识指数/交易所分组。",
        "",
        "## 图一原始问题与修正",
        "",
        "- 原问题：描述性统计目录 `outputs/figures/03_descriptive/` 原本为空；旧图分散在 `outputs/descriptive_diagnostics/figures/` 与 `outputs/figures/01_data/`，不符合本轮统一描述性统计输出位置。",
        "- 原问题：旧覆盖图以逐日或过密证券轴展示时，读者难以在论文版面中辨认长期覆盖结构。",
        "- 修正：改为 code-month 聚合覆盖率热力图，按交易所/指数和平均覆盖率排序，保留 validation/test 分界标记，使用 300dpi PNG 直接输出到 `03_descriptive`。",
        "",
        "## 生成图表",
        "",
        "| 编号 | 图名 | 路径 | 去向 | 说明 |",
        "|---|---|---|---|---|",
    ]
    for _, row in audit.iterrows():
        lines.append(f"| {row['figure_id']} | {row['title']} | `{row['path']}` | {row['destination']} | {row['notes']} |")
    lines.extend(
        [
            "",
            "## 审计结论",
            "",
            f"- 本轮生成/重绘描述性统计 PNG：{len(audit)} 张。",
            "- 所有 PNG 均保存在 `outputs/figures/03_descriptive/`。",
            "- 覆盖说明：`03_descriptive` 原本没有同名正式描述性统计图；最终脚本二次运行会覆盖本轮生成的同名 PNG，以保证原位刷新，旧 `01_data/`、`02_lsi/` 与 `descriptive_diagnostics/` 图未删除、未覆盖。",
            "- 本轮未输出 PDF。",
            "- 本轮未修改 stage0-stage3 数据处理逻辑，未重跑 RGARCH-CARR-SK、QVAR、SMARTBoost。",
            "- 未使用 `CrossStress` 作为预测特征；描述性相关图也未把 `CrossStress` 纳入核心相关性证据。",
            "- D05 对尾盘与午后开盘极值采用“全样本范围 + 主体区间放大”的双面板表达，避免极值压扁主体日内波动。",
            "- 当前未发现因数据限制无法生成的建议图。",
        ]
    )
    (AUDIT_DIR / "descriptive_figures_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_figure_registry() -> None:
    registry = PROJECT_ROOT / "docs/admin" / "figure_registry.md"
    block = [
        "",
        "## 描述性统计图表体系补齐（2026-05-20）",
        "",
        "本节记录本轮统一输出到 `outputs/figures/03_descriptive/` 的描述性统计正文候选图。旧 `01_data/` 与 `02_lsi/` 中同类图保留为历史/模块图，不再作为描述性统计章节的首选路径。",
        "",
        "| 编号 | 标题 | PNG 路径 | 输入数据 | 去向 | 备注 |",
        "|---|---|---|---|---|---|",
    ]
    for rec in FIGURES:
        block.append(f"| {rec.figure_id} | {rec.title} | `{rec.path}` | `{rec.input_data}` | {rec.destination} | {rec.notes} |")
    text = registry.read_text(encoding="utf-8")
    marker = "## 描述性统计图表体系补齐（2026-05-20）"
    if marker in text:
        text = text.split(marker)[0].rstrip()
    registry.write_text(text.rstrip() + "\n" + "\n".join(block) + "\n", encoding="utf-8")


def main() -> int:
    OUT_FIG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    split = load_time_split()
    plot_coverage_heatmap(split)
    plot_sample_split_timeline(split)
    daily = load_market_daily(split)
    daily.to_csv(OUT_TABLE_DIR / "descriptive_daily_market_context.csv", index=False, encoding="utf-8-sig")
    plot_market_lsi_timeseries(daily, split)
    rates = plot_event_rate_timeseries(split)
    plot_intraday_pattern()
    plot_intraday_by_period(split)
    plot_variable_distribution(daily)
    plot_event_rate_period_comparison(rates, split)
    plot_correlation_heatmap(daily, rates)
    audit = audit_outputs()
    write_audit_md(audit)
    update_figure_registry()
    print(f"descriptive_figures_complete n={len(FIGURES)} output={OUT_FIG_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
