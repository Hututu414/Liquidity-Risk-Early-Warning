# CODEX.md

Codex 是本项目最高权限最终工程师。

## Codex 负责

1. 创建或修复真实代码工程；
2. 统一路径系统、配置文件、CLI、日志；
3. 生成正式 Python 脚本和必要 PowerShell 入口；
4. 实现防泄漏的数据流水线；
5. 实现或核验 RGARCH-CARR-SK 简化口径；
6. 实现 QVAR 尾部分位传导；
7. 建立 SMARTboost 核验门槛；
8. 整合 Gemini 与 DeepSeek v4 的结果；
9. 编译 LaTeX 报告；
10. 最终审计和打包。

## Codex 不得

1. 跳过 SMARTboost 核验；
2. 编造模型结果；
3. 将本文改成收益率预测；
4. 将 LSI 说成真实订单簿流动性；
5. 将监管分段写成严格因果识别；
6. 引入 XGBoost、DeepVol、滚动 VAR、HAR-RV-X、QFAVAR 作为正文主模型。

## 代码生成要求

当前 agent-only 工作区不含任何 `.py` 或 `.ps1`。  
Codex 第一次进入后，应根据 `prompts/codex_00_create_or_repair_project.md` 自行生成代码骨架，并将所有生成文件记录到：

```text
agent_workspaces/codex_workspace/handoff_create_or_repair_project.md
reviews/final_package_audit/project_skeleton_audit.md
```

## 固定解释器

所有 Python 命令必须使用：

```text
D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe
```
