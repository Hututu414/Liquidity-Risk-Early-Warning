# main_v2_final_integrated 分页与图文排版修复说明

## 修改对象

- TeX：`08_report/latex_project/main_v2_final_integrated.tex`
- PDF：`08_report/latex_project/main_v2_final_integrated.pdf`

本轮仅修复分页、图文邻近性和图表尺寸；未修改模型结果、表格核心数值、参考文献、数据文件或图片文件。

## Needspace 处理

- 删除了正文中所有 `\Needspace{18\baselineskip}`、`\Needspace{20\baselineskip}` 和 `\Needspace{24\baselineskip}`。
- 修复后大号 `Needspace` 数量为 0。
- 仅在少数小节标题前保留 `\Needspace{8\baselineskip}`，用于避免小节标题孤立在页底；全文共 4 处，未出现在图表或表格前。

## 图片宽度调整

正文核心图宽度已下调如下：

- `figures/fig_timeline.png`：`0.72\textwidth`
- `figures/fig_coverage.png`：`0.78\textwidth`
- `figures/fig_intraday.png`：`0.82\textwidth`
- `figures/fig_marketlsi.png`：`0.82\textwidth`
- `figures/fig_rgarch_risk.png`：`0.82\textwidth`
- `figures/fig_rgarch_dynamic_skewness_refined.png`：`0.82\textwidth`
- `figures/fig_qvar_response.png`：`0.78\textwidth`
- `figures/fig_qvar_stress.png`：`0.82\textwidth`
- `figures/fig_sb_pr.png`：`0.78\textwidth`
- `figures/fig_sb_top5.png`：`0.78\textwidth`
- `figures/fig_sb_partial.png`：`0.86\textwidth`
- `figures/fig_robust_label_threshold.png`：`0.82\textwidth`
- `figures/fig_rgarch_realized_measure_distribution_refined.png`：`0.82\textwidth`
- `figures/fig_qvar_tail_response_summary_refined.png`：`0.82\textwidth`
- `figures/fig_robust_sb_topk.png`：`0.82\textwidth`

所有 `\includegraphics` 图片路径与 `main_v2_final.tex` 完全一致，未新增、删除、移动或重画图片。

## FloatBarrier 处理

- 删除了正文中图表后和小段落后的多余 `\FloatBarrier`。
- 当前仅保留 2 处 `\FloatBarrier`：一处在进入附录前，一处在参考文献前。
- 对 `\captionof{figure}` / `\captionof{table}` 非浮动证据块，不再额外使用 `\FloatBarrier`。

## 局部分页处理

- 在第 3 章开头前加入明确分页，使“研究设计与方法”不再被挤在前一页底部。
- 在 4.3、4.4、5.2、6.2、6.3 和 6.4 等小节前加入局部分页，使引出段、图表和解释段作为完整证据块排布。
- 未在图表前使用 18、20 或 24 行的大号 `Needspace`。

## 导言区排版参数

已加入或调整：

- `\raggedbottom`
- `\setlength{\textfloatsep}{8pt plus 2pt minus 2pt}`
- `\setlength{\floatsep}{8pt plus 2pt minus 2pt}`
- `\setlength{\intextsep}{8pt plus 2pt minus 2pt}`
- `\captionsetup{font=small,labelfont=bf,skip=4pt}`
- `\captionsetup[table]{skip=4pt}`

## 图文分离修复结果

- 第 3.1 节表 2 的引出句与表格均位于第 7 页。
- 第 4.3 节图 2 的引出句与图表均位于第 13 页。
- 第 4.4 节图 3 的引出句与图表均位于第 14 页。
- 第 5.2 节 QVAR 的 pinball loss 表、尾部分位响应图、情景表和情景响应图均按“文字—图表—解释”顺序排布，集中在第 18 至第 19 页。
- 第 5.3 节 SMARTBoost 的指标表、PR 图、Top 5% 图、Top-K 表和 Partial Effects 图均按“文字—图表—解释”顺序排布，集中在第 20 至第 22 页。
- 第 6 章稳健性检验中图 13、图 14 和图 15 的引出句与图表均位于同页。
- 未发现修复后仍存在核心图表与对应解释段落明显分离的页面。

## 编译与引用检查

- 编译链：XeLaTeX + BibTeX + XeLaTeX + XeLaTeX。
- PDF 页数：31 页。
- PDF 文本抽取未发现 `图 ??`、`表 ??` 或 `[?]`。
- LaTeX 日志未发现 undefined references、undefined citations 或需要再次 rerun 的交叉引用提示。
- 静态检查未发现重复 label、缺失 ref 或缺失 citation key。
