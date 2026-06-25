from __future__ import annotations

import sys
import warnings
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from config import paths
from src.models.model_data import (
    MARKET_VARIABLES,
    add_period,
    load_market_context,
    load_time_split,
    standardize_with_train,
    train_stats,
    write_markdown,
)
from src.visualization.plot_style import apply_cn_academic_style


QUANTILES = [0.10, 0.50, 0.90, 0.95]
LAG = 1


def prepare_qvar_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    split = load_time_split()
    market = add_period(load_market_context(), split)
    market = market.dropna(subset=MARKET_VARIABLES).copy()
    stats = train_stats(market, MARKET_VARIABLES)
    z = standardize_with_train(market, MARKET_VARIABLES, stats, prefix="z_")
    target_cols = [f"z_{col}" for col in MARKET_VARIABLES]
    for col in target_cols:
        z[f"{col}_lag1"] = z[col].shift(LAG)
    z = z.dropna(subset=[*target_cols, *(f"{col}_lag1" for col in target_cols)]).copy()
    return z, stats


def pinball_loss(y: np.ndarray, yhat: np.ndarray, q: float) -> float:
    diff = y - yhat
    return float(np.nanmean(np.maximum(q * diff, (q - 1.0) * diff)))


def fit_qvar(df: pd.DataFrame, fit_periods: list[str], model_label: str) -> tuple[pd.DataFrame, dict[float, dict[str, pd.Series]]]:
    target_cols = [f"z_{col}" for col in MARKET_VARIABLES]
    lag_cols = [f"{col}_lag1" for col in target_cols]
    fit_df = df.loc[df["period"].isin(fit_periods)].copy()
    if len(fit_df) < 1000:
        raise RuntimeError(f"Insufficient rows for QVAR fit {model_label}: {len(fit_df)}")

    x = sm.add_constant(fit_df[lag_cols], has_constant="add")
    rows: list[dict[str, object]] = []
    models: dict[float, dict[str, pd.Series]] = {}
    for q in QUANTILES:
        models[q] = {}
        for target in target_cols:
            y = fit_df[target]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = sm.QuantReg(y, x).fit(q=q, max_iter=1000, p_tol=1.0e-6)
            models[q][target] = result.params
            for name, value in result.params.items():
                rows.append(
                    {
                        "model_period": model_label,
                        "quantile": q,
                        "target": target.replace("z_", ""),
                        "regressor": name.replace("z_", "").replace("_lag1", ""),
                        "estimate": float(value),
                        "pseudo_rsquared": float(getattr(result, "prsquared", np.nan)),
                        "nobs": int(result.nobs),
                    }
                )
    return pd.DataFrame(rows), models


def coefficient_matrix(model: dict[str, pd.Series]) -> tuple[np.ndarray, np.ndarray]:
    target_cols = [f"z_{col}" for col in MARKET_VARIABLES]
    lag_cols = [f"{col}_lag1" for col in target_cols]
    intercept = np.zeros(len(target_cols), dtype="float64")
    matrix = np.zeros((len(target_cols), len(target_cols)), dtype="float64")
    for i, target in enumerate(target_cols):
        params = model[target]
        intercept[i] = float(params.get("const", 0.0))
        for j, lag_col in enumerate(lag_cols):
            matrix[i, j] = float(params.get(lag_col, 0.0))
    return intercept, matrix


def simulate_path(model: dict[str, pd.Series], initial_state: np.ndarray, steps: int) -> pd.DataFrame:
    intercept, matrix = coefficient_matrix(model)
    state = np.asarray(initial_state, dtype="float64").copy()
    rows = []
    for step in range(steps + 1):
        rows.append({"horizon": step, **{var: state[i] for i, var in enumerate(MARKET_VARIABLES)}})
        state = intercept + matrix @ state
        state = np.clip(state, -8.0, 8.0)
    return pd.DataFrame(rows)


