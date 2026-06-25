# Codex LaTeX 完整性盘点

## 当前 TeX 已插入图
- `figures/fig_timeline.png`
- `figures/fig_coverage.png`
- `figures/fig_intraday.png`
- `figures/fig_marketlsi.png`
- `figures/fig_event_rate.png`
- `figures/fig_corr.png`
- `figures/fig_rgarch_risk.png`
- `figures/fig_rgarch_realized.png`
- `figures/fig_rgarch_loss.png`
- `figures/fig_qvar_response.png`
- `figures/fig_qvar_stress.png`
- `figures/fig_sb_pr.png`
- `figures/fig_sb_top5.png`
- `figures/fig_sb_partial.png`
- `figures/fig_robust_label_threshold.png`
- `figures/fig_robust_sb_topk.png`

## 当前 TeX 已插入表
- `tables/tab_model_framework.tex`
- `tables/tab_sample_cleaning.tex`
- `tables/tab_variable_definition.tex`
- `tables/tab_label_distribution.tex`
- `tables/tab_rgarch_fit_loss.tex`
- `tables/tab_qvar_pinball.tex`
- `tables/tab_qvar_scenarios.tex`
- `tables/tab_smartboost_leakage.tex`
- `tables/tab_smartboost_metrics.tex`
- `tables/tab_smartboost_topk.tex`
- `tables/tab_robustness_summary.tex`

