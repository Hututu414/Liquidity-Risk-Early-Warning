# 图表登记：Figure Registry

本登记表记录本轮全量图表论文级重构后的原位 PNG 输出。`99_paper_ready/` 为历史派生目录，不再作为最终图表来源。

## 最终 PNG 图表

| 编号 | 标题 | PNG 路径 | 模块 | 用途说明 | 对应章节 | SMARTBoost 修正后结果 | 去向 |
|---|---|---|---|---|---|---|---|
| F01 | 股票-月份有效分钟覆盖率 | `outputs/figures/01_data/fig_refined_coverage_heatmap.png` | diagnostics/data | 按 code 总覆盖率排序，颜色为 code-month 平均有效分钟覆盖率。 | 第3章 数据 | 不适用 | 正文 |
| F02 | 按交易所/指数分组的覆盖率摘要 | `outputs/figures/01_data/fig_coverage_by_exchange_summary.png` | diagnostics/data | 辅助检查不同交易所与指数样本覆盖差异。 | 第3章 数据 | 不适用 | 附录 |
| F03 | LSI 日内模式 | `outputs/figures/02_lsi/fig_refined_lsi_intraday.png` | MarketLSI/LSI | 展示均值、中位数及分位带；关键时点为开盘、午后开盘和尾盘。 | 第4章 LSI与标签 | 不适用 | 正文 |
| F04 | 分阶段 LSI 日内模式 | `outputs/figures/02_lsi/fig_lsi_intraday_by_stage.png` | MarketLSI/LSI | 监管阶段仅作为时间分段背景，不表示因果识别。 | 第4章 LSI与标签 | 不适用 | 附录/正文备选 |
| F05 | 市场压力指数（MarketLSI）时间序列 | `outputs/figures/02_lsi/fig_refined_market_lsi_timeseries.png` | MarketLSI/LSI | 日度聚合与滚动均值；阶段阴影仅为时间背景。 | 第4章 LSI与标签 | 不适用 | 正文 |
| F06 | MarketLSI 分阶段分布 | `outputs/figures/02_lsi/fig_market_lsi_stage_distribution.png` | MarketLSI/LSI | 分阶段描述性比较，不表示严格因果识别。 | 第4章 LSI与标签 | 不适用 | 正文/附录 |
| F07 | 极端 MarketLSI 分钟的日内分布 | `outputs/figures/02_lsi/fig_market_lsi_extreme_slot_distribution.png` | MarketLSI/LSI | 用于观察极端压力分钟在日内的集中位置。 | 第4章 LSI与标签 | 不适用 | 附录 |
| F08 | RGARCH-CARR-SK 条件压力风险路径 | `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_conditional_risk.png` | RGARCH-CARR-SK | 选用样本外 R2LOG 较优模型；展示条件风险、realized pressure 和训练期阈值。 | 第6章 RGARCH-CARR-SK | 不适用 | 正文 |
| F09 | 条件压力风险 lambda_t 路径 | `outputs/figures/04_rgarch/fig_rgarch_conditional_risk_path.png` | RGARCH-CARR-SK | 单独展示条件压力风险主线，避免与 realized measure 叠加过密。 | 第6章 RGARCH-CARR-SK | 不适用 | 正文 |
| F10 | RGARCH-CARR-SK 动态偏度与动态峰度 | `outputs/figures/04_rgarch/fig_rgarch_dynamic_skew_kurtosis.png` | RGARCH-CARR-SK | 模型隐含高阶矩路径，不解释为 realized sample moment。 | 第6章 RGARCH-CARR-SK | 不适用 | 正文 |
| F11 | RGARCH-CARR-SK 动态偏度 | `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_skewness.png` | RGARCH-CARR-SK | 单独高阶矩路径图。 | 第6章 RGARCH-CARR-SK | 不适用 | 正文/附录 |
| F12 | RGARCH-CARR-SK 动态峰度 | `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png` | RGARCH-CARR-SK | 单独高阶矩路径图。 | 第6章 RGARCH-CARR-SK | 不适用 | 正文/附录 |
| F13 | realized pressure measures 标准化分布 | `outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png` | RGARCH-CARR-SK | 比较 RV、RBV、MedRV、RMAD；使用标准化 log measure 避免量纲混画。 | 第6章 RGARCH-CARR-SK | 不适用 | 正文/附录 |
| F14 | realized pressure measures 密度对比 | `outputs/figures/04_rgarch/fig_rgarch_realized_measure_density.png` | RGARCH-CARR-SK | 辅助比较不同 realized pressure measure 的分布形态。 | 第6章 RGARCH-CARR-SK | 不适用 | 附录 |
| F15 | RGARCH-CARR-SK 样本外损失对比 | `outputs/figures/04_rgarch/fig_rgarch_oos_loss_comparison.png` | RGARCH-CARR-SK | 比较不同 realized pressure measure 的 validation/test R2LOG。 | 第6章 RGARCH-CARR-SK | 不适用 | 正文/附录 |
| F16 | RGARCH-CARR-SK 风险与高阶矩演化 | `outputs/figures/04_rgarch/fig_refined_rgarch_risk_evolution.png` | RGARCH-CARR-SK | 综合展示条件风险、动态偏度和动态峰度。 | 第6章 RGARCH-CARR-SK | 不适用 | 附录 |
| F17 | QVAR 尾部分位响应 | `outputs/figures/05_qvar/fig_qvar_tail_quantile_response.png` | QVAR | 展示尾部分位传导，不表示严格因果识别。 | 第7章 QVAR | 不适用 | 正文 |
| F18 | QVAR 压力测试情景 | `outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png` | QVAR | 四类标准化情景冲击模拟；不是严格因果识别。 | 第7章 QVAR | 不适用 | 正文 |
| F19 | QVAR 响应衰减对比 | `outputs/figures/05_qvar/fig_qvar_response_decay.png` | QVAR | q=0.95 下不同冲击对 MarketLSI 的响应路径。 | 第7章 QVAR | 不适用 | 附录 |
| F20 | QVAR MarketLSI 样本外 pinball loss | `outputs/figures/05_qvar/fig_qvar_pinball_loss.png` | QVAR | 只展示 MarketLSI 方程的 validation/test 损失。 | 第7章 QVAR | 不适用 | 附录 |
| F21 | QVAR MarketLSI 方程系数热力图 | `outputs/figures/05_qvar/fig_qvar_coefficient_heatmap.png` | QVAR | 训练期分位数回归系数；用于解释系统变量关系。 | 第7章 QVAR | 不适用 | 附录 |
| F22 | SMARTBoost 样本外 PR 曲线 | `outputs/figures/06_smartboost/fig_smartboost_pr_curve.png` | SMARTBoost | 使用剔除 CrossStress 后的新预测结果。 | 第8章 SMARTBoost | 是 | 正文 |
| F23 | SMARTBoost 样本外 ROC 曲线 | `outputs/figures/06_smartboost/fig_smartboost_roc_curve.png` | SMARTBoost | ROC 为辅助证据，不替代 PR 曲线。 | 第8章 SMARTBoost | 是 | 附录 |
| F24 | SMARTBoost validation/test PR 与 ROC 对比 | `outputs/figures/06_smartboost/fig_smartboost_pr_roc_by_period.png` | SMARTBoost | 辅助展示不同样本外期间曲线。 | 第8章 SMARTBoost | 是 | 附录 |
| F25 | SMARTBoost Calibration 曲线 | `outputs/figures/06_smartboost/fig_smartboost_calibration_curve.png` | SMARTBoost | 分箱点图和45度参考线。 | 第8章 SMARTBoost | 是 | 正文/附录 |
| F26 | SMARTBoost Top 5% 高风险组真实压力发生率 | `outputs/figures/06_smartboost/fig_smartboost_top5_realized_rate.png` | SMARTBoost | 柱上标注为 Top5 lift。 | 第8章 SMARTBoost | 是 | 正文 |
| F27 | SMARTBoost 高风险分组命中率 | `outputs/figures/06_smartboost/fig_refined_top5_realized_rate.png` | SMARTBoost | 展示 Top 1/5/10/20% 分组真实压力发生率。 | 第8章 SMARTBoost | 是 | 附录 |
| F28 | SMARTBoost lift curve | `outputs/figures/06_smartboost/fig_smartboost_lift_curve.png` | SMARTBoost | 高风险分组相对基准事件率的 lift。 | 第8章 SMARTBoost | 是 | 正文/附录 |
| F29 | SMARTBoost Partial Effects | `outputs/figures/06_smartboost/fig_smartboost_partial_effects.png` | SMARTBoost | 选择局部响应幅度最大的4个无泄漏变量；不含 CrossStress。 | 第8章 SMARTBoost | 是 | 正文/附录 |
| F30 | SMARTBoost refined Partial Effects | `outputs/figures/06_smartboost/fig_refined_partial_effects.png` | SMARTBoost | 展示当前 partial effects 表中的无泄漏变量。 | 第8章 SMARTBoost | 是 | 附录 |
| F31 | SMARTBoost 预测概率分布 | `outputs/figures/06_smartboost/fig_smartboost_probability_distribution.png` | SMARTBoost | 展示 test 样本正负例预测概率分离。 | 第8章 SMARTBoost | 是 | 附录 |
| F32 | SMARTBoost 分阶段 PR-AUC | `outputs/figures/06_smartboost/fig_smartboost_regime_metrics.png` | SMARTBoost | 分阶段描述性性能对比，不作因果识别。 | 第8章 SMARTBoost | 是 | 附录 |
| F33 | SMARTBoost feature importance | `outputs/figures/06_smartboost/fig_smartboost_feature_importance.png` | SMARTBoost | 若 importance 全为0，图中如实说明。 | 第8章 SMARTBoost | 是 | 附录 |

