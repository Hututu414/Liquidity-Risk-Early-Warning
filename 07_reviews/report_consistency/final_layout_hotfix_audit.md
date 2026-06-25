# Final Layout Hotfix Audit

日期：2026-05-20

## 修改范围

本轮只处理两个排版硬伤：结论与附录之间的浮动体隔离，以及数学模式中多字母变量的排版。未修改模型结果、数据、Python 模型代码、文献综述、实证结论或新增图表。

## 浮动体修复结果

- `main.tex` 导言区已存在 `\usepackage{placeins}`，本轮未新增该包。
- 在 `\input{sections/07_conclusion.tex}` 后、`\appendix` 前加入：
  - `\FloatBarrier`
  - `\clearpage`
- 将 `sections/appendix_figures.tex` 中 3 个附录图的浮动参数由 `[tbp]` 调整为 `[H]`，防止附录图上浮到附录标题之前。
- PDF 文本抽取核查结果：
  - 第 7 章“结论与局限性”位于第 28-29 页；
  - `A 附录图表` 从第 30 页开始；
  - 图 16、图 17 和图 18 均出现在 `A 附录图表` 标题之后；
  - 未发现图 16 或其他附录图插入第 7 章结论正文。
- `main.aux` 显示：
  - 第 7 章页码：28；
  - 附录 A 页码：30；
  - 图 16 页码：30；
  - 图 17 页码：30；
  - 图 18 页码：31。

## 公式变量排版修复结果

在数学模式中修复了以下多字母变量或指标的排版：

- `MarketLSI` -> `\MarketLSI`
- `LSI` -> `\LSI`
- `Stress_H` / `Stress_H5` / `Stress_H10` -> `\StressH` / `\StressHfive` / `\StressHten`
- `FutureMaxLSI` -> `\FutureMaxLSI`
- `IndexRet` -> `\IndexRet`
- `IndexRV` -> `\IndexRV`
- `MarketRelAmt` -> `\MarketRelAmt`
- `ILLIQ`、`Range`、`RV`、`RelAmt` -> `\mathrm{...}`
- `Median_{train,slot}`、`MAD_{train,slot}` -> `\operatorname{...}_{\mathrm{train},\mathrm{slot}}`
- `HitRate_{TopK}`、`Lift_{TopK}` -> `\mathrm{HitRate}_{\mathrm{TopK}}`、`\mathrm{Lift}_{\mathrm{TopK}}`
- `Stress_{H,t}`、`\bar{Stress}_H` -> `\mathrm{Stress}_{H,t}`、`\bar{\mathrm{Stress}}_H`

只调整数学模式中的排版；正文普通文本中的专业术语未强制改为数学格式。

## 编译与扫描状态

- 编译命令：`08_report/latex_project/build_report.ps1`
- 编译结果：成功生成 `08_report/latex_project/main.pdf`
- PDF 页数：33 页
- `scan_tex_floats.md`：18 个 figure、1 个 table，缺 caption 0，缺 label 0，未引用 label 0。
- `scan_overfull_log.md`：Overfull hbox 0，Underfull hbox 0，未定义引用 0，缺文件 0，citation warnings 0。
- 数学模式变量检查：目标裸写变量命中 0。

## 仍需人工检查的问题

- 未发现阻塞性问题。
- 因附录图改为 `[H]`，建议最终提交前人工翻看第 30-31 页，确认附录图之间的留白符合审美预期。
