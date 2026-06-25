# 模型登记表

| 模型 | 状态 | 负责人 | 输入 | 输出 | 核验要求 |
|---|---|---|---|---|---|
| RGARCH-CARR-SK | 已完成原文框架适配实现 | Codex | MarketLSI 压力创新与 RV/RBV/MedRV/RMAD 广义 realized pressure measures | 参数估计、LLK/AIC/BIC、条件压力风险路径、动态偏度峰度、样本外损失表 | 写成“基于 Liu、Zhou 和 Chen（2025）RGARCH-CARR-SK 框架的 MarketLSI 压力风险适配实现”，不是 GEM 指数复刻 |
| QVAR | 已实现 | Codex | MarketLSI, CrossStress, IndexRet, IndexRV, MarketRelAmt | 分位数系统、尾部分位响应、压力测试 | 使用 QuantReg 一阶分位系统，不使用均值 VAR 替代 |
| SMARTboost | 已完成 Python 适配实证，已通过深度防泄漏复核 | Codex | 高频窗口特征、市场状态特征（剔除 label-derived `CrossStress`）、日内时点、监管阶段、Stress_H5/H10 | 样本外预测概率、PR/ROC/校准/Top风险组/分阶段指标、事件率与 lift、预测完整性复核 | 原文、DOI、算法和作者代码已核验；正文须写明“基于原文算法定义的 Python 适配实现”，不是直接运行作者 Julia 包 |
