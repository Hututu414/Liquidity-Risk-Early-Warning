# Codex Handoff: Stage0-Stage3

## 读取的文件

- `README.md`
- `AGENTS.md`
- `CODEX.md`
- `00_admin/project_spec.md`
- `00_admin/no_code_manifest.md`
- `00_admin/task_board.md`
- `00_admin/semantic_residue_checklist.md`
- `04_code/README_AGENT_GENERATES_CODE_HERE.md`
- `04_code/EXPECTED_CODE_STRUCTURE.md`
- `prompts/codex_00_create_or_repair_project.md`
- `prompts/codex_01_core_pipeline_and_models.md`
- `.agents/skills/hft-data-audit/SKILL.md`
- `.agents/skills/minute-panel-feature-engineering/SKILL.md`
- `.agents/skills/no-lookahead-validation/SKILL.md`
- `.agents/skills/academic-visualization-cn/SKILL.md`
- `.agents/skills/semantic-residue-cleanup/SKILL.md`
- `02_data_inbox/preprocessed/quality/preprocessed_quality_report.md`
- `02_data_inbox/preprocessed/quality/preprocessed_security_list.csv`
- `02_data_inbox/preprocessed/panel/minute_panel_preprocessed_raw.parquet` metadata and samples

## 生成的代码文件

- `04_code/config/__init__.py`
- `04_code/config/paths.py`
- `04_code/config/project_config.yaml`
- `04_code/config/schema_minute_panel.yaml`
- `04_code/config/variable_config.yaml`
- `04_code/src/__init__.py`
- `04_code/src/common/__init__.py`
- `04_code/src/common/bootstrap.py`
- `04_code/src/common/config_loader.py`
- `04_code/src/common/features.py`
- `04_code/src/common/io_utils.py`
- `04_code/src/common/logging_utils.py`
- `04_code/src/common/splits.py`
- `04_code/src/common/time_utils.py`
- `04_code/src/data/00_verify_preprocessed_inputs.py`
- `04_code/src/data/01_make_model_ready_panel.py`
- `04_code/src/data/02_make_stress_components.py`
- `04_code/src/data/03_make_stress_index_and_labels.py`
- `04_code/src/diagnostics/04_descriptive_diagnostics.py`
- `04_code/src/visualization/plot_style.py`
- `04_code/src/report/semantic_residue_scan.py`
- `04_code/tests/test_paths.py`
- `04_code/tests/test_schema.py`
- `04_code/tests/test_no_lookahead.py`
- `04_code/tests/test_label_construction.py`
- `04_code/tests/test_time_split.py`

## 生成的 PowerShell 入口

- `run_stage0_verify_input.ps1`
- `run_stage1_make_model_ready_panel.ps1`
- `run_stage2_make_lsi_labels.ps1`
- `run_stage3_descriptive_diagnostics.ps1`

全部入口使用固定解释器：

```text
D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe
```

日志输出到 `09_pipeline_logs/`。

## 已成功运行的 stage

- Stage0 成功：`run_stage0_verify_input.ps1`
- Stage1 成功：`run_stage1_make_model_ready_panel.ps1`
- Stage2 成功：`run_stage2_make_lsi_labels.ps1`
- Stage3 成功：`run_stage3_descriptive_diagnostics.ps1`

说明：Stage3 第一次运行时 matplotlib 使用 Tk 后端失败，已改为 `Agg` 后端并重跑成功。旧 traceback 保留在 `07_reviews/stage_failures/stage3_descriptive_diagnostics_failure.txt`，用于记录已修复问题。

## 每个 stage 的输出位置

### Stage0

- `03_data_intermediate/stage0_input_profile/input_profile.json`
- `03_data_intermediate/stage0_input_profile/schema_check.csv`
- `07_reviews/data_audit/stage0_input_audit.md`

原始 parquet 行数：14,546,275；row groups：1,470；required schema 通过。

### Stage1

- `03_data_intermediate/stage1_model_ready/model_ready_panel_by_code/*.parquet`
- `03_data_intermediate/stage1_model_ready/model_ready_manifest.csv`
- `03_data_intermediate/stage1_model_ready/coverage_by_code_date.csv`
- `03_data_intermediate/stage1_model_ready/excluded_code_dates.csv`
- `03_data_intermediate/stage1_model_ready/duplicate_code_datetime_rows.csv`
- `03_data_intermediate/stage1_model_ready/stage1_metadata.json`
- `07_reviews/data_audit/stage1_model_ready_audit.md`