## 废弃或仅作历史备查

| 路径 | 处理 | 原因 |
|---|---|---|
| `outputs/figures/99_paper_ready/*.png` | 不作为最终图表来源 | 派生目录不符合本轮原位更新要求；旧 QVAR 情景图只含两类情景 |
| `outputs/figures/99_paper_ready/*.pdf` | 不作为最终图表来源 | 本轮只登记 PNG，不输出 PDF |
| 旧 `CrossStress` 相关可视化 | 不进入正文 | `CrossStress` 来自未来压力标签横截面聚合，不能作为 SMARTBoost 预测特征或预警证据 |

## 审计

- 全量图清单：`reviews/report_consistency/full_figure_inventory_before_rebuild.md`
- 重构计划：`reviews/report_consistency/full_figure_rebuild_plan_v2.md`
- QVAR 情景核查：`reviews/report_consistency/qvar_scenario_coverage_check.md`
- 最终审计：`reviews/report_consistency/full_figure_rebuild_final_audit.md`
- 审计 CSV：`reviews/report_consistency/full_figure_rebuild_audit.csv`
- CSV registry：`outputs/figures/in_place_figure_registry.csv`

## 描述性统计图表体系补齐（2026-05-20）

本节记录本轮统一输出到 `outputs/figures/03_descriptive/` 的描述性统计正文候选图。旧 `01_data/` 与 `02_lsi/` 中同类图保留为历史/模块图，不再作为描述性统计章节的首选路径。

