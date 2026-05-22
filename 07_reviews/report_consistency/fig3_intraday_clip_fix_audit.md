# 图 3：LSI_5 日内模式截断修复审计

## 修改范围

本轮仅处理“图 3：LSI\_5 日内模式”的图片截断问题，未改动论文正文、表格、参考文献、章节结构、公式、图题或其他图片。

## 修改文件

- `04_code/src/visualization/rebuild_descriptive_figures.py`
- `05_outputs/figures/03_descriptive/fig_descriptive_05_intraday_pattern.png`
- `08_report/latex_project/figures/fig_intraday.png`
- `08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.tex`
- `08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.pdf`

## 修复方式

- 定位到 `plot_intraday_pattern()` 生成 `fig_descriptive_05_intraday_pattern.png`。
- 将图 3 的画布高度由 `6.7` 提高到 `8.2`，增加上下两个子图的垂直空间。
- 取消该图依赖 `constrained_layout` 的自动边距，改用显式 `subplots_adjust(left=0.085, right=0.985, top=0.885, bottom=0.105, hspace=0.22)`。
- 保存图像时不再使用可能裁切底部区域的 `bbox_inches="tight"`，改为 `bbox_inches=None`。
- 将重新生成的源图片同步到 LaTeX 项目中的现有图片副本 `figures/fig_intraday.png`。
- 仅针对图 3 的 `\includegraphics` 做最小排版修正：加入 `height=0.50\textheight,keepaspectratio`，避免 PDF 中再次压缩或裁切；图题保持为 `LSI\_5 日内模式`。

## 编译与检查

- 编译文件：`08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.tex`
- 输出 PDF：`08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.pdf`
- 编译结果：成功。
- 日志检查：未发现 `undefined references`、`undefined citations`、`LaTeX Error`、`Label(s) may have changed` 或 `Overfull`。
- PDF 文本检查：未发现 `图 ??`、`表 ??` 或 `[?]`。
- 页面渲染检查：`07_reviews/report_consistency/fig3_render_check/page-13.png` 显示图 3 下方子图、坐标轴与尾盘区域完整。

## 未改动确认

- 未修改论文正文表述。
- 未修改图题、表题、图注、表注。
- 未修改表格、公式、参考文献。
- 未移动图片位置。
- 未修改除图 3 以外的其他图片。
