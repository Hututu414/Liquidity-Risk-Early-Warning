# 数据字典模板

| 字段名 | 数据层 | 类型 | 含义 | 来源 | 缺失处理 | 是否用于模型 | 备注 |
|---|---|---|---|---|---|---|---|
| datetime | 预处理原始面板 | datetime | 分钟时间戳 | 原始分钟行情 | 不允许缺失 | 是 | 与指数按 datetime 对齐 |
| code | 预处理原始面板 | string | 证券代码 | 原始分钟行情 | 不允许缺失 | 是 | 区分股票与指数 |
| open | 预处理原始面板 | numeric | 开盘价 | OHLCV | 检查非正值 | 是 | |
| high | 预处理原始面板 | numeric | 最高价 | OHLCV | 检查非正值 | 是 | |
| low | 预处理原始面板 | numeric | 最低价 | OHLCV | 检查非正值 | 是 | |
| close | 预处理原始面板 | numeric | 收盘价 | OHLCV | 检查非正值 | 是 | |
| volume | 预处理原始面板 | numeric | 成交量 | OHLCV | 允许零值但需诊断 | 是 | |
| amount | 预处理原始面板 | numeric | 成交额 | OHLCV | 允许零值但需诊断 | 是 | |
