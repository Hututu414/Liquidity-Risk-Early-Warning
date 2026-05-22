# Codex Handoff: Core Models

## 读取的文件

- `README.md`
- `AGENTS.md`
- `CODEX.md`
- `00_admin/project_spec.md`
- `00_admin/model_registry.md`
- `00_admin/figure_registry.md`
- `00_admin/table_registry.md`
- `06_agent_workspaces/codex_workspace/handoff_stage0_to_stage3.md`
- `06_agent_workspaces/gemini_workspace/handoff_stage3_diagnostics.md`
- `07_reviews/data_audit/gemini_stage3_data_diagnostics.md`
- `prompts/codex_01_core_pipeline_and_models.md`
- `.agents/skills/rgarch-carr-sk-risk/SKILL.md`
- `.agents/skills/qvar-tail-transmission/SKILL.md`
- `.agents/skills/smartboost-verification/SKILL.md`
- `.agents/skills/no-lookahead-validation/SKILL.md`

说明：`07_reviews/model_audit/deepseek_stage3_readiness_review.md` 在本地未发现；已有 `_deepseek_data_integrity_check.py`，但缺少用户指定的 readiness review Markdown。该缺口已记录在 `07_reviews/model_audit/core_model_readiness_check.md`，不阻断本轮建模。

## 修改和新增的代码

- 更新：`04_code/config/paths.py`
- 新增：`04_code/src/models/__init__.py`
- 新增：`04_code/src/models/model_data.py`
- 新增：`04_code/src/models/00_check_core_model_readiness.py`
- 新增：`04_code/src/models/05_rgarch_carr_sk.py`
- 新增：`04_code/src/models/06_qvar_tail_transmission.py`
- 新增：`04_code/src/models/07_smartboost_verification.py`
- 新增：`04_code/src/models/08_core_model_no_lookahead_audit.py`
- 更新：`00_admin/model_registry.md`
- 更新：`07_reviews/environment_missing_packages.md`

## 环境变更

QVAR 首次运行时，`statsmodels 0.14.4` 与预装 `scipy 1.17.1` 不兼容，导入失败。已按任务要求在固定虚拟环境中安装兼容版本：

```text
D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe -m pip install scipy==1.13.1
```

安装后 `statsmodels.api` 导入成功。未使用系统 Python、`py`、Conda 或 Microsoft Store Python。

本轮 RGARCH 原文 PDF 提取还安装了：

```text
D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe -m pip install pdfplumber pypdf
```

用途仅为读取 `01_materials/literature/1-s2.0-S1062940825000488-main.pdf` 并生成方程 digest。

## 模型实现情况

### RGARCH-CARR-SK

状态：已升级为原文框架驱动的 MarketLSI 压力风险适配实现。

本轮新增读取原文 PDF：

- `01_materials/literature/1-s2.0-S1062940825000488-main.pdf`

并生成方程 digest：

- `07_reviews/model_audit/rgarch_carr_sk_original_equation_digest.md`

当前 RGARCH 阶段应写成 **基于 Liu、Zhou 和 Chen（2025）RGARCH-CARR-SK 框架的 MarketLSI 压力风险适配实现**。实现保留原文 Eq. (1)-Eq. (6) 的主递推结构，包含 `log lambda_t`、measurement equation、dynamic skewness `s_t`、dynamic kurtosis `k_t` 和 leverage function `d(z_t)`；同时实现 Eq. (7)-Eq. (10) 的 GCE density，以及 Eq. (16)-Eq. (19) 的 MLE 结构。

模型说明：

- `07_reviews/model_audit/rgarch_carr_sk_model_note.md`

已实现的 generalized realized pressure measures：

- `RV_pressure`
- `RBV_pressure`
- `MedRV_pressure`
- `RMAD_pressure`

`RVaR_pressure_optional` 已计算为诊断变量，但未纳入主 MLE 表。

可进入报告的内容：

- 原文方程迁移与本项目变量映射；
- 四个 realized pressure measure 版本的参数估计；
- log likelihood / AIC / BIC；
- 条件压力风险路径；
- dynamic skewness / dynamic kurtosis paths；
- generalized realized pressure measures 对比；
- validation/test 样本外预测损失。

需要谨慎解释的内容：

- 本文不是原文 GEM 指数波动率复刻；
- `r_t` 是 MarketLSI 压力创新，不是资产收益率；
- VaR backtesting 和 VaR loss functions 尚未正式实现。

### QVAR

状态：已实现。

实现使用低维市场系统变量：

```text
MarketLSI, CrossStress, IndexRet, IndexRV, MarketRelAmt
```

分位点：

```text
0.10, 0.50, 0.90, 0.95
```

