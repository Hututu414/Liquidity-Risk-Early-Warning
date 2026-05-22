# Codex Visual Final Audit

## 1. Skill 使用情况

- 已显式读取并使用 `.agents/skills/academic-finance-visualization-cn/SKILL.md`。
- 已读取并复用 `.agents/skills/academic-finance-visualization-cn/scripts/finance_paper_style.py`。
- 已读取并运行 `.agents/skills/academic-finance-visualization-cn/scripts/figure_audit.py`。
- `04_code/src/visualization/rebuild_paper_figures.py` 通过 `importlib` 显式加载 skill style helper，不使用默认 matplotlib 风格。

## 2. 应用的 skill 规则

- 所有 paper-ready 图输出 PNG 300dpi 与 PDF。
- 使用克制的论文风格、白底、 muted palette、轻量网格和统一 legend。
- 保留 `RGARCH-CARR-SK`、`QVAR`、`SMARTBoost`、`MarketLSI`、`PR-AUC`、`ROC-AUC`、`Top 5%`、`Partial Effects` 等英文术语。
- 对长时间序列做日度或周度聚合，避免分钟级“黑墙”。
- SMARTBoost 图只使用剔除 `CrossStress` 后的新结果。
- 未重新引入 `CrossStress` 作为 SMARTBoost 特征。

## 3. 成功生成的 paper-ready 图

输出目录：`05_outputs/figures/99_paper_ready/`

| 图号 | 文件前缀 | 标题 | 建议去向 |
|---|---|---|---|
| F01 | `fig_01_coverage_heatmap` | 股票-月份有效分钟覆盖率 | 正文 |
| F02 | `fig_02_lsi_intraday_pattern` | LSI 日内模式 | 正文 |
| F03 | `fig_03_market_lsi_time_series` | 市场压力指数（MarketLSI）时间序列 | 正文 |
| F04 | `fig_04_rgarch_conditional_pressure_risk` | RGARCH-CARR-SK 条件压力风险路径 | 正文 |
| F05 | `fig_05_rgarch_dynamic_skew_kurtosis` | RGARCH-CARR-SK 动态偏度与动态峰度 | 正文 |
| F06 | `fig_06_rgarch_realized_pressure_measures` | realized pressure measures 对比 | 正文/附录 |
| F07 | `fig_07_qvar_tail_quantile_response` | QVAR 尾部分位响应 | 正文 |
| F08 | `fig_08_qvar_pressure_test_scenarios` | QVAR 压力测试情景 | 正文，但需注明现有表只含两类情景 |
| F09 | `fig_09_smartboost_pr_curve` | SMARTBoost 样本外 PR 曲线 | 正文 |
| F10 | `fig_10_smartboost_roc_curve` | SMARTBoost 样本外 ROC 曲线 | 附录 |
| F11 | `fig_11_smartboost_calibration_curve` | SMARTBoost Calibration 曲线 | 正文/附录 |
| F12 | `fig_12_smartboost_top5_event_rate` | SMARTBoost Top 5% 高风险组真实压力发生率 | 正文 |
| F13 | `fig_13_smartboost_partial_effects` | SMARTBoost Partial Effects | 正文/附录 |

## 4. 废弃或降级旧图

- 旧 `figure_registry.md` 中的 `CrossStress 时间序列` 不再作为正文候选图。原因：`CrossStress` 是未来标签聚合比例，不能作为 SMARTBoost 预测证据。
- 原目录下 `05_outputs/figures/04_rgarch/`、`05_outputs/figures/05_qvar/`、`05_outputs/figures/06_smartboost/` 的旧图保留为模型原始输出或备查图，不作为本轮 paper-ready 正文图直接使用。
- 旧 SMARTBoost 图若无法确认来自剔除 `CrossStress` 后的预测结果，不得进入正文。

## 5. CrossStress 泄漏复核

- `smartboost_model_metadata.json` 的 `feature_columns` 不包含 `CrossStress`。
- `smartboost_partial_effects.csv` 不包含 `CrossStress`。
- paper-ready SMARTBoost 图均标记 `uses_current_smartboost=yes`、`contains_crossstress=no`。
- `figure_audit.py` 未发现 CrossStress 泄漏疑点。

## 6. 图表审计结果

审计输出：`07_reviews/report_consistency/codex_visual_figure_audit.csv`

- 审计图数：13。
- PASS：13。
- FAIL：0。
- PNG 300dpi：全部通过。
- PDF 对应版本：全部存在。
- 文件名规范：全部通过。
- 空图疑点：无。
- CrossStress 泄漏疑点：无。

## 7. 需要人工检查或后续确认

- F08 QVAR 压力测试：当前 `qvar_pressure_test_paths.csv` 只提供 `volatility_negative_return` 与 `liquidity_pressure` 两类情景，没有四类完整情景拆分；本轮未伪造缺失情景。
- F01 覆盖率热力图行数较多，建议用户确认论文版面是否接受当前高度；必要时可按行业或覆盖率分组压缩。
- F13 Partial Effects 建议用户确认 4 个变量是否符合论文解释重点；当前未包含 `CrossStress`。
- 所有图仍需人工视觉终审，重点看中文字体、图例位置和版面压缩后的可读性。

## 8. 本轮未做事项

- 未重跑 stage0-stage3。
- 未修改 RGARCH-CARR-SK、QVAR、SMARTBoost 模型定义。
- 未重新引入 `CrossStress`。
- 未使用旧版含 `CrossStress` 泄漏特征的 SMARTBoost 指标。
- 未进入 LaTeX 编译。
- 未生成最终提交包。