def build_response_tables(models: dict[float, dict[str, pd.Series]], steps: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline = np.zeros(len(MARKET_VARIABLES), dtype="float64")
    irf_rows: list[pd.DataFrame] = []
    scenario_rows: list[pd.DataFrame] = []
    scenarios = {
        "volatility_negative_return": {"IndexRV": 2.0, "IndexRet": -2.0},
        "liquidity_pressure": {"MarketLSI": 2.0, "CrossStress": 2.0, "MarketRelAmt": -2.0},
    }

    for q, model in models.items():
        base_path = simulate_path(model, baseline, steps)
        for shock_var in MARKET_VARIABLES:
            shocked = baseline.copy()
            shocked[MARKET_VARIABLES.index(shock_var)] += 1.0
            shock_path = simulate_path(model, shocked, steps)
            diff = shock_path[MARKET_VARIABLES] - base_path[MARKET_VARIABLES]
            part = diff.copy()
            part["horizon"] = shock_path["horizon"]
            part["quantile"] = q
            part["shock_variable"] = shock_var
            irf_rows.append(part)

        for scenario_name, shock_values in scenarios.items():
            initial = baseline.copy()
            for var, value in shock_values.items():
                initial[MARKET_VARIABLES.index(var)] = value
            path = simulate_path(model, initial, steps)
            path["quantile"] = q
            path["scenario"] = scenario_name
            scenario_rows.append(path)

    return pd.concat(irf_rows, ignore_index=True), pd.concat(scenario_rows, ignore_index=True)


def build_oos_metrics(df: pd.DataFrame, models_by_block: dict[str, dict[float, dict[str, pd.Series]]]) -> pd.DataFrame:
    target_cols = [f"z_{col}" for col in MARKET_VARIABLES]
    lag_cols = [f"{col}_lag1" for col in target_cols]
    rows: list[dict[str, object]] = []
    for eval_period, models in models_by_block.items():
        eval_df = df.loc[df["period"] == eval_period].copy()
        x_eval = sm.add_constant(eval_df[lag_cols], has_constant="add")
        for q, model in models.items():
            for target in target_cols:
                aligned = x_eval.reindex(columns=model[target].index, fill_value=1.0)
                pred = np.asarray(aligned @ model[target])
                actual = eval_df[target].to_numpy()
                rows.append(
                    {
                        "eval_period": eval_period,
                        "quantile": q,
                        "target": target.replace("z_", ""),
                        "pinball_loss": pinball_loss(actual, pred, q),
                        "nobs": int(len(eval_df)),
                    }
                )
    return pd.DataFrame(rows)


def _plot_tail_response(irf: pd.DataFrame, output: Path) -> None:
    plot = irf.loc[irf["shock_variable"].eq("MarketLSI")].copy()
    quantile_styles = {
        0.10: {"color": "#9E9E9E", "linestyle": ":", "linewidth": 1.8},
        0.50: {"color": "#4477AA", "linestyle": "-", "linewidth": 1.8},
        0.90: {"color": "#F28E2B", "linestyle": "--", "linewidth": 1.8},
        0.95: {"color": "#EE6677", "linestyle": "-.", "linewidth": 1.8},
    }
    fig, ax = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    for q, group in plot.groupby("quantile", sort=True):
        ax.plot(group["horizon"], group["MarketLSI"], label=f"q={q:.2f}", **quantile_styles.get(float(q), {}))
    ax.axhline(0, color="#8A8A8A", linestyle="--", linewidth=0.8)
    ax.set_title("QVAR 灏鹃儴鍒嗕綅鍝嶅簲锛歁arketLSI shock", loc="left")
    ax.set_xlabel("棰勬祴姝ラ暱")
    ax.set_ylabel("MarketLSI 鍝嶅簲")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=4, frameon=True)
    fig.savefig(output)
    plt.close(fig)


