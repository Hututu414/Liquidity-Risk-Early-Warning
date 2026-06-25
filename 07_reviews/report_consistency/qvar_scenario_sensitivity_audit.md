# QVAR 情景设定敏感性分析审计报告

日期：2026-05-22

## 本轮边界

- 本轮只生成候选结果、候选图和审计报告。
- 未修改论文正文、TeX 文件、PDF 文件、现有论文图片或参考文献。
- 未重新估计 QVAR；所有响应均基于既有训练期 QVAR 系数表递推生成。
- 未人为改变响应符号，也未按结果好坏筛选情景设定。

## 使用的数据文件和脚本

- QVAR 系数：`05_outputs/tables/05_qvar/qvar_quantile_coefficients_train.csv`
- 原始情景路径：`05_outputs/tables/05_qvar/qvar_pressure_test_paths.csv`
- 训练期标准化参数：`05_outputs/tables/05_qvar/qvar_train_standardization_stats.csv`
- 原始情景定义：`05_outputs/tables/05_qvar/qvar_pressure_test_scenario_definitions.csv`
- 本轮新增脚本：`06_agent_workspaces/codex_workspace/qvar_scenario_sensitivity_analysis.py`
- 网格路径输出：`05_outputs/tables/07_robustness/qvar_scenario_sensitivity/qvar_scenario_sensitivity_paths.csv`
- 网格统计输出：`05_outputs/tables/07_robustness/qvar_scenario_sensitivity/qvar_scenario_sensitivity_summary.csv`
- 响应方向表：`05_outputs/tables/07_robustness/qvar_scenario_sensitivity/qvar_scenario_direction_stability.csv`

## QVAR 响应审计

1. 情景冲击方向符合变量定义：市场急跌使用 `IndexRet` 下降；波动放大使用 `IndexRV` 上升；成交收缩/流动性压力使用 `MarketRelAmt` 下降；复合压力同时使用收益下降、波动上升和成交承接下降。
2. `MarketLSI_response` 处于训练期标准化空间。QVAR 估计输入为 `z_MarketLSI` 等标准化变量，情景冲击幅度表示标准化单位。训练期 `MarketLSI` 标准差为 `2.788926`。
3. 响应递推为一次性初始冲击。脚本只在 `h=0` 改变初始状态，此后按 `state = intercept + A @ state` 递推，不在后续 horizon 持续追加冲击。
4. 原始图和本轮网格在 `2.0` 个标准差设定下可以复现原始路径数据。对本轮网格使用的 `q=0.50/q=0.90/q=0.95` 与 `qvar_pressure_test_paths.csv` 比较，最大绝对差为 `4.441e-16`。
5. 未发现变量方向处理或响应递推的程序性错误。`q=0.95` 下负响应主要来自既有系数递推，而不是符号写反。

### MarketLSI 方程关键系数

| regressor    |         0.5 |         0.9 |       0.95 |
|:-------------|------------:|------------:|-----------:|
| CrossStress  |  0.0945749  |  0.17913    |  0.225213  |
| IndexRV      | -0.0103916  | -0.0113288  | -0.0287496 |
| IndexRet     |  0.00699181 |  0.00833455 |  0.0079277 |
| MarketLSI    |  0.87095    |  0.858025   |  0.853905  |
| MarketRelAmt | -0.00106396 |  0.0188867  |  0.0291479 |
| const        | -0.00410893 |  0.143918   |  0.203189  |

从系数看，`q=0.95` 的 `MarketLSI` 方程中 `IndexRet` 和 `MarketRelAmt` 系数为正，因此负向收益冲击或成交承接下降会给出负向一阶响应；`IndexRV` 系数为负，因此波动上升也会给出负向一阶响应。后续递推会沿系统矩阵继续放大或衰减该方向。

## 预先定义的情景网格

- 冲击幅度：`1.0`、`1.5`、`2.0` 个标准化单位。
- 分位点：`q=0.50`、`q=0.90`、`q=0.95`。
- 响应统计口径：固定 `h=5` 带符号响应、固定 `h=10` 带符号响应、前 10 期累计带符号响应、前 10 期累计绝对响应强度。
- 四类情景全部保留：市场急跌、波动放大、成交收缩/流动性压力、复合压力。

