# 术语、章节与图题注释规范化审计

生成时间：2026-05-21  
处理对象：`08_report/latex_project/main_v2_final_clean.tex`、`08_report/latex_project/refs.bib`  
编译产物：`08_report/latex_project/main_v2_final_clean.pdf`

## 1. 术语统一

- 将全文“压力创新”统一改为“压力冲击”。
- 替换数量：13 处。
- 修订后检查结果：`main_v2_final_clean.tex` 与 PDF 抽取文本中均未检出“压力创新”。
- 对 RGARCH-CARR-SK 方法段中的关键定义做了顺读修正：将 `r_t` 解释为 MarketLSI 相邻时点之间的新变化，将 `z_t` 解释为剔除条件风险尺度后的标准化压力冲击，避免机械替换造成语义不清。

## 2. 第 6.5 节删除

- 删除小节：`6.5 特征边界核查`。
- 删除内容包括该小节标题、正文、特征边界核查表及其 `tab:smartboost-leakage` 标签。
- 删除后章节编号变化：第 6 章保留 `6.1` 至 `6.4`，目录中不再出现 `6.5`。
- 保留的未来信息边界结论已并入 SMARTBoost 样本外结果解释段：预测特征矩阵排除由未来窗口或未来标签聚合得到的变量，滚动特征仅使用 `t` 时点及以前信息，训练、验证与测试样本按时间顺序划分。

## 3. 图表 caption 规范化

本轮将 caption 中的解释性长句移出或删除，使图题、表题主要回答“图表是什么”。修改清单如下：

- 表 `tab:lit-map`：文献脉络、代表文献与本文用途。
- 表 `tab:model-framework`：研究框架、技术实现与解释边界。
- 表 `tab:sample-structure`：样本结构与数据清洗结果。
- 图 `fig:timeline`：训练、验证与测试样本划分。
- 表 `tab:variables`：核心变量、压力标签与时间边界。
- 图 `fig:coverage`：股票—月份有效分钟覆盖率热力图。
- 图 `fig:intraday`：LSI_5 日内模式。
- 图 `fig:marketlsi`：MarketLSI 日度时间序列。
- 表 `tab:label-dist`：未来压力标签的样本区间分布。
- 图 `fig:rgarch-risk`：RGARCH-CARR-SK 条件压力风险路径。
- 图 `fig:rgarch_dynamic_skewness`：RGARCH-CARR-SK 动态偏度 `s_t` 路径。
- 表 `tab:rgarch-fit`：RGARCH-CARR-SK 拟合准则。
- 表 `tab:rgarch-loss`：RGARCH-CARR-SK 样本外损失。
- 表 `tab:qvar-pinball`：QVAR MarketLSI 方程样本外 pinball loss。
- 图 `fig:qvar-response`：QVAR 尾部分位响应。
- 表 `tab:qvar-scenarios`：QVAR 压力测试情景设定。
- 图 `fig:qvar-stress`：QVAR 四类压力测试情景响应路径。
- 表 `tab:smartboost-metrics`：SMARTBoost 验证集/测试集样本外预警指标。
- 图 `fig:sb-pr`：SMARTBoost 样本外 PR 曲线。
- 图 `fig:sb-top5`：SMARTBoost Top 5% 高风险组真实压力发生率。
- 表 `tab:sb-topk`：SMARTBoost 测试集高风险组真实压力发生率与 lift。
- 图 `fig:sb-partial`：SMARTBoost 核心变量 Partial Effects。
- 图 `fig:robust-label`：标签阈值变化下的 SMARTBoost 样本外预警表现。
- 图 `fig:rgarch-realized-dist`：Realized pressure measures 标准化分布对比。
- 图 `fig:qvar-tail-summary`：不同压力情景下 MarketLSI 最大响应的分位点差异。
- 图 `fig:robust-topk`：不同高风险分组宽度下的真实压力发生率与 lift。
- 表 `tab:robust-design`：稳健性检验设计汇总。
- 表 `tab:robust-conclusion`：稳健性检验核心结论。
- 附录图 `fig:app-event-rate`：H5/H10 压力事件率月度时间变化。
- 附录图 `fig:app-corr`：核心市场状态变量相关性热力图（日度）。
- 附录图 `fig:app-sb-calibration`：SMARTBoost 样本外校准曲线。

## 4. 解释移入正文的位置

- `fig:sb-pr`：将水平基准线和 PR 曲线含义移入图后正文。
- `fig:sb-top5`：将柱状图与菱形标记的含义移入图后正文。
- `fig:sb-partial`：将横轴分位数、纵轴预测概率变化的含义移入图前后正文。
- `fig:robust-label`：将 85%、90%、95% 阈值下 PR-AUC 与 Top 5% lift 的比较目的移入图前正文。
- `fig:qvar-tail-summary`：将 `q=0.50` 与 `q=0.95` 的最大响应比较目的移入图前正文。
- `fig:qvar-response` 与 `fig:qvar-stress`：将预测期含义、情景响应含义移入正文说明。
- `tab:smartboost-metrics`：精简表下注释，仅保留 Top5 率和 ROC-AUC 的必要说明。

## 5. 参考文献与正文引用修正

- SMARTBoost 文献 [12] 原条目：Paolo Giordani, David Kohns, and Mattias Villani. Smartboost: Sparse multivariate additive regression trees. Journal of Financial Econometrics, 23(3):nbae028, 2025.
- SMARTBoost 文献 [12] 修正后条目：Paolo Giordani. SMARTboost Learning for Tabular Data. Journal of Financial Econometrics, 23(3):nbae028, 2025.
- 正文中直接由“Giordani、Kohns 和 Villani \cite{giordani2025smartboost}”改为“Giordani \cite{giordani2025smartboost}”的表述：1 处。
- 同步将“Giordani 等 \cite{giordani2025smartboost}”规范为“Giordani \cite{giordani2025smartboost}”：2 处。
- 修订后 `main_v2_final_clean.tex` 中 SMARTBoost 文献引用位置：第 95、116、280 行。
- 已同步修改 `refs.bib` 中 `giordani2025smartboost` 条目；正文未使用 TeX 内置参考文献列表。
- 同步将 ECB 条目类型规范为 `European Central Bank Working Paper No.`，不改变文献来源。
- BibTeX 与 XeLaTeX 编译后未发现 undefined citations、重复引用或参考文献编号异常。

## 6. 编译与检查结果

- 编译链：XeLaTeX + BibTeX + XeLaTeX + XeLaTeX。
- 输出 PDF：`main_v2_final_clean.pdf`，共 31 页。
- 编译日志检查：未发现 undefined references、undefined citations、Overfull 或 LaTeX Error。
- PDF 文本抽取检查：未发现“压力创新”、“图 ??”、“表 ??”、“[?]”、“模型竞赛”、“这次任务”、“之前失败”、“工程代码”、“pipeline”、“特征边界核查”。
- 图片路径检查：沿用原有 `\includegraphics` 路径，未移动、重画或新增图片文件。
- 数据与模型结果：未修改 CSV、Parquet、Excel、PNG/PDF 图片文件，未修改模型数值或实证结论。
