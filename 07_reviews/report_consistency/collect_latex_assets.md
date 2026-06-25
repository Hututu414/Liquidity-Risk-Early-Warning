# collect_latex_assets

- Project root: `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only`
- Python expected by project: `D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe`
- TeX files scanned: 20
- Referenced figures: 17
- Figure files under `figures/`: 28
- Unused figure files: 11
- Referenced table inputs: 11
- Table `.tex` files under `tables/`: 11
- Unused table files: 0

## figure_table_map Draft

| type | source tex | line | label | assets | caption draft |
|---|---|---:|---|---|---|
| figure | `08_report/latex_project/sections/04_data_descriptive.tex` | 11 | `fig:timeline` | `figures/fig_timeline.png` | 训练、验证与测试样本划分。图中按照时间顺序展示本文样本外检验的三个区间，其中训练期用于标准化参数、标签阈值和模型参数估计，验证期用于模型选择，测试期仅用于最终样本外评价。 |
| figure | `08_report/latex_project/sections/04_data_descriptive.tex` | 30 | `fig:coverage` | `figures/fig_coverage.png` | 股票-月份有效分钟覆盖率热力图。颜色表示对应股票在对应月份的有效分钟覆盖程度，用于检验分钟面板在横截面和时间维度上的连续性。 |
| figure | `08_report/latex_project/sections/04_data_descriptive.tex` | 43 | `fig:intraday` | `figures/fig_intraday.png` | LSI\_5 日内模式。图中保留 LSI 术语，并使用分位带展示横截面与日期维度下的离散程度。 |
| figure | `08_report/latex_project/sections/04_data_descriptive.tex` | 56 | `fig:marketlsi` | `figures/fig_marketlsi.png` | 市场压力指数（MarketLSI）日度时间序列。背景区间对应训练、验证与测试样本划分，峰值标记用于辅助识别高压力时段。 |
| figure | `08_report/latex_project/sections/05_empirical_results.tex` | 9 | `fig:rgarch-risk` | `figures/fig_rgarch_risk.png` | RGARCH-CARR-SK 条件压力风险路径。该图用于刻画 MarketLSI 压力风险的阶段性聚集，而非收益率波动预测。 |
| figure | `08_report/latex_project/sections/05_empirical_results.tex` | 44 | `fig:qvar-response` | `figures/fig_qvar_response.png` | QVAR 尾部分位响应。横轴为预测步长，曲线展示不同分位点下 MarketLSI 的条件响应路径；该结果反映尾部分位联动而非严格因果识别。 |
| figure | `08_report/latex_project/sections/05_empirical_results.tex` | 61 | `fig:qvar-stress` | `figures/fig_qvar_stress.png` | QVAR 四类压力测试情景。情景设定基于标准化变量，用于刻画不同市场状态恶化时 MarketLSI 的响应路径。 |
| figure | `08_report/latex_project/sections/05_empirical_results.tex` | 86 | `fig:sb-pr` | `figures/fig_sb_pr.png` | SMARTBoost 样本外 PR 曲线。水平基准线表示对应样本的事件发生率，曲线越高说明模型越能在高风险排序中集中识别未来压力事件。 |
| figure | `08_report/latex_project/sections/05_empirical_results.tex` | 97 | `fig:sb-top5` | `figures/fig_sb_top5.png` | SMARTBoost Top 5\% 高风险组真实压力发生率。柱状图展示 validation/test 与 H5/H10 组合下的高风险组命中表现，并与基准事件率对照。 |
| figure | `08_report/latex_project/sections/05_empirical_results.tex` | 114 | `fig:sb-partial` | `figures/fig_sb_partial.png` | SMARTBoost 核心变量 Partial Effects。横轴使用“中文说明 + 英文变量名”的形式，纵轴表示预测概率的局部响应。 |
| figure | `08_report/latex_project/sections/06_robustness.tex` | 9 | `fig:robust-label` | `figures/fig_robust_label_threshold.png` | 标签阈值变化下的 SMARTBoost 样本外预警表现。图中比较不同训练期分位阈值下的事件率、PR-AUC 与高风险组 lift。 |
| figure | `08_report/latex_project/sections/06_robustness.tex` | 24 | `fig:rgarch-realized-dist` | `figures/fig_rgarch_realized_measure_distribution_refined.png` | Realized pressure measures 标准化分布对比。图中比较 RV、RBV、MedRV 与 RMAD 的分布形态差异。 |
| figure | `08_report/latex_project/sections/06_robustness.tex` | 37 | `fig:qvar-tail-summary` | `figures/fig_qvar_tail_response_summary_refined.png` | 不同分位点下压力情景的最大响应差异。图中比较 \(q=0.50\) 中位数状态与 \(q=0.95\) 尾部状态下的响应强度。 |
| figure | `08_report/latex_project/sections/06_robustness.tex` | 52 | `fig:robust-topk` | `figures/fig_robust_sb_topk.png` | 不同高风险分组下的真实压力发生率与 lift。图中考察 Top-K 分组扩展对预警集中度的影响。 |
| figure | `08_report/latex_project/sections/appendix_figures.tex` | 7 | `fig:app-event-rate` | `figures/fig_event_rate.png` | H5/H10 压力事件率时间变化。该图用于补充说明压力事件在训练、验证和测试阶段的时变性。 |
| figure | `08_report/latex_project/sections/appendix_figures.tex` | 16 | `fig:app-corr` | `figures/fig_corr.png` | 核心市场状态变量相关性热力图。相关结构仅用于描述变量共动，不构成因果识别。 |
| figure | `08_report/latex_project/sections/appendix_figures.tex` | 29 | `fig:app-sb-calibration` | `figures/fig_sb_calibration.png` | SMARTBoost 样本外校准曲线。该图作为 Brier 指标的视觉补充，不替代 PR-AUC 和高风险组命中率证据。 |

## Unused Figures

- `08_report/latex_project/figures/.gitkeep`
- `08_report/latex_project/figures/fig_descriptive_01_sample_coverage_heatmap.png`
- `08_report/latex_project/figures/fig_distribution.png`
- `08_report/latex_project/figures/fig_qvar_pinball.png`
- `08_report/latex_project/figures/fig_rgarch_dynamic_skew_kurtosis_refined.png`
- `08_report/latex_project/figures/fig_rgarch_loss.png`
- `08_report/latex_project/figures/fig_rgarch_realized.png`
- `08_report/latex_project/figures/fig_rgarch_skew_kurt.png`
- `08_report/latex_project/figures/fig_robust_qvar_shock.png`
- `08_report/latex_project/figures/fig_robust_rgarch_measure.png`
- `08_report/latex_project/figures/fig_robust_sb_ablation.png`

## Unused Table Files

- None detected.

## Note

This script only reports asset usage. It does not delete, move, or rewrite any file.