## 已复制到 LaTeX 工程的图
- 研究样本划分时间轴: `figures/fig_timeline.png` <- `05_outputs/figures/03_descriptive/fig_descriptive_02_sample_split_timeline.png` (copied, 正文)
- 股票-月份有效分钟覆盖率热力图: `figures/fig_coverage.png` <- `05_outputs/figures/03_descriptive/fig_descriptive_01_sample_coverage_heatmap.png` (copied, 正文)
- LSI_5 日内模式: `figures/fig_intraday.png` <- `05_outputs/figures/03_descriptive/fig_descriptive_05_intraday_pattern.png` (copied, 正文)
- MarketLSI 日度时间序列: `figures/fig_marketlsi.png` <- `05_outputs/figures/03_descriptive/fig_descriptive_03_marketlsi_timeseries.png` (copied, 正文)
- H5/H10 压力事件率: `figures/fig_event_rate.png` <- `05_outputs/figures/03_descriptive/fig_descriptive_04_event_rate_h5_h10_timeseries.png` (copied, 正文)
- 核心变量相关性热力图: `figures/fig_corr.png` <- `05_outputs/figures/03_descriptive/fig_descriptive_09_correlation_heatmap.png` (copied, 正文/附录)
- 核心变量分布图: `figures/fig_distribution.png` <- `05_outputs/figures/03_descriptive/fig_descriptive_07_core_variable_distribution.png` (copied, 附录)
- RGARCH-CARR-SK 条件压力风险路径: `figures/fig_rgarch_risk.png` <- `05_outputs/figures/04_rgarch/fig_rgarch_conditional_risk_path.png` (copied, 正文)
- realized pressure measures 对比: `figures/fig_rgarch_realized.png` <- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png` (copied, 正文)
- RGARCH-CARR-SK R2LOG 样本外损失: `figures/fig_rgarch_loss.png` <- `05_outputs/figures/04_rgarch/fig_rgarch_oos_loss_comparison.png` (copied, 正文)
- RGARCH-CARR-SK 动态偏度与峰度诊断: `figures/fig_rgarch_skew_kurt.png` <- `05_outputs/figures/04_rgarch/fig_rgarch_dynamic_skew_kurtosis.png` (copied, 附录/诊断)
- QVAR 尾部分位响应: `figures/fig_qvar_response.png` <- `05_outputs/figures/05_qvar/fig_qvar_tail_quantile_response.png` (copied, 正文)
- QVAR 四类压力测试情景: `figures/fig_qvar_stress.png` <- `05_outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png` (copied, 正文)
- QVAR pinball loss: `figures/fig_qvar_pinball.png` <- `05_outputs/figures/05_qvar/fig_qvar_pinball_loss.png` (copied, 附录/正文补充)
- SMARTBoost PR 曲线: `figures/fig_sb_pr.png` <- `05_outputs/figures/06_smartboost/fig_smartboost_pr_curve.png` (copied, 正文)
- SMARTBoost Top 5% 高风险组真实压力发生率: `figures/fig_sb_top5.png` <- `05_outputs/figures/06_smartboost/fig_smartboost_top5_realized_rate.png` (copied, 正文)
- SMARTBoost Partial Effects: `figures/fig_sb_partial.png` <- `05_outputs/figures/06_smartboost/fig_smartboost_partial_effects.png` (copied, 正文)
- SMARTBoost calibration 曲线: `figures/fig_sb_calibration.png` <- `05_outputs/figures/06_smartboost/fig_smartboost_calibration_curve.png` (copied, 附录/正文补充)
- 标签阈值稳健性: `figures/fig_robust_label_threshold.png` <- `05_outputs/figures/07_robustness/fig_label_threshold_robustness.png` (copied, 正文)
- RGARCH realized measure 稳健性: `figures/fig_robust_rgarch_measure.png` <- `05_outputs/figures/07_robustness/fig_rgarch_realized_measure_robustness.png` (copied, 正文/附录)
- QVAR 冲击幅度稳健性: `figures/fig_robust_qvar_shock.png` <- `05_outputs/figures/07_robustness/fig_qvar_shock_size_robustness.png` (copied, 附录)
- SMARTBoost 特征组消融: `figures/fig_robust_sb_ablation.png` <- `05_outputs/figures/07_robustness/fig_smartboost_feature_ablation.png` (copied, 正文/附录)
- SMARTBoost Top-K 稳健性: `figures/fig_robust_sb_topk.png` <- `05_outputs/figures/07_robustness/fig_smartboost_topk_robustness.png` (copied, 正文)

## 05_outputs 中尚未插入的 PNG 图
- `05_outputs/figures/01_data/fig_coverage_by_exchange_summary.png`
- `05_outputs/figures/01_data/fig_refined_coverage_heatmap.png`
- `05_outputs/figures/02_lsi/fig_lsi_intraday_by_stage.png`
- `05_outputs/figures/02_lsi/fig_market_lsi_extreme_slot_distribution.png`
- `05_outputs/figures/02_lsi/fig_market_lsi_stage_distribution.png`
- `05_outputs/figures/02_lsi/fig_refined_lsi_intraday.png`
- `05_outputs/figures/02_lsi/fig_refined_market_lsi_timeseries.png`
- `05_outputs/figures/03_descriptive/fig_descriptive_06_intraday_pattern_by_period.png`
- `05_outputs/figures/03_descriptive/fig_descriptive_08_event_rate_period_comparison.png`
- `05_outputs/figures/04_rgarch/fig_refined_rgarch_risk_evolution.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_conditional_risk.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_skewness.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_realized_measure_density.png`
- `05_outputs/figures/05_qvar/fig_qvar_coefficient_heatmap.png`
- `05_outputs/figures/05_qvar/fig_qvar_response_decay.png`
- `05_outputs/figures/06_smartboost/fig_refined_partial_effects.png`
- `05_outputs/figures/06_smartboost/fig_refined_top5_realized_rate.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_feature_importance.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_lift_curve.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_pr_roc_by_period.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_probability_distribution.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_regime_metrics.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_roc_curve.png`
- `05_outputs/figures/07_robustness/fig_qvar_quantile_robustness.png`

## 05_outputs 中尚未转为 TeX 摘要表的表格/JSON
- `05_outputs/tables/03_descriptive/descriptive_core_variable_correlation.csv`
- `05_outputs/tables/03_descriptive/descriptive_daily_market_context.csv`
- `05_outputs/tables/03_descriptive/descriptive_event_rate_by_period.csv`
- `05_outputs/tables/03_descriptive/descriptive_intraday_lsi_by_period.csv`
- `05_outputs/tables/03_descriptive/descriptive_monthly_event_rate.csv`
- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv`
- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_parameter_estimates.csv`
- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_realized_pressure_measures.csv`
- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_scaling.csv`
- `05_outputs/tables/04_rgarch/rgarch_simplified_daily_risk.csv`
- `05_outputs/tables/04_rgarch/rgarch_simplified_parameter_summary.csv`
- `05_outputs/tables/04_rgarch/rgarch_simplified_period_summary.csv`
- `05_outputs/tables/04_rgarch/rgarch_simplified_risk_path.csv`
- `05_outputs/tables/05_qvar/qvar_pressure_test_paths.csv`
- `05_outputs/tables/05_qvar/qvar_quantile_coefficients_train.csv`
- `05_outputs/tables/05_qvar/qvar_quantile_coefficients_train_plus_validation.csv`
- `05_outputs/tables/05_qvar/qvar_tail_quantile_response.csv`
- `05_outputs/tables/05_qvar/qvar_train_standardization_stats.csv`
- `05_outputs/tables/06_smartboost/smartboost_best_iterations.csv`
- `05_outputs/tables/06_smartboost/smartboost_calibration_table.csv`
- `05_outputs/tables/06_smartboost/smartboost_feature_importance.csv`
- `05_outputs/tables/06_smartboost/smartboost_high_risk_group_rates.csv`
- `05_outputs/tables/06_smartboost/smartboost_iteration_selection.csv`
- `05_outputs/tables/06_smartboost/smartboost_model_metadata.json`
- `05_outputs/tables/06_smartboost/smartboost_partial_effects.csv`
- `05_outputs/tables/06_smartboost/smartboost_prediction_integrity_check.csv`
- `05_outputs/tables/06_smartboost/smartboost_prediction_manifest.csv`
- `05_outputs/tables/06_smartboost/smartboost_regime_metrics.csv`
- `05_outputs/tables/06_smartboost/smartboost_training_sample_summary.csv`
- `05_outputs/tables/07_robustness/horizon_robustness.csv`
- `05_outputs/tables/07_robustness/missing_minute_threshold_robustness.csv`
- `05_outputs/tables/07_robustness/qvar_shock_size_robustness.csv`
- `05_outputs/tables/07_robustness/rgarch_oos_loss_robustness.csv`
- `05_outputs/tables/07_robustness/smartboost_calibration_robustness.csv`
- `05_outputs/tables/07_robustness/smartboost_time_split_robustness.csv`
- `05_outputs/tables/07_robustness/standardization_robustness.csv`

## 适合正文的图
- `05_outputs/figures/03_descriptive/fig_descriptive_02_sample_split_timeline.png`
- `05_outputs/figures/03_descriptive/fig_descriptive_01_sample_coverage_heatmap.png`
- `05_outputs/figures/03_descriptive/fig_descriptive_05_intraday_pattern.png`
- `05_outputs/figures/03_descriptive/fig_descriptive_03_marketlsi_timeseries.png`
- `05_outputs/figures/03_descriptive/fig_descriptive_04_event_rate_h5_h10_timeseries.png`
- `05_outputs/figures/03_descriptive/fig_descriptive_09_correlation_heatmap.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_conditional_risk_path.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_oos_loss_comparison.png`
- `05_outputs/figures/05_qvar/fig_qvar_tail_quantile_response.png`
- `05_outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_pr_curve.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_top5_realized_rate.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_partial_effects.png`
- `05_outputs/figures/07_robustness/fig_label_threshold_robustness.png`
- `05_outputs/figures/07_robustness/fig_rgarch_realized_measure_robustness.png`
- `05_outputs/figures/07_robustness/fig_smartboost_feature_ablation.png`
- `05_outputs/figures/07_robustness/fig_smartboost_topk_robustness.png`

## 适合附录的图
- `05_outputs/figures/03_descriptive/fig_descriptive_09_correlation_heatmap.png`
- `05_outputs/figures/03_descriptive/fig_descriptive_07_core_variable_distribution.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_dynamic_skew_kurtosis.png`
- `05_outputs/figures/05_qvar/fig_qvar_pinball_loss.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_calibration_curve.png`
- `05_outputs/figures/07_robustness/fig_rgarch_realized_measure_robustness.png`
- `05_outputs/figures/07_robustness/fig_qvar_shock_size_robustness.png`
- `05_outputs/figures/07_robustness/fig_smartboost_feature_ablation.png`

## 不应作为正文主图使用的图
- `05_outputs/figures/06_smartboost/fig_smartboost_feature_importance.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_roc_curve.png`
- `05_outputs/figures/99_paper_ready/fig_01_coverage_heatmap.png`
- `05_outputs/figures/99_paper_ready/fig_02_lsi_intraday_pattern.png`
- `05_outputs/figures/99_paper_ready/fig_03_market_lsi_time_series.png`
- `05_outputs/figures/99_paper_ready/fig_04_rgarch_conditional_pressure_risk.png`
- `05_outputs/figures/99_paper_ready/fig_05_rgarch_dynamic_skew_kurtosis.png`
- `05_outputs/figures/99_paper_ready/fig_06_rgarch_realized_pressure_measures.png`
- `05_outputs/figures/99_paper_ready/fig_07_qvar_tail_quantile_response.png`
- `05_outputs/figures/99_paper_ready/fig_08_qvar_pressure_test_scenarios.png`
- `05_outputs/figures/99_paper_ready/fig_09_smartboost_pr_curve.png`
- `05_outputs/figures/99_paper_ready/fig_10_smartboost_roc_curve.png`
- `05_outputs/figures/99_paper_ready/fig_11_smartboost_calibration_curve.png`
- `05_outputs/figures/99_paper_ready/fig_12_smartboost_top5_event_rate.png`
- `05_outputs/figures/99_paper_ready/fig_13_smartboost_partial_effects.png`

## 必须进入正文或正文摘要的表
- `08_report\latex_project\tables\tab_model_framework.tex`
- `08_report\latex_project\tables\tab_variable_definition.tex`
- `08_report\latex_project\tables\tab_sample_cleaning.tex`
- `08_report\latex_project\tables\tab_label_distribution.tex`
- `08_report\latex_project\tables\tab_rgarch_fit_loss.tex`
- `08_report\latex_project\tables\tab_qvar_pinball.tex`
- `08_report\latex_project\tables\tab_qvar_scenarios.tex`
- `08_report\latex_project\tables\tab_smartboost_metrics.tex`
- `08_report\latex_project\tables\tab_smartboost_topk.tex`
- `08_report\latex_project\tables\tab_smartboost_leakage.tex`
- `08_report\latex_project\tables\tab_robustness_summary.tex`

## 仍需核验的数值
- RGARCH-CARR-SK 中 RMAD 的 R2LOG 很低，已在图形审计中说明其为真实输出而非填零；正文按损失指标解释，避免过度概括。
- QVAR 情景响应路径应按图中具体方向解释，不写成所有情景均推高 MarketLSI。
- SMARTBoost 所有正文数值来自删除 CrossStress 后的输出表；旧版含 CrossStress 的结果不得引用。
