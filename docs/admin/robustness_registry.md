# 稳健性检验登记表

| 编号 | 模块 | 输出 | 类型 | 正文/附录建议 | 说明 |
|---|---|---|---|---|---|
| R01 | LSI/标签 | `outputs/tables/07_robustness/label_threshold_robustness.csv` | table | 正文 | 标签阈值 85/90/95 稳健性。 |
| R02 | LSI/标签 | `outputs/figures/07_robustness/fig_label_threshold_robustness.png` | figure | 正文 | PR-AUC 与 Top 5% lift 随阈值变化。 |
| R03 | LSI/标签 | `outputs/tables/07_robustness/horizon_robustness.csv` | table | 附录 | H5/H10/H20 标签分布；H20 不作为主模型。 |
| R04 | LSI/标签 | `outputs/tables/07_robustness/missing_minute_threshold_robustness.csv` | table | 附录 | 有效分钟阈值 236/238 样本影响。 |
| R05 | LSI/标签 | `outputs/tables/07_robustness/standardization_robustness.csv` | table | 附录 | 训练期 mean/std 替代标准化对照。 |
| R06 | RGARCH-CARR-SK | `outputs/tables/07_robustness/rgarch_realized_measure_robustness.csv` | table | 正文 | RV/RBV/MedRV/RMAD fit 与 loss。 |
| R07 | RGARCH-CARR-SK | `outputs/figures/07_robustness/fig_rgarch_realized_measure_robustness.png` | figure | 正文/附录 | BIC 与 test R2LOG 对比。 |
| R08 | RGARCH-CARR-SK | `outputs/tables/07_robustness/rgarch_oos_loss_robustness.csv` | table | 正文 | R2LOG/MSE/MAE/QLIKE。 |
| R09 | QVAR | `outputs/tables/07_robustness/qvar_quantile_robustness.csv` | table | 正文 | 分位点与 pinball loss。 |
| R10 | QVAR | `outputs/figures/07_robustness/fig_qvar_quantile_robustness.png` | figure | 正文/附录 | 分位点响应稳健性。 |
| R11 | QVAR | `outputs/tables/07_robustness/qvar_shock_size_robustness.csv` | table | 正文/附录 | ±1.5/±2.0/±2.5 情景冲击。 |
| R12 | QVAR | `outputs/figures/07_robustness/fig_qvar_shock_size_robustness.png` | figure | 正文/附录 | 四情景冲击幅度稳健性。 |
| R13 | SMARTBoost | `outputs/tables/07_robustness/smartboost_time_split_robustness.csv` | table | 正文 | 时间窗口敏感性。 |
| R14 | SMARTBoost | `outputs/tables/07_robustness/smartboost_feature_ablation.csv` | table | 正文/附录 | 固定抽样特征组消融。 |
| R15 | SMARTBoost | `outputs/figures/07_robustness/fig_smartboost_feature_ablation.png` | figure | 正文/附录 | 消融 PR-AUC 对比。 |
| R16 | SMARTBoost | `outputs/tables/07_robustness/smartboost_topk_robustness.csv` | table | 正文 | Top 1/5/10/20% lift。 |
| R17 | SMARTBoost | `outputs/figures/07_robustness/fig_smartboost_topk_robustness.png` | figure | 正文 | Top-K lift。 |
| R18 | SMARTBoost | `outputs/tables/07_robustness/smartboost_calibration_robustness.csv` | table | 附录 | 校准与 Brier。 |