| 编号 | 标题 | PNG 路径 | 输入数据 | 去向 | 备注 |
|---|---|---|---|---|---|
| D01 | 股票-月份有效分钟覆盖率 | `outputs/figures/03_descriptive/fig_descriptive_01_sample_coverage_heatmap.png` | `data_intermediate/stage1_model_ready/coverage_by_code_date.csv` | 正文 | 图一；按月聚合避免逐日热力图过密，按交易所和平均覆盖率排序。 |
| D02 | 样本划分时间轴 | `outputs/figures/03_descriptive/fig_descriptive_02_sample_split_timeline.png` | `data_intermediate/stage2_lsi_labels/time_split.json` | 正文 | 展示 training / validation / test 的时间区间。 |
| D03 | MarketLSI 日度时间序列 | `outputs/figures/03_descriptive/fig_descriptive_03_marketlsi_timeseries.png` | `data_intermediate/stage2_lsi_labels/market_context.parquet` | 正文 | 日均 MarketLSI、20日滚动均值和高压力日标注。 |
| D04 | H5 / H10 压力事件率时间图 | `outputs/figures/03_descriptive/fig_descriptive_04_event_rate_h5_h10_timeseries.png` | `outputs/descriptive_diagnostics/tables/stress_rate_by_date.csv` | 正文 | 按月展示 Stress_H5 与 Stress_H10 的时变事件率。 |
| D05 | LSI_5 日内模式 | `outputs/figures/03_descriptive/fig_descriptive_05_intraday_pattern.png` | `outputs/descriptive_diagnostics/tables/lsi_intraday_stats.csv` | 正文 | 展示均值、中位数和 IQR 分位带；采用全范围与主体区间放大，避免尾盘极值压扁主体波动。 |
| D06 | 分样本区间 LSI_5 日内模式 | `outputs/figures/03_descriptive/fig_descriptive_06_intraday_pattern_by_period.png` | `data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet` | 正文/附录 | 按 training / validation / test 对比日内模式稳定性。 |
| D07 | 核心变量分布 | `outputs/figures/03_descriptive/fig_descriptive_07_core_variable_distribution.png` | `market_context.parquet; lsi_labels_by_code/*.parquet sampled` | 正文/附录 | 对极端 1% 尾部做 winsorized 展示，仅用于避免主体分布被极值压扁。 |
| D08 | H5 / H10 事件率比较 | `outputs/figures/03_descriptive/fig_descriptive_08_event_rate_period_comparison.png` | `outputs/descriptive_diagnostics/tables/stress_rate_by_date.csv` | 正文 | 比较 training / validation / test 中 Stress_H5 与 Stress_H10 的平均事件率。 |
| D09 | 核心变量相关系数热力图 | `outputs/figures/03_descriptive/fig_descriptive_09_correlation_heatmap.png` | `market_context.parquet; stress_rate_by_date.csv` | 正文/附录 | 只选日度核心变量，不使用 CrossStress 作为预测特征证据。 |