实现方式：每个方程用一阶滞后 QuantReg 分位数回归估计；训练期模型用于尾部分位响应与压力测试；验证期使用训练期模型，测试期使用训练+验证期扩展模型评估 pinball loss。

模型说明：

- `07_reviews/model_audit/qvar_model_note.md`

可进入报告的内容：

- QVAR 分位系数表；
- 尾部分位响应；
- 压力测试路径；
- blocked out-of-sample pinball loss。

### SMARTboost

状态：原文和代码核验通过；未做正式实证。

已核验：

- 原文：Paolo Giordani, `SMARTboost Learning for Tabular Data`, Journal of Financial Econometrics, Volume 23, Issue 3, 2025, nbae028；
- DOI：https://doi.org/10.1093/jjfinec/nbae028；
- 作者代码：https://github.com/PaoloGiordani/SMARTboost.jl；
- 算法定义：boosting of symmetric smooth additive regression trees；
- 损失函数：原文聚焦 Gaussian likelihood / squared loss；作者 Julia README 当前说明 `loss [:L2]`；
- 基学习器：symmetric smooth trees；
- 调参方式：CV 或验证集早停，并强调时间序列/面板不能随机 CV。

未生成 `SMARTBOOST_VERIFICATION_BLOCKER.md`，因为原文、DOI、算法定义和作者代码来源已可核验。但本轮未生成 SMARTboost 正式预测结论；后续需要单独确认 Julia/R bridge、purged chronological validation 和事件标签损失函数口径。

核验说明：

- `07_reviews/model_audit/smartboost_verification.md`

## 生成的表格

### RGARCH

- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_parameter_estimates.csv`
- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_fit_criteria.csv`
- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_conditional_paths.csv`
- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_realized_pressure_measures.csv`
- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_oos_losses.csv`
- `05_outputs/tables/04_rgarch/rgarch_carr_sk_adapted_scaling.csv`

### QVAR

- `05_outputs/tables/05_qvar/qvar_quantile_coefficients_train.csv`
- `05_outputs/tables/05_qvar/qvar_quantile_coefficients_train_plus_validation.csv`
- `05_outputs/tables/05_qvar/qvar_train_standardization_stats.csv`
- `05_outputs/tables/05_qvar/qvar_tail_quantile_response.csv`
- `05_outputs/tables/05_qvar/qvar_pressure_test_paths.csv`
- `05_outputs/tables/05_qvar/qvar_blocked_oos_pinball_loss.csv`

## 生成的图像

### RGARCH

- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_conditional_risk.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_skewness.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_dynamic_kurtosis.png`
- `05_outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png`

### QVAR

- `05_outputs/figures/05_qvar/fig_qvar_tail_quantile_response.png`
- `05_outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png`

## 防泄漏审计

- `07_reviews/leakage_audit/core_model_no_lookahead_audit.md`

结论：PASS。

审计要点：

- Stage2 标准化参数来自训练期 code-slot median/MAD；
- 标签阈值来自训练期；
- RGARCH-CARR-SK MarketLSI 适配模型参数只在训练期估计；
- QVAR 标准化参数来自训练期，验证/测试按时间顺序推进；
- 未使用随机打乱。

## 关键结果提示

RGARCH-CARR-SK 适配模型四个 realized pressure measure 版本均完成 MLE。训练期 log likelihood / AIC / BIC 表明 `RGARCH-CARR-SK-RV` 拟合准则最低；validation/test 样本外相对误差指标显示 `RGARCH-CARR-SK-RMAD` 更稳健。解释时应同时呈现拟合准则和样本外损失，不应只选择单一指标。

QVAR 已输出验证期和测试期 pinball loss；解释时应重点看 `MarketLSI` 与 `CrossStress` 的 0.90/0.95 分位响应，不要把 QVAR 写成收益率预测模型。

## 下一步建议 Gemini 如何解释结果

- RGARCH 结果应写成“原文框架的 MarketLSI 压力风险适配实现”，并明确本文不是原文 GEM 指数研究复刻。
- QVAR 解释应围绕 MarketLSI、CrossStress 与 IndexRV/MarketRelAmt 的尾部分位联动。
- SMARTboost 只能写“已核验、尚未实证”，不要写预测性能。

## 下一步建议 DeepSeek v4 如何做一致性检查

- 检查报告和图表标题是否明确“MarketLSI 压力风险适配实现”，且不再误写成简单 GARCH 代理。
- 检查 QVAR 是否被误写为均值 VAR 或收益率预测。
- 检查 SMARTboost 是否出现未经实证的性能结论。
- 检查输出路径、表号、图号是否与 registry 一致。
