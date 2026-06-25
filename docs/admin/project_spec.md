# 项目规格说明

## 研究对象

A 股一分钟 OHLCV 与成交额数据。

## 核心问题

可得的一分钟市场状态信息是否足以提前识别未来 5 分钟或 10 分钟短时流动性压力。

## 正式模型

| 模型 | 功能 | 回答的问题 |
|---|---|---|
| RGARCH-CARR-SK | 动态高阶风险度量 | 连续型 LSI 是否存在动态波动、高阶矩变化与尾部风险上升 |
| QVAR | 尾部分位传导 | 市场收益、波动、成交状态与横截面压力是否存在尾部动态传导 |
| SMARTboost | 样本外机器学习预警 | 高频窗口特征与市场共同性特征是否提升未来压力事件预警能力 |

## 数据阶段

### 第一层：预处理原始面板

来自：

```text
data_inbox/preprocessed/panel/minute_panel_preprocessed_raw.parquet
```

只完成字段统一、证券范围处理和去重。

### 第二层：模型就绪面板

应完成：

- 连续竞价过滤；
- 严重缺分钟 code-date 剔除；
- 收益率构造；
- slot 构造。

### 第三层：变量与标签仓库

应构造：

```text
ILLIQ(k)
Range(k)
RV(k)
RelAmt(k)
LSI(k)
Stress_H5
Stress_H10
MarketLSI
CrossStress
IndexRet
IndexRV
MarketRelAmt
```

其中 k ∈ {5, 10, 20}。

## 防泄漏原则

1. 所有标准化参数来自训练期；
2. 标准化按“股票-日内槽位”历史 median 和 MAD；
3. 不使用全样本均值、全样本分位数或同日未来信息；
4. 标签阈值来自训练期历史分布；
5. 预测验证使用时间滚动样本外，不得随机打乱。
