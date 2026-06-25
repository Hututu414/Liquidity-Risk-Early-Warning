# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STYLE_DIR = PROJECT_ROOT / ".agents" / "skills" / "academic-finance-visualization-cn" / "scripts"
if str(STYLE_DIR) not in sys.path:
    sys.path.insert(0, str(STYLE_DIR))

from finance_paper_style import apply_finance_paper_style, despine_axes


QVAR_PATHS = PROJECT_ROOT / "05_outputs" / "tables" / "05_qvar" / "qvar_pressure_test_paths.csv"
SHOCK_SIZE = PROJECT_ROOT / "05_outputs" / "tables" / "07_robustness" / "qvar_shock_size_robustness.csv"
OUT_DIR = PROJECT_ROOT / "05_outputs" / "figures" / "07_robustness" / "candidate_qvar_robustness_figures"

SCENARIO_ORDER = [
    "market_crash",
    "volatility_spike",
    "liquidity_contraction",
    "composite_pressure",
]
SCENARIO_LABELS = {
    "market_crash": "市场急跌",
    "volatility_spike": "波动放大",
    "liquidity_contraction": "成交收缩/流动性压力",
    "composite_pressure": "复合压力",
}

QUANTILE_COLORS = {
    0.50: "#4E79A7",
    0.90: "#F28E2B",
    0.95: "#E15759",
}
SHOCK_COLORS = {
    1.5: "#76B7B2",
    2.0: "#59A14F",
    2.5: "#B07AA1",
}


def _require_columns(df: pd.DataFrame, columns: list[str], path: Path) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"{path} 缺少必要字段: {missing}")


def _scenario_labels() -> list[str]:
    return [SCENARIO_LABELS[key] for key in SCENARIO_ORDER]


