# Codex Handoff: SMARTBoost Forecasting

## 读取的文件

- `README.md`
- `AGENTS.md`
- `CODEX.md`
- `00_admin/project_spec.md`
- `06_agent_workspaces/codex_workspace/handoff_core_models.md`
- `07_reviews/model_audit/smartboost_verification.md`
- `07_reviews/model_audit/rgarch_carr_sk_model_note.md`
- `07_reviews/model_audit/qvar_model_note.md`
- `07_reviews/leakage_audit/core_model_no_lookahead_audit.md`
- `prompts/codex_01_core_pipeline_and_models.md`
- `.agents/skills/smartboost-verification/SKILL.md`
- `.agents/skills/no-lookahead-validation/SKILL.md`

## 本轮代码变更

- 新增：`04_code/src/models/07b_smartboost_verification_gate.py`
- 新增：`04_code/src/models/07_smartboost_forecasting.py`
- 新增：`04_code/src/models/07c_smartboost_deep_audit.py`
- 更新：`00_admin/model_registry.md`
- 更新：`08_report/report_fragments/chapter_08_smartboost.md`
- 生成：`07_reviews/model_audit/smartboost_model_note.md`
- 生成：`07_reviews/model_audit/smartboost_verification_gate.md`
- 生成：`07_reviews/leakage_audit/smartboost_no_lookahead_audit.md`
- 生成：`07_reviews/leakage_audit/smartboost_feature_leakage_deep_audit.md`

未修改 RGARCH-CARR-SK 和 QVAR 结果，未重跑 stage0-stage3，未触碰 `02_data_inbox/preprocessed/`。

## 核验结论

SMARTBoost 核验通过。已有文件 `07_reviews/model_audit/smartboost_verification.md` 覆盖：

- 原文：Paolo Giordani, `SMARTboost Learning for Tabular Data`, Journal of Financial Econometrics, Volume 23, Issue 3, 2025, nbae028；
- DOI：https://doi.org/10.1093/jjfinec/nbae028；
- 算法定义：boosting of symmetric smooth additive regression trees；
- 基学习器：symmetric smooth trees；
- 损失函数说明：原文聚焦 Gaussian likelihood / squared loss，作者 Julia README 写明 `loss [:L2]`；
- 调参方式：CV 或验证集早停；时间序列/面板数据不能随机 CV；
- 作者代码：https://github.com/PaoloGiordani/SMARTboost.jl。

本轮没有生成 `SMARTBOOST_VERIFICATION_BLOCKER.md`。

## 实现口径

本轮结果不是直接运行作者 Julia `SMARTboost.jl`，而是 **基于原文算法定义的 Python 适配实现**。Python 适配使用正则化 shallow additive tree boosting 做二元压力事件概率预警。

目标变量仅为：

- `Stress_H5`
- `Stress_H10`

SMARTBoost 是本文唯一正式机器学习预警模型，不是收益率预测模型。

## 特征

特征包括：

- 个股自身窗口特征：lag LSI、rolling mean/max LSI、ILLIQ/Range/RV/RelAmt 的 5/10/20 分钟窗口、过去 5/10/20 分钟收益累计、开盘以来累计收益、开盘以来累计成交额 log；
- 市场状态特征：`MarketLSI`、`IndexRet`、`IndexRV`、`MarketRelAmt`；
- 日内时点特征：`slot`、slot sin/cos、开盘 10 分钟、午后开盘 10 分钟、尾盘 10 分钟；
- 监管阶段特征：三个日期区间哑变量。

没有使用 `future_max_LSI_5_H5` 或 `future_max_LSI_5_H10` 作为特征。后续深度复核确认旧版 `CrossStress` 来自未来压力标签的横截面聚合，已从 SMARTBoost 特征、训练、预测和 partial effects 中剔除，并已重跑全部样本外预测。

## 时间切分和训练

- 训练期：2023-05-15 至 2025-02-28；
- 验证期：2025-03-03 至 2025-09-26；
- 测试期：2025-09-29 至 2026-05-13。

验证期预测使用训练期模型；测试期预测使用训练期加验证期模型。训练样本为了控制大面板计算成本，使用确定性系统抽样并做类别平衡；没有随机划分 train/validation/test。

