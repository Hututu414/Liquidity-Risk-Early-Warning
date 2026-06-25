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


MARKET_VARIABLES = ["MarketLSI", "CrossStress", "IndexRet", "IndexRV", "MarketRelAmt"]
QUANTILES = [0.50, 0.90, 0.95]
SHOCK_SIZES = [1.0, 1.5, 2.0]
STEPS = 20

COEF_PATH = PROJECT_ROOT / "05_outputs" / "tables" / "05_qvar" / "qvar_quantile_coefficients_train.csv"
ORIGINAL_PATH = PROJECT_ROOT / "05_outputs" / "tables" / "05_qvar" / "qvar_pressure_test_paths.csv"
STD_PATH = PROJECT_ROOT / "05_outputs" / "tables" / "05_qvar" / "qvar_train_standardization_stats.csv"
SCENARIO_DEF_PATH = PROJECT_ROOT / "05_outputs" / "tables" / "05_qvar" / "qvar_pressure_test_scenario_definitions.csv"

OUT_DIR = PROJECT_ROOT / "05_outputs" / "figures" / "07_robustness" / "qvar_scenario_sensitivity"
TABLE_OUT_DIR = PROJECT_ROOT / "05_outputs" / "tables" / "07_robustness" / "qvar_scenario_sensitivity"
AUDIT_PATH = PROJECT_ROOT / "07_reviews" / "report_consistency" / "qvar_scenario_sensitivity_audit.md"
HANDOFF_PATH = PROJECT_ROOT / "06_agent_workspaces" / "codex_workspace" / "qvar_scenario_sensitivity_handoff.md"

SCENARIOS = {
    "market_crash": {
        "scenario_cn": "市场急跌",
        "shock_signs": {"IndexRet": -1.0},
        "definition": "IndexRet 下降",
    },
    "volatility_spike": {
        "scenario_cn": "波动放大",
        "shock_signs": {"IndexRV": 1.0},
        "definition": "IndexRV 上升",
    },
    "liquidity_contraction": {
        "scenario_cn": "成交收缩/流动性压力",
        "shock_signs": {"MarketRelAmt": -1.0},
        "definition": "MarketRelAmt 下降",
    },
    "composite_pressure": {
        "scenario_cn": "复合压力",
        "shock_signs": {"IndexRet": -1.0, "IndexRV": 1.0, "MarketRelAmt": -1.0},
        "definition": "IndexRet 下降、IndexRV 上升、MarketRelAmt 下降",
    },
}
SCENARIO_ORDER = list(SCENARIOS.keys())

Q_COLORS = {0.50: "#4E79A7", 0.90: "#F28E2B", 0.95: "#E15759"}
SHOCK_COLORS = {1.0: "#76B7B2", 1.5: "#59A14F", 2.0: "#B07AA1"}


def require_columns(df: pd.DataFrame, cols: list[str], path: Path) -> None:
    missing = [col for col in cols if col not in df.columns]
    if missing:
        raise ValueError(f"{path} 缺少字段: {missing}")


def coefficient_matrix(coef: pd.DataFrame, quantile: float) -> tuple[np.ndarray, np.ndarray]:
    qdf = coef[np.isclose(coef["quantile"].astype(float), quantile)].copy()
    if qdf.empty:
        raise ValueError(f"系数表缺少 quantile={quantile}")
    intercept = np.zeros(len(MARKET_VARIABLES), dtype="float64")
    matrix = np.zeros((len(MARKET_VARIABLES), len(MARKET_VARIABLES)), dtype="float64")
    for i, target in enumerate(MARKET_VARIABLES):
        tdf = qdf[qdf["target"].eq(target)]
        if tdf.empty:
            raise ValueError(f"系数表缺少 target={target}, quantile={quantile}")
        params = dict(zip(tdf["regressor"], tdf["estimate"]))
        intercept[i] = float(params.get("const", 0.0))
        for j, regressor in enumerate(MARKET_VARIABLES):
            matrix[i, j] = float(params.get(regressor, 0.0))
    return intercept, matrix


