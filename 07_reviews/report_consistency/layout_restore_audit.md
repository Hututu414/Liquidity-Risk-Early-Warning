# 仅排版修复审计

生成时间：2026-05-21  
源文件备份：`08_report/latex_project/main_v2_final_before_layout_restore.tex`  
修复文件：`08_report/latex_project/main_v2_final_layout_fixed.tex`  
编译产物：`08_report/latex_project/main_v2_final_layout_fixed.pdf`

## 1. 修改范围

本轮仅调整 LaTeX 排版控制，不修改正文内容、公式、图题、表题、图注、表注、参考文献、图片文件或图片路径。  
机器核查结果：caption 列表一致、label 列表一致、`\includegraphics` 路径一致，去除布局命令差异后的正文内容一致。

## 2. 浮动与分页参数

导言区新增或调整以下排版参数：

- `\captionsetup{skip=4pt}` 与 `\captionsetup[table]{skip=4pt}`，缩短图表与 caption 的垂直距离。
- `\raggedbottom`，避免页面为了强行底部对齐而拉出大空白。
- `\textfloatsep`、`\floatsep`、`\intextsep` 统一设为 `8pt plus 2pt minus 2pt`。
- 加入 `\topfraction=0.85`、`\bottomfraction=0.75`、`\textfraction=0.10`、`\floatpagefraction=0.75`，减少浮动体集中堆到浮动页的概率。

## 3. 图表浮动参数与尺寸

第 4 章描述性图像保留普通浮动 `[!htbp]`，仅压缩正文图尺寸：

- `fig_timeline.png`：改为 `width=0.78\linewidth,height=0.28\textheight,keepaspectratio`。
- `fig_coverage.png`：改为 `width=0.82\linewidth,height=0.36\textheight,keepaspectratio`。
- `fig_intraday.png`：改为 `width=0.82\linewidth,height=0.34\textheight,keepaspectratio`。
- `fig_marketlsi.png`：改为 `width=0.86\linewidth,height=0.38\textheight,keepaspectratio`。

第 5 章核心证据块使用局部 `[H]`，以保持“引出段—图表—解释段”顺序：

- RGARCH：图 5、图 6 改为 `[H]`，并设置 `width=0.82\linewidth,height=0.31\textheight,keepaspectratio`。
- RGARCH：表 6、表 7 改为 `[H]`。
- QVAR：表 8、图 7、表 9、图 8 改为 `[H]`；图 7 为 `0.80\linewidth / 0.34\textheight`，图 8 为 `0.82\linewidth / 0.36\textheight`。
- SMARTBoost：表 10、图 9、图 10、表 11、图 11 改为 `[H]`；图 9、图 10 为 `0.80\linewidth / 0.34\textheight`，图 11 为 `0.84\linewidth / 0.38\textheight`。

第 6 章稳健性图像使用局部 `[H]` 并限制高度：

- 图 12：`0.82\linewidth / 0.34\textheight`。
- 图 13：`0.82\linewidth / 0.34\textheight`。
- 图 14：`0.82\linewidth / 0.34\textheight`。
- 图 15：`0.82\linewidth / 0.34\textheight`。

附录图像未调整。

## 4. FloatBarrier 与分页命令

- 未新增 `\FloatBarrier`。
- 未删除正文内容附近的既有 `\FloatBarrier`，保留位置均位于 section 或 subsection 结束处，用于阻止图表跨节漂移。
- 未新增 `\clearpage`、`\newpage`、`\pagebreak` 或 `\afterpage`。
- 保留 `\newpage`：目录之后。
- 保留 `\clearpage`：进入附录前、参考文献前。
- 正文第 4、5、6 章未使用新增强制分页命令。

## 5. 重点页面修复结果

- 第 5.1 节：图 5 和图 6 均贴近首次引用位置；两图之间保留图 5 的解释段和图 6 的引出段，不再是连续图像堆叠页。
- 第 5.2 节：表 8、图 7、表 9、图 8 按正文逻辑顺序出现。表 9 与图 8 仍位于同页，但中间保留情景解释与图 8 引出句，图后紧跟解释段，未形成机械堆叠。
- 第 5.3 节：表 10、图 9、图 10、表 11、图 11 按原正文顺序排列，图表后均有对应解释段。
- 第 6 章：图 12、图 13、图 14、图 15 均贴近对应小节文字。第 22 页底部有正常换页留白，原因是保持图 14 与其引出段和解释段相邻；未发现严重整页空白。

## 6. 编译检查

- 编译链：XeLaTeX + BibTeX + XeLaTeX + XeLaTeX。
- 编译结果：成功，输出 `main_v2_final_layout_fixed.pdf`，共 30 页。
- 日志检查：未发现 undefined references、undefined citations、LaTeX Error 或 Overfull hbox。
- PDF 文本检查：未发现 `图 ??`、`表 ??` 或 `[?]`。
- 需要人工微调页面：未发现必须继续人工微调的严重页面。
