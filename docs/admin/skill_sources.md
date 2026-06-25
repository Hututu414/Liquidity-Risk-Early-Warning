# Skill Sources

当前压缩包为 agent-only 版，所有 skills 均为本地自建改写版，只提供任务说明，不包含外部仓库代码。

| skill 名称 | 来源说明 | 许可证 | 是否原样引用 | 是否改写 | 改写点 | 位置 |
|---|---|---|---|---|---|---|
| hft-data-audit | 本地自建 | 项目内部 | 否 | 是 | 针对 A 股分钟面板字段、重复键、缺分钟检查 | .agents/skills/hft-data-audit |
| minute-panel-feature-engineering | 本地自建 | 项目内部 | 否 | 是 | 针对 slot、ILLIQ、Range、RV、RelAmt、LSI、Stress 标签 | .agents/skills/minute-panel-feature-engineering |
| no-lookahead-validation | 本地自建 | 项目内部 | 否 | 是 | 训练期标准化、标签阈值、时间滚动样本外检查 | .agents/skills/no-lookahead-validation |
| rgarch-carr-sk-risk | 本地自建 | 项目内部 | 否 | 是 | 要求完整实现或明确简化实现 | .agents/skills/rgarch-carr-sk-risk |
| qvar-tail-transmission | 本地自建 | 项目内部 | 否 | 是 | 尾部分位传导与压力测试 | .agents/skills/qvar-tail-transmission |
| smartboost-verification | 本地自建 | 项目内部 | 否 | 是 | 原文、DOI、代码、算法定义核验 | .agents/skills/smartboost-verification |
| academic-visualization-cn | 本地自建 | 项目内部 | 否 | 是 | 中文论文图表、300dpi、少文字堆叠 | .agents/skills/academic-visualization-cn |
| academic-finance-visualization-cn | 参考 tvhahn/matplotlib-skill、K-Dense-AI/claude-scientific-skills、davila7/claude-code-templates 后本项目改写 | MIT / MIT / MIT | 否 | 是 | 改写为 A 股高频流动性压力论文专用：MarketLSI、RGARCH-CARR-SK、QVAR、SMARTBoost、CrossStress 泄漏边界、PNG/PDF 双输出、图表审计脚本 | .agents/skills/academic-finance-visualization-cn |
| latex-report-cn | 本地自建 | 项目内部 | 否 | 是 | 中文 LaTeX、三线表、作者童奕然 | .agents/skills/latex-report-cn |
| academic-latex-typesetting-cn | 参考 openai/skills、ndpvt-web/latex-document-skill、renocrypt/latex-arxiv-SKILL、Noi1r/beamer-skill、google-research/arxiv-latex-cleaner、K-Dense-AI/scientific-agent-skills、Master-cai/Research-Paper-Writing-Skills 后本项目改写 | mixed：单 skill 许可证、MIT、未明确、MIT、Apache-2.0、MIT/单 skill 元数据、MIT | 否 | 是 | 改写为中文金融科技实证论文 LaTeX 排版、图表筛选、表格重排、PDF 视觉审计、最终 TeX 包审计专用；仅借鉴结构和 workflow，不复制外部正文或脚本 | .agents/skills/academic-latex-typesetting-cn |
| beamer-academic-ppt | 本地自建，参考此前本地 beamer-academic-ppt 工作流思想 | 项目内部 | 否 | 是 | 只保留答辩 Beamer/PPT 任务规范 | .agents/skills/beamer-academic-ppt |
| semantic-residue-cleanup | 本地自建 | 项目内部 | 否 | 是 | 扫描旧金融工程模板残留和 agent 工程痕迹 | .agents/skills/semantic-residue-cleanup |
| agent-handoff | 本地自建 | 项目内部 | 否 | 是 | 规定 agent 交接文件 | .agents/skills/agent-handoff |

## 2026-05-20 外部 skill 来源记录

本轮为 `academic-finance-visualization-cn` 联网读取并参考了以下仓库，但没有原样复制其 skill 内容或脚本：

| GitHub 仓库 | 本地位置 | 许可证 | 是否原样复制 | 是否改写 | 借鉴内容 | 本项目适配位置 |
|---|---|---|---|---|---|---|
| `https://github.com/tvhahn/matplotlib-skill.git` | `01_materials/skill_sources/tvhahn-matplotlib-skill` | MIT | 否 | 是 | publication-quality figure 的组织方式、style reference、PNG/PDF 双输出、time series、heatmap、multi-panel、PR/ROC pattern 的结构 | `.agents/skills/academic-finance-visualization-cn/SKILL.md`、`scripts/finance_paper_style.py`、`scripts/figure_audit.py` |
| `https://github.com/K-Dense-AI/claude-scientific-skills.git` | `01_materials/skill_sources/k-dense-claude-scientific-skills` | MIT | 否 | 是 | 科学 skill 的分类方式、scientific visualization 作为科研传播工具的定位、references/scripts/assets 的组织思想 | `.agents/skills/academic-finance-visualization-cn/references/visual_standards.md` |
| `https://github.com/davila7/claude-code-templates.git` | `01_materials/skill_sources/davila7-claude-code-templates` | MIT | 否 | 是 | skill/template 仓库的组件化组织方式；该仓库因 Windows 路径过长 checkout 不完整，只读取了许可证、README、仓库索引与可用目录 | `.agents/skills/academic-finance-visualization-cn/templates/` |

