# 图表与结果资产清单

## 1. 描述性统计 (03_descriptive)
- **fig_descriptive_01_sample_coverage_heatmap.png**
  - **路径**: `05_outputs/figures/03_descriptive/fig_descriptive_01_sample_coverage_heatmap.png`
  - **是否入正文**: 是
- **fig_descriptive_02_sample_split_timeline.png**
  - **路径**: `05_outputs/figures/03_descriptive/fig_descriptive_02_sample_split_timeline.png`
  - **是否入正文**: 是
- **fig_descriptive_03_marketlsi_timeseries.png**
  - **路径**: `05_outputs/figures/03_descriptive/fig_descriptive_03_marketlsi_timeseries.png`
  - **是否入正文**: 是
- **fig_descriptive_05_intraday_pattern.png**
  - **路径**: `05_outputs/figures/03_descriptive/fig_descriptive_05_intraday_pattern.png`
  - **是否入正文**: 是

## 2. RGARCH-CARR-SK 模型 (04_rgarch)
- **fig_rgarch_conditional_risk_path.png**
  - **路径**: `05_outputs/figures/04_rgarch/fig_rgarch_conditional_risk_path.png`
  - **说明**: 展示条件压力风险的时间路径。
  - **是否入正文**: 是
- **fig_rgarch_dynamic_skew_kurtosis.png**
  - **路径**: `05_outputs/figures/04_rgarch/fig_rgarch_dynamic_skew_kurtosis.png`
  - **说明**: 动态偏度与峰度诊断图。当前可能需要从这重新绘制优化版。
  - **是否入正文**: 是（将作为第二张主图移入正文 5.1）
- **fig_rgarch_carr_sk_adapted_realized_measures.png**
  - **路径**: `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png`
  - **说明**: Realized pressure measures 对比图。
  - **是否入正文**: 否（目前在附录，考虑移入 6.2 稳健性章节）
- **rgarch_carr_sk_adapted_fit_criteria.csv**
  - **路径**: `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_fit_criteria.csv`
  - **说明**: 样本内拟合准则表。
  - **是否入正文**: 是
- **rgarch_carr_sk_adapted_oos_losses.csv**
  - **路径**: `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_oos_losses.csv`
  - **说明**: 样本外损失表。
  - **是否入正文**: 是

## 3. QVAR 模型 (05_qvar)
- **fig_qvar_tail_quantile_response.png**
  - **路径**: `05_outputs/figures/05_qvar/fig_qvar_tail_quantile_response.png`
  - **说明**: QVAR 尾部分位响应图。
  - **是否入正文**: 是
- **fig_qvar_pressure_test_paths.png**
  - **路径**: `05_outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png`
  - **说明**: QVAR 四类压力测试情景响应图。
  - **是否入正文**: 是
- **qvar_blocked_oos_pinball_loss.csv**
  - **路径**: `05_outputs/tables/05_qvar/qvar_blocked_oos_pinball_loss.csv`
  - **说明**: 验证集与测试集的 Pinball loss。
  - **是否入正文**: 是

## 4. SMARTBoost 模型 (06_smartboost)
- **fig_smartboost_pr_curve.png**
  - **路径**: `05_outputs/figures/06_smartboost/fig_smartboost_pr_curve.png`
  - **说明**: PR 曲线图。
  - **是否入正文**: 是
- **fig_smartboost_top5_realized_rate.png**
  - **路径**: `05_outputs/figures/06_smartboost/fig_smartboost_top5_realized_rate.png`
  - **说明**: Top 5% 真实压力发生率图。
  - **是否入正文**: 是
- **fig_smartboost_partial_effects.png**
  - **路径**: `05_outputs/figures/06_smartboost/fig_smartboost_partial_effects.png`
  - **说明**: 部分依赖图。
  - **是否入正文**: 是
- **smartboost_metrics.csv**
  - **路径**: `05_outputs/tables/06_smartboost/smartboost_metrics.csv`
  - **说明**: 核心指标评估表。
  - **是否入正文**: 是

## 5. 稳健性检验 (07_robustness)
- **fig_label_threshold_robustness.png**
  - **路径**: `05_outputs/figures/07_robustness/fig_label_threshold_robustness.png`
  - **说明**: 标签阈值稳健性图。
  - **是否入正文**: 是
- **fig_smartboost_topk_robustness.png**
  - **路径**: `05_outputs/figures/07_robustness/fig_smartboost_topk_robustness.png`
  - **说明**: Top-K 分组稳健性图。
  - **是否入正文**: 是
- **qvar_quantile_robustness.csv** / **qvar_shock_size_robustness.csv**
  - **路径**: `05_outputs/tables/07_robustness/qvar_quantile_robustness.csv`
  - **说明**: QVAR 分位点稳健性数据表，可以用于补充稳健性章节说明。
  - **是否入正文**: 可考虑制表。