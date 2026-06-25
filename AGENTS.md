# AGENTS.md

本文件约束所有 agent 的行为。

## 统一项目定位

本项目研究：A 股 1 分钟 OHLCV 与成交额数据能否预警未来 5 或 10 分钟短时流动性压力。

正式模型只有三个：

1. RGARCH-CARR-SK；
2. QVAR；
3. SMARTboost。

三个模型形成递进证据链，而不是模型比赛。

## 统一 Python 约束

所有 agent 生成并运行 Python 代码时，必须使用：

```text
D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe
```

不得调用 `python`、`py`、Conda 或系统 Python。

## 本工作区性质

当前压缩包是 agent-only 版：

- 不包含 Python 文件；
- 不包含 PowerShell 自动化脚本；
- 不直接提供可执行流水线；
- 只提供任务说明、目录规范、prompts、skills 和审计清单。

具体代码由各 agent 在执行任务时生成，并必须写明修改记录。

## 数据三层结构

1. 预处理原始面板：来自 `data_inbox/preprocessed/panel/minute_panel_preprocessed_raw.parquet`；
2. 模型就绪面板：连续竞价过滤、缺分钟剔除、slot、收益率；
3. 变量与标签仓库：ILLIQ、Range、RV、RelAmt、LSI、Stress_H5、Stress_H10、MarketLSI、CrossStress。

## 旧模板污染禁令

旧金融工程模板只可参考工程组织方式，不可继承研究语义。

正式项目目标、报告正文、模型脚本、图表标题和 prompt 主体中不得出现：

```text
套期保值
期货
IF 主力
沪深300ETF
510300
价格发现
VECM
Hasbrouck
Gonzalo-Granger
统计套利
配对交易
Kalman 动态价差
OU 半衰期
DCC-GARCH
Bayesian SSM
Markov regime filter
金融工程课堂大作业
```

这些词仅允许出现在禁止清单或残留审计说明中。

## LaTeX 论文排版 skill 规则

当任务涉及中文 LaTeX 论文、图表排版、表格重排、caption 修复、浮动体修复、编译日志处理、PDF 视觉审计或最终 TeX 项目打包时，应优先显式使用：

```text
$academic-latex-typesetting-cn
```

该 skill 只能用于排版、图表筛选、浮动体修复、caption 修复、PDF 视觉审计和最终 TeX 包整理；不得修改 RGARCH-CARR-SK、QVAR、SMARTBoost 的模型结论，不得伪造文献、稳健性检验或实证结果。

## Handoff 规则

任何 agent 完成任务后，必须在自己的 workspace 中写 handoff 文件：

```text
agent_workspaces/<agent>_workspace/handoff_*.md
```

内容包括：

- 读取了哪些文件；
- 修改了哪些文件；
- 生成了哪些产物；
- 未解决问题；
- 下一位 agent 应该接着做什么。