结果：84 个证券 shard；模型就绪行数 14,536,695；剔除 code-date 数 51；重复 code-datetime 行数 0。

### Stage2

- `03_data_intermediate/stage2_lsi_labels/stress_components_raw_by_code/*.parquet`
- `03_data_intermediate/stage2_lsi_labels/standardization_params_train_code_slot.parquet`
- `03_data_intermediate/stage2_lsi_labels/time_split.json`
- `03_data_intermediate/stage2_lsi_labels/label_thresholds_train.json`
- `03_data_intermediate/stage2_lsi_labels/market_context.parquet`
- `03_data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet`
- `03_data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv`
- `07_reviews/leakage_audit/stage2a_components_audit.md`
- `07_reviews/leakage_audit/no_lookahead_audit.md`

结果：最终变量标签行数 14,536,695。时间切分为：

- 训练期：2023-05-15 至 2025-02-28
- 验证期：2025-03-03 至 2025-09-26
- 测试期：2025-09-29 至 2026-05-13

训练期标签阈值：

- H5：7.972218375552092
- H10：9.606480057878922

### Stage3

- `05_outputs/descriptive_diagnostics/tables/summary_statistics_by_code.csv`
- `05_outputs/descriptive_diagnostics/tables/lsi_intraday_by_slot.csv`
- `05_outputs/descriptive_diagnostics/tables/stress_rate_by_date.csv`
- `05_outputs/descriptive_diagnostics/tables/market_context_by_datetime.csv`
- `05_outputs/descriptive_diagnostics/figures/fig_lsi_intraday.png`
- `05_outputs/descriptive_diagnostics/figures/fig_stress_rate_timeseries.png`
- `05_outputs/descriptive_diagnostics/figures/fig_market_lsi_timeseries.png`
- `07_reviews/data_audit/stage3_descriptive_diagnostics.md`

## 修改过的配置

本轮新建配置：

- `04_code/config/project_config.yaml`
- `04_code/config/schema_minute_panel.yaml`
- `04_code/config/variable_config.yaml`

关键配置：

- 连续交易 slot 数：240
- code-date 有效分钟阈值：236
- LSI 窗口：5、10、20
- 标签 horizon：5、10
- 训练期分位阈值：0.9
- 标准化：训练期 code-slot median/MAD

## 缺包情况

- `pytest` 缺失，已记录到 `07_reviews/environment_missing_packages.md`。
- 该缺包只影响额外运行 `04_code/tests/`，不影响 stage0-stage3 主流程。
- 未安装任何包。

## 数据字段不匹配

未发现 required schema 不匹配。raw parquet 包含：

```text
code, is_index, datetime, date, time, year, month, open, high, low, close, volume, amount, source_file, source_sheet, batch, row_in_sheet
```

## 内存或性能风险

- stage2 已按 code shard 读写，避免全量 DataFrame rolling。
- 最终 `lsi_labels_by_code` 约 4.33 GB，后续模型阶段不要一次性读入全部列。
- 建议后续模型只读取必要列，并继续按 date window 或 code batch 处理。
- `market_context_by_datetime.csv` 约 19 MB，可用于快速诊断，但正式建模优先读 parquet shard。

## 下一步建议 Gemini 做什么

- 基于 Stage3 输出补充数据章节初稿。
- 检查 `excluded_code_dates.csv` 中被剔除样本是否集中于个别证券或日期。
- 细化描述性图表，包括覆盖热力图、日内 LSI 分位带、CrossStress 时间序列。

## 下一步建议 DeepSeek v4 检查什么

- 审查 schema、字段命名、变量定义和图表标题一致性。
- 检查 `no_lookahead_audit.md`、标准化参数和标签阈值是否只来自训练期。
- 运行语义残留扫描，区分正式输出与项目管理文件的允许范围。

## 下一步建议 Codex 在核心模型阶段做什么

- 不实现新主模型，继续只围绕 RGARCH-CARR-SK、QVAR、SMARTboost。
- 为 RGARCH-CARR-SK 明确完整或简化口径，并写实现说明。
- 为 QVAR 设计严格的时间滚动样本外估计与尾部传导输出。
- SMARTboost 先做文献、DOI、算法和代码可复现性核验；若不能核验，生成 blocker。
- 模型阶段继续使用 fixed Python，不使用随机划分。

