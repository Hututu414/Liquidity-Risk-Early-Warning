# Literature Visual Style Digest: Visualization Standards for HFT Liquidity Project

This document summarizes the visual and structural standards derived from key literature to guide the optimization of figures and tables in the high-frequency liquidity pressure forecasting project.

## 1. Reference Literature Overview

| Paper | Theme | Key Models | Visual Highlights |
|---|---|---|---|
| **Liu et al. (2025)** | High-frequency Volatility & Dynamic Higher Moments | RGARCH-CARR-SK | Time series risk paths, realized measure comparisons, MLE tables. |
| **Giordani (2025)** | SMARTboost for Tabular Financial Data | SMARTboost | **Partial effect plots**, marginal effect plots, sigmoid curves, simulation performance. |
| **Stauskas & Sucarrat (2025)** | Non-Stationary Periodicity in Zero-Process | Zero-Process LM Tests | **Intraday periodicity plots** (unconditional probabilities across slots). |
| **Zhang et al. (2024)** | ML & Intraday Commonality | NNs, XGBoost, HAR | **Diurnal pattern plots**, commonality time series, **interaction effects plots**, sensitivity analysis. |

## 2. Applicable Visual Style Standards

### 2.1. Intraday and Diurnal Patterns (Reference: Stauskas & Sucarrat 2025; Zhang et al. 2024)
- **Visual Style:** Clear X-axis representing intraday slots or time buckets (e.g., 09:30 - 15:00).
- **Application to LSI:** Use for "图 4 LSI 日内模式图". Instead of raw probability, plot the median LSI across stocks for each minute slot.
- **Labeling:** Chinese labels (e.g., "日内时间槽位", "流动性压力指数 LSI").

### 2.2. Risk Paths and Realized Measures (Reference: Liu et al. 2025)
- **Visual Style:** Stacked or overlaid time series showing conditional volatility/risk alongside realized measures.
- **Application to RGARCH:** Use for "图 6 RGARCH-CARR-SK 条件风险路径". Plot MarketLSI conditional variance ($\lambda_t$) and dynamic skewness/kurtosis paths.
- **Comparison:** Show how different realized pressure measures (RV, RBV, MedRV, RMAD) track the underlying pressure.

### 2.3. SMARTboost Interpretation (Reference: Giordani 2025; Zhang et al. 2024)
- **Partial Effect Plots:** Crucial for "图 10 SMARTboost partial effects 图". Use smooth curves with confidence bands (if available) or multi-line plots showing interaction effects.
- **Interaction Plots:** Plot the predicted probability as a function of one feature while conditioning on quantiles of another (e.g., individual LSI vs. MarketLSI).
- **Metrics:** Use PR curves and Calibration curves. PR curves are prioritized over ROC due to the imbalanced nature of "pressure events" (top 5% or 10%).

### 2.4. Table Organization (Reference: All)
- **Parameter Tables:** Standard regression format with standard errors in parentheses and significance stars (*, **, ***).
- **Comparison Tables:** Group models (e.g., Group 1: Benchmarks, Group 2: Proposed) with horizontal lines separating panels.
- **Metrics:** Report in-sample fit (AIC, BIC, Log-Likelihood) alongside out-of-sample losses (MSE, QLIKE, Pinball Loss).

## 3. Localization and Refinement Principles

1. **Academic Neutrality:** Avoid "BI Dashboard" styles. No overly bright colors or excessive decorations. Use professional colormaps (e.g., tab10, viridis, or grayscale).
2. **Variable Renaming:** 
   - `LSI` $\rightarrow$ 流动性压力指数 (LSI)
   - `MarketLSI` $\rightarrow$ 市场整体压力指数 (MarketLSI)
   - `Stress_H5` $\rightarrow$ 未来 5 分钟压力事件标签
   - `slot` $\rightarrow$ 日内槽位
   - `reg_stage` $\rightarrow$ 监管阶段 (Stage I, II, III)
3. **Consistency:** All plots must use the same font (SimSun or similar Chinese font for text, Times New Roman for numbers/English) and consistent line widths.
4. **Resolution:** 300 DPI for PNG; PDF for key vector graphics.

## 4. Specific Optimization List

- **Coverage Heatmap:** Clear colorbar, labeled axes (股票, 日期), distinct title.
- **QVAR Tail Response:** Plot impulse response functions with quantiles labeled (0.1, 0.5, 0.9, 0.95). Focus on the 0.95 response to MarketLSI shocks.
- **SmartBoost Top 5% Rate:** Bar chart or line chart comparing the predicted top 5% group's realized event rate across different regimes or periods.

---
*Note: This digest is a foundational mandate for thePost-Visualization Optimization phase.*
