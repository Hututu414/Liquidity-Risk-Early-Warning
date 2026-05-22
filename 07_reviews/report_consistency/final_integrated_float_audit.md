# main_v2_final_integrated 图文证据块审计

## 处理范围

- 输入 TeX：`08_report/latex_project/main_v2_final.tex`
- 输出 TeX：`08_report/latex_project/main_v2_final_integrated.tex`
- 输出 PDF：`08_report/latex_project/main_v2_final_integrated.pdf`
- 参考文献：`08_report/latex_project/refs.bib`

本轮仅调整正文核心图表的排版位置与断页控制，未修改数据文件、图片文件、参考文献文件、模型设定或表格核心数值。

## 非浮动证据块转换

已将正文第 3 至第 6 章的核心图表由浮动体改为 `\captionof` 非浮动证据块，并在关键引出段前使用 `\Needspace` 控制“引出文字—图表—解释文字”的邻近关系。导言区已加入 `\usepackage{needspace}`。

转换为非浮动证据块的正文图包括：

- `fig:timeline`
- `fig:coverage`
- `fig:intraday`
- `fig:marketlsi`
- `fig:rgarch-risk`
- `fig:rgarch_dynamic_skewness`
- `fig:qvar-response`
- `fig:qvar-stress`
- `fig:sb-pr`
- `fig:sb-top5`
- `fig:sb-partial`
- `fig:robust-label`
- `fig:rgarch-realized-dist`
- `fig:qvar-tail-summary`
- `fig:robust-topk`

转换为非浮动证据块的正文表包括：

- `tab:literature-map`
- `tab:model-framework`
- `tab:sample-cleaning`
- `tab:variables`
- `tab:label-distribution`
- `tab:rgarch-fit`
- `tab:rgarch-loss`
- `tab:qvar-pinball`
- `tab:qvar-scenarios`
- `tab:smartboost-metrics`
- `tab:smartboost-topk`
- `tab:smartboost-leakage`
- `tab:robustness-design`
- `tab:robustness-conclusions`

附录中的 3 个附录图仍保留为附录浮动体，未插入正文结论部分。

## 图表位置调整

- 第 3.1 节中，`tab:model-framework` 已紧跟“如表 \ref{tab:model-framework} 所示”所在引出句之后；PDF 文本抽取显示第 3.1 标题、引出句、表题“研究框架、技术实现与解释边界”均位于第 6 页。
- 第 4 章中，样本结构、样本时间轴、覆盖率热力图、LSI 日内模式图、MarketLSI 时间序列图与压力标签分布表均放回各自第一次解释位置附近。
- 第 5.1 节中，条件压力风险路径图、动态偏度图、拟合准则表和样本外损失表均采用“引出段—图表—解释段”的顺序；动态峰度图未作为正文核心图展示。
- 第 5.2 节中，QVAR 部分按“pinball loss 表—解释—尾部分位响应图—解释—压力情景表—解释—四类情景响应图—解释”重排。PDF 文本抽取显示相关表图依次出现在第 20 至第 22 页，没有集中漂移到后续小节。
- 第 5.3 节中，SMARTBoost 部分按“预警指标表—解释—PR 曲线—解释—Top 5% 图—解释—Top-K 表—解释—Partial Effects 图—解释”重排。PDF 文本抽取显示相关表图依次出现在第 23 至第 27 页。
- 第 6 章中，标签阈值、realized pressure measure、QVAR 分位点、Top-K 与特征边界核查均按“检验目的—图表/表格—结论解释”组织，未发现稳健性图表在小节末尾集中堆叠。

## 对应解释检查

- 未发现正文核心图片缺少对应解释段。
- 未发现新增的结果解释段缺少对应图表或表格支撑；综合性结论段落均引用前文证据。
- 未新增图片路径，未移动图片文件，未修改图片文件本身。
- `main_v2_final.tex` 与 `main_v2_final_integrated.tex` 的 `\includegraphics` 路径列表完全一致，共 18 个路径。

## 交叉引用与编译检查

- 正文部分残留 `figure` 浮动体数量：0。
- 正文部分残留 `table` 浮动体数量：0。
- 正文 `\captionof{figure}` 数量：15。
- 正文 `\captionof{table}` 数量：14。
- 重复 label：无。
- 缺失 `\ref` / `\autoref` / `\eqref` 对应 label：无。
- 缺失 citation key：无。
- PDF 文本抽取未发现 `图 ??`、`表 ??` 或 `[?]`。
- LaTeX 日志未发现 undefined references 或 undefined citations。

## 编译结果

编译链使用：XeLaTeX + BibTeX + XeLaTeX + XeLaTeX。

`main_v2_final_integrated.pdf` 已完整编译成功，共 38 页。输出文件位于：

`08_report/latex_project/main_v2_final_integrated.pdf`
