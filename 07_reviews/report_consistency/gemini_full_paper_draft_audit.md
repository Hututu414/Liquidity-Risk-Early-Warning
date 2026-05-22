# Gemini Full Paper Draft Audit

> **Audit Date:** 2026-05-20  
> **Auditor:** Gemini Agent  
> **Target:** `08_report/report_fragments/full_paper_gemini_draft.md`及各个章节 fragments

## 1. 结构完整性核验

- [x] **摘要与标题**：已包含。明确了基于 OHLCV 的 LSI 构造，并强调了三模型递进证据链（RGARCH-CARR-SK、QVAR、SMARTBoost）。避免了过度承诺因果识别与收益率预测的表述。
- [x] **各章节 Fragments**：1 至 9 章均已生成并填充。
- [x] **参考文献**：已提供基础框架和待补充占位符。

## 2. 语义残留与禁令合规核验

- [x] **语义残留清除**：原 `chapter_05_descriptive.md` 中的“价格发现”已被成功替换为“开盘定价”。未发现诸如“期货”、“套期保值”、“IF”、“VECM”、“ETF 510300”、“配对交易”等旧项目禁语。
- [x] **非过度承诺**：
  - QVAR 部分已写明为“基于已估计系数的情景模拟”，不代表严格因果识别。
  - SMARTBoost 明确不作收益率预测，且是在剔除泄漏变量 `CrossStress` 后的实证结论。
  - RGARCH-CARR-SK 的解释聚焦于条件压力风险及其高阶矩特征。

## 3. 数据与图表指标核对

- **数据基础**：明确提及约 84 只证券，2023-05-15 至 2026-05-13，以及 H5 约 9.1% 的基础事件率（描述性）。
- **SMARTBoost 结果**：使用了准确的测试集指标，H5-test PR-AUC 为 0.603，Top 5% Lift 约 10.9 倍；H10-test PR-AUC 为 0.545，Top 5% Lift 约 9.7 倍。
- **图表引用**：使用了如（见 QVAR 尾部分位响应图）、（见 SMARTBoost Partial Effects 图）等占位表述，图号未硬编码，以便后续 Codex 进行统一编号及跨文件同步。

## 4. 后续 Codex 精修建议 (Action Items for Codex)

1. **图表编号统一**：将文本中如“图 5.1”、“（图 7.2）”以及各类括号内图名引用，统一映射至最新的 Figure Registry 编号。
2. **文献补充**：将 `[待补充引用]` 替换为正式的 BibTeX 交叉引用格式，并完善引言、文献综述和结论部分的相关文献论述。
3. **公式排版**：对 Markdown 格式下的数学公式进行确认，以确保随后能够被 LaTeX 引擎（如 XeLaTeX/pdflatex）无缝编译。
4. **数值精度核对**：精修定稿时，建议再次检查 SMARTBoost 指标（例如 59.3%、10.9 倍）与最新的 `smartboost_metrics.csv` 中的舍入是否完全一致。
5. **润色与学术化表述**：在粗稿基础上，进行最终的语言润色，提高表达的严谨性与连贯性。