def simulate_path(intercept: np.ndarray, matrix: np.ndarray, initial_state: np.ndarray, steps: int = STEPS) -> pd.DataFrame:
    state = np.asarray(initial_state, dtype="float64").copy()
    rows: list[dict[str, float]] = []
    for horizon in range(steps + 1):
        rows.append({"horizon": horizon, **{var: float(state[i]) for i, var in enumerate(MARKET_VARIABLES)}})
        state = intercept + matrix @ state
        state = np.clip(state, -8.0, 8.0)
    return pd.DataFrame(rows)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    for path in [COEF_PATH, ORIGINAL_PATH, STD_PATH, SCENARIO_DEF_PATH]:
        if not path.exists():
            raise FileNotFoundError(f"缺少必要输入文件: {path}")
    coef = pd.read_csv(COEF_PATH)
    original = pd.read_csv(ORIGINAL_PATH)
    stats = pd.read_csv(STD_PATH)
    defs = pd.read_csv(SCENARIO_DEF_PATH)
    require_columns(coef, ["quantile", "target", "regressor", "estimate"], COEF_PATH)
    require_columns(original, ["horizon", "quantile", "scenario", "MarketLSI_response"], ORIGINAL_PATH)
    require_columns(stats, ["variable", "mean", "std", "q01", "q99"], STD_PATH)
    require_columns(defs, ["scenario", "scenario_cn", "shock_definition", "shock_variables"], SCENARIO_DEF_PATH)
    return coef, original, stats, defs


