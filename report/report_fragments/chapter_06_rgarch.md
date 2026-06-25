# 第 6 章：RGARCH-CARR-SK 动态压力风险度量

## 6.1 模型定位

Liu、Zhou 和 Chen（2025）提出的 RGARCH-CARR-SK 模型原本用于高频波动预测和风险度量。其核心思想是在 realized measure 驱动的条件风险递推中，同时引入 Gram-Charlier expansion（GCE）分布、动态偏度和动态峰度，从而刻画风险分布的非对称性与厚尾变化。

本文不复刻原文的 GEM 指数波动率研究，而是将其模型结构迁移到 A 股分钟数据构造的 MarketLSI 压力风险序列。这里的 `r_t` 不是资产收益率，而是日内 MarketLSI 的压力创新；`y_t` 不是价格波动率，而是由日内 MarketLSI 增量构造的 realized pressure measure 的平方根。因此，本章结果应解释为短时流动性压力风险的动态刻画，而不是收益率预测或订单簿流动性度量。

## 6.2 原文结构与本文适配

原文 RGARCH-CARR-SK 的主结构包括：

```text
r_t = rho * lambda_t * z_t
log(lambda_t) = omega + beta log(lambda_{t-1}) + gamma log(y_{t-1}) + d(z_{t-1})
y_t = lambda_t * u_t
s_t = omega_1 + beta_1 s_{t-1} + v_1 z_{t-1}
k_t = omega_2 + beta_2 k_{t-1} + v_2 |z_{t-1}|
d(z_t) = d_1 z_t + d_2 (z_t^2 - 1)
```

本文实现保留上述递推结构，并将 `lambda_t` 解释为 MarketLSI 条件压力风险强度。`z_t` 服从由动态 `s_t` 和 `k_t` 控制的 GCE 分布；measurement equation 中的 `u_t` 按原文设为 lognormal residual。估计目标使用压力创新密度与 measurement residual 密度组成的联合 log likelihood。

## 6.3 广义 realized pressure measures

本文基于日内 MarketLSI 增量构造四类主 realized pressure measures：

- `RV_pressure`：日内 MarketLSI 增量平方和；
- `RBV_pressure`：相邻绝对增量乘积构造的 bipower variation；
- `MedRV_pressure`：三点局部中位绝对增量构造的 median realized variation；
- `RMAD_pressure`：MarketLSI 增量相对日内均值的绝对离差和。

`RVaR_pressure` 已作为 optional diagnostic measure 计算，但本轮未纳入主 MLE 表。原因是压力增量的分位方向与原文资产收益 VaR 口径并不完全一致，若进入正文需要单独定义压力下尾或上尾事件。

## 6.4 估计结果摘要

四个主模型均完成 MLE 并输出参数估计、log likelihood、AIC 和 BIC。训练期样本数为 435 个交易日。当前拟合准则显示，`RGARCH-CARR-SK-RV` 的 AIC/BIC 最低；样本外损失表显示，`RGARCH-CARR-SK-RMAD` 在验证期和测试期的相对误差类指标更小。这一结果提示：不同 realized pressure measures 在拟合和样本外压力风险刻画中可能承担不同角色。

主要输出位于：

- `outputs/tables/04_rgarch/rgarch_carr_sk_adapted_parameter_estimates.csv`
- `outputs/tables/04_rgarch/rgarch_carr_sk_adapted_fit_criteria.csv`
- `outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv`
- `outputs/tables/04_rgarch/rgarch_carr_sk_adapted_oos_losses.csv`
- `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_conditional_risk.png`
- `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_skewness.png`
- `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png`
- `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png`

## 6.5 解释边界

本章模型已实现原文主递推方程、GCE density、动态偏度/峰度方程、RV/RBV/MedRV/RMAD 广义 realized pressure measures 和 MLE。因此可称为“基于 Liu、Zhou 和 Chen（2025）RGARCH-CARR-SK 框架的 MarketLSI 压力风险适配实现”。

需要保留两点边界：第一，本文变量是 MarketLSI 压力序列，不是原文资产收益和价格波动率；第二，VaR loss functions 和 VaR backtesting 本轮未正式实现，可在后续作为压力分位风险扩展。

