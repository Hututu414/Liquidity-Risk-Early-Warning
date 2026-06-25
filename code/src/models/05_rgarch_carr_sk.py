from __future__ import annotations

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
from scipy.optimize import minimize

from config import paths
from src.models.model_data import add_period, load_market_context, load_time_split, write_markdown
from src.visualization.plot_style import apply_cn_academic_style


EPS = 1.0e-10
LOG_2PI = math.log(2.0 * math.pi)
MEASURE_COLUMNS = ["RV_pressure", "RBV_pressure", "MedRV_pressure", "RMAD_pressure"]
MODEL_NAMES = {
    "RV_pressure": "RGARCH-CARR-SK-RV",
    "RBV_pressure": "RGARCH-CARR-SK-RBV",
    "MedRV_pressure": "RGARCH-CARR-SK-MedRV",
    "RMAD_pressure": "RGARCH-CARR-SK-RMAD",
}
PARAM_NAMES = [
    "rho",
    "omega",
    "beta",
    "gamma",
    "d1",
    "d2",
    "sigma_u",
    "omega_1",
    "beta_1",
    "v_1",
    "omega_2",
    "beta_2",
    "v_2",
]


@dataclass
class FitResult:
    measure: str
    model: str
    params: np.ndarray
    loglik: float
    aic: float
    bic: float
    nobs: int
    success: bool
    message: str
    path: pd.DataFrame


def _winsorize(values: np.ndarray, lower: float, upper: float) -> np.ndarray:
    return np.clip(values, lower, upper)