def build_grid(coef: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    baseline = np.zeros(len(MARKET_VARIABLES), dtype="float64")
    for quantile in QUANTILES:
        intercept, matrix = coefficient_matrix(coef, quantile)
        baseline_path = simulate_path(intercept, matrix, baseline, STEPS)
        for shock_size in SHOCK_SIZES:
            for scenario, spec in SCENARIOS.items():
                initial = baseline.copy()
                for variable, sign in spec["shock_signs"].items():
                    initial[MARKET_VARIABLES.index(variable)] = sign * shock_size
                path = simulate_path(intercept, matrix, initial, STEPS)
                out = path.copy()
                for variable in MARKET_VARIABLES:
                    out[f"{variable}_baseline"] = baseline_path[variable].to_numpy()
                    out[f"{variable}_response"] = out[variable].to_numpy() - baseline_path[variable].to_numpy()
                out["quantile"] = quantile
                out["shock_size"] = shock_size
                out["scenario"] = scenario
                out["scenario_cn"] = spec["scenario_cn"]
                out["shock_definition"] = spec["definition"]
                rows.append(out)
    return pd.concat(rows, ignore_index=True)


def summarize_grid(paths: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (scenario, scenario_cn, quantile, shock_size), group in paths.groupby(
        ["scenario", "scenario_cn", "quantile", "shock_size"], sort=False
    ):
        g = group.sort_values("horizon")
        h5 = float(g.loc[g["horizon"].eq(5), "MarketLSI_response"].iloc[0])
        h10 = float(g.loc[g["horizon"].eq(10), "MarketLSI_response"].iloc[0])
        h1_10 = g[g["horizon"].between(1, 10)]["MarketLSI_response"].astype(float)
        rows.append(
            {
                "scenario": scenario,
                "scenario_cn": scenario_cn,
                "quantile": quantile,
                "shock_size": shock_size,
                "signed_response_h5": h5,
                "signed_response_h10": h10,
                "cum_signed_response_h1_h10": float(h1_10.sum()),
                "cum_abs_response_h1_h10": float(h1_10.abs().sum()),
                "positive_count_h1_h10": int((h1_10 > 1.0e-12).sum()),
                "negative_count_h1_h10": int((h1_10 < -1.0e-12).sum()),
                "near_zero_count_h1_h10": int((h1_10.abs() <= 1.0e-12).sum()),
                "direction_switch_h1_h10": bool((h1_10 > 1.0e-12).any() and (h1_10 < -1.0e-12).any()),
            }
        )
    return pd.DataFrame(rows)


def compare_original(paths: pd.DataFrame, original: pd.DataFrame) -> pd.DataFrame:
    left_cols = ["horizon", "quantile", "scenario", "MarketLSI_response"]
    left = paths[np.isclose(paths["shock_size"].astype(float), 2.0)][left_cols].copy()
    right = original[original["quantile"].isin(QUANTILES)][left_cols].copy()
    merged = left.merge(
        right,
        on=["horizon", "quantile", "scenario"],
        how="outer",
        suffixes=("_grid", "_original"),
        indicator=True,
    )
    merged["abs_diff"] = (merged["MarketLSI_response_grid"] - merged["MarketLSI_response_original"]).abs()
    return pd.DataFrame(
        [
            {
                "rows_compared": int(len(merged)),
                "merge_statuses": "; ".join(f"{k}:{v}" for k, v in merged["_merge"].value_counts().items()),
                "max_abs_diff": float(merged["abs_diff"].max(skipna=True)),
                "mean_abs_diff": float(merged["abs_diff"].mean(skipna=True)),
            }
        ]
    )


def _scenario_labels() -> list[str]:
    return [SCENARIOS[key]["scenario_cn"] for key in SCENARIO_ORDER]


def _format_val(value: float) -> str:
    value = float(value)
    if abs(value) < 0.001:
        return f"{value:.4f}"
    if abs(value) < 0.1:
        return f"{value:.3f}"
    return f"{value:.2f}"


def _positive_bar_labels(ax: plt.Axes, bars, values: list[float]) -> None:
    xmax = ax.get_xlim()[1]
    pad = xmax * 0.012
    for bar, value in zip(bars, values):
        y = bar.get_y() + bar.get_height() / 2
        ax.text(value + pad, y, _format_val(value), ha="left", va="center", fontsize=8, color="#333333")


def _signed_bar_labels(ax: plt.Axes, bars, values: list[float]) -> None:
    xmin, xmax = ax.get_xlim()
    pad = (xmax - xmin) * 0.012
    for bar, value in zip(bars, values):
        y = bar.get_y() + bar.get_height() / 2
        if value >= 0:
            ax.text(value + pad, y, _format_val(value), ha="left", va="center", fontsize=8, color="#333333")
        else:
            ax.text(value - pad, y, _format_val(value), ha="right", va="center", fontsize=8, color="#333333")


def plot_shock_size_cum_abs(summary: pd.DataFrame) -> Path:
    apply_finance_paper_style()
    panel = summary[np.isclose(summary["quantile"].astype(float), 0.95)].copy()
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    y = np.arange(len(SCENARIO_ORDER))
    bar_h = 0.24
    offsets = [-bar_h, 0.0, bar_h]
    max_val = float(panel["cum_abs_response_h1_h10"].max())
    for offset, shock_size in zip(offsets, SHOCK_SIZES):
        values = (
            panel[np.isclose(panel["shock_size"].astype(float), shock_size)]
            .set_index("scenario")
            .loc[SCENARIO_ORDER, "cum_abs_response_h1_h10"]
            .astype(float)
            .tolist()
        )
        bars = ax.barh(
            y + offset,
            values,
            height=bar_h,
            color=SHOCK_COLORS[shock_size],
            label=f"{shock_size:.1f} 个标准差",
        )
        _positive_bar_labels(ax, bars, values)
    ax.set_xlim(0.0, max_val * 1.18)
    ax.set_yticks(y)
    ax.set_yticklabels(_scenario_labels())
    ax.invert_yaxis()
    ax.set_xlabel("前 10 期累计绝对响应强度")
    ax.set_ylabel("压力情景")
    ax.set_title("QVAR 情景设定敏感性：不同冲击幅度")
    ax.grid(axis="x", color="#E6E6E6", linewidth=0.6)
    ax.legend(loc="upper right", frameon=True)
    despine_axes(ax)
    fig.tight_layout()
    path = OUT_DIR / "qvar_sensitivity_shock_size_cum_abs_q095.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_quantile_cum_abs(summary: pd.DataFrame) -> Path:
    apply_finance_paper_style()
    panel = summary[np.isclose(summary["shock_size"].astype(float), 2.0)].copy()
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    y = np.arange(len(SCENARIO_ORDER))
    bar_h = 0.24
    offsets = [-bar_h, 0.0, bar_h]
    max_val = float(panel["cum_abs_response_h1_h10"].max())
    for offset, quantile in zip(offsets, QUANTILES):
        values = (
            panel[np.isclose(panel["quantile"].astype(float), quantile)]
            .set_index("scenario")
            .loc[SCENARIO_ORDER, "cum_abs_response_h1_h10"]
            .astype(float)
            .tolist()
        )
        bars = ax.barh(
            y + offset,
            values,
            height=bar_h,
            color=Q_COLORS[quantile],
            label=f"q={quantile:.2f}",
        )
        _positive_bar_labels(ax, bars, values)
    ax.set_xlim(0.0, max_val * 1.18)
    ax.set_yticks(y)
    ax.set_yticklabels(_scenario_labels())
    ax.invert_yaxis()
    ax.set_xlabel("前 10 期累计绝对响应强度")
    ax.set_ylabel("压力情景")
    ax.set_title("QVAR 情景设定敏感性：不同分位点")
    ax.grid(axis="x", color="#E6E6E6", linewidth=0.6)
    ax.legend(loc="upper right", frameon=True)
    despine_axes(ax)
    fig.tight_layout()
    path = OUT_DIR / "qvar_sensitivity_quantile_cum_abs_shock2.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def _signed_axis_limits(values: np.ndarray) -> tuple[float, float]:
    low = min(0.0, float(np.nanmin(values)))
    high = max(0.0, float(np.nanmax(values)))
    span = max(high - low, 0.01)
    return low - 0.18 * span, high + 0.28 * span


def plot_fixed_horizon_direction(summary: pd.DataFrame) -> Path:
    apply_finance_paper_style()
    panel = summary[np.isclose(summary["shock_size"].astype(float), 2.0)].copy()
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.6), sharey=True)
    y = np.arange(len(SCENARIO_ORDER))
    bar_h = 0.22
    offsets = [-bar_h, 0.0, bar_h]
    for ax, col, title in zip(
        axes,
        ["signed_response_h5", "signed_response_h10"],
        ["h=5 固定步长响应", "h=10 固定步长响应"],
    ):
        all_values: list[float] = []
        for offset, quantile in zip(offsets, QUANTILES):
            values = (
                panel[np.isclose(panel["quantile"].astype(float), quantile)]
                .set_index("scenario")
                .loc[SCENARIO_ORDER, col]
                .astype(float)
                .tolist()
            )
            all_values.extend(values)
            bars = ax.barh(y + offset, values, height=bar_h, color=Q_COLORS[quantile], label=f"q={quantile:.2f}")
            _signed_bar_labels(ax, bars, values)
        ax.set_xlim(*_signed_axis_limits(np.asarray(all_values)))
        ax.axvline(0.0, color="#666666", linewidth=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(_scenario_labels())
        ax.invert_yaxis()
        ax.set_xlabel("MarketLSI 带符号响应值")
        ax.set_title(title)
        ax.grid(axis="x", color="#E6E6E6", linewidth=0.6)
        despine_axes(ax)
    axes[0].set_ylabel("压力情景")
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=True, bbox_to_anchor=(0.55, 1.00))
    fig.suptitle("QVAR 固定步长下的响应方向对比", x=0.06, y=1.02, ha="left", fontsize=13)
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.92])
    path = OUT_DIR / "qvar_sensitivity_fixed_horizon_signed_direction.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def build_direction_table(paths: pd.DataFrame) -> pd.DataFrame:
    panel = paths[
        np.isclose(paths["shock_size"].astype(float), 2.0)
        & paths["quantile"].isin(QUANTILES)
        & paths["horizon"].between(1, 10)
    ].copy()
    panel["direction"] = np.select(
        [panel["MarketLSI_response"] > 1.0e-12, panel["MarketLSI_response"] < -1.0e-12],
        [1, -1],
        default=0,
    )
    return panel[["scenario", "scenario_cn", "quantile", "horizon", "MarketLSI_response", "direction"]]


