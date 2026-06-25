# QVAR 图 14 定点替换审计

日期：2026-05-22

## 修改范围

- 仅修改 `08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.tex` 第 6.3 节“QVAR 分位点与情景设定稳健性”中图 14 及其对应说明文字。
- 未修改第 5.2 节 QVAR 正文结果。
- 未修改表格、公式、参考文献、图 7、图 8、图 12、图 13、图 15 或其他图片引用。
- 未移动、复制、重画或覆盖任何图片文件。

## 图 14 替换

- 原图路径：`figures/fig_qvar_tail_response_summary_refined.png`
- 新图路径：`../../05_outputs/figures/07_robustness/qvar_scenario_sensitivity/qvar_sensitivity_quantile_cum_abs_shock2.png`
- 图题已改为：`不同分位点下 QVAR 情景响应累计强度比较`
- `fig:qvar-tail-summary` 标签保留，图号仍由 LaTeX 自动生成。

## 文字替换

第 6.3 节中删除/替换了以下旧表述：

- “最大响应强度”
- “最大响应差异”
- “中位数状态 $q=0.50$ 与尾部状态 $q=0.95$ 下四类压力情景的最大响应强度”

替换为用户指定段落，说明改用不同分位点下各情景的累计绝对响应强度，并使用 `$q=0.90$`、`$q=0.95$`、`$q=0.50$` 的 LaTeX 数学格式。

## 编译检查

- 编译链：XeLaTeX + BibTeX + XeLaTeX + XeLaTeX；因一次 XeLaTeX 进程超时中断，随后补跑 XeLaTeX 直至交叉引用稳定。
- 输出 PDF：`08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.pdf`
- 最终日志未发现 undefined references。
- 最终日志未发现 undefined citations。
- 最终日志未发现 LaTeX error。
- PDF 文本检查未发现 “图 ??”、“表 ??” 或 “[?]”。
- PDF 文本中图 14 标题为“不同分位点下 QVAR 情景响应累计强度比较”。

## 未修改项确认

- 未修改其他章节正文。
- 未修改其他图片路径。
- 未修改参考文献。
- 未修改图片文件本身。
- 未新增或删除图表编号。
