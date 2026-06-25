# Codex Visual Rebuild Plan

## 1. 当前图表问题诊断

- 旧 `figure_registry.md` 仍包含 `CrossStress 时间序列`，但 `CrossStress` 已确认由未来 `Stress_H5` / `Stress_H10` 横截面聚合得到，不能作为 SMARTBoost 预测特征或正文预警证据图。
- `05_outputs/figures/04_rgarch/` 中已有 RGARCH 图，但存在分钟或日路径视觉密度过高、PDF 不完整、正文图命名不统一的问题；条件风险路径需要转为日度/周度平滑后的 paper-ready 图。
- `05_outputs/figures/06_smartboost/` 中已有 SMARTBoost 图，多数只有 PNG，没有统一 PDF；partial effects 图过挤，需压缩到 3-4 个核心变量。
- 当前 registry 只登记旧目录，没有 paper-ready 输出层，也未标明是否使用剔除 `CrossStress` 后的 SMARTBoost 结果。
- QVAR 图已存在，但需要统一线型、标题、分面和“非因果识别”图注口径。

## 2. 废弃或降级的旧图

- 废弃正文图：`图 5 CrossStress 时间序列`。原因：`CrossStress` 是未来压力标签聚合比例，只能作为描述性事实或审计说明，不能作为预测特征图。
- 废弃正文候选：旧 SMARTBoost 图中任何无法确认来自剔除 `CrossStress` 后结果的版本。
- 降级为原始模型输出备查：`05_outputs/figures/04_rgarch/*.png`、`05_outputs/figures/05_qvar/*.png`、`05_outputs/figures/06_smartboost/*.png`。本轮不覆盖它们，只另存到 `99_paper_ready/`。

## 3. 本轮重画清单

所有 paper-ready 图输出到：

`05_outputs/figures/99_paper_ready/`

| 编号 | 图名 | 输入数据 | 输出文件前缀 | 去向 |
|---|---|---|---|---|
| F01 | 股票-日期覆盖率热力图 | `03_data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet` | `fig_01_coverage_heatmap` | 正文 |
| F02 | LSI 日内模式图 | `03_data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet` | `fig_02_lsi_intraday_pattern` | 正文 |
| F03 | MarketLSI 时间序列图 | `03_data_intermediate/stage2_lsi_labels/market_context.parquet` | `fig_03_market_lsi_time_series` | 正文 |
| F04 | RGARCH-CARR-SK 条件压力风险路径 | `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv` | `fig_04_rgarch_conditional_pressure_risk` | 正文 |
| F05 | 动态偏度和动态峰度图 | 同上 | `fig_05_rgarch_dynamic_skew_kurtosis` | 正文 |
| F06 | realized pressure measures 对比图 | `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_realized_pressure_measures.csv` | `fig_06_rgarch_realized_pressure_measures` | 正文/附录 |
| F07 | QVAR 尾部分位响应图 | `05_outputs/tables/05_qvar/qvar_tail_quantile_response.csv` | `fig_07_qvar_tail_quantile_response` | 正文 |
| F08 | QVAR 压力测试情景图 | `05_outputs/tables/05_qvar/qvar_pressure_test_paths.csv` | `fig_08_qvar_pressure_test_scenarios` | 正文 |
| F09 | SMARTBoost PR 曲线 | `05_outputs/tables/06_smartboost/predictions_by_code/*.parquet` + metrics | `fig_09_smartboost_pr_curve` | 正文 |
| F10 | SMARTBoost ROC 曲线 | 同上 | `fig_10_smartboost_roc_curve` | 附录 |
| F11 | SMARTBoost 校准曲线 | `05_outputs/tables/06_smartboost/smartboost_calibration_table.csv` | `fig_11_smartboost_calibration_curve` | 正文/附录 |
| F12 | SMARTBoost Top 5% 高风险组 | `05_outputs/tables/06_smartboost/smartboost_event_rate_and_lift.csv` | `fig_12_smartboost_top5_event_rate` | 正文 |
| F13 | SMARTBoost Partial Effects | `05_outputs/tables/06_smartboost/smartboost_partial_effects.csv` | `fig_13_smartboost_partial_effects` | 正文/附录 |

## 4. 正文图与附录图建议

正文建议：

- F01 覆盖率热力图：数据质量与样本完整性。
- F02 LSI 日内模式：解释短时压力指标的日内规律。
- F03 MarketLSI 时间序列：展示市场压力状态演化和阶段差异。
- F04 RGARCH-CARR-SK 条件压力风险路径：展示 MarketLSI 条件压力风险。
- F05 动态偏度和动态峰度：展示模型高阶矩路径；如峰度稳定，在图注说明。
- F07 QVAR 尾部分位响应：展示尾部分位传导。
- F08 QVAR 压力测试情景：展示情景路径。
- F09 SMARTBoost PR 曲线：作为机器学习预警主证据。
- F12 SMARTBoost Top 5% 高风险组：展示高风险排序的实际事件率和 lift。