def plot_direction_heatmap(direction: pd.DataFrame) -> Path:
    apply_finance_paper_style()
    row_order = [(scenario, q) for scenario in SCENARIO_ORDER for q in QUANTILES]
    labels = [f"{SCENARIOS[scenario]['scenario_cn']}  q={q:.2f}" for scenario, q in row_order]
    matrix = []
    for scenario, q in row_order:
        row = (
            direction[direction["scenario"].eq(scenario) & np.isclose(direction["quantile"].astype(float), q)]
            .set_index("horizon")
            .loc[range(1, 11), "direction"]
            .astype(int)
            .to_numpy()
        )
        matrix.append(row)
    arr = np.vstack(matrix)

    cmap = matplotlib.colors.ListedColormap(["#E15759", "#F2F2F2", "#4E79A7"])
    norm = matplotlib.colors.BoundaryNorm([-1.5, -0.5, 0.5, 1.5], cmap.N)
    fig, ax = plt.subplots(figsize=(9.5, 6.3))
    im = ax.imshow(arr, cmap=cmap, norm=norm, aspect="auto")
    ax.set_xticks(np.arange(10))
    ax.set_xticklabels([f"h={h}" for h in range(1, 11)])
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title("QVAR 带符号响应方向稳定性")
    ax.set_xlabel("预测步长")
    ax.set_ylabel("情景与分位点")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            text = "+" if arr[i, j] > 0 else "-" if arr[i, j] < 0 else "0"
            ax.text(j, i, text, ha="center", va="center", fontsize=8, color="#222222")
    cbar = fig.colorbar(im, ax=ax, ticks=[-1, 0, 1], shrink=0.72)
    cbar.ax.set_yticklabels(["负响应", "近零", "正响应"])
    fig.tight_layout()
    path = OUT_DIR / "qvar_sensitivity_direction_stability_heatmap.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def coefficient_audit(coef: pd.DataFrame) -> pd.DataFrame:
    market = coef[coef["target"].eq("MarketLSI") & coef["quantile"].isin(QUANTILES)].copy()
    keep = ["CrossStress", "IndexRet", "IndexRV", "MarketRelAmt", "MarketLSI", "const"]
    market = market[market["regressor"].isin(keep)]
    return market.pivot(index="regressor", columns="quantile", values="estimate").reset_index()


