# QVAR Scenario Coverage Check

## 核查结论

原始不完整原因：`04_code/src/models/06_qvar_tail_transmission.py` 的 `build_response_tables()` 最初只硬编码生成两类情景；不是绘图代码漏读。

本轮状态：已通过 `04_code/src/models/06b_qvar_stress_test.py` 基于既有训练期 QVAR 系数补齐四类标准化情景冲击模拟，未重估 QVAR，未修改 stage0-stage3、RGARCH-CARR-SK 或 SMARTBoost。

当前 `qvar_pressure_test_paths.csv` 可用情景数：4。

## 当前可用情景

| 情景 | 中文标签 | 冲击定义 | 数据来源 | 是否已绘制 |
|---|---|---|---|---|
| `market_crash` | 市场急跌 | `IndexRet=-2.0 standard deviations` | 训练期 QVAR 系数递推 | 是 |
| `volatility_spike` | 波动放大 | `IndexRV=+2.0 standard deviations` | 训练期 QVAR 系数递推 | 是 |
| `liquidity_contraction` | 成交收缩 / 流动性压力 | `MarketRelAmt=-2.0 standard deviations` | 训练期 QVAR 系数递推 | 是 |
| `composite_pressure` | 复合压力 | `IndexRet=-2.0, IndexRV=+2.0, MarketRelAmt=-2.0 standard deviations` | 训练期 QVAR 系数递推 | 是 |

## 未绘制情景

无。四类标准情景均已绘制到 `05_outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png`。

## 解释边界

该图表示 QVAR 情景冲击模拟和尾部分位压力传导，不表示严格因果识别。