附录建议：

- F06 realized pressure measures 对比：若正文篇幅有限，放附录。
- F10 SMARTBoost ROC 曲线：辅助图，不替代 PR 曲线。
- F11 SMARTBoost Calibration：若正文图位紧张，放附录。
- F13 Partial Effects：若解释篇幅不足，放附录；正文可引用关键变量结论。

补充检查：当前 `qvar_pressure_test_paths.csv` 实际只提供 `volatility_negative_return` 和 `liquidity_pressure` 两类情景，未提供“市场急跌、波动放大、成交收缩、复合压力”四类完整拆分。本轮不得伪造缺失情景，因此 F08 只绘制已有情景，并在最终审计中列为需要用户/后续模型阶段确认的输入限制。

## 5. 每张正文候选图的标题和图注建议

| 图 | 标题建议 | 图注建议 |
|---|---|---|
| F01 | 股票-月份有效分钟覆盖率 | 按月聚合 code-date 有效分钟覆盖率，颜色越深代表模型就绪样本覆盖越充分。 |
| F02 | LSI 日内模式 | 展示 LSI_5 在日内 slot 上的均值和 25%-75% 分位带，标注开盘、午后开盘和尾盘。 |
| F03 | 市场压力指数（MarketLSI）时间序列 | 日度聚合 MarketLSI 与滚动均值；监管阶段仅作为时间分段背景，不表示因果识别。 |
| F04 | RGARCH-CARR-SK 条件压力风险路径 | 基于 MarketLSI 压力风险适配模型的 `lambda_t` 路径，与 realized pressure measure 对比。 |
| F05 | RGARCH-CARR-SK 动态偏度与动态峰度 | 动态高阶矩为模型隐含风险分布特征；峰度若较稳定，应在正文说明。 |
| F06 | realized pressure measures 对比 | 比较 RV、RBV、MedRV、RMAD 的标准化日度序列或分布，不混用原始量纲。 |
| F07 | QVAR 尾部分位响应 | 展示 MarketLSI shock 下不同分位点响应；解释为尾部分位传导，不写成严格因果识别。 |
| F08 | QVAR 压力测试情景 | 展示市场急跌、波动放大、成交收缩和复合压力情景下的 MarketLSI 路径。 |
| F09 | SMARTBoost 样本外 PR 曲线 | 使用剔除 `CrossStress` 后的新预测概率，基准线为测试期事件率。 |
| F10 | SMARTBoost 样本外 ROC 曲线 | 附录辅助图，配合 PR-AUC 与 Top 5% lift 解释。 |
| F11 | SMARTBoost Calibration 曲线 | 分箱展示平均预测概率与真实压力发生率。 |
| F12 | SMARTBoost Top 5% 高风险组真实压力发生率 | 展示 validation/test 与 H5/H10 的 Top 5% 事件率，并对比全样本基准事件率。 |
| F13 | SMARTBoost Partial Effects | 只保留当前无泄漏特征中的核心变量，展示预测概率局部响应。 |

## 6. CrossStress 泄漏残留判断

- 当前 `smartboost_feature_leakage_deep_audit.md` 已确认旧版 `CrossStress` 泄漏并完成修正。
- 当前 SMARTBoost metadata 不含 `CrossStress`。
- 本轮脚本将从 `smartboost_model_metadata.json` 检查 `feature_columns`，若发现 `CrossStress` 将直接报错。
- 本轮 paper-ready SMARTBoost 图只读取剔除 `CrossStress` 后的 `predictions_by_code`、`smartboost_metrics.csv`、`smartboost_event_rate_and_lift.csv`、`smartboost_calibration_table.csv`、`smartboost_partial_effects.csv`。

## 7. 如何应用 academic-finance-visualization-cn skill

- 绘图脚本显式加载 `.agents/skills/academic-finance-visualization-cn/scripts/finance_paper_style.py`。
- 使用 `apply_finance_paper_style()` 统一字体、负号、线宽、保存参数。
- 使用 `save_figure_dual_format()` 对所有 paper-ready 图保存 PNG 300dpi 和 PDF。
- 使用 `get_model_palette()` 与 `get_line_styles()` 控制模型、期间、分位点的颜色和线型。
- 使用 `.agents/skills/academic-finance-visualization-cn/scripts/figure_audit.py` 审计 PNG/PDF、dpi、空图、文件名和 CrossStress 泄漏疑点。
