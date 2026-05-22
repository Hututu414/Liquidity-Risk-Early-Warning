# 稳健性检验最终报告

## 完成范围

- LSI 与标签构造：阈值、窗口、缺分钟阈值、替代标准化。
- RGARCH-CARR-SK：realized pressure measure、样本外损失、高阶矩诊断。
- QVAR：分位点、情景冲击幅度、解释边界。
- SMARTBoost：无泄漏复核、时间窗口、特征组消融、Top-K 排序、校准。

## 输出表格

- `05_outputs/tables/07_robustness/horizon_robustness.csv`
- `05_outputs/tables/07_robustness/label_threshold_robustness.csv`
- `05_outputs/tables/07_robustness/missing_minute_threshold_robustness.csv`
- `05_outputs/tables/07_robustness/qvar_quantile_robustness.csv`
- `05_outputs/tables/07_robustness/qvar_shock_size_robustness.csv`
- `05_outputs/tables/07_robustness/rgarch_oos_loss_robustness.csv`
- `05_outputs/tables/07_robustness/rgarch_realized_measure_robustness.csv`
- `05_outputs/tables/07_robustness/smartboost_calibration_robustness.csv`
- `05_outputs/tables/07_robustness/smartboost_feature_ablation.csv`
- `05_outputs/tables/07_robustness/smartboost_time_split_robustness.csv`
- `05_outputs/tables/07_robustness/smartboost_topk_robustness.csv`
- `05_outputs/tables/07_robustness/standardization_robustness.csv`

## 输出图像

- `05_outputs/figures/07_robustness/fig_label_threshold_robustness.png`
- `05_outputs/figures/07_robustness/fig_qvar_quantile_robustness.png`
- `05_outputs/figures/07_robustness/fig_qvar_shock_size_robustness.png`
- `05_outputs/figures/07_robustness/fig_rgarch_realized_measure_robustness.png`
- `05_outputs/figures/07_robustness/fig_smartboost_feature_ablation.png`
- `05_outputs/figures/07_robustness/fig_smartboost_topk_robustness.png`

## 限制说明

- H20 仅作为标签分布延伸检验，本轮不新增 H20 正式预警模型。
- 缺分钟阈值 238 仅基于 code-date 覆盖统计评估样本影响，未重跑 stage1-stage3。
- SMARTBoost 特征组消融采用固定系统抽样轻量复核，不能替代已保存的全量主结果。
- QVAR 情景冲击是统计模拟，不是严格因果识别。
