# 任务看板

## Phase 0：项目骨架与代码生成

负责人：Codex  
输入：本 agent-only 工作区  
输出：真实代码工程、路径系统、入口脚本、测试框架  
Prompt：`prompts/codex_00_create_or_repair_project.md`

## Phase 1：数据核验与模型就绪面板

负责人：Codex 主导，Gemini 协助  
输出：模型就绪面板、数据审计报告

## Phase 2：LSI 与压力标签

负责人：Codex 主导  
输出：压力组件、LSI、Stress_H5、Stress_H10、MarketLSI、CrossStress、防泄漏审计

## Phase 3：描述性事实与图表初稿

负责人：Gemini 主导  
输出：样本结构、覆盖热力图、LSI 日内图、CrossStress 图、文字草稿

## Phase 4：RGARCH-CARR-SK

负责人：Codex  
输出：动态风险度量结果、简化实现说明或完整实现说明

## Phase 5：QVAR

负责人：Codex  
输出：分位数系统、IRF、压力测试

## Phase 6：SMARTboost

负责人：Codex  
前置：SMARTboost 原文与算法核验  
输出：样本外预测与解释，或 blocker 文件

## Phase 7：报告生成

负责人：Codex + Gemini  
输出：中文论文初稿、图表、三线表

## Phase 8：最终审计与打包

负责人：Codex，DeepSeek v4 复核  
输出：可提交包、复现清单、残留审计
