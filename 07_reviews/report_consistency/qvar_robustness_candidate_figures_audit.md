# QVAR 稳健性候选替代图审计说明

日期：2026-05-22

## 本轮边界

- 本轮仅基于现有 QVAR 输出数据生成候选 PNG 图。
- 未修改论文正文、TeX 文件、PDF 文件、公式、参考文献、既有图片文件或图片路径。
- 未重跑 QVAR 模型，未重画论文已引用图片，未覆盖当前图 14。
- 新增候选绘图脚本：`06_agent_workspaces/codex_workspace/plot_candidate_qvar_robustness_figures.py`。
- 新候选图输出目录：`05_outputs/figures/07_robustness/candidate_qvar_robustness_figures/`。

## 数据来源

- QVAR 情景路径数据：`05_outputs/tables/05_qvar/qvar_pressure_test_paths.csv`
  - 字段包括 `horizon`、`quantile`、`scenario`、`scenario_cn`、`MarketLSI_response`。
  - 覆盖分位点：`q=0.10`、`q=0.50`、`q=0.90`、`q=0.95`。
  - 覆盖预测步长：`h=0` 到 `h=20`。
  - 覆盖情景：市场急跌、波动放大、成交收缩/流动性压力、复合压力。
- QVAR 冲击幅度稳健性数据：`05_outputs/tables/07_robustness/qvar_shock_size_robustness.csv`
  - 字段包括 `quantile`、`shock_size`、`scenario`、`horizon`、`MarketLSI_response`。
  - 覆盖冲击幅度：`1.5`、`2.0`、`2.5` 个标准化单位。

## 候选图清单

| 候选图 | 文件名 | 数据来源 | 统计口径 | 使用分位点 | 说明 |
|---|---|---|---|---|---|
| A | `candidate_a_qvar_fixed_horizon_response.png` | `qvar_pressure_test_paths.csv` | 固定预测步长响应值，分别取 `h=1`、`h=5`、`h=10` 的 `MarketLSI_response` | `q=0.50`、`q=0.95` | 避免使用最大响应，直接比较固定步长下中位数状态与尾部状态的响应差异。 |
| B | `candidate_b_qvar_cumulative_abs_response_h1_h10.png` | `qvar_pressure_test_paths.csv` | 前 10 期累计绝对响应强度，即 `h=1...10` 的 `abs(MarketLSI_response)` 求和 | `q=0.50`、`q=0.95` | 用累计强度替代单点最大响应，适合概括尾部状态下的总体响应强度。 |
| C | `candidate_c_qvar_quantile_extension_h5_response.png` | `qvar_pressure_test_paths.csv` | 固定预测步长 `h=5` 的 `MarketLSI_response` | `q=0.50`、`q=0.90`、`q=0.95` | 加入 `q=0.90`，用于观察尾部分位响应是否随分位点上升呈连续变化。 |
| D | `candidate_d_qvar_shock_size_h10_q095_response.png` | `qvar_shock_size_robustness.csv` | 固定 `q=0.95`、固定预测步长 `h=10`，比较 1.5、2.0、2.5 个标准化单位冲击下的 `MarketLSI_response` | `q=0.95` | 现有数据允许生成；用于检查尾部分位响应是否随冲击幅度有单调变化。 |

## 关键结果读数

- 候选图 A 显示，`q=0.95` 下波动放大和复合压力情景在 `h=5`、`h=10` 的响应明显强于 `q=0.50`；市场急跌情景在三个固定步长下均较弱，尤其 `q=0.95, h=10` 接近 0。
- 候选图 B 使用累计绝对响应强度。`q=0.95` 下复合压力约为 `10.85`，波动放大约为 `8.46`，成交收缩/流动性压力约为 `2.31`；市场急跌仅约为 `0.075`，属于响应较弱情景。
- 候选图 C 在 `h=5` 固定响应下显示，波动放大、成交收缩/流动性压力和复合压力从 `q=0.50` 到 `q=0.90`、`q=0.95` 的响应强度逐步增强；市场急跌在三个分位点下均较弱。
- 候选图 D 显示，在 `q=0.95, h=10` 下，波动放大和复合压力对冲击幅度较敏感，响应随 1.5、2.0、2.5 个标准化单位冲击增强；市场急跌响应接近 0，不建议单独作为正文核心证据。

## 替换图 14 的建议

- 首选候选图 C：它保留了当前图 14 的“分位点差异”主题，同时加入 `q=0.90`，比只比较 `q=0.50` 与 `q=0.95` 更能展示尾部响应的连续性，且使用固定 `h=5` 响应而非最大响应。
- 备选候选图 B：如果正文希望强调“前 10 期总体响应强度”，B 的累计绝对响应口径最稳健、最容易解释，但需要在正文中说明该图刻画的是响应强度而非响应方向。
- 候选图 A 信息最完整，但三联图占用空间更大，适合附录或正文空间允许时使用。
- 候选图 D 适合补充说明冲击幅度稳健性；由于市场急跌情景响应接近 0，不建议作为替换图 14 的首选正文图。

## 文件检查

- `candidate_a_qvar_fixed_horizon_response.png`：3721 x 1574，300 dpi 输出。
- `candidate_b_qvar_cumulative_abs_response_h1_h10.png`：2491 x 1532，300 dpi 输出。
- `candidate_c_qvar_quantile_extension_h5_response.png`：2611 x 1592，300 dpi 输出。
- `candidate_d_qvar_shock_size_h10_q095_response.png`：2611 x 1591，300 dpi 输出。

## 明确未修改项

- 未修改 `08_report/latex_project/*.tex`。
- 未修改 `08_report/latex_project/*.pdf`。
- 未修改 `08_report/latex_project/figures/fig_qvar_tail_response_summary_refined.png`。
- 未修改任何 CSV、Parquet、Excel 或原始数据文件。
- 未修改任何参考文献或论文正文结论。
