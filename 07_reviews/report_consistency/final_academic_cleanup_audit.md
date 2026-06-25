# main_v2 正式提交前修正审计

审计时间：2026-05-21

## 1. 不合适表述处理

- 删除或改写了“模型竞赛”“相互竞争的替代方案”“唯一正式”“防泄漏建模流程”“压缩”等表述。
- 将防御式边界改为正面学术表述，例如“时间边界约束”“预测特征边界”“训练期历史分布限定参数”“条件联动分析”。
- 将摘要中的工程化表述改为：严格时间顺序训练、验证与测试划分，且预测特征仅来自当前及历史可观测信息。
- 将“将分钟级 OHLCV 与成交额信息压缩为……”改为“综合为短时流动性压力代理指标”。

## 2. 图表与正文衔接修复

- 第 4 章：为样本结构表、时间轴图、核心变量表、覆盖率热力图、LSI 日内模式图、MarketLSI 图和标签分布表补充或强化“引出段—图表—解释段”结构。
- 第 5.1 节：保留条件压力风险路径和动态偏度路径；动态峰度仅作为模型诊断信息写入文字，不作为正文核心图展示；将 RGARCH 拟合准则表与样本外损失表之间加入承接解释。
- 第 5.2 节：保持 pinball loss 表、尾部分位响应图、压力情景表、四类情景响应图的顺序，并弱化因果识别防御性表述。
- 第 5.3 节：强化 PR 曲线、Top 5% 图、Top-K 表和 Partial Effects 图与“未来 H5/H10 压力事件预警能力”的关系。
- 第 6 章：为各稳健性小节加入或保留“检验目的—图表/表格—结论解释”结构，并使用 `\FloatBarrier` 限制图表跨小节漂移。

## 3. 浮动体位置与路径

- 将正文与附录主要 `figure/table` 浮动参数调整为 `[!htbp]`，并在关键小节边界加入 `\FloatBarrier`。
- 附录前保留 `\clearpage` 与 `\appendix`，附录图表未进入结论正文。
- 未新增图片路径，未移动图片文件，未重画图片。
- 备份与最终版本的 `\includegraphics` 路径数量均为 18，路径逐项一致，且均为相对路径。

## 4. 引用与编号检查

- 静态检查结果：无重复 `\label{}`，无缺失 `\ref{}`，无缺失 `\cite{}` key。
- `refs.bib` 未新增、未伪造文献；本文使用现有 BibTeX key。
- PDF 抽文本检查结果：未发现 `图 ??`、`表 ??`、`[?]` 或 `??`。
- 最终 log 检查结果：未发现 undefined references、undefined citations、Citation undefined 或 Reference undefined。

## 5. 图片解释与结果支撑

- 未发现没有对应解释段的正文核心图片。
- 附录图片均在附录内出现，并有简短解释。
- 未发现没有对应图表或表格支撑的新增结果段落。

## 6. 编译结果

- `main_v2_final.pdf` 完整编译成功。
- PDF 页数：33 页。
- 编译链：XeLaTeX + BibTeX + XeLaTeX + XeLaTeX。
- 使用 BibTeX 的依据：源文件采用 `\bibliographystyle{plain}` 与 `\bibliography{refs}`，未使用 `biblatex` / `biber`。
- 最终编译日志未保留 overfull、undefined reference 或 undefined citation 警告。

## 7. 交付文件

- `08_report/latex_project/main_v2_before_academic_cleanup.tex`
- `08_report/latex_project/main_v2_final.tex`
- `08_report/latex_project/main_v2_final.pdf`
- `07_reviews/report_consistency/final_academic_cleanup_audit.md`

