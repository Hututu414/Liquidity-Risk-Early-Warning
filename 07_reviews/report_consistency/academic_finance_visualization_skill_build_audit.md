# Academic Finance Visualization Skill Build Audit

## 构建结论

- 状态：完成。
- skill 路径：`.agents/skills/academic-finance-visualization-cn/`
- 本轮只生成 skill、脚本、模板、来源记录和审计文件。
- 未重画任何图。
- 未修改 RGARCH-CARR-SK、QVAR、SMARTBoost 模型代码。
- 未运行 RGARCH-CARR-SK、QVAR、SMARTBoost。
- 未重跑 stage0-stage3。
- 未进入 LaTeX 编译。
- 未触碰 `02_data_inbox/preprocessed/`。

## 创建的文件

- `.agents/skills/academic-finance-visualization-cn/SKILL.md`
- `.agents/skills/academic-finance-visualization-cn/references/visual_standards.md`
- `.agents/skills/academic-finance-visualization-cn/references/source_adaptation_notes.md`
- `.agents/skills/academic-finance-visualization-cn/scripts/finance_paper_style.py`
- `.agents/skills/academic-finance-visualization-cn/scripts/figure_audit.py`
- `.agents/skills/academic-finance-visualization-cn/templates/figure_registry_template.csv`
- `.agents/skills/academic-finance-visualization-cn/templates/plot_script_template.py`

## 读取的外部来源

- `01_materials/skill_sources/tvhahn-matplotlib-skill/skills/matplotlib/SKILL.md`
- `01_materials/skill_sources/tvhahn-matplotlib-skill/skills/matplotlib/style-reference.md`
- `01_materials/skill_sources/tvhahn-matplotlib-skill/skills/matplotlib/patterns/P3-time-series.md`
- `01_materials/skill_sources/tvhahn-matplotlib-skill/skills/matplotlib/patterns/P7-heatmap.md`
- `01_materials/skill_sources/tvhahn-matplotlib-skill/skills/matplotlib/patterns/P8-multi-panel.md`
- `01_materials/skill_sources/tvhahn-matplotlib-skill/skills/matplotlib/patterns/P9-pr-roc.md`
- `01_materials/skill_sources/k-dense-claude-scientific-skills/docs/scientific-skills.md`
- 三个仓库的 `LICENSE` / `LICENSE.md`

`davila7/claude-code-templates` 克隆时因 Windows 路径过长导致 checkout 不完整；已读取许可证、README、可用目录和 Git 索引，未展开无关长路径模板。

## 借鉴内容

- publication-quality figure 的结构化规范写法。
- 图形尺寸、线宽、字体、图例、网格、边距的规范组织方式。
- PNG/PDF 双输出原则。
- figure audit 的检查项组织。
- style preset 与 templates 的目录组织。
- time series、heatmap、multi-panel、PR/ROC 曲线的设计原则。

## 本项目自写内容

- 中文金融科技高频流动性压力论文的图表定位。
- MarketLSI、RGARCH-CARR-SK、QVAR、SMARTBoost 的证据链绘图规则。
- 中英文术语保留规则。
- `CrossStress` 泄漏边界：不得作为 SMARTBoost 特征，不得使用旧版含泄漏结果图表。
- `finance_paper_style.py` 的项目调色板、字体、保存、轴格式和图例工具。
- `figure_audit.py` 的 PNG/PDF、dpi、空图、文件名、registry、CrossStress 泄漏疑点检查。

## 验证

- 使用指定解释器执行 AST 语法检查：
  `D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe`
- 结果：`syntax ok`
- `py_compile` 未使用作最终验证，因为 `.agents` 下不允许生成 `__pycache__`。

## 后续显式调用方式

后续绘图任务应明确写：

> 请使用 `.agents/skills/academic-finance-visualization-cn` 的规范重画/审计某组图。

或在任务中点名：

> 使用 `academic-finance-visualization-cn` skill。

使用该 skill 时，应先读取 `SKILL.md`；需要写绘图脚本时再读取 `scripts/finance_paper_style.py`；需要审计现有图时再运行 `scripts/figure_audit.py`。