## 候选图和统计口径

| 图 | 文件 | 统计口径 | 用途判断 |
|---|---|---|---|
| 1 | `05_outputs/figures/07_robustness/qvar_scenario_sensitivity/qvar_sensitivity_shock_size_cum_abs_q095.png` | `q=0.95`，比较 1.0/1.5/2.0 个标准化冲击的前 10 期累计绝对响应强度 | 用于判断结论是否对冲击幅度敏感。 |
| 2 | `05_outputs/figures/07_robustness/qvar_scenario_sensitivity/qvar_sensitivity_quantile_cum_abs_shock2.png` | 当前 2.0 个标准化冲击下，比较 `q=0.50/q=0.90/q=0.95` 的前 10 期累计绝对响应强度 | 最适合展示尾部分位联动强度的连续性。 |
| 3 | `05_outputs/figures/07_robustness/qvar_scenario_sensitivity/qvar_sensitivity_fixed_horizon_signed_direction.png` | 当前 2.0 个标准化冲击下，比较 `h=5` 与 `h=10` 的带符号响应方向 | 用于说明方向解释存在不稳定性。 |
| 4 | `05_outputs/figures/07_robustness/qvar_scenario_sensitivity/qvar_sensitivity_direction_stability_heatmap.png` | 当前 2.0 个标准化冲击下，`h=1...10` 的响应方向热力图 | 用于审计正负方向是否跨 horizon 稳定。 |

## 主要结果

- 在 `q=0.95`、2.0 个标准化冲击下，前 10 期累计绝对响应强度依次为：市场急跌 `0.0751`，波动放大 `8.4638`，成交收缩/流动性压力 `2.3083`，复合压力 `10.8473`。
- 响应方向表中，当前 2.0 标准化冲击、`q=0.50/0.90/0.95`、`h=1...10` 的格点里，负响应占比约 `91.7%`，正响应占比约 `8.3%`。
- 按 `h=1...10` 统计，带符号方向在同一情景-分位点组合内发生正负切换的组合数为 `0`；在 `h=5/h=10` 固定口径下，跨分位点出现正负方向不一致的情景-口径组合数为 `2`。
- 因此，当前问题主要不是 horizon 内频繁变号，而是尾部分位下的带符号响应方向与“压力情景必然提高 MarketLSI”的强压力测试叙事不一致。
- 市场急跌情景在多数口径下响应较弱；波动放大和复合压力在尾部分位下的累计绝对响应强度更突出。

## 哪些结果不建议进入正文

- 不建议使用单一最大响应值作为正文核心图，因为该口径依赖极值，容易放大递推路径中的局部峰值。
- 不建议把带符号响应解释为“压力必然上升”。当前 QVAR 系数下，多个压力情景在 `q=0.95` 给出负向 `MarketLSI` 响应，若强行解读为正向压力测试会与估计结果冲突。
- 候选图 3 和图 4 适合作为审计或附录依据，但若正文篇幅有限，不适合作为唯一主图，因为它们会把重点放在方向不稳定性上。

## 第 6.3 节替代图建议

- 最推荐图 2：`qvar_sensitivity_quantile_cum_abs_shock2.png`。它使用前 10 期累计绝对响应强度，不依赖单个极值；同时保留 `q=0.50/q=0.90/q=0.95`，可展示尾部分位条件联动强度是否具有连续性。
- 如果正文需要强调冲击设定稳健性，可将图 1 作为附录或补充图。
- 若所有带符号响应都难以解释，正文应明确使用“累计绝对响应强度”而不是“正向响应”，并将 QVAR 表述为“尾部分位条件联动”而非“强因果压力测试”。

## 明确未修改项

- 未修改任何 `08_report/latex_project/*.tex` 文件。
- 未修改任何 `08_report/latex_project/*.pdf` 文件。
- 未替换或覆盖现有图 14。
- 未修改模型估计结果、原始数据、参考文献或论文正文结论。