最优 boosting iteration：

- H5：180
- H10：180

两者都达到本轮搜索上限，后续如做稳健性可扩展 iteration 网格。

## 输出表格

- `05_outputs/tables/06_smartboost/smartboost_metrics.csv`
- `05_outputs/tables/06_smartboost/smartboost_regime_metrics.csv`
- `05_outputs/tables/06_smartboost/smartboost_calibration_table.csv`
- `05_outputs/tables/06_smartboost/smartboost_high_risk_group_rates.csv`
- `05_outputs/tables/06_smartboost/smartboost_event_rate_and_lift.csv`
- `05_outputs/tables/06_smartboost/smartboost_prediction_integrity_check.csv`
- `05_outputs/tables/06_smartboost/smartboost_iteration_selection.csv`
- `05_outputs/tables/06_smartboost/smartboost_best_iterations.csv`
- `05_outputs/tables/06_smartboost/smartboost_training_sample_summary.csv`
- `05_outputs/tables/06_smartboost/smartboost_partial_effects.csv`
- `05_outputs/tables/06_smartboost/smartboost_model_metadata.json`
- `05_outputs/tables/06_smartboost/smartboost_prediction_manifest.csv`
- `05_outputs/tables/06_smartboost/predictions_by_code/*.parquet`

预测 shard：

- 文件数：80
- 行数：26,229,964
- 大小约：340.8 MB

每行包含 `code`, `datetime`, `slot`, `horizon`, `period`, `reg_stage`, `y_true`, `predicted_probability`, `model_source`。

## 输出图像

- `05_outputs/figures/06_smartboost/fig_smartboost_pr_curve.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_roc_curve.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_calibration_curve.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_top5_realized_rate.png`
- `05_outputs/figures/06_smartboost/fig_smartboost_partial_effects.png`

## 样本外指标

| horizon | period | PR-AUC | ROC-AUC | Recall@Top5% | Precision@Top5% | Brier |
|---|---:|---:|---:|---:|---:|---:|
| H5 | validation | 0.589263 | 0.929633 | 0.550103 | 0.556276 | 0.040321 |
| H5 | test | 0.603484 | 0.930469 | 0.544908 | 0.593026 | 0.038087 |
| H10 | validation | 0.528243 | 0.901018 | 0.492971 | 0.520240 | 0.043390 |
| H10 | test | 0.544503 | 0.909100 | 0.486017 | 0.564155 | 0.043546 |

Top 5% 高风险分钟真实压力发生率：

- H5 validation：0.556276，lift=11.002
- H5 test：0.593026，lift=10.898
- H10 validation：0.520240，lift=9.859
- H10 test：0.564155，lift=9.720

## 防泄漏审计

审计文件：

- `07_reviews/leakage_audit/smartboost_no_lookahead_audit.md`
- `07_reviews/leakage_audit/smartboost_feature_leakage_deep_audit.md`

状态：PASS。旧版 `CrossStress` 泄漏已确认并修正；当前可进入正文的是剔除 `CrossStress` 后的重跑结果。

要点：

- 特征只用 t 时点及过去信息；
- 标签来自 stage2 的未来窗口标签；
- LSI 与组件标准化沿用 stage2 训练期 code-slot median/MAD；SMARTBoost 阶段未额外拟合全样本标准化器；
- 标签阈值来自训练期；
- 模型选择使用验证期，不使用测试期调参；
- 监管阶段变量只由日期区间决定；
- 没有随机打乱时间切分。

## 下一步建议 Gemini

- 在报告中将 SMARTBoost 写成“样本外预警模型”，不要写成收益率预测。
- 强调 PR-AUC、Top 5% 真实压力发生率和校准图，不只看 ROC-AUC。
- 如实说明 Python 适配实现，不写成直接运行作者 Julia 包。

## 下一步建议 DeepSeek v4

- 检查报告中 SMARTBoost 是否被误写为 XGBoost、一般 GBDT 或收益率预测。
- 检查所有数值是否来自 `05_outputs/tables/06_smartboost/`。
- 检查 `predictions_by_code` 是否满足每个 `code-datetime-horizon` 保存概率的要求。
- 检查监管阶段解释是否避免因果识别表述。