def construct_daily_pressure_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build daily MarketLSI pressure innovation and realized pressure measures."""

    split = load_time_split()
    market = add_period(load_market_context(), split)
    market = market.dropna(subset=["MarketLSI"]).sort_values("datetime").copy()
    train_values = market.loc[market["period"] == "train", "MarketLSI"].dropna()
    lo = float(train_values.quantile(0.005))
    hi = float(train_values.quantile(0.995))

    rows: list[dict[str, object]] = []
    for date_value, group in market.groupby("date", sort=True):
        g = group.sort_values("datetime")
        values = _winsorize(g["MarketLSI"].to_numpy(dtype="float64"), lo, hi)
        if len(values) < 60:
            continue
        increments = np.diff(values)
        increments = increments[np.isfinite(increments)]
        n = len(increments)
        if n < 20:
            continue

        rv = float(np.sum(increments**2))
        rbv = float((math.pi / 2.0) * (n / max(n - 1, 1)) * np.sum(np.abs(increments[1:]) * np.abs(increments[:-1])))
        if n >= 3:
            triples = np.vstack([np.abs(increments[:-2]), np.abs(increments[1:-1]), np.abs(increments[2:])])
            med = np.median(triples, axis=0)
            medrv = float((math.pi / (6.0 - 4.0 * math.sqrt(3.0) + math.pi)) * (n / max(n - 2, 1)) * np.sum(med**2))
        else:
            medrv = np.nan
        rmad = float(np.sum(np.abs(increments - np.mean(increments))))
        rvar = float(math.sqrt(n) * abs(np.quantile(increments, 0.05)))
        rows.append(
            {
                "date": date_value,
                "datetime": pd.Timestamp(date_value),
                "period": str(g["period"].iloc[0]),
                "n_intraday": int(len(values)),
                "pressure_open": float(values[0]),
                "pressure_close": float(values[-1]),
                "pressure_mean": float(np.mean(values)),
                "pressure_innovation_raw": float(values[-1] - values[0]),
                "RV_pressure": max(rv, EPS),
                "RBV_pressure": max(rbv, EPS),
                "MedRV_pressure": max(medrv, EPS) if np.isfinite(medrv) else np.nan,
                "RMAD_pressure": max(rmad, EPS),
                "RVaR_pressure_optional": max(rvar, EPS),
            }
        )

    daily = pd.DataFrame(rows).sort_values("datetime").reset_index(drop=True)
    train = daily.loc[daily["period"] == "train"].copy()
    r_scale = float(train["pressure_innovation_raw"].std(ddof=0))
    if not np.isfinite(r_scale) or r_scale <= EPS:
        r_scale = 1.0
    daily["pressure_innovation"] = daily["pressure_innovation_raw"] / r_scale

    scale_rows = [{"variable": "pressure_innovation_raw", "scale": r_scale, "source": "train_std"}]
    for measure in [*MEASURE_COLUMNS, "RVaR_pressure_optional"]:
        y = np.sqrt(pd.to_numeric(train[measure], errors="coerce").dropna().clip(lower=EPS))
        scale = float(y.median()) if len(y) else 1.0
        if not np.isfinite(scale) or scale <= EPS:
            scale = 1.0
        daily[f"sqrt_{measure}"] = np.sqrt(daily[measure].clip(lower=EPS)) / scale
        scale_rows.append({"variable": f"sqrt_{measure}", "scale": scale, "source": "train_median_sqrt_measure"})
    return daily, pd.DataFrame(scale_rows)


def leverage(z: float, d1: float, d2: float) -> float:
    return d1 * z + d2 * (z * z - 1.0)


def gce_logpdf(z: np.ndarray, s: np.ndarray, k: np.ndarray) -> np.ndarray:
    z_safe = np.clip(np.asarray(z, dtype="float64"), -12.0, 12.0)
    s_safe = np.clip(np.asarray(s, dtype="float64"), -2.0, 2.0)
    k_safe = np.clip(np.asarray(k, dtype="float64"), 3.0001, 20.0)
    h3 = z_safe**3 - 3.0 * z_safe
    h4 = z_safe**4 - 6.0 * z_safe**2 + 3.0
    psi = 1.0 + (s_safe / 6.0) * h3 + ((k_safe - 3.0) / 24.0) * h4
    gamma = 1.0 + (s_safe**2 / 6.0) + ((k_safe - 3.0) ** 2 / 24.0)
    log_phi = -0.5 * (LOG_2PI + z_safe**2)
    return log_phi + 2.0 * np.log(np.maximum(np.abs(psi), EPS)) - np.log(np.maximum(gamma, EPS))


def filter_paths(r: np.ndarray, y: np.ndarray, params: np.ndarray) -> dict[str, np.ndarray]:
    rho, omega, beta, gamma, d1, d2, sigma_u, omega_1, beta_1, v_1, omega_2, beta_2, v_2 = params
    n = len(r)
    lam = np.empty(n, dtype="float64")
    s = np.empty(n, dtype="float64")
    k = np.empty(n, dtype="float64")
    z_raw = np.empty(n, dtype="float64")
    z_update = np.empty(n, dtype="float64")
    u = np.empty(n, dtype="float64")

    initial_lambda = float(np.nanmedian(y))
    if not np.isfinite(initial_lambda) or initial_lambda <= EPS:
        initial_lambda = 1.0
    lam[0] = np.clip(initial_lambda, 0.02, 50.0)
    s[0] = np.clip(omega_1 / max(1.0 - beta_1, 0.05), -1.5, 1.5)
    k_uncond = (omega_2 + v_2 * math.sqrt(2.0 / math.pi)) / max(1.0 - beta_2, 0.05)
    k[0] = np.clip(k_uncond, 3.0001, 15.0)
    z_raw[0] = r[0] / max(rho * lam[0], EPS)
    z_update[0] = np.clip(z_raw[0], -8.0, 8.0)
    u[0] = max(y[0] / max(lam[0], EPS), EPS)

    for idx in range(1, n):
        log_lambda = (
            omega
            + beta * math.log(max(lam[idx - 1], EPS))
            + gamma * math.log(max(y[idx - 1], EPS))
            + leverage(z_update[idx - 1], d1, d2)
        )
        lam[idx] = math.exp(float(np.clip(log_lambda, -6.0, 4.0)))
        z_raw[idx] = r[idx] / max(rho * lam[idx], EPS)
        z_update[idx] = np.clip(z_raw[idx], -8.0, 8.0)
        s[idx] = np.clip(omega_1 + beta_1 * s[idx - 1] + v_1 * z_update[idx - 1], -1.5, 1.5)
        k[idx] = np.clip(omega_2 + beta_2 * k[idx - 1] + v_2 * abs(z_update[idx - 1]), 3.0001, 15.0)
        u[idx] = max(y[idx] / max(lam[idx], EPS), EPS)

    return {"lambda": lam, "s": s, "k": k, "z_raw": z_raw, "z_update": z_update, "u": u}


def loglikelihood(r: np.ndarray, y: np.ndarray, params: np.ndarray) -> float:
    rho, omega, beta, gamma, d1, d2, sigma_u, omega_1, beta_1, v_1, omega_2, beta_2, v_2 = params
    if rho <= 0 or sigma_u <= 0 or beta < 0 or beta_1 < 0 or beta_2 < 0:
        return -np.inf
    if beta + max(gamma, 0.0) >= 0.995:
        return -np.inf
    paths_ = filter_paths(r, y, params)
    lam = paths_["lambda"]
    z = paths_["z_raw"]
    u = paths_["u"]
    s = paths_["s"]
    k = paths_["k"]

    log_f1 = gce_logpdf(z, s, k) - np.log(np.maximum(rho * lam, EPS))
    log_u = np.log(np.maximum(u, EPS))
    log_f2 = -0.5 * LOG_2PI - np.log(sigma_u) - log_u - ((log_u + 0.5 * sigma_u**2) ** 2) / (2.0 * sigma_u**2)
    overflow_penalty = 0.05 * np.sum(np.maximum(np.abs(z) - 12.0, 0.0) ** 2)
    ll = float(np.sum(log_f1 + log_f2) - overflow_penalty)
    if not np.isfinite(ll):
        return -np.inf
    return ll


def fit_one_measure(data: pd.DataFrame, measure: str) -> FitResult:
    model_name = MODEL_NAMES[measure]
    fit_data = data.dropna(subset=["pressure_innovation", f"sqrt_{measure}", "period"]).copy()
    train = fit_data.loc[fit_data["period"] == "train"].copy()
    if len(train) < 200:
        raise RuntimeError(f"Insufficient training rows for {model_name}: {len(train)}")

    r_train = train["pressure_innovation"].to_numpy(dtype="float64")
    y_train = train[f"sqrt_{measure}"].to_numpy(dtype="float64")

    sigma_start = float(np.std(np.log(np.maximum(y_train / np.nanmedian(y_train), EPS))))
    sigma_start = float(np.clip(sigma_start, 0.08, 0.8))
    starts = [
        np.array([1.0, 0.02, 0.55, 0.35, 0.00, 0.01, sigma_start, -0.03, 0.20, 0.02, 2.40, 0.20, 0.05]),
        np.array([0.8, 0.00, 0.70, 0.20, -0.02, 0.02, sigma_start, 0.00, 0.05, 0.00, 3.00, 0.05, 0.00]),
        np.array([1.2, -0.02, 0.40, 0.45, 0.02, 0.00, sigma_start, -0.05, 0.40, 0.03, 2.10, 0.30, 0.08]),
    ]
    bounds = [
        (0.05, 5.00),  # rho
        (-2.00, 2.00),  # omega
        (0.00, 0.98),  # beta
        (-0.50, 0.98),  # gamma
        (-1.00, 1.00),  # d1
        (-1.00, 1.00),  # d2
        (0.03, 2.00),  # sigma_u
        (-0.80, 0.80),  # omega_1
        (0.00, 0.98),  # beta_1
        (-0.80, 0.80),  # v_1
        (0.05, 8.00),  # omega_2
        (0.00, 0.98),  # beta_2
        (0.00, 2.00),  # v_2
    ]

    def objective(params: np.ndarray) -> float:
        ll = loglikelihood(r_train, y_train, params)
        if not np.isfinite(ll):
            return 1.0e12
        penalty = 0.0
        if params[2] + max(params[3], 0.0) >= 0.995:
            penalty += 1.0e9 * (params[2] + max(params[3], 0.0) - 0.995) ** 2
        return -ll + penalty

    best = None
    for start in starts:
        result = minimize(objective, start, method="L-BFGS-B", bounds=bounds, options={"maxiter": 2500, "ftol": 1.0e-8})
        if best is None or result.fun < best.fun:
            best = result
    if best is None:
        raise RuntimeError(f"Optimization did not run for {model_name}")

    params = np.asarray(best.x, dtype="float64")
    train_ll = loglikelihood(r_train, y_train, params)
    k_params = len(params)
    nobs = len(train)
    aic = 2.0 * k_params - 2.0 * train_ll
    bic = math.log(nobs) * k_params - 2.0 * train_ll

    r_all = fit_data["pressure_innovation"].to_numpy(dtype="float64")
    y_all = fit_data[f"sqrt_{measure}"].to_numpy(dtype="float64")
    p = filter_paths(r_all, y_all, params)
    path = fit_data[["date", "datetime", "period", "pressure_innovation", f"sqrt_{measure}", measure]].copy()
    path = path.rename(columns={f"sqrt_{measure}": "realized_pressure_scale", measure: "realized_pressure_measure"})
    path["measure"] = measure
    path["model"] = model_name
    path["lambda_t"] = p["lambda"]
    path["s_t"] = p["s"]
    path["k_t"] = p["k"]
    path["z_t"] = p["z_raw"]
    path["u_t"] = p["u"]
    path["loglik_t"] = gce_logpdf(p["z_raw"], p["s"], p["k"]) - np.log(np.maximum(params[0] * p["lambda"], EPS))
    path["squared_error"] = (path["realized_pressure_scale"] - path["lambda_t"]) ** 2
    path["absolute_error"] = np.abs(path["realized_pressure_scale"] - path["lambda_t"])
    return FitResult(
        measure=measure,
        model=model_name,
        params=params,
        loglik=train_ll,
        aic=aic,
        bic=bic,
        nobs=nobs,
        success=bool(best.success),
        message=str(best.message),
        path=path,
    )


def forecast_loss(path: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for period, g in path.groupby("period", sort=False):
        if period == "train":
            continue
        actual = g["realized_pressure_scale"].to_numpy(dtype="float64")
        pred = g["lambda_t"].to_numpy(dtype="float64")
        mask = np.isfinite(actual) & np.isfinite(pred) & (actual > EPS) & (pred > EPS)
        actual = actual[mask]
        pred = pred[mask]
        if len(actual) == 0:
            continue
        rows.append(
            {
                "model": str(g["model"].iloc[0]),
                "measure": str(g["measure"].iloc[0]),
                "period": period,
                "nobs": int(len(actual)),
                "MSE": float(np.mean((actual - pred) ** 2)),
                "MAE": float(np.mean(np.abs(actual - pred))),
                "HMSE": float(np.mean((1.0 - pred / actual) ** 2)),
                "HMAE": float(np.mean(np.abs(1.0 - pred / actual))),
                "R2LOG": float(np.mean((np.log(pred) - np.log(actual)) ** 2)),
            }
        )
    return pd.DataFrame(rows)


def plot_risk_path(path_all: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for model, g in path_all.groupby("model"):
        ax.plot(pd.to_datetime(g["date"]), g["lambda_t"], linewidth=1.0, label=model.replace("RGARCH-CARR-SK-", ""))
    ax.set_title("RGARCH-CARR-SK 适配模型条件压力风险路径")
    ax.set_xlabel("日期")
    ax.set_ylabel("lambda_t")
    ax.legend(fontsize=8)
    fig.savefig(output)
    plt.close(fig)


def plot_dynamic_path(path_all: pd.DataFrame, output: Path, variable: str, title: str, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for model, g in path_all.groupby("model"):
        ax.plot(pd.to_datetime(g["date"]), g[variable], linewidth=1.0, label=model.replace("RGARCH-CARR-SK-", ""))
    ax.set_title(title)
    ax.set_xlabel("日期")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8)
    fig.savefig(output)
    plt.close(fig)


def plot_realized_measures(daily: pd.DataFrame, output: Path) -> None:
    plot = daily[["date", *MEASURE_COLUMNS]].copy()
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.2), sharex=True)
    axes = axes.ravel()
    for ax, col in zip(axes, MEASURE_COLUMNS):
        ax.plot(pd.to_datetime(plot["date"]), plot[col], linewidth=0.9)
        ax.set_title(col)
    fig.savefig(output)
    plt.close(fig)


def write_model_note(results: list[FitResult], losses: pd.DataFrame) -> None:
    converged = sum(1 for result in results if result.success)
    best = losses.sort_values(["period", "R2LOG"]).groupby("period").head(1) if not losses.empty else pd.DataFrame()
    best_lines = []
    for row in best.itertuples(index=False):
        best_lines.append(f"- {row.period}: {row.model}, R2LOG={row.R2LOG:.6g}")
    note = "\n".join(
        [
            "# RGARCH-CARR-SK Model Note",
            "",
            "## 模型命名",
            "",
            "本轮实现为 **基于 Liu、Zhou 和 Chen（2025）RGARCH-CARR-SK 框架的 MarketLSI 压力风险适配实现**。",
            "",
            "## 实现依据",
            "",
            "- 已按原文 Eq. (1)-Eq. (6) 实现 `r_t = rho lambda_t z_t`、`log lambda_t`、measurement equation、动态 skewness、动态 kurtosis 和 leverage function。",
            "- 已按原文 Eq. (7)-Eq. (10) 实现平方并标准化后的 GCE density。",
            "- 已按原文 Eq. (16)-Eq. (19) 构造 return-density component 与 lognormal measurement residual density 的联合 log likelihood，并用 scipy.optimize 做 MLE。",
            "- 已实现 RV、RBV、MedRV、RMAD 四类 generalized realized pressure measures。RVaR pressure 只作为 optional diagnostic measure 计算，未纳入主 MLE 表。",
            "- 已输出参数估计、log likelihood、AIC、BIC、条件压力风险路径、动态 skewness/kurtosis 路径和样本外预测损失。",
            "",
            "## 本项目适配",
            "",
            "- 原文研究高频波动预测与风险度量；本文迁移其结构刻画 A 股分钟数据构造的 MarketLSI 短时流动性压力风险。",
            "- `r_t` 不是资产收益率，而是日内 MarketLSI close-open pressure innovation。",
            "- `y_t` 是日内 MarketLSI increments 构造的 realized pressure measure 的平方根。",
            "- 本文不是复刻原文 GEM 指数波动率研究。",
            "",
            "## 数值说明",
            "",
            f"- 完成 MLE 的模型数量：{len(results)}。",
            f"- optimizer success 标记为 True 的模型数量：{converged}。",
            "- 为避免 GCE 密度下溢和极端 innovation 破坏递推，代码对 `psi`, `Gamma`, `lambda_t`, `s_t`, `k_t`, `z_t` 设置了稳定性保护。",
            "- 若个别参数贴近边界（例如 measurement residual volatility 或高阶矩冲击项），报告中应解释为压力序列适配下的数值估计特征，而不是原文资产波动模型的结构性结论。",
            "",
            "## 样本外损失较优模型",
            "",
            *(best_lines if best_lines else ["- 暂无"]),
            "",
            "## 输出位置",
            "",
            "- `outputs/tables/04_rgarch/rgarch_carr_sk_adapted_parameter_estimates.csv`",
            "- `outputs/tables/04_rgarch/rgarch_carr_sk_adapted_fit_criteria.csv`",
            "- `outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv`",
            "- `outputs/tables/04_rgarch/rgarch_carr_sk_adapted_realized_pressure_measures.csv`",
            "- `outputs/tables/04_rgarch/rgarch_carr_sk_adapted_oos_losses.csv`",
            "- `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_conditional_risk.png`",
            "- `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_skewness.png`",
            "- `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png`",
            "- `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png`",
            "",
        ]
    )
    write_markdown(paths.REVIEWS_DIR / "model_audit" / "rgarch_carr_sk_model_note.md", note)


def run() -> None:
    paths.ensure_runtime_dirs()
    apply_cn_academic_style(300)
    paths.RGARCH_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    paths.RGARCH_FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    (paths.REVIEWS_DIR / "model_audit").mkdir(parents=True, exist_ok=True)

    daily, scaling = construct_daily_pressure_data()
    daily.to_csv(paths.RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_realized_pressure_measures.csv", index=False, encoding="utf-8-sig")
    scaling.to_csv(paths.RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_scaling.csv", index=False, encoding="utf-8-sig")

    results: list[FitResult] = []
    failures: list[str] = []
    for measure in MEASURE_COLUMNS:
        try:
            result = fit_one_measure(daily, measure)
            results.append(result)
            print(f"{result.model} completed: loglik={result.loglik:.3f}, success={result.success}")
        except Exception as exc:
            failures.append(f"{measure}: {exc}")

    if len(results) < len(MEASURE_COLUMNS):
        blocker = "\n".join(
            [
                "# RGARCH-CARR-SK Full Implementation Blocker",
                "",
                "At least one required realized pressure measure failed during MLE.",
                "",
                *(f"- {item}" for item in failures),
                "",
            ]
        )
        write_markdown(paths.REVIEWS_DIR / "model_audit" / "RGARCH_CARR_SK_FULL_IMPLEMENTATION_BLOCKER.md", blocker)
        raise RuntimeError("; ".join(failures))

    param_rows = []
    fit_rows = []
    path_parts = []
    loss_parts = []
    for result in results:
        for name, value in zip(PARAM_NAMES, result.params):
            param_rows.append(
                {
                    "model": result.model,
                    "measure": result.measure,
                    "parameter": name,
                    "estimate": float(value),
                    "optimizer_success": result.success,
                    "optimizer_message": result.message,
                }
            )
        fit_rows.append(
            {
                "model": result.model,
                "measure": result.measure,
                "nobs_train": result.nobs,
                "log_likelihood": result.loglik,
                "AIC": result.aic,
                "BIC": result.bic,
                "optimizer_success": result.success,
                "optimizer_message": result.message,
            }
        )
        path_parts.append(result.path)
        loss_parts.append(forecast_loss(result.path))

    params = pd.DataFrame(param_rows)
    fit = pd.DataFrame(fit_rows)
    paths_all = pd.concat(path_parts, ignore_index=True)
    losses = pd.concat(loss_parts, ignore_index=True) if loss_parts else pd.DataFrame()
    params.to_csv(paths.RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_parameter_estimates.csv", index=False, encoding="utf-8-sig")
    fit.to_csv(paths.RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_fit_criteria.csv", index=False, encoding="utf-8-sig")
    paths_all.to_csv(paths.RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_conditional_paths.csv", index=False, encoding="utf-8-sig")
    losses.to_csv(paths.RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_oos_losses.csv", index=False, encoding="utf-8-sig")

    plot_risk_path(paths_all, paths.RGARCH_FIGURE_DIR / "fig_rgarch_carr_sk_adapted_conditional_risk.png")
    plot_dynamic_path(
        paths_all,
        paths.RGARCH_FIGURE_DIR / "fig_rgarch_carr_sk_adapted_dynamic_skewness.png",
        "s_t",
        "RGARCH-CARR-SK 适配模型动态偏度路径",
        "s_t",
    )
    plot_dynamic_path(
        paths_all,
        paths.RGARCH_FIGURE_DIR / "fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png",
        "k_t",
        "RGARCH-CARR-SK 适配模型动态峰度路径",
        "k_t",
    )
    plot_realized_measures(daily, paths.RGARCH_FIGURE_DIR / "fig_rgarch_carr_sk_adapted_realized_measures.png")
    write_model_note(results, losses)

    print("RGARCH-CARR-SK original-framework adaptation stage completed")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"RGARCH-CARR-SK original-framework adaptation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
