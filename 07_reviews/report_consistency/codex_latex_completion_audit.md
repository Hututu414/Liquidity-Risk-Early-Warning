# Codex LaTeX 完整化审计

## 已完成
- 重写 `main.tex`，补充表格、图片、引用与排版包。
- 重写 01--09 章，使正文围绕分钟级高频数据、LSI、RGARCH-CARR-SK、QVAR 与 SMARTBoost 展开。
- 将核心 PNG 从 `05_outputs/figures/` 复制到 LaTeX 工程 `figures/`，未修改原图。
- 从 CSV/JSON 结果抽取摘要指标，生成 `booktabs` 三线表。
- 修正 CrossStress 表述：可作为 QVAR 系统状态变量，但不进入 SMARTBoost 预测特征。
- 修正 QVAR 表述：情景模拟不是严格因果识别，且不同情景响应路径存在差异。
- 修正 RGARCH 表述：R2LOG 为损失指标，动态峰度局部跳动不解释为重大结构突变。

## 生成的 LaTeX 表
- `08_report\latex_project\tables\tab_model_framework.tex`: 研究框架与三类模型功能定位
- `08_report\latex_project\tables\tab_variable_definition.tex`: 核心变量与压力标签定义
- `08_report\latex_project\tables\tab_sample_cleaning.tex`: 样本结构与数据清洗结果
- `08_report\latex_project\tables\tab_label_distribution.tex`: 压力标签分布
- `08_report\latex_project\tables\tab_rgarch_fit_loss.tex`: RGARCH-CARR-SK 拟合准则与样本外损失
- `08_report\latex_project\tables\tab_qvar_pinball.tex`: QVAR MarketLSI 方程样本外 pinball loss
- `08_report\latex_project\tables\tab_qvar_scenarios.tex`: QVAR 压力测试情景设定
- `08_report\latex_project\tables\tab_smartboost_metrics.tex`: SMARTBoost validation/test 样本外预测指标
- `08_report\latex_project\tables\tab_smartboost_topk.tex`: SMARTBoost test 高风险组命中率与 lift
- `08_report\latex_project\tables\tab_smartboost_leakage.tex`: SMARTBoost 防泄漏特征检查
- `08_report\latex_project\tables\tab_robustness_summary.tex`: 稳健性检验汇总

## 插入的核心图
- `figures/fig_timeline.png`: 研究样本划分时间轴 (正文)
- `figures/fig_coverage.png`: 股票-月份有效分钟覆盖率热力图 (正文)
- `figures/fig_intraday.png`: LSI_5 日内模式 (正文)
- `figures/fig_marketlsi.png`: MarketLSI 日度时间序列 (正文)
- `figures/fig_event_rate.png`: H5/H10 压力事件率 (正文)
- `figures/fig_corr.png`: 核心变量相关性热力图 (正文/附录)
- `figures/fig_rgarch_risk.png`: RGARCH-CARR-SK 条件压力风险路径 (正文)
- `figures/fig_rgarch_realized.png`: realized pressure measures 对比 (正文)
- `figures/fig_rgarch_loss.png`: RGARCH-CARR-SK R2LOG 样本外损失 (正文)
- `figures/fig_qvar_response.png`: QVAR 尾部分位响应 (正文)
- `figures/fig_qvar_stress.png`: QVAR 四类压力测试情景 (正文)
- `figures/fig_qvar_pinball.png`: QVAR pinball loss (附录/正文补充)
- `figures/fig_sb_pr.png`: SMARTBoost PR 曲线 (正文)
- `figures/fig_sb_top5.png`: SMARTBoost Top 5% 高风险组真实压力发生率 (正文)
- `figures/fig_sb_partial.png`: SMARTBoost Partial Effects (正文)
- `figures/fig_sb_calibration.png`: SMARTBoost calibration 曲线 (附录/正文补充)
- `figures/fig_robust_label_threshold.png`: 标签阈值稳健性 (正文)
- `figures/fig_robust_rgarch_measure.png`: RGARCH realized measure 稳健性 (正文/附录)
- `figures/fig_robust_sb_ablation.png`: SMARTBoost 特征组消融 (正文/附录)
- `figures/fig_robust_sb_topk.png`: SMARTBoost Top-K 稳健性 (正文)

## 不适合正文的图表
- `05_outputs/figures/99_paper_ready/` 下的历史派生图不作为本版来源。
- SMARTBoost ROC 曲线和 calibration 曲线只作为辅助，不作为主证据。
- SMARTBoost feature importance 若为空或全 0，不进入正文。

## 待人工复核
- Liu、Zhou 和 Chen (2025) 的完整期刊卷期页码仍需根据最终文献信息补齐。
- 论文最终排版仍建议人工检查长表宽度和图题页码位置。

## 编译状态
- 已运行 `xelatex -> bibtex -> xelatex -> xelatex`。
- `08_report/latex_project/main.pdf` 已生成，大小约 3.8 MB。
- 最终 `main.log` 未检出 undefined references、citation warning、overfull hbox、TeX error 或 emergency stop。
