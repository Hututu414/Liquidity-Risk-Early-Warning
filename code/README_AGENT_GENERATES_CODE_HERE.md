# 代码目录说明

当前压缩包是 agent-only 版，故本目录不包含任何 `.py` 文件。

后续应由 Codex 在读取以下文件后生成真实代码工程：

```text
AGENTS.md
CODEX.md
docs/admin/project_spec.md
prompts/codex_00_create_or_repair_project.md
```

Codex 生成代码时应建立：

```text
code/config/
code/src/data/
code/src/diagnostics/
code/src/models/
code/src/robustness/
code/src/visualization/
code/src/report/
code/tests/
```

但这些代码不应由本压缩包预置。
