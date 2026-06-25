# Codex Final Paper Audit

## A. 总体修改摘要

- 修改章节：摘要、引言、文献综述、研究设计与方法、数据与描述性事实、实证结果分析、稳健性检验、结论与局限性、附录图表。
- 删除正文图：RGARCH-CARR-SK 动态偏度与动态峰度合并图 `fig_rgarch_dynamic_skew_kurtosis_refined.png` 已从正文移除，未放入附录。
- 移动图表：股票-月份有效分钟覆盖率图从附录移入正文 4.3；RGARCH realized measure 旧附录图删除，正文保留 refined 分布图；附录保留 3 张补充图。
- 新增或重写段落：5.1 RGARCH-CARR-SK、5.2 QVAR、5.3 SMARTBoost、6.1--6.5 稳健性检验均重写或局部重写，改为“文字引出图表--图表--文字解释图表”的证据链。
- 正文动态峰度图：已删除。动态峰度 \(k_t\) 仅在方法和结果文字中作为诊断信息简要说明，不作为核心经验发现。

## B. RGARCH 修正记录

- 动态峰度 \(k_t\) 已从正文图表中删除。
- 方法部分保留 \(k_t\) 公式，但明确其只是 RGARCH-CARR-SK 允许的高阶矩扩展和诊断信息。
- 5.1 节现在保留：
  - 图 \ref{fig:rgarch-risk}：条件压力风险 \(\lambda_t\) 路径；
  - 表 \ref{tab:rgarch-fit}：不同 realized pressure measure 下的拟合准则；
  - 表 \ref{tab:rgarch-loss}：不同 realized pressure measure 下的样本外损失。
- 摘要、文献综述、方法、5.1、5.4 和结论中的“动态高阶矩/高阶矩特征”核心表述已改为条件压力风险、动态偏度诊断和 realized pressure measure 敏感性。

## C. QVAR 修正记录

- 5.2 节顺序已调整为：表 \ref{tab:qvar-pinball}、图 \ref{fig:qvar-response}、表 \ref{tab:qvar-scenarios}、图 \ref{fig:qvar-stress}。
- 文中避免使用“导致”“因果影响”“外生冲击造成”“证明某变量引发压力”“结构性冲击”等表述。
- 图 \ref{fig:qvar-response} 和图 \ref{fig:qvar-stress} 前后均有引入和解释文字，统一解释为条件响应、标准化情景响应和尾部分位联动。

## D. SMARTBoost 修正记录

- 5.3 节顺序已调整为：表 \ref{tab:smartboost-metrics}、图 \ref{fig:sb-pr}、图 \ref{fig:sb-top5}、表 \ref{tab:smartboost-topk}、图 \ref{fig:sb-partial}、防泄漏说明。
- 正文显式突出 test 样本 H5 PR-AUC=0.603、H10 PR-AUC=0.545，以及 Top 5% lift 约 10 倍。
- Top 5% 高风险组图被作为最直观预警证据重点解释。
- Partial Effects 仅解释为预测模型局部响应，不作因果解释。
- 防泄漏说明保留，并改为论文语言；Stress_H5、Stress_H10、FutureMaxLSI 和 CrossStress 均不进入最终预测特征矩阵。

## E. 稳健性检验修正记录

- 6.1 保留标签阈值稳健性图，强调不同阈值下 lift 方向稳定，表述为核心排序结论保持一致。
- 6.2 保留 realized pressure measure refined 分布图，结合表 \ref{tab:rgarch-loss} 说明测度敏感性，不宣称单一测度绝对最优。
- 6.3 保留 QVAR 最大响应差异图，解释响应强度主要集中在波动放大、成交收缩或复合压力状态下，未夸大所有情景。
- 6.4 保留 Top-K 稳健性图，解释 Top-K 扩大后 lift 下降属于风险排序任务的正常现象。
- 6.5 保留特征边界核查，并加入表 \ref{tab:smartboost-leakage}。
- 表 \ref{tab:robustness-design} 和表 \ref{tab:robustness-conclusions} 保留为章节总结表，使用 `tabularx` 和 booktabs，最终扫描未发现表格溢出。

## F. 语言清理记录

- 已检查并清理：当前版本、本轮、这轮、脚本、输出目录、生成文件、pipeline、agent、Gemini、Codex、模型就绪样本、旧版、重跑、metadata、debug、检查脚本、图片跑出来、机械拟合、完全黑箱、图形证据说明等工程化或过程化表述。
- 正文 TeX 文件中未检出 Gemini、Codex、脚本、当前版本、输出目录、pipeline 等词。
- CrossStress、FutureMaxLSI、Stress_H5 和 Stress_H10 仍在正文或表格中出现，原因是它们属于正式变量边界核查对象，不是工程残留。

## G. 编译记录

- 编译命令：在 `08_report/latex_project/` 下运行 `.\build_report.ps1`。
- 编译流程：XeLaTeX -> BibTeX -> XeLaTeX -> XeLaTeX。
- 编译结果：成功生成 `08_report/latex_project/main.pdf`。
- PDF 页数：35 页。
- `scan_overfull_log.py` 结果：
  - Overfull hbox: 0
  - Underfull hbox: 0
  - Undefined references: 0
  - Missing files: 0
  - Citation warnings: 0
- `scan_figure_references.py` 结果：
  - Includegraphics commands: 17
  - Missing files: 0
  - Absolute paths: 0
  - Outside figures directory: 0
- `scan_tex_floats.py` 结果：
  - Figures: 17
  - `[H]` placements: 0
  - Missing captions: 0
  - Missing labels: 0
  - Unreferenced labels: 0
- `scan_table_width.py` 结果：
  - Most tables: ok
  - SMARTBoost metrics table remains a compact 8-column table; final PDF visual review shows it is readable and no overfull box is produced.

## Visual Audit Notes

- Final PDF rendered to `tmp/pdf_audit_final_20260520/` and checked through a contact sheet.
- RGARCH 5.1 no longer contains the dynamic skewness/kurtosis figure.
- QVAR and SMARTBoost figures now appear near their explanatory text.
- Robustness figures are in Section 6, not concentrated in the appendix.
- Appendix contains only three supplemental diagnostic figures: event-rate time variation, correlation heatmap, and SMARTBoost calibration.
- Several image files still contain small internal plot titles from the verified figure outputs. They were not redrawn because this final pass did not rerun model or plotting pipelines; formal titles are provided in LaTeX captions.
