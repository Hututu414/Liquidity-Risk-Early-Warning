from __future__ import annotations

import importlib.util
import sys
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

from config import paths


MARKET_VARIABLES = ["MarketLSI", "CrossStress", "IndexRet", "IndexRV", "MarketRelAmt"]
QUANTILES = [0.10, 0.50, 0.90, 0.95]
PLOT_QUANTILES = [0.50, 0.95]
STEPS = 20

SCENARIOS = {
    "market_crash": {
        "scenario_cn": "市场急跌",
        "shock_values": {"IndexRet": -2.0},
        "shock_definition": "IndexRet=-2.0 standard deviations",
    },
    "volatility_spike": {
        "scenario_cn": "波动放大",
        "shock_values": {"IndexRV": 2.0},
        "shock_definition": "IndexRV=+2.0 standard deviations",
    },
    "liquidity_contraction": {
        "scenario_cn": "成交收缩 / 流动性压力",
        "shock_values": {"MarketRelAmt": -2.0},
        "shock_definition": "MarketRelAmt=-2.0 standard deviations",
    },
    "composite_pressure": {
        "scenario_cn": "复合压力",
        "shock_values": {"IndexRet": -2.0, "IndexRV": 2.0, "MarketRelAmt": -2.0},
        "shock_definition": "IndexRet=-2.0, IndexRV=+2.0, MarketRelAmt=-2.0 standard deviations",
    },
}


