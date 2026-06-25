# terminology_cn_layout_insert_audit

Date: 2026-05-21

## 文件范围

- 实际读取的输入文件：`D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\08_report\latex_project\main_v2_final_terminology_cn.tex`
- 修改并编译的输出文件：`D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\08_report\latex_project\main_v2_final_terminology_cn_layout_fixed.tex`
- 编译输出 PDF：`D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\08_report\latex_project\main_v2_final_terminology_cn_layout_fixed.pdf`
- 修改前备份：`D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\08_report\latex_project\main_v2_final_terminology_cn_before_layout_insert.tex`
- `main_v2_final_terminology_cn.tex` 与备份文件哈希一致，确认真实输入文件未被改写。
- `latex_project` 目录下未发现 `main_v2_final.tex`，本轮未创建、未读取为基础、未修改该文件。

## 定点文本插入

- 已在第 4.1 节“数据来源与样本边界”中，紧接“跨交易日的第一分钟收益率设为缺失，避免隔夜信息混入分钟级压力测度。”之后插入用户指定的两段样本股票池说明。
- 插入后仍直接衔接“表 \ref{tab:sample-cleaning} 汇总了样本处理的核心环节与结果。”，未移动表 3，未改动表 3 内容。
- 插入前检查目标文字在输入文件中的出现次数为 0；输出文件中出现次数为 1，未重复插入。

## 排版修复

- 正文主体使用 `center` + `\captionof{figure/table}` 的非浮动证据块；本轮未把正文图表改写为新浮动体，未新增 `[H]`。
- 删除正文第 4、5、6 节中会造成硬分页的局部 `\newpage`：
  - 第 4 章样本覆盖与 LSI 日内模式前的 2 处 `\newpage`；
  - 第 5.2 节 QVAR 前的 1 处 `\newpage`，改为 `\Needspace{8\baselineskip}`；
  - 第 6.2、6.3、6.4 小节前的 3 处 `\newpage`，其中 6.2 与 6.3 改为 `\Needspace{8\baselineskip}`，6.4 保留原有 `\Needspace{8\baselineskip}`。
- 保留导言目录后的 `\newpage`、第 3 章前的 `\newpage`，以及正文结束进入附录和附录结束进入参考文献前的 `\FloatBarrier` + `\clearpage`。
- 全文未发现 `\pagebreak`、`\afterpage` 或 `[H]`。

## 图片尺寸调整

仅调整 `\includegraphics` 的宽度/最大高度/`keepaspectratio`，未改图片路径、图题、图注或标签。

- 图 5：`fig_rgarch_risk.png` 调整为 `width=0.78\linewidth,height=0.31\textheight,keepaspectratio`。
- 图 6：`fig_rgarch_dynamic_skewness_refined.png` 调整为 `width=0.78\linewidth,height=0.31\textheight,keepaspectratio`。
- 图 7：`fig_qvar_response.png` 调整为 `width=0.78\linewidth,height=0.34\textheight,keepaspectratio`。
- 图 8：`fig_qvar_stress.png` 调整为 `width=0.82\linewidth,height=0.36\textheight,keepaspectratio`。
- 图 9：`fig_sb_pr.png` 调整为 `width=0.78\linewidth,height=0.35\textheight,keepaspectratio`。
- 图 10：`fig_sb_top5.png` 调整为 `width=0.78\linewidth,height=0.32\textheight,keepaspectratio`。
- 图 11：`fig_sb_partial.png` 调整为 `width=0.82\linewidth,height=0.38\textheight,keepaspectratio`。
- 图 13：`fig_rgarch_realized_measure_distribution_refined.png` 调整为 `width=0.78\linewidth,height=0.35\textheight,keepaspectratio`。
- 图 14：`fig_qvar_tail_response_summary_refined.png` 调整为 `width=0.78\linewidth,height=0.35\textheight,keepaspectratio`。
- 图 15：`fig_robust_sb_topk.png` 调整为 `width=0.78\linewidth,height=0.34\textheight,keepaspectratio`。

## 重点章节视觉审计

- 第 5.1 节 RGARCH-CARR-SK：
  - 图 5 位于首次引用段落之后，解释段落紧接在下一页页首；
  - 图 6 位于引出段落之后，解释段落紧随图像；
  - 渲染页 14--15 未再出现图 5、图 6 连续堆叠且中间无正文解释的页面。
- 第 5.2 节 QVAR：
  - 表 8、图 7、表 9、图 8 按正文逻辑顺序出现；
  - 表 9 位于第 17 页，图 8 位于第 18 页，二者未机械堆叠在同一页；
  - 图 8 后紧接现有解释段落，并自然进入 SMARTBoost 小节。
- 第 5.3 节 SMARTBoost：
  - 表 10、图 9、图 10、表 11、图 11 顺序正常；
  - 图表之间有正文解释穿插，未出现超过一页的连续图表堆叠。
- 第 6 章稳健性检验：
  - 图 12、图 13、图 14、图 15 均靠近对应小节文字；
  - 未在每个小节后使用 `\clearpage` 强制分页；
  - 渲染页 21--24 未发现仅有图表而缺少解释段落的小节页。

## 内容边界检查

- 未修改正文既有观点、公式、图题、表题、图注、表注、参考文献和图片文件。
- `\captionof{figure}`、`\captionof{table}`、`\caption{...}` 行逐项对比一致。
- `\begin{equation}` 数量与原文件一致。
- `\bibliography{refs}` 保持不变。

## 编译检查

- 编译命令顺序：`xelatex -> bibtex -> xelatex -> xelatex`。
- 编译成功，生成 29 页 `main_v2_final_terminology_cn_layout_fixed.pdf`。
- 最终日志检查：
  - undefined references：0；
  - undefined citations：0；
  - overfull hbox：0；
  - `Float too large`：0；
  - rerun warning：0；
  - underfull hbox：1 处，位于表格单元格断词位置，不属于溢出或严重版面错误。

## 仍需人工微调的页面

- 未发现需要立即人工微调的严重页面。
- 若后续追求更紧凑的版心，可微调第 6 章页 21 的图 12 起始位置；当前版本未出现图表堆叠、交叉引用错误或大面积异常空白。
