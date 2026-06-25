# 样本股票池说明插入审计

生成时间：2026-05-21  
处理文件：`08_report/latex_project/main_v2_final.tex`  
编译产物：`08_report/latex_project/main_v2_final.pdf`

## 插入位置

- 定位章节：第 4.1 节“数据来源与样本边界”。
- 定位句子：`跨交易日的第一分钟收益率设为缺失，避免隔夜信息混入分钟级压力测度。`
- 插入位置：上述句子之后，`表 \ref{tab:sample-cleaning} 汇总了样本处理的核心环节与结果。` 之前。
- 插入内容：按用户要求加入两段样本股票池构造说明，以及 84 个行情代码中 80 个 A 股个股和 4 个宽基指数代码的用途说明。

## 文件结构核查

- `main_v2_final.tex` 未通过 `\input{}` 或 `\include{}` 引入分章节正文文件。
- 本轮只修改 `main_v2_final.tex`，未修改 `sections/*.tex`。

## 未改动范围

- 未新增、删除或移动图表。
- 未修改表 3 内容、表格环境或表格编号。
- 未修改任何 `\includegraphics` 路径。
- 未修改 figure caption、公式、参考文献、`refs.bib` 或图片文件。
- 未修改数据文件或模型结果。

## 编译检查

- 编译链：XeLaTeX + BibTeX + XeLaTeX + XeLaTeX。
- 编译结果：成功生成 `main_v2_final.pdf`，共 31 页。
- 日志检查：未发现 undefined references、undefined citations 或 LaTeX Error。
- PDF 文本检查：未发现 `图 ??`、`表 ??` 或 `[?]`。
