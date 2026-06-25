# Agent Handoff 规则

每个 agent 完成任务后，必须写 handoff 文件。

## 文件位置

```text
agent_workspaces/codex_workspace/
agent_workspaces/gemini_workspace/
agent_workspaces/deepseek_v4_workspace/
```

## 必须包含

1. 执行时间；
2. 读取的规范文件；
3. 修改的文件；
4. 新生成的文件；
5. 未解决的问题；
6. 是否存在数据或模型风险；
7. 下一位 agent 的建议任务；
8. 是否违反以下禁令：
   - 随机划分；
   - 全样本标准化；
   - 编造 SMARTboost；
   - 引入额外主模型；
   - 旧模板语义残留。
