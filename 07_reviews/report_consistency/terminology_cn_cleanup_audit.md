# 正文与表格英文术语中文化审计

生成时间：2026-05-21  
处理文件：`08_report/latex_project/main_v2_final_terminology_cn.tex`  
输出 PDF：`08_report/latex_project/main_v2_final_terminology_cn.pdf`

## 1. 修改摘要

本轮仅对正文文字、表格标题、表头、表注和表格附近解释文字中的非必要英文术语进行中文化精修。未修改图片文件，未重画图片，未移动图片，未改动 `\includegraphics` 路径，未修改 figure caption，未修改公式、参考文献、数据文件、模型结果或表格数值。

本轮以 `main_v2_final_clean.tex` 为当前成品源文件生成 `main_v2_final_terminology_cn.tex`，避免回退前序已完成的章节精简、caption 规范化和参考文献修正。

## 2. 术语替换表

| 原表达 | 修改后表达 | 修改位置 | 修改对象类型 | 是否完成 | 未修改原因 |
|---|---|---|---|---|---|
| realized pressure measure | 已实现压力测度 | 第 3.2、5.1、5.4、6 章正文与表注 | 正文 / 表注 / 小节标题 / 表格说明 | 完成 | figure caption 中的 `Realized pressure measures` 按任务边界保留 |
| realized measure | 已实现测度 | 第 1、2、3、5、6 章正文与表头 | 正文 / 表头 / 表格说明 | 完成 | `Realized GARCH` 作为模型名保留 |
| pinball loss | 分位损失 | QVAR 结果段、QVAR 表题、表头与稳健性结论表 | 正文 / 表题 / 表头 / 表格说明 | 完成 | 无 |
| Partial Effects | 局部效应 | SMARTBoost 正文解释段 | 正文 / 表格附近解释文字 | 完成 | figure caption 中 `SMARTBoost 核心变量 Partial Effects` 保持不变 |
| lift | 提升倍数 | 摘要后贡献段、SMARTBoost 结果段、Top-K 表题/表注、稳健性表 | 正文 / 表题 / 表头 / 表注 / 表格说明 | 完成 | Top-K 表头保留一次“提升倍数（lift）”作为指标括注；figure caption 中 `lift` 保持不变 |
| Top5率 | Top 5% 命中率 | SMARTBoost 指标表表头与表注 | 表头 / 表注 | 完成 | 无 |
| Top5召回 | Top 5% 召回率 | SMARTBoost 指标表表头 | 表头 | 完成 | 无 |
| logistic 概率映射函数 | Logistic 概率映射函数 | SMARTBoost 方法段 | 正文 | 完成 | 统一采用首字母大写的专有函数名写法 |
| slot | 日内时间片 | LSI 标准化说明、变量表、日内模式解释 | 正文 / 表格说明 | 完成 | 公式符号 `\mathrm{train},\mathrm{slot}` 按任务边界保留 |
| validation / test | 验证集 / 测试集 | 标签分布表、QVAR 表、SMARTBoost 指标表、样本外损失表头 | 表头 / 表格行名 / 正文 | 完成 | 无 |
| pressure innovation / 压力创新 | 压力冲击 | 本轮源文件中未残留；继续核查 | 正文 | 完成 | 无 |

## 3. 保留英文清单

以下英文或缩写属于模型名、变量名、指标缩写、数学符号或专业名词，按任务要求保留：

- 模型名：RGARCH-CARR-SK、QVAR、SMARTBoost、Realized GARCH。
- 压力指标与变量名：LSI、MarketLSI、Stress_H5、Stress_H10、CrossStress、FutureMaxLSI、IndexRet、IndexRV、MarketRelAmt、OHLCV。
- 评价指标与统计缩写：PR-AUC、ROC-AUC、Brier、Top-K、Top 5%、RV、RBV、MedRV、RMAD、AIC、BIC、LLK、R2LOG、MAE。
- 数学符号：`\mathrm{train}`、`\mathrm{slot}`、`\mathrm{Lift}_{\mathrm{TopK}}` 等公式内部符号。
- LaTeX 命令、BibTeX 条目、文件路径和图片文件名。

保留原因：上述表达属于论文的专业模型、变量、指标或公式标识，强行翻译会降低可读性并破坏与公式、图表、参考文献之间的一致性。

## 4. 未处理项说明

按本轮边界，以下英文项未修改：

- figure caption：`SMARTBoost 核心变量 Partial Effects`、`Realized pressure measures 标准化分布对比`、`不同高风险分组宽度下的真实压力发生率与 lift`。
- 公式符号：`\operatorname{Median}_{\mathrm{train},\mathrm{slot}}`、`\operatorname{MAD}_{\mathrm{train},\mathrm{slot}}`、`\mathrm{Lift}_{\mathrm{TopK}}`。
- 表头括注：Top-K 表头保留 `提升倍数（lift）`，用于首次明确该指标英文缩写。
- 图片内部英文、坐标轴、图例和图中标题未处理；本轮禁止修改图片文件或重画图。

## 5. 编译检查结果

- 编译链：XeLaTeX + BibTeX + XeLaTeX + XeLaTeX。
- 编译结果：成功生成 `main_v2_final_terminology_cn.pdf`，共 31 页。
- 日志检查：未发现 undefined references、undefined citations、Overfull 或 LaTeX Error。
- PDF 文本抽取检查：未发现“图 ??”、“表 ??”、“[?]”、“压力创新”、“pressure innovation”、“realized pressure measure”、“pinball loss”、“Top5率”、“Top5召回”或“logistic 概率映射函数”。
- 图片与图题检查：`includegraphics` 路径与 `main_v2_final_clean.tex` 完全一致；18 条 figure caption 与源文件完全一致。
