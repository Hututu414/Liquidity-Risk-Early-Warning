# RGARCH-CARR-SK 动态偏度图插入审计

日期：2026-05-20

## 修改范围

- 修改文件：`08_report/latex_project/sections/05_empirical_results.tex`
- 目标小节：5.1 “RGARCH-CARR-SK 动态压力风险结果”
- 未修改范围：QVAR、SMARTBoost、稳健性检验和附录未做正文内容调整。

## 图片路径

- 项目输出目录中已存在图片：`05_outputs/figures/04_rgarch/fig_rgarch_dynamic_skewness_refined.png`
- LaTeX 项目中已存在同名图片：`08_report/latex_project/figures/fig_rgarch_dynamic_skewness_refined.png`
- 两处文件 SHA256 一致：`B5C252051872A09B524686FDD0BA490F21BE99C161EBEA726FD75C33BD001EEA`
- 正文实际使用的相对路径：`figures/fig_rgarch_dynamic_skewness_refined.png`

## 插入位置与标签

- 插入位置：5.1 中“RGARCH-CARR-SK 条件压力风险路径”图及其解释段落之后，动态峰度 \(k_t\) 谨慎说明之前。
- 新增图 label：`fig:rgarch_dynamic_skewness`
- 现有条件压力风险图 label：`fig:rgarch-risk`

## 编译结果

- 编译命令：执行 `08_report/latex_project/build_report.ps1`
- 编译产物：`08_report/latex_project/main.pdf`
- 编译状态：成功。
- 最终 `main.aux` 显示：
  - 条件压力风险图：图 5，页 16；
  - 动态偏度图：图 6，页 17。
- 最终 `main.log` 未检出未解析引用、Overfull 或 Underfull 告警。

## 顺序与漂移检查

- 源文件顺序为：条件压力风险 \(\lambda_t\) 图 -> \(\lambda_t\) 解释 -> 动态偏度 \(s_t\) 图 -> \(s_t\) 解释 -> 动态峰度 \(k_t\) 谨慎说明 -> realized pressure measure 表格。
- PDF 文本抽取确认：图 5 条件压力风险图之后出现图 6 动态偏度图，之后才出现动态峰度说明和 realized pressure measure 表格。
- 未发现新增图漂移到 5.2 小节或附录的问题。

## 静态图像引用检查

- 已运行：`.agents/skills/academic-latex-typesetting-cn/scripts/scan_figure_references.py`
- 输出报告：`07_reviews/report_consistency/scan_figure_references.md`
- 检查结果：`includegraphics` 共 18 处，缺失图片 0，绝对路径 0，位于 `08_report/latex_project/figures` 之外的图片 0。