def _plot_stress_paths(scenarios: pd.DataFrame, output: Path) -> None:
    plot = scenarios.loc[scenarios["quantile"].isin([0.90, 0.95])].copy()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), sharey=False)
    for ax, variable in zip(axes, ["MarketLSI", "CrossStress"]):
        for (scenario, q), group in plot.groupby(["scenario", "quantile"]):
            ax.plot(group["horizon"], group[variable], linewidth=1.1, label=f"{scenario}, q={q:.2f}")
        ax.set_title(f"{variable} 鍘嬪姏娴嬭瘯璺緞")
        ax.set_xlabel("姝ラ暱")
        ax.set_ylabel("鏍囧噯鍖栨按骞?)
        ax.legend(fontsize=8)
    fig.savefig(output)
    plt.close(fig)


def run() -> None:
    paths.ensure_runtime_dirs()
    apply_cn_academic_style(300)
    paths.QVAR_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    paths.QVAR_FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    (paths.REVIEWS_DIR / "model_audit").mkdir(parents=True, exist_ok=True)

    df, stats = prepare_qvar_data()
    train_params, train_models = fit_qvar(df, ["train"], "train_only")
    expanded_params, expanded_models = fit_qvar(df, ["train", "validation"], "train_plus_validation")
    irf, scenarios = build_response_tables(train_models, steps=20)
    oos_metrics = build_oos_metrics(df, {"validation": train_models, "test": expanded_models})

    train_params.to_csv(paths.QVAR_TABLE_DIR / "qvar_quantile_coefficients_train.csv", index=False, encoding="utf-8-sig")
    expanded_params.to_csv(paths.QVAR_TABLE_DIR / "qvar_quantile_coefficients_train_plus_validation.csv", index=False, encoding="utf-8-sig")
    stats.to_csv(paths.QVAR_TABLE_DIR / "qvar_train_standardization_stats.csv", index=False, encoding="utf-8-sig")
    irf.to_csv(paths.QVAR_TABLE_DIR / "qvar_tail_quantile_response.csv", index=False, encoding="utf-8-sig")
    scenarios.to_csv(paths.QVAR_TABLE_DIR / "qvar_pressure_test_paths.csv", index=False, encoding="utf-8-sig")
    oos_metrics.to_csv(paths.QVAR_TABLE_DIR / "qvar_blocked_oos_pinball_loss.csv", index=False, encoding="utf-8-sig")

    _plot_tail_response(irf, paths.QVAR_FIGURE_DIR / "fig_qvar_tail_quantile_response.png")
    _plot_stress_paths(scenarios, paths.QVAR_FIGURE_DIR / "fig_qvar_pressure_test_paths.png")

    note = "\n".join(
        [
            "# QVAR Model Note",
            "",
            "## 瀹炵幇鍙ｅ緞",
            "",
            "- 浣跨敤浣庣淮甯傚満绯荤粺鍙橀噺锛歚MarketLSI`, `CrossStress`, `IndexRet`, `IndexRV`, `MarketRelAmt`銆?,
            "- 浣跨敤涓€闃舵粸鍚庡垎浣嶆暟绯荤粺锛屾瘡涓柟绋嬪垎鍒敤 QuantReg 浼拌銆?,
            "- 鍒嗕綅鐐癸細0.10銆?.50銆?.90銆?.95銆?,
            "- 鎵€鏈夋爣鍑嗗寲鍙傛暟鍙潵鑷缁冩湡銆?,
            "- 鏍锋湰澶?pinball loss 璇勪及锛氶獙璇佹湡鐢?train-only 绯绘暟锛屾祴璇曟湡鐢?train+validation 绯绘暟銆?,
            "",
            "## 杈撳嚭",
            "",
            "- `outputs/tables/05_qvar/qvar_quantile_coefficients_train.csv`",
            "- `outputs/tables/05_qvar/qvar_quantile_coefficients_train_plus_validation.csv`",
            "- `outputs/tables/05_qvar/qvar_tail_quantile_response.csv`",
            "- `outputs/tables/05_qvar/qvar_pressure_test_paths.csv`",
            "- `outputs/tables/05_qvar/qvar_blocked_oos_pinball_loss.csv`",
            "- `outputs/figures/05_qvar/fig_qvar_tail_quantile_response.png`",
            "- `outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png`",
            "",
            "## 杈圭晫",
            "",
            "- 杩欎笉鏄潎鍊?VAR锛屼篃涓嶆槸棰濆涓绘ā鍨嬨€?,
            "- 涓嶄娇鐢ㄩ殢鏈烘墦涔憋紝涓嶄娇鐢ㄥ叏鏍锋湰鏍囧噯鍖栥€?,
            "- QVAR 鎯呮櫙鍝嶅簲鏄潯浠跺垎浣嶈仈鍔ㄧ殑璇婃柇璇佹嵁锛屼笉浣滀弗鏍煎洜鏋滆В閲娿€?,
            "",
        ]
    )
    write_markdown(paths.REVIEWS_DIR / "model_audit" / "qvar_model_note.md", note)
    print("QVAR tail-transmission stage completed")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"qvar stage failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
