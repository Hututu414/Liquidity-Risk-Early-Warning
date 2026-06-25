# Full Figure Rebuild Plan V2

## 1. 总体策略

本轮不是单独美化正文候选图，而是重建当前所有原模块 PNG，并补充有实证解释价值的辅助图。所有最终图只输出 PNG 300dpi，保存回各自模块目录：

- `05_outputs/figures/01_data/`
- `05_outputs/figures/02_lsi/`
- `05_outputs/figures/04_rgarch/`
- `05_outputs/figures/05_qvar/`
- `05_outputs/figures/06_smartboost/`

不向 `99_paper_ready/` 输出任何新图，不输出 PDF。

## 2. 数据/诊断图

| 原图/新增图 | 输入 | 处理方案 | 输出目录 | 去向 |
|---|---|---|---|---|
| `fig_refined_coverage_heatmap.png` | `stage1_model_ready/coverage_by_code_date.csv` | 保留并重绘；按 code 总覆盖率排序，列按月份聚合，色标为有效分钟覆盖率 | `01_data` | 正文 |
| `fig_coverage_by_exchange_summary.png` | 同上 | 新增；按交易所/指数样本做覆盖率箱线或点图 | `01_data` | 附录/数据说明 |

## 3. MarketLSI / LSI 图

| 原图/新增图 | 输入 | 处理方案 | 输出目录 | 去向 |
|---|---|---|---|---|
| `fig_refined_lsi_intraday.png` | `stage2_lsi_labels/lsi_labels_by_code/*.parquet` | 保留并重绘；slot 维度展示均值/中位数和 IQR，标注开盘、午后开盘、尾盘 | `02_lsi` | 正文 |
| `fig_lsi_intraday_by_stage.png` | 同上 | 新增；按监管阶段对比日内 LSI 模式，不作因果解释 | `02_lsi` | 附录/正文备选 |
| `fig_refined_market_lsi_timeseries.png` | `market_context.parquet` | 保留并重绘；日度均值、20日 rolling mean、阶段阴影和峰值标记 | `02_lsi` | 正文 |
| `fig_market_lsi_stage_distribution.png` | `market_context.parquet` | 新增；分阶段 MarketLSI 分布/箱线图 | `02_lsi` | 正文/附录 |
| `fig_market_lsi_extreme_slot_distribution.png` | `market_context.parquet` | 新增；极端压力分钟的日内 slot 分布 | `02_lsi` | 附录 |

## 4. RGARCH-CARR-SK 图

| 原图/新增图 | 输入 | 处理方案 | 输出目录 | 去向 |
|---|---|---|---|---|
| `fig_rgarch_carr_sk_adapted_conditional_risk.png` | `rgarch_carr_sk_adapted_conditional_paths.csv` | 保留并重绘；使用日度路径，突出 `lambda_t`、realized pressure 和训练期阈值 | `04_rgarch` | 正文 |
| `fig_rgarch_conditional_risk_path.png` | 同上 | 保留并重绘为单独条件风险主线图 | `04_rgarch` | 正文 |
| `fig_rgarch_dynamic_skew_kurtosis.png` | 同上 | 保留并重绘为双面板，高阶矩路径共享 x 轴 | `04_rgarch` | 正文 |
| `fig_rgarch_carr_sk_adapted_dynamic_skewness.png` | 同上 | 保留并重绘为动态偏度单图 | `04_rgarch` | 正文 |
| `fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png` | 同上 | 保留并重绘为动态峰度单图；若稳定则注释 | `04_rgarch` | 正文/附录 |
| `fig_rgarch_carr_sk_adapted_realized_measures.png` | `rgarch_carr_sk_adapted_realized_pressure_measures.csv` | 保留并重绘；标准化 log measure 箱线/小提琴，不混用量纲 | `04_rgarch` | 正文/附录 |
| `fig_refined_rgarch_risk_evolution.png` | 条件路径表 | 保留并重绘为风险、偏度、峰度三面板 | `04_rgarch` | 附录 |
| `fig_rgarch_realized_measure_density.png` | realized measures 表 | 新增；展示 RV/RBV/MedRV/RMAD 标准化分布密度 | `04_rgarch` | 附录 |
| `fig_rgarch_oos_loss_comparison.png` | `rgarch_carr_sk_adapted_oos_losses.csv` | 新增；比较不同 realized pressure measure 的样本外损失 | `04_rgarch` | 正文/附录 |

## 5. QVAR 图

