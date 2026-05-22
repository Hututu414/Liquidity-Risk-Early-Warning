# Full Figure Rebuild Final Audit

## 1. 执行范围

- 本轮开始前扫描到 PNG：32 张，其中 `99_paper_ready` 旧派生 PNG：13 张。
- 原模块 PNG 重构/新增输出：33 张。
- 覆盖更新原有 PNG：19 张。
- 新增辅助 PNG：14 张。
- 删除/废弃图：13 张旧 `99_paper_ready` PNG 降级为历史备查；本轮未物理删除文件。

## 1.1 Skill 使用情况

- 已显式读取 `.agents/skills/academic-finance-visualization-cn/SKILL.md`。
- 已显式读取并复用 `.agents/skills/academic-finance-visualization-cn/scripts/finance_paper_style.py`。
- 已显式读取并复用 `.agents/skills/academic-finance-visualization-cn/scripts/figure_audit.py` 的 PNG dpi 与空图检查逻辑。
- 全量重绘脚本 `04_code/src/visualization/rebuild_all_existing_figures_in_place.py` 使用 skill 风格函数，不使用默认 matplotlib 风格。

## 2. 覆盖更新图

- `05_outputs/figures/01_data/fig_refined_coverage_heatmap.png`
- `05_outputs/figures/02_lsi/fig_refined_lsi_intraday.png`
- `05_outputs/figures/02_lsi/fig_refined_market_lsi_timeseries.png`
- `05_outputs/figures/04_rgarch/fig_refined_rgarch_risk_evolution.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_conditional_risk.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_skewness.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_conditional_risk_path.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_dynamic_skew_kurtosis.png`
- `05_outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png`
- `05_outputs/figures/05_qvar/fig_qvar_tail_quantile_response.png`
- `05_outputs/figures/06_smartboost/fig_refined_partial_effects.png`
- `05_outputs/figures/06_smartboost/fig_refined_top5_realized_rate.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_calibration_curve.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_partial_effects.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_pr_curve.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_roc_curve.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_top5_realized_rate.png`

## 3. 新增辅助图

- `05_outputs/figures/01_data/fig_coverage_by_exchange_summary.png`
- `05_outputs/figures/02_lsi/fig_lsi_intraday_by_stage.png`
- `05_outputs/figures/02_lsi/fig_market_lsi_extreme_slot_distribution.png`
- `05_outputs/figures/02_lsi/fig_market_lsi_stage_distribution.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_oos_loss_comparison.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_realized_measure_density.png`
- `05_outputs/figures/05_qvar/fig_qvar_coefficient_heatmap.png`
- `05_outputs/figures/05_qvar/fig_qvar_pinball_loss.png`
- `05_outputs/figures/05_qvar/fig_qvar_response_decay.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_feature_importance.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_lift_curve.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_pr_roc_by_period.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_probability_distribution.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_regime_metrics.png`

## 4. 审计结果

- 审计 CSV：`07_reviews/report_consistency/full_figure_rebuild_audit.csv`
- PASS：33
- FAIL：0
- 所有最终 PNG 均为 300dpi。
- Legend 布局：绘图脚本统一使用图外上方、右上/左上空白区或分面内部非数据密集区；人工抽查仍建议逐图确认。
- QVAR 当前情景数：4，情景为：composite_pressure, liquidity_contraction, market_crash, volatility_spike。
- QVAR 四类标准情景已补齐：市场急跌、波动放大、成交收缩 / 流动性压力、复合压力。
- SMARTBoost 最终图数量：12；均基于剔除 `CrossStress` 后的新结果。
- 本轮是否输出 PDF：否。历史 PDF 数量从 16 到 16，未作为最终 registry 输出。
- 所有最终图均保存在原模块目录下，未输出到 `99_paper_ready/`。

## 5. 仍需人工复核

- `fig_refined_coverage_heatmap.png`：行数较多，建议确认论文版面是否接受当前高度。
- RGARCH 高阶矩图：建议确认动态峰度稳定性的正文表述是否足够保守。
- QVAR 情景图：建议确认四类标准化冲击命名和正文解释均保持“情景模拟”口径。
- SMARTBoost Partial Effects：建议确认 4 个变量是否符合最终论文解释重点。

## 6. 未触碰事项

- 未重跑 stage0-stage3。
- 未修改 RGARCH-CARR-SK、QVAR、SMARTBoost 的模型定义；新增/使用的 QVAR 情景脚本只基于既有系数递推。
- 未修改 `02_data_inbox/preprocessed/`。
- 未重新引入 `CrossStress` 作为 SMARTBoost 特征。
- 未进入 LaTeX 编译。