def load_style_module():
    style_path = PROJECT_ROOT / ".agents" / "skills" / "academic-finance-visualization-cn" / "scripts" / "finance_paper_style.py"
    spec = importlib.util.spec_from_file_location("finance_paper_style", style_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load finance paper style from {style_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STYLE = load_style_module()


def coefficient_matrix(coef: pd.DataFrame, quantile: float) -> tuple[np.ndarray, np.ndarray]:
    qdf = coef.loc[np.isclose(coef["quantile"].astype(float), quantile)].copy()
    if qdf.empty:
        raise RuntimeError(f"Missing QVAR coefficients for quantile={quantile}")

    intercept = np.zeros(len(MARKET_VARIABLES), dtype="float64")
    matrix = np.zeros((len(MARKET_VARIABLES), len(MARKET_VARIABLES)), dtype="float64")
    for i, target in enumerate(MARKET_VARIABLES):
        tdf = qdf.loc[qdf["target"].eq(target)]
        if tdf.empty:
            raise RuntimeError(f"Missing QVAR target equation: {target}, quantile={quantile}")
        params = dict(zip(tdf["regressor"], tdf["estimate"]))
        intercept[i] = float(params.get("const", 0.0))
        for j, regressor in enumerate(MARKET_VARIABLES):
            matrix[i, j] = float(params.get(regressor, 0.0))
    return intercept, matrix


def simulate_path(intercept: np.ndarray, matrix: np.ndarray, initial_state: np.ndarray, steps: int = STEPS) -> pd.DataFrame:
    state = np.asarray(initial_state, dtype="float64").copy()
    rows: list[dict[str, float]] = []
    for step in range(steps + 1):
        rows.append({"horizon": step, **{var: float(state[i]) for i, var in enumerate(MARKET_VARIABLES)}})
        state = intercept + matrix @ state
        state = np.clip(state, -8.0, 8.0)
    return pd.DataFrame(rows)


def build_four_scenario_paths() -> tuple[pd.DataFrame, pd.DataFrame]:
    coef_path = paths.QVAR_TABLE_DIR / "qvar_quantile_coefficients_train.csv"
    if not coef_path.exists():
        raise FileNotFoundError(f"Missing QVAR coefficient table: {coef_path}")
    coef = pd.read_csv(coef_path)
    if "model_period" in coef.columns:
        coef = coef.loc[coef["model_period"].eq("train_only")].copy()

    baseline = np.zeros(len(MARKET_VARIABLES), dtype="float64")
    rows: list[pd.DataFrame] = []
    scenario_def_rows: list[dict[str, object]] = []

    for scenario_name, spec in SCENARIOS.items():
        scenario_def_rows.append(
            {
                "scenario": scenario_name,
                "scenario_cn": spec["scenario_cn"],
                "shock_definition": spec["shock_definition"],
                "shock_variables": ",".join(spec["shock_values"].keys()),
            }
        )

    for quantile in QUANTILES:
        intercept, matrix = coefficient_matrix(coef, quantile)
        base_path = simulate_path(intercept, matrix, baseline, STEPS)
        for scenario_name, spec in SCENARIOS.items():
            initial = baseline.copy()
            for variable, value in spec["shock_values"].items():
                initial[MARKET_VARIABLES.index(variable)] = value
            path = simulate_path(intercept, matrix, initial, STEPS)
            out = path.copy()
            for variable in MARKET_VARIABLES:
                out[f"{variable}_baseline"] = base_path[variable].to_numpy()
                out[f"{variable}_response"] = out[variable].to_numpy() - base_path[variable].to_numpy()
            out["quantile"] = quantile
            out["scenario"] = scenario_name
            out["scenario_cn"] = spec["scenario_cn"]
            out["shock_definition"] = spec["shock_definition"]
            rows.append(out)

    paths_df = pd.concat(rows, ignore_index=True)
    definitions = pd.DataFrame(scenario_def_rows)
    return paths_df, definitions


def plot_market_lsi_response(paths_df: pd.DataFrame, output_path: Path) -> None:
    STYLE.apply_finance_paper_style()
    quantile_styles = {
        0.50: {"color": "#4477AA", "linestyle": "-", "linewidth": 1.8},
        0.95: {"color": "#EE6677", "linestyle": "-.", "linewidth": 1.8},
    }

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2), sharex=True, sharey=True, constrained_layout=False)
    axes = axes.reshape(-1)

    handles = []
    labels = []
    for ax, (scenario_name, spec) in zip(axes, SCENARIOS.items()):
        panel = paths_df.loc[
            paths_df["scenario"].eq(scenario_name) & paths_df["quantile"].isin(PLOT_QUANTILES)
        ].copy()
        for quantile, group in panel.groupby("quantile", sort=True):
            (line,) = ax.plot(
                group["horizon"],
                group["MarketLSI_response"],
                label=f"q={quantile:.2f}",
                **quantile_styles.get(float(quantile), {"linewidth": 1.8}),
            )
            if f"q={quantile:.2f}" not in labels:
                handles.append(line)
                labels.append(f"q={quantile:.2f}")
        ax.axhline(0.0, color="#8A8A8A", linestyle="--", linewidth=0.8)
        ax.set_title(spec["scenario_cn"], loc="left")
        ax.set_xlabel("预测步长")
        ax.set_ylabel("MarketLSI 响应")
        STYLE.despine_axes(ax)

    fig.suptitle("QVAR 情景冲击模拟：MarketLSI 响应", x=0.06, y=0.98, ha="left", fontsize=13)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.56, 0.985),
        ncol=len(labels),
        frameon=True,
        framealpha=0.92,
        edgecolor="#D0D0D0",
    )
    fig.text(
        0.06,
        0.02,
        "注：基于训练期 QVAR 系数和标准化冲击的情景模拟，展示尾部分位压力传导，不表示严格因果识别。",
        ha="left",
        va="bottom",
        fontsize=9,
        color="#555555",
    )
    fig.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.12, hspace=0.32, wspace=0.20)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def run() -> None:
    paths.ensure_runtime_dirs()
    paths.QVAR_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    paths.QVAR_FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    paths_df, definitions = build_four_scenario_paths()
    paths_df.to_csv(paths.QVAR_TABLE_DIR / "qvar_pressure_test_paths.csv", index=False, encoding="utf-8-sig")
    definitions.to_csv(paths.QVAR_TABLE_DIR / "qvar_pressure_test_scenario_definitions.csv", index=False, encoding="utf-8-sig")
    plot_market_lsi_response(paths_df, paths.QVAR_FIGURE_DIR / "fig_qvar_pressure_test_paths.png")
    print("QVAR four-scenario stress test paths and figure regenerated")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"qvar stress-test scenario repair failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