| 原图/新增图 | 输入 | 处理方案 | 输出目录 | 去向 |
|---|---|---|---|---|
| `fig_qvar_tail_quantile_response.png` | `qvar_tail_quantile_response.csv` | 保留并重绘；`MarketLSI` shock 下展示 q=0.10/0.50/0.90/0.95 | `05_qvar` | 正文 |
| `fig_qvar_pressure_test_paths.png` | `qvar_pressure_test_paths.csv` | 保留并重绘；四类情景 2x2 分面，q=0.50/q=0.95，legend 在顶部 | `05_qvar` | 正文 |
| `fig_qvar_response_decay.png` | `qvar_tail_quantile_response.csv` | 新增；不同 shock 对 MarketLSI 响应的衰减对比 | `05_qvar` | 附录 |
| `fig_qvar_pinball_loss.png` | `qvar_blocked_oos_pinball_loss.csv` | 新增；validation/test 的 pinball loss 对比 | `05_qvar` | 附录 |
| `fig_qvar_coefficient_heatmap.png` | `qvar_quantile_coefficients_train.csv` | 新增；核心 MarketLSI 方程系数热力图 | `05_qvar` | 附录 |

QVAR 两类情景问题已核查：上游原始脚本只生成两类，非绘图漏读。已通过 `06b_qvar_stress_test.py` 基于既有训练期 QVAR 系数补齐四类标准化情景，不重估模型、不伪造结果。

## 6. SMARTBoost 图

| 原图/新增图 | 输入 | 处理方案 | 输出目录 | 去向 |
|---|---|---|---|---|
| `fig_smartboost_pr_curve.png` | predictions + metrics | 保留并重绘；test PR 曲线，基准事件率线，legend 外置 | `06_smartboost` | 正文 |
| `fig_smartboost_roc_curve.png` | predictions + metrics | 保留并重绘；test ROC 曲线，no-skill 线，legend 外置 | `06_smartboost` | 附录 |
| `fig_smartboost_calibration_curve.png` | calibration table | 保留并重绘；分箱点图与 45 度线，按 horizon/period 简洁区分 | `06_smartboost` | 正文/附录 |
| `fig_smartboost_top5_realized_rate.png` | event rate/lift | 保留并重绘；Top 5% 事件率、baseline、lift 标注 | `06_smartboost` | 正文 |
| `fig_refined_top5_realized_rate.png` | high-risk rates | 保留并重绘；Top 1/5/10/20% 分组命中率 | `06_smartboost` | 附录 |
| `fig_smartboost_partial_effects.png` | partial effects | 保留并重绘；选择局部响应幅度最大的 4 个无泄漏变量 | `06_smartboost` | 正文/附录 |
| `fig_refined_partial_effects.png` | partial effects | 保留并重绘；更宽松的 refined 版本，不含 CrossStress | `06_smartboost` | 附录 |
| `fig_smartboost_pr_roc_by_period.png` | predictions + metrics | 新增；validation/test x PR/ROC 多面板 | `06_smartboost` | 附录 |
| `fig_smartboost_lift_curve.png` | high-risk group rates | 新增；Top 分组 lift 曲线 | `06_smartboost` | 正文/附录 |
| `fig_smartboost_probability_distribution.png` | predictions | 新增；预测概率分布和正例/负例分离 | `06_smartboost` | 附录 |
| `fig_smartboost_regime_metrics.png` | regime metrics | 新增；监管阶段性能对比，作为分段描述，不作因果识别 | `06_smartboost` | 附录 |
| `fig_smartboost_feature_importance.png` | feature importance | 新增；如 importance 全为零则在图注中说明该表不提供有效排序 | `06_smartboost` | 附录 |

SMARTBoost 图全部读取剔除 `CrossStress` 后的新 metadata、prediction manifest、metrics 和 partial effects。若 metadata 或 partial effects 出现 `CrossStress`，重绘脚本将直接报错。

## 7. 旧派生目录处理

`05_outputs/figures/99_paper_ready/` 中 13 张 PNG 和 13 个 PDF 为上一轮派生产物。本轮不更新、不引用、不登记为最终图；其中旧 QVAR 情景图只含两类情景，明确废弃。历史文件不物理删除，以免破坏已有审计链。

## 8. 审计口径

- 审计对象：原模块目录下最终 PNG。
- 关键检查：PNG 存在、300dpi、非空、文件名、registry 登记、SMARTBoost CrossStress 泄漏疑点、legend 人工抽查。
- 不检查 PDF，因为本轮不输出 PDF。
