# LaTeX 图表映射

本文件记录最终版正文与附录实际引用的图表。所有图片路径均为相对路径。

## 正文图

| label | 题名 | LaTeX 文件 | 图像文件 | 用途 |
|---|---|---|---|---|
| `fig:timeline` | 训练、验证与测试样本划分 | `sections/04_data_descriptive.tex` | `figures/fig_timeline.png` | 说明时间切分和样本外检验边界。 |
| `fig:coverage` | 股票-月份有效分钟覆盖率热力图 | `sections/04_data_descriptive.tex` | `figures/fig_coverage.png` | 检查分钟面板覆盖质量。 |
| `fig:intraday` | LSI_5 日内模式 | `sections/04_data_descriptive.tex` | `figures/fig_intraday.png` | 展示日内压力结构。 |
| `fig:marketlsi` | MarketLSI 日度时间序列 | `sections/04_data_descriptive.tex` | `figures/fig_marketlsi.png` | 展示市场层面压力阶段变化。 |
| `fig:rgarch-risk` | RGARCH-CARR-SK 条件压力风险路径 | `sections/05_empirical_results.tex` | `figures/fig_rgarch_risk.png` | RGARCH-CARR-SK 主证据。 |
| `fig:qvar-response` | QVAR 尾部分位响应 | `sections/05_empirical_results.tex` | `figures/fig_qvar_response.png` | 比较不同分位点下的条件响应路径。 |
| `fig:qvar-stress` | QVAR 四类压力测试情景 | `sections/05_empirical_results.tex` | `figures/fig_qvar_stress.png` | 展示标准化情景响应路径。 |
| `fig:sb-pr` | SMARTBoost 样本外 PR 曲线 | `sections/05_empirical_results.tex` | `figures/fig_sb_pr.png` | 样本外预警主证据。 |
| `fig:sb-top5` | SMARTBoost Top 5% 高风险组真实压力发生率 | `sections/05_empirical_results.tex` | `figures/fig_sb_top5.png` | 直观展示 Top 5% 预警集中度。 |
| `fig:sb-partial` | SMARTBoost 核心变量 Partial Effects | `sections/05_empirical_results.tex` | `figures/fig_sb_partial.png` | 展示预测模型局部响应，不作因果解释。 |
| `fig:robust-label` | 标签阈值稳健性 | `sections/06_robustness.tex` | `figures/fig_robust_label_threshold.png` | 检查不同标签阈值下的排序稳定性。 |
| `fig:rgarch-realized-dist` | realized pressure measures 分布对比 | `sections/06_robustness.tex` | `figures/fig_rgarch_realized_measure_distribution_refined.png` | 解释 RGARCH 测度敏感性。 |
| `fig:qvar-tail-summary` | QVAR 最大响应差异 | `sections/06_robustness.tex` | `figures/fig_qvar_tail_response_summary_refined.png` | 检查尾部和中位数状态下响应强度差异。 |
| `fig:robust-topk` | SMARTBoost Top-K 稳健性 | `sections/06_robustness.tex` | `figures/fig_robust_sb_topk.png` | 检查不同预警宽度下的高风险排序。 |

## 附录图

| label | 题名 | LaTeX 文件 | 图像文件 | 处理理由 |
|---|---|---|---|---|
| `fig:app-event-rate` | H5/H10 压力事件率时间变化 | `sections/appendix_figures.tex` | `figures/fig_event_rate.png` | 描述性补充。 |
| `fig:app-corr` | 核心市场状态变量相关性热力图 | `sections/appendix_figures.tex` | `figures/fig_corr.png` | 相关结构补充，不作因果识别。 |
| `fig:app-sb-calibration` | SMARTBoost 样本外校准曲线 | `sections/appendix_figures.tex` | `figures/fig_sb_calibration.png` | Brier 指标的视觉补充。 |

## 未引用图

| 图像文件 | 处理 |
|---|---|
| `figures/fig_rgarch_dynamic_skew_kurtosis_refined.png` | 不进入正文或附录；动态峰度路径不作为核心经验发现。 |
| `figures/fig_rgarch_skew_kurt.png` | 不进入正文或附录；旧的偏度/峰度诊断图。 |
| `figures/fig_rgarch_loss.png` | 不引用；R2LOG/RMAD 量纲差异改由表格呈现。 |
| `figures/fig_rgarch_realized.png` | 不引用；由正文稳健性图 `fig_rgarch_realized_measure_distribution_refined.png` 替代。 |
| `figures/fig_qvar_pinball.png` | 不引用；pinball loss 由表格呈现。 |
| `figures/fig_distribution.png` | 不引用；变量定义和正文解释已覆盖主要信息。 |
| `figures/fig_robust_qvar_shock.png` | 不引用；QVAR 稳健性改用最大响应差异图。 |
| `figures/fig_robust_rgarch_measure.png` | 不引用；RGARCH 稳健性改用 refined 分布图。 |
| `figures/fig_robust_sb_ablation.png` | 不引用；SMARTBoost 稳健性以 Top-K 和特征边界表为主。 |
| `figures/fig_descriptive_01_sample_coverage_heatmap.png` | 不引用；正文使用 `fig_coverage.png`。 |

## 正文表

| label | 题名 | 文件 |
|---|---|---|
| `tab:model-framework` | 研究框架、技术实现与解释边界 | `tables/tab_model_framework.tex` |
| `tab:literature-map` | 文献脉络、代表文献与本文用途 | `sections/02_literature.tex` |
| `tab:sample-cleaning` | 样本结构与数据清洗结果 | `tables/tab_sample_cleaning.tex` |
| `tab:variables` | 核心变量、压力标签与防泄漏边界 | `tables/tab_variable_definition.tex` |
| `tab:label-distribution` | 未来压力标签的样本区间分布 | `tables/tab_label_distribution.tex` |
| `tab:rgarch-fit` | RGARCH-CARR-SK 拟合准则 | `tables/tab_rgarch_fit_loss.tex` |
| `tab:rgarch-loss` | RGARCH-CARR-SK 样本外损失 | `tables/tab_rgarch_fit_loss.tex` |
| `tab:qvar-pinball` | QVAR MarketLSI 方程样本外 pinball loss | `tables/tab_qvar_pinball.tex` |
| `tab:qvar-scenarios` | QVAR 压力测试情景设定 | `tables/tab_qvar_scenarios.tex` |
| `tab:smartboost-metrics` | SMARTBoost validation/test 样本外预警指标 | `tables/tab_smartboost_metrics.tex` |
| `tab:smartboost-topk` | SMARTBoost test 高风险组真实压力发生率与 lift | `tables/tab_smartboost_topk.tex` |
| `tab:smartboost-leakage` | SMARTBoost 特征边界核查 | `tables/tab_smartboost_leakage.tex` |
| `tab:robustness-design` | 稳健性检验设计 | `tables/tab_robustness_summary.tex` |
| `tab:robustness-conclusions` | 稳健性检验核心结论 | `tables/tab_robustness_summary.tex` |