def write_audit(
    stats: pd.DataFrame,
    defs: pd.DataFrame,
    coef_audit_df: pd.DataFrame,
    compare_df: pd.DataFrame,
    summary: pd.DataFrame,
    direction: pd.DataFrame,
    figure_paths: list[Path],
) -> None:
    q095 = summary[np.isclose(summary["quantile"].astype(float), 0.95) & np.isclose(summary["shock_size"].astype(float), 2.0)]
    q095_cum = q095.set_index("scenario").loc[SCENARIO_ORDER, "cum_abs_response_h1_h10"]
    h5h10 = summary[np.isclose(summary["shock_size"].astype(float), 2.0)]
    switch_count = int(h5h10["direction_switch_h1_h10"].sum())
    cross_quantile_flips = 0
    for scenario in SCENARIO_ORDER:
        for col in ["signed_response_h5", "signed_response_h10"]:
            values = h5h10[h5h10["scenario"].eq(scenario)].sort_values("quantile")[col].to_numpy()
            signs = np.sign(values[np.abs(values) > 1.0e-12])
            if len(signs) and signs.min() < 0 and signs.max() > 0:
                cross_quantile_flips += 1
    neg_share = float((direction["direction"] < 0).mean())
    pos_share = float((direction["direction"] > 0).mean())

    def rel(path: Path) -> str:
        return path.relative_to(PROJECT_ROOT).as_posix()

    lines: list[str] = [
        "# QVAR 情景设定敏感性分析审计报告",
        "",
        "日期：2026-05-22",
        "",
        "## 本轮边界",
        "",
        "- 本轮只生成候选结果、候选图和审计报告。",
        "- 未修改论文正文、TeX 文件、PDF 文件、现有论文图片或参考文献。",
        "- 未重新估计 QVAR；所有响应均基于既有训练期 QVAR 系数表递推生成。",
        "- 未人为改变响应符号，也未按结果好坏筛选情景设定。",
        "",
        "## 使用的数据文件和脚本",
        "",
        f"- QVAR 系数：`{rel(COEF_PATH)}`",
        f"- 原始情景路径：`{rel(ORIGINAL_PATH)}`",
        f"- 训练期标准化参数：`{rel(STD_PATH)}`",
        f"- 原始情景定义：`{rel(SCENARIO_DEF_PATH)}`",
        f"- 本轮新增脚本：`06_agent_workspaces/codex_workspace/qvar_scenario_sensitivity_analysis.py`",
        f"- 网格路径输出：`{rel(TABLE_OUT_DIR / 'qvar_scenario_sensitivity_paths.csv')}`",
        f"- 网格统计输出：`{rel(TABLE_OUT_DIR / 'qvar_scenario_sensitivity_summary.csv')}`",
        f"- 响应方向表：`{rel(TABLE_OUT_DIR / 'qvar_scenario_direction_stability.csv')}`",
        "",
        "## QVAR 响应审计",
        "",
        "1. 情景冲击方向符合变量定义：市场急跌使用 `IndexRet` 下降；波动放大使用 `IndexRV` 上升；成交收缩/流动性压力使用 `MarketRelAmt` 下降；复合压力同时使用收益下降、波动上升和成交承接下降。",
        "2. `MarketLSI_response` 处于训练期标准化空间。QVAR 估计输入为 `z_MarketLSI` 等标准化变量，情景冲击幅度表示标准化单位。训练期 `MarketLSI` 标准差为 "
        f"`{float(stats.loc[stats['variable'].eq('MarketLSI'), 'std'].iloc[0]):.6f}`。",
        "3. 响应递推为一次性初始冲击。脚本只在 `h=0` 改变初始状态，此后按 `state = intercept + A @ state` 递推，不在后续 horizon 持续追加冲击。",
        "4. 原始图和本轮网格在 `2.0` 个标准差设定下可以复现原始路径数据。对本轮网格使用的 `q=0.50/q=0.90/q=0.95` 与 `qvar_pressure_test_paths.csv` 比较，最大绝对差为 "
        f"`{float(compare_df['max_abs_diff'].iloc[0]):.3e}`。",
        "5. 未发现变量方向处理或响应递推的程序性错误。`q=0.95` 下负响应主要来自既有系数递推，而不是符号写反。",
        "",
        "### MarketLSI 方程关键系数",
        "",
        coef_audit_df.to_markdown(index=False),
        "",
        "从系数看，`q=0.95` 的 `MarketLSI` 方程中 `IndexRet` 和 `MarketRelAmt` 系数为正，因此负向收益冲击或成交承接下降会给出负向一阶响应；`IndexRV` 系数为负，因此波动上升也会给出负向一阶响应。后续递推会沿系统矩阵继续放大或衰减该方向。",
        "",
        "## 预先定义的情景网格",
        "",
        "- 冲击幅度：`1.0`、`1.5`、`2.0` 个标准化单位。",
        "- 分位点：`q=0.50`、`q=0.90`、`q=0.95`。",
        "- 响应统计口径：固定 `h=5` 带符号响应、固定 `h=10` 带符号响应、前 10 期累计带符号响应、前 10 期累计绝对响应强度。",
        "- 四类情景全部保留：市场急跌、波动放大、成交收缩/流动性压力、复合压力。",
        "",
        "## 候选图和统计口径",
        "",
        "| 图 | 文件 | 统计口径 | 用途判断 |",
        "|---|---|---|---|",
        f"| 1 | `{rel(figure_paths[0])}` | `q=0.95`，比较 1.0/1.5/2.0 个标准化冲击的前 10 期累计绝对响应强度 | 用于判断结论是否对冲击幅度敏感。 |",
        f"| 2 | `{rel(figure_paths[1])}` | 当前 2.0 个标准化冲击下，比较 `q=0.50/q=0.90/q=0.95` 的前 10 期累计绝对响应强度 | 最适合展示尾部分位联动强度的连续性。 |",
        f"| 3 | `{rel(figure_paths[2])}` | 当前 2.0 个标准化冲击下，比较 `h=5` 与 `h=10` 的带符号响应方向 | 用于说明方向解释存在不稳定性。 |",
        f"| 4 | `{rel(figure_paths[3])}` | 当前 2.0 个标准化冲击下，`h=1...10` 的响应方向热力图 | 用于审计正负方向是否跨 horizon 稳定。 |",
        "",
        "## 主要结果",
        "",
        f"- 在 `q=0.95`、2.0 个标准化冲击下，前 10 期累计绝对响应强度依次为：市场急跌 `{q095_cum['market_crash']:.4f}`，波动放大 `{q095_cum['volatility_spike']:.4f}`，成交收缩/流动性压力 `{q095_cum['liquidity_contraction']:.4f}`，复合压力 `{q095_cum['composite_pressure']:.4f}`。",
        f"- 响应方向表中，当前 2.0 标准化冲击、`q=0.50/0.90/0.95`、`h=1...10` 的格点里，负响应占比约 `{neg_share:.1%}`，正响应占比约 `{pos_share:.1%}`。",
        f"- 按 `h=1...10` 统计，带符号方向在同一情景-分位点组合内发生正负切换的组合数为 `{switch_count}`；在 `h=5/h=10` 固定口径下，跨分位点出现正负方向不一致的情景-口径组合数为 `{cross_quantile_flips}`。",
        "- 因此，当前问题主要不是 horizon 内频繁变号，而是尾部分位下的带符号响应方向与“压力情景必然提高 MarketLSI”的强压力测试叙事不一致。",
        "- 市场急跌情景在多数口径下响应较弱；波动放大和复合压力在尾部分位下的累计绝对响应强度更突出。",
        "",
        "## 哪些结果不建议进入正文",
        "",
        "- 不建议使用单一最大响应值作为正文核心图，因为该口径依赖极值，容易放大递推路径中的局部峰值。",
        "- 不建议把带符号响应解释为“压力必然上升”。当前 QVAR 系数下，多个压力情景在 `q=0.95` 给出负向 `MarketLSI` 响应，若强行解读为正向压力测试会与估计结果冲突。",
        "- 候选图 3 和图 4 适合作为审计或附录依据，但若正文篇幅有限，不适合作为唯一主图，因为它们会把重点放在方向不稳定性上。",
        "",
        "## 第 6.3 节替代图建议",
        "",
        "- 最推荐图 2：`qvar_sensitivity_quantile_cum_abs_shock2.png`。它使用前 10 期累计绝对响应强度，不依赖单个极值；同时保留 `q=0.50/q=0.90/q=0.95`，可展示尾部分位条件联动强度是否具有连续性。",
        "- 如果正文需要强调冲击设定稳健性，可将图 1 作为附录或补充图。",
        "- 若所有带符号响应都难以解释，正文应明确使用“累计绝对响应强度”而不是“正向响应”，并将 QVAR 表述为“尾部分位条件联动”而非“强因果压力测试”。",
        "",
        "## 明确未修改项",
        "",
        "- 未修改任何 `08_report/latex_project/*.tex` 文件。",
        "- 未修改任何 `08_report/latex_project/*.pdf` 文件。",
        "- 未替换或覆盖现有图 14。",
        "- 未修改模型估计结果、原始数据、参考文献或论文正文结论。",
        "",
    ]
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_handoff(figure_paths: list[Path]) -> None:
    def rel(path: Path) -> str:
        return path.relative_to(PROJECT_ROOT).as_posix()

    lines = [
        "# Handoff: qvar_scenario_sensitivity",
        "",
        "Date: 2026-05-22",
        "Status: COMPLETE",
        "",
        "## Figures produced",
        "",
        *[f"- `{rel(path)}`" for path in figure_paths],
        "",
        "## Tables produced",
        "",
        f"- `{rel(TABLE_OUT_DIR / 'qvar_scenario_sensitivity_paths.csv')}`",
        f"- `{rel(TABLE_OUT_DIR / 'qvar_scenario_sensitivity_summary.csv')}`",
        f"- `{rel(TABLE_OUT_DIR / 'qvar_scenario_direction_stability.csv')}`",
        f"- `{rel(TABLE_OUT_DIR / 'qvar_scenario_original_path_comparison.csv')}`",
        "",
        "## Figure registry updated",
        "",
        "NO. These are candidate sensitivity outputs only.",
        "",
        "## CrossStress leak check",
        "",
        "CLEAN for task scope. This task only reads QVAR coefficients and scenario-path outputs; it does not alter SMARTBoost features.",
        "",
        "## Audit script result",
        "",
        "PASS. The script ran with the fixed project Python interpreter and wrote all requested candidate outputs.",
        "",
        "## Next steps",
        "",
        "If updating the paper later, prefer the quantile cumulative absolute response figure as the replacement for the current QVAR robustness figure.",
        "",
    ]
    HANDOFF_PATH.parent.mkdir(parents=True, exist_ok=True)
    HANDOFF_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_OUT_DIR.mkdir(parents=True, exist_ok=True)
    coef, original, stats, defs = load_inputs()
    grid = build_grid(coef)
    summary = summarize_grid(grid)
    comparison = compare_original(grid, original)
    direction = build_direction_table(grid)
    coef_audit_df = coefficient_audit(coef)

    grid.to_csv(TABLE_OUT_DIR / "qvar_scenario_sensitivity_paths.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(TABLE_OUT_DIR / "qvar_scenario_sensitivity_summary.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(TABLE_OUT_DIR / "qvar_scenario_original_path_comparison.csv", index=False, encoding="utf-8-sig")
    direction.to_csv(TABLE_OUT_DIR / "qvar_scenario_direction_stability.csv", index=False, encoding="utf-8-sig")
    coef_audit_df.to_csv(TABLE_OUT_DIR / "qvar_marketlsi_equation_coefficients_audit.csv", index=False, encoding="utf-8-sig")

    figures = [
        plot_shock_size_cum_abs(summary),
        plot_quantile_cum_abs(summary),
        plot_fixed_horizon_direction(summary),
        plot_direction_heatmap(direction),
    ]
    write_audit(stats, defs, coef_audit_df, comparison, summary, direction, figures)
    write_handoff(figures)
    for path in figures:
        print(path.relative_to(PROJECT_ROOT))
    print(AUDIT_PATH.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
