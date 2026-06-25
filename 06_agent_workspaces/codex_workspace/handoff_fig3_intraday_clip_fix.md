# Handoff: 图 3 LSI_5 日内模式截断修复

## 读取文件

- `04_code/src/visualization/rebuild_descriptive_figures.py`
- `08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.tex`
- `05_outputs/figures/03_descriptive/fig_descriptive_05_intraday_pattern.png`
- `08_report/latex_project/figures/fig_intraday.png`
- `08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.log`
- `08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.pdf`

## 修改文件

- `04_code/src/visualization/rebuild_descriptive_figures.py`
  - 仅修改 `plot_intraday_pattern()` 中图 3 的画布高度、子图边距、子图间距与保存参数。
- `05_outputs/figures/03_descriptive/fig_descriptive_05_intraday_pattern.png`
  - 重新生成并覆盖保存同一路径。
- `08_report/latex_project/figures/fig_intraday.png`
  - 同步更新 LaTeX 项目使用的图 3 图片副本。
- `08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.tex`
  - 仅修改图 3 的 `\includegraphics` 尺寸参数，未改图题或正文。

## 生成产物

- `08_report/latex_project/main_v2_final_terminology_cn_layout_fixed.pdf`
- `07_reviews/report_consistency/fig3_intraday_clip_fix_audit.md`
- `07_reviews/report_consistency/fig3_render_check/page-13.png`

## 验证结果

- 使用固定解释器重新生成图 3：
  - `D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe`
- 使用 XeLaTeX 重新编译当前最终论文 PDF，两轮编译后日志无 undefined references/citations。
- PDF 第 13 页渲染显示图 3 下方子图未再被截断。

## 未解决问题

- 无。

## 下一步

- 若后续需要更换主 TeX 文件名，应将同样的图 3 `\includegraphics` 尺寸参数同步到新的主文件；图片源文件已修复。