说明：本轮只借鉴结构和规范思想，没有复制外部仓库的模板代码作为项目产物。后续若继续联网检索 skill 模板，必须按许可证记录来源，不得盲目复制。

## 2026-05-20 `academic-latex-typesetting-cn` 外部来源记录

本轮为中文金融科技实证论文 LaTeX 排版、图表筛选、表格重排、PDF 视觉审计和最终 TeX 包修复创建了本地 skill。下表按本轮强制字段记录来源和许可证处理。

| 仓库名 | GitHub 地址 | 许可证 | 是否允许复制 | 本项目是否复制原文 | 本项目是否只借鉴结构 | 借鉴了什么 | 改写到了本项目哪个文件 | 许可证不明确或不适合直接引入的问题 |
|---|---|---|---|---|---|---|---|---|
| openai/skills | https://github.com/openai/skills | 仓库说明称单个 skill 的许可证在各 skill 目录 `LICENSE.txt` 中 | 需逐 skill 核验 | 否 | 是 | Codex skill 的基本目录结构、`SKILL.md` front matter、`references/` 与 `scripts/` progressive disclosure 思路 | `.agents/skills/academic-latex-typesetting-cn/SKILL.md`、`references/github_reference_notes.md` | 不把 openai/skills 当作整仓库统一许可证来源；只作结构参考 |
| ndpvt-web/latex-document-skill | https://github.com/ndpvt-web/latex-document-skill | MIT | 是，但本项目未复制 | 否 | 是 | 通用 LaTeX 文档 skill 的 references/scripts/assets 分层、编译与 QA 自动化思路 | `SKILL.md`、`references/table_typesetting_rules.md`、`scripts/scan_table_width.py`、`scripts/scan_overfull_log.py` | 主题过泛，含大量模板和自动生成场景，不适合直接引入 |
| renocrypt/latex-arxiv-SKILL | https://github.com/renocrypt/latex-arxiv-SKILL | 未在 GitHub 页面看到清晰 LICENSE 文件或 License 区块 | 否 | 否 | 是 | issue-driven paper workflow、BibTeX 核验、compile QA、论文 scaffold 检查思路 | `references/github_reference_notes.md`、`references/final_latex_package_rules.md` | 许可证不明确，且主题偏 arXiv / IEEE / ML review paper |
| Noi1r/beamer-skill | https://github.com/Noi1r/beamer-skill | MIT | 是，但本项目未复制 | 否 | 是 | compile -> review -> audit -> polish -> verify 闭环、学术视觉审计意识 | `SKILL.md`、`references/pdf_visual_audit_rules.md`、`scripts/scan_overfull_log.py` | Beamer 主题不适合中文论文正文排版，未引入 slide 模板 |
| google-research/arxiv-latex-cleaner | https://github.com/google-research/arxiv-latex-cleaner | Apache-2.0 | 是，但本项目未复制 | 否 | 是 | 最终 LaTeX 项目清理、辅助文件过滤、隐私和打包思路 | `references/final_latex_package_rules.md`、`scripts/collect_latex_assets.py` | 它是清理工具不是 skill；本项目只写只读审计脚本，不重实现 cleaner |
| K-Dense-AI/scientific-agent-skills | https://github.com/K-Dense-AI/scientific-agent-skills | 仓库 MIT，但说明单个 skill 可有独立 license metadata | 需逐 skill 核验 | 否 | 是 | scientific-writing 的学术写作、引用、图表、报告结构审计思路 | `references/empirical_finance_paper_rules.md`、`references/figure_selection_rules.md` | 领域偏综合科学写作，不专门解决 ctex 浮动体和表格排版 |
| Master-cai/Research-Paper-Writing-Skills | https://github.com/Master-cai/Research-Paper-Writing-Skills | MIT | 是，但本项目未复制 | 否 | 是 | claim-evidence alignment、论文表达和审稿式自查 | `references/empirical_finance_paper_rules.md`、`references/ctex_paper_layout_rules.md` | 主题偏 ML/CV/NLP 写作，且含上游笔记归属，不适合直接引入正文 |

结论：`academic-latex-typesetting-cn` 是本项目自建改写版。即便源仓库为 MIT 或 Apache-2.0，本项目也只抽取结构思路和审计 workflow，不复制外部仓库原文、模板或脚本。