def _ordered_panel(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["scenario"] = pd.Categorical(out["scenario"], categories=SCENARIO_ORDER, ordered=True)
    out = out.sort_values(["scenario"])
    out["scenario_label"] = out["scenario"].astype(str).map(SCENARIO_LABELS)
    return out


def _value_label(value: float) -> str:
    value = float(value)
    if abs(value) < 0.001:
        return f"{value:.4f}"
    if abs(value) < 0.1:
        return f"{value:.3f}"
    return f"{value:.2f}"


def _set_signed_xlim(ax: plt.Axes, values: np.ndarray) -> None:
    values = np.asarray(values, dtype=float)
    low = min(float(np.nanmin(values)), 0.0)
    high = max(float(np.nanmax(values)), 0.0)
    span = max(high - low, 0.01)
    ax.set_xlim(low - 0.18 * span, high + 0.28 * span)


def _label_signed_bars(ax: plt.Axes, bars, values: list[float]) -> None:
    xmin, xmax = ax.get_xlim()
    pad = (xmax - xmin) * 0.015
    for bar, value in zip(bars, values):
        y = bar.get_y() + bar.get_height() / 2
        if value >= 0:
            ax.text(value + pad, y, _value_label(value), ha="left", va="center", fontsize=8, color="#333333")
        else:
            ax.text(value - pad, y, _value_label(value), ha="right", va="center", fontsize=8, color="#333333")


def _label_positive_bars(ax: plt.Axes, bars, values: list[float]) -> None:
    xmax = ax.get_xlim()[1]
    pad = xmax * 0.012
    for bar, value in zip(bars, values):
        y = bar.get_y() + bar.get_height() / 2
        ax.text(value + pad, y, _value_label(value), ha="left", va="center", fontsize=8, color="#333333")


def load_qvar_paths() -> pd.DataFrame:
    if not QVAR_PATHS.exists():
        raise FileNotFoundError(f"未找到 QVAR 情景路径数据: {QVAR_PATHS}")
    df = pd.read_csv(QVAR_PATHS)
    _require_columns(df, ["horizon", "quantile", "scenario", "MarketLSI_response"], QVAR_PATHS)
    return df


def load_shock_size() -> pd.DataFrame:
    if not SHOCK_SIZE.exists():
        raise FileNotFoundError(f"未找到 QVAR 冲击幅度稳健性数据: {SHOCK_SIZE}")
    df = pd.read_csv(SHOCK_SIZE)
    _require_columns(df, ["quantile", "shock_size", "scenario", "horizon", "MarketLSI_response"], SHOCK_SIZE)
    return df


def plot_candidate_a(paths_df: pd.DataFrame) -> Path:
    apply_finance_paper_style()
    horizons = [1, 5, 10]
    quantiles = [0.50, 0.95]
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 5.1), sharey=True)
    y = np.arange(len(SCENARIO_ORDER))
    bar_h = 0.34

    for ax, horizon in zip(axes, horizons):
        panel = paths_df[
            paths_df["horizon"].eq(horizon)
            & paths_df["quantile"].isin(quantiles)
            & paths_df["scenario"].isin(SCENARIO_ORDER)
        ].copy()
        panel = _ordered_panel(panel)
        all_values: list[float] = []
        for idx, q in enumerate(quantiles):
            values = (
                panel[panel["quantile"].eq(q)]
                .set_index("scenario")
                .loc[SCENARIO_ORDER, "MarketLSI_response"]
                .astype(float)
                .tolist()
            )
            all_values.extend(values)
            bars = ax.barh(
                y + (idx - 0.5) * bar_h,
                values,
                height=bar_h,
                color=QUANTILE_COLORS[q],
                label=f"q={q:.2f}",
            )
            _label_signed_bars(ax, bars, values)
        _set_signed_xlim(ax, np.asarray(all_values))
        ax.axvline(0.0, color="#666666", linewidth=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(_scenario_labels())
        ax.invert_yaxis()
        ax.set_title(f"h={horizon}")
        ax.set_xlabel("MarketLSI 响应值")
        ax.grid(axis="x", color="#E6E6E6", linewidth=0.6)
        despine_axes(ax)

    axes[0].set_ylabel("压力情景")
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=True, bbox_to_anchor=(0.52, 0.995))
    fig.suptitle("固定预测步长下的 QVAR 情景响应比较", x=0.07, y=1.02, ha="left", fontsize=13)
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.92])
    path = OUT_DIR / "candidate_a_qvar_fixed_horizon_response.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_candidate_b(paths_df: pd.DataFrame) -> Path:
    apply_finance_paper_style()
    quantiles = [0.50, 0.95]
    panel = paths_df[
        paths_df["horizon"].between(1, 10)
        & paths_df["quantile"].isin(quantiles)
        & paths_df["scenario"].isin(SCENARIO_ORDER)
    ].copy()
    panel["abs_response"] = panel["MarketLSI_response"].astype(float).abs()
    agg = (
        panel.groupby(["scenario", "quantile"], as_index=False)["abs_response"]
        .sum()
        .pipe(_ordered_panel)
    )

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    y = np.arange(len(SCENARIO_ORDER))
    bar_h = 0.34
    max_value = float(agg["abs_response"].max())

    for idx, q in enumerate(quantiles):
        values = (
            agg[agg["quantile"].eq(q)]
            .set_index("scenario")
            .loc[SCENARIO_ORDER, "abs_response"]
            .astype(float)
            .tolist()
        )
        bars = ax.barh(
            y + (idx - 0.5) * bar_h,
            values,
            height=bar_h,
            color=QUANTILE_COLORS[q],
            label=f"q={q:.2f}",
        )
        _label_positive_bars(ax, bars, values)

    ax.set_xlim(0.0, max_value * 1.18)
    ax.set_yticks(y)
    ax.set_yticklabels(_scenario_labels())
    ax.invert_yaxis()
    ax.set_xlabel("前 10 期累计绝对响应强度")
    ax.set_ylabel("压力情景")
    ax.set_title("QVAR 情景响应累计强度比较")
    ax.grid(axis="x", color="#E6E6E6", linewidth=0.6)
    ax.legend(loc="upper right", frameon=True)
    despine_axes(ax)
    fig.tight_layout()
    path = OUT_DIR / "candidate_b_qvar_cumulative_abs_response_h1_h10.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_candidate_c(paths_df: pd.DataFrame) -> Path:
    apply_finance_paper_style()
    quantiles = [0.50, 0.90, 0.95]
    horizon = 5
    panel = paths_df[
        paths_df["horizon"].eq(horizon)
        & paths_df["quantile"].isin(quantiles)
        & paths_df["scenario"].isin(SCENARIO_ORDER)
    ].copy()
    panel = _ordered_panel(panel)

    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    y = np.arange(len(SCENARIO_ORDER))
    bar_h = 0.25
    all_values: list[float] = []
    offsets = [-bar_h, 0.0, bar_h]

    for offset, q in zip(offsets, quantiles):
        values = (
            panel[panel["quantile"].eq(q)]
            .set_index("scenario")
            .loc[SCENARIO_ORDER, "MarketLSI_response"]
            .astype(float)
            .tolist()
        )
        all_values.extend(values)
        bars = ax.barh(y + offset, values, height=bar_h, color=QUANTILE_COLORS[q], label=f"q={q:.2f}")
        _label_signed_bars(ax, bars, values)

    _set_signed_xlim(ax, np.asarray(all_values))
    ax.axvline(0.0, color="#666666", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(_scenario_labels())
    ax.invert_yaxis()
    ax.set_xlabel("MarketLSI 响应值")
    ax.set_ylabel("压力情景")
    ax.set_title("QVAR 分位点扩展稳健性：预测步长 h=5")
    ax.grid(axis="x", color="#E6E6E6", linewidth=0.6)
    ax.legend(loc="lower right", frameon=True)
    despine_axes(ax)
    fig.tight_layout()
    path = OUT_DIR / "candidate_c_qvar_quantile_extension_h5_response.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_candidate_d(shock_df: pd.DataFrame) -> Path:
    apply_finance_paper_style()
    shock_sizes = [1.5, 2.0, 2.5]
    panel = shock_df[
        np.isclose(shock_df["quantile"].astype(float), 0.95)
        & shock_df["horizon"].eq(10)
        & shock_df["scenario"].isin(SCENARIO_ORDER)
        & shock_df["shock_size"].isin(shock_sizes)
    ].copy()
    panel = _ordered_panel(panel)

    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    y = np.arange(len(SCENARIO_ORDER))
    bar_h = 0.25
    all_values: list[float] = []
    offsets = [-bar_h, 0.0, bar_h]

    for offset, shock_size in zip(offsets, shock_sizes):
        values = (
            panel[np.isclose(panel["shock_size"].astype(float), shock_size)]
            .set_index("scenario")
            .loc[SCENARIO_ORDER, "MarketLSI_response"]
            .astype(float)
            .tolist()
        )
        all_values.extend(values)
        bars = ax.barh(
            y + offset,
            values,
            height=bar_h,
            color=SHOCK_COLORS[shock_size],
            label=f"{shock_size:.1f} 个标准差",
        )
        _label_signed_bars(ax, bars, values)

    _set_signed_xlim(ax, np.asarray(all_values))
    ax.axvline(0.0, color="#666666", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(_scenario_labels())
    ax.invert_yaxis()
    ax.set_xlabel("MarketLSI 响应值")
    ax.set_ylabel("压力情景")
    ax.set_title("QVAR 冲击幅度稳健性：q=0.95，预测步长 h=10")
    ax.grid(axis="x", color="#E6E6E6", linewidth=0.6)
    ax.legend(loc="lower right", frameon=True)
    despine_axes(ax)
    fig.tight_layout()
    path = OUT_DIR / "candidate_d_qvar_shock_size_h10_q095_response.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths_df = load_qvar_paths()
    shock_df = load_shock_size()

    outputs = [
        plot_candidate_a(paths_df),
        plot_candidate_b(paths_df),
        plot_candidate_c(paths_df),
        plot_candidate_d(shock_df),
    ]

    for path in outputs:
        print(path.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
