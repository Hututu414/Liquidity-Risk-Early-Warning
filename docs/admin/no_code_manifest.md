# No-code Manifest

本工作区为 agent-only 版。

## 不包含

- `.py`
- `.ps1`
- `.sh`
- `.bat`
- `.cmd`
- 可执行数据处理脚本
- 预先写好的模型代码

## 只包含

- Markdown 任务说明；
- agent prompts；
- skill 说明；
- 目录占位；
- registry；
- audit checklist；
- LaTeX 报告占位说明；
- Gemini / Roo 配置说明。

## 设计原因

具体代码需要交由 Codex、Gemini、DeepSeek v4 / Roo 在读取任务规范后生成，便于各 agent 按能力分工并保留 handoff 与审计记录。
