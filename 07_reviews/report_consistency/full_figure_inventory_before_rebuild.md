# Full Figure Inventory Before Rebuild

## Scope

- 扫描目录：`05_outputs/figures/` 及全部子目录。
- 扫描到 PNG：32 张。
- 扫描到历史 PDF：16 个。本轮不再输出 PDF，历史 PDF 不作为最终 registry 图。
- 最终重构目标：原模块目录下 PNG，即 `01_data`, `02_lsi`, `04_rgarch`, `05_qvar`, `06_smartboost`。
- `99_paper_ready` 是上一轮派生目录，本轮纳入清点但不作为最终成果目录。

## Inventory

| # | 文件路径 | 图名/用途 | 所属模块 | 当前问题 | 处理方案 | 新增辅助图 | 建议去向 |
|---:|---|---|---|---|---|---|---|
| 1 | `05_outputs/figures/01_data/fig_refined_coverage_heatmap.png` | 股票-月份覆盖率热力图 | diagnostics/data | 可读但排序、刻度和色标仍偏粗；缺少交易所/覆盖率分组辅助信息 | 保留并原位重绘 | 是，新增交易所覆盖率摘要 | 正文 |
| 2 | `05_outputs/figures/02_lsi/fig_refined_lsi_intraday.png` | LSI 日内模式 | MarketLSI/LSI | 需要更清晰的中位数、分位带和关键时点标记；需要阶段对比 | 保留并原位重绘 | 是，新增分阶段日内模式 | 正文 |
| 3 | `05_outputs/figures/02_lsi/fig_refined_market_lsi_timeseries.png` | MarketLSI 时间序列 | MarketLSI/LSI | 时间序列信息较密，需要阶段阴影、滚动均值和峰值标记 | 保留并原位重绘 | 是，新增阶段分布和极端时点图 | 正文 |
| 4 | `05_outputs/figures/04_rgarch/fig_refined_rgarch_risk_evolution.png` | RGARCH 风险与高阶矩综合图 | RGARCH-CARR-SK | 多序列可能拥挤，legend/面板层级需统一 | 保留并原位重绘为三面板 | 否 | 正文/附录 |
| 5 | `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_conditional_risk.png` | 原文框架适配条件风险路径 | RGARCH-CARR-SK | 需要突出条件风险、realized pressure 和训练期阈值；避免过密线 | 保留并原位重绘 | 是，拆出 realized/threshold 对照 | 正文 |
| 6 | `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png` | 动态峰度路径 | RGARCH-CARR-SK | 峰度较稳定时不应强行放大噪声；需注释稳定性 | 保留并原位重绘 | 否 | 正文/附录 |
| 7 | `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_skewness.png` | 动态偏度路径 | RGARCH-CARR-SK | 需更清楚的零线、阶段背景和模型标签 | 保留并原位重绘 | 否 | 正文 |
| 8 | `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png` | realized pressure measures 对比 | RGARCH-CARR-SK | 当前图有解释价值，但需要统一尺度和更论文化布局 | 保留并原位重绘 | 是，新增密度/统计摘要图 | 正文/附录 |
| 9 | `05_outputs/figures/04_rgarch/fig_rgarch_conditional_risk_path.png` | 条件风险路径 | RGARCH-CARR-SK | 与 adapted conditional risk 有重叠，但可作为单独条件风险主线图 | 保留并原位重绘 | 否 | 正文 |
| 10 | `05_outputs/figures/04_rgarch/fig_rgarch_dynamic_skew_kurtosis.png` | 动态偏度与峰度双面板 | RGARCH-CARR-SK | 需要改善面板留白、统一 y 轴含义与 legend 位置 | 保留并原位重绘 | 否 | 正文 |
| 11 | `05_outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png` | QVAR 压力测试情景 | QVAR | 历史问题是只含两类情景；已可基于系数补齐四类，需要论文级 2x2 分面 | 保留并原位重绘 | 是，新增情景对比/损失图 | 正文 |
| 12 | `05_outputs/figures/05_qvar/fig_qvar_tail_quantile_response.png` | QVAR 尾部分位响应 | QVAR | 需更清楚线型、分位点标签、非因果说明；legend 不得遮挡 | 保留并原位重绘 | 是，新增响应衰减与系数热力图 | 正文 |
| 13 | `05_outputs/figures/06_smartboost/fig_refined_partial_effects.png` | 旧 refined Partial Effects | SMARTBoost | 六宫格/多变量布局偏挤；需只保留核心无泄漏变量 | 保留并原位重绘为核心变量图 | 否 | 正文/附录 |
| 14 | `05_outputs/figures/06_smartboost/fig_refined_top5_realized_rate.png` | 旧 refined Top 5% 命中率 | SMARTBoost | 需要 baseline/lift 与 validation/test 分组更清楚 | 保留并原位重绘 | 否 | 正文 |
| 15 | `05_outputs/figures/06_smartboost/fig_smartboost_calibration_curve.png` | Calibration 曲线 | SMARTBoost | 需要 45 度线、分箱点和 horizon/period 简洁区分 | 保留并原位重绘 | 否 | 正文/附录 |
| 16 | `05_outputs/figures/06_smartboost/fig_smartboost_partial_effects.png` | SMARTBoost Partial Effects | SMARTBoost | 需避免拥挤；不得包含 CrossStress | 保留并原位重绘 | 是，可拆出 refined 版本 | 正文/附录 |
| 17 | `05_outputs/figures/06_smartboost/fig_smartboost_pr_curve.png` | 样本外 PR 曲线 | SMARTBoost | 重点图；需加入基准事件率、外置 legend 和 validation/test 口径 | 保留并原位重绘 | 是，新增 period 多面板 | 正文 |
| 18 | `05_outputs/figures/06_smartboost/fig_smartboost_roc_curve.png` | 样本外 ROC 曲线 | SMARTBoost | 附录辅助图；legend 需避开曲线，配 no-skill 线 | 保留并原位重绘 | 否 | 附录 |
| 19 | `05_outputs/figures/06_smartboost/fig_smartboost_top5_realized_rate.png` | Top 5% 真实压力发生率 | SMARTBoost | 需柱上标注、baseline/lift 对照、period/horizon 分组 | 保留并原位重绘 | 是，新增 lift curve 与概率分布 | 正文 |
| 20 | `05_outputs/figures/99_paper_ready/fig_01_coverage_heatmap.png` | 上一轮 paper-ready 覆盖率图 | others/legacy | 派生目录，不符合本轮“原位更新”要求 | 废弃为历史备查，不作为最终成果 | 否 | 删除/备查 |
| 21 | `05_outputs/figures/99_paper_ready/fig_02_lsi_intraday_pattern.png` | 上一轮 paper-ready LSI 日内图 | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 22 | `05_outputs/figures/99_paper_ready/fig_03_market_lsi_time_series.png` | 上一轮 paper-ready MarketLSI 图 | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 23 | `05_outputs/figures/99_paper_ready/fig_04_rgarch_conditional_pressure_risk.png` | 上一轮 paper-ready RGARCH 条件风险 | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 24 | `05_outputs/figures/99_paper_ready/fig_05_rgarch_dynamic_skew_kurtosis.png` | 上一轮 paper-ready 高阶矩 | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 25 | `05_outputs/figures/99_paper_ready/fig_06_rgarch_realized_pressure_measures.png` | 上一轮 paper-ready realized measures | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 26 | `05_outputs/figures/99_paper_ready/fig_07_qvar_tail_quantile_response.png` | 上一轮 paper-ready QVAR 响应 | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 27 | `05_outputs/figures/99_paper_ready/fig_08_qvar_pressure_test_scenarios.png` | 上一轮 paper-ready QVAR 情景 | others/legacy | 旧图只反映两类情景，不可继续使用 | 废弃，不进 registry | 否 | 删除/备查 |
| 28 | `05_outputs/figures/99_paper_ready/fig_09_smartboost_pr_curve.png` | 上一轮 paper-ready PR | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 29 | `05_outputs/figures/99_paper_ready/fig_10_smartboost_roc_curve.png` | 上一轮 paper-ready ROC | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 30 | `05_outputs/figures/99_paper_ready/fig_11_smartboost_calibration_curve.png` | 上一轮 paper-ready Calibration | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 31 | `05_outputs/figures/99_paper_ready/fig_12_smartboost_top5_event_rate.png` | 上一轮 paper-ready Top 5% | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |
| 32 | `05_outputs/figures/99_paper_ready/fig_13_smartboost_partial_effects.png` | 上一轮 paper-ready Partial Effects | others/legacy | 派生目录，不符合本轮要求 | 废弃为历史备查 | 否 | 删除/备查 |

## Summary

- 原模块现有 PNG：19 张。
- `99_paper_ready` 旧派生 PNG：13 张。
- 本轮重构对象：原模块 19 张全部原位覆盖，并在原模块目录新增有解释价值的辅助图。
- 本轮不物理删除历史文件；registry 将只登记本轮原模块 PNG，`99_paper_ready` 全部降级为历史备查。
