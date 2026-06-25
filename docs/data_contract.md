# Data Contract

默认复现实验数据文件：

```text
data/processed/onset_model_panel_full80.parquet
```

该文件不提交 Git。请在本地、Codespaces 或其他受控运行环境中手动放置。

## Expected Scale

参考 full80 面板规模：

- 股票范围：约 80 只非指数 A 股。
- 时间范围：约 2023-05-15 至 2026-05-13。
- 频率：1 分钟。
- 字段数：约 40 列。

实际复现时允许行数因数据清理版本略有差异，但字段语义必须一致。

## Required Columns

基础标识：

```text
code
date
datetime
slot
is_index
```

兼容标识：

```text
stock_code
symbol
```

原始 OHLCV 与成交额数据用于上游构造流程；`onset_model_panel_full80.parquet` 是模型就绪面板，默认不要求保留原始 OHLCV 列。

流动性压力组成变量：

```text
ILLIQ_5
Range_5
RV_5
RelAmt_5
ILLIQ_10
Range_10
RV_10
RelAmt_10
ILLIQ_20
Range_20
RV_20
RelAmt_20
```

标准化组成变量：

```text
z_ILLIQ_5
z_Range_5
z_RV_5
z_RelAmt_5
z_ILLIQ_10
z_Range_10
z_RV_10
z_RelAmt_10
z_ILLIQ_20
z_Range_20
z_RV_20
z_RelAmt_20
```

LSI、市场状态与标签：

```text
LSI_5
LSI_10
LSI_20
MarketLSI
IndexRet
IndexRV
MarketRelAmt
Stress_H5
Stress_H10
```

## Label Definition

onset baseline 使用统一标签设置：

```text
gap = 5
lookback_clean = 10
threshold_quantile = 0.90
horizons = H5, H10
```

实验脚本会在不改动原始 `Stress_H5` / `Stress_H10` 字段的前提下构造 onset 标签。

## Time Split

实验应使用训练、验证、测试边界，并在边界附近按 `gap + horizon` 做 embargo，避免未来窗口跨越样本区间。若使用旧的 stage2 shard 数据，切分文件可来自：

```text
data_intermediate/stage2_lsi_labels/time_split.json
```

该目录是本地中间产物，不提交 Git。

## Compatibility Fallback

`experiments/onset_baseline_check/run_onset_baseline.py` 优先读取 `data/processed/onset_model_panel_full80.parquet`。如果该文件不存在且未显式指定 `--data-path`，脚本仍可回退到旧的 shard manifest：

```text
data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv
```

该 fallback 只用于本地兼容，不是干净 GitHub 仓库的数据提交策略。

## Data Exclusion Policy

不得提交：

```text
*.parquet
data/raw/
data_inbox/
data_intermediate/
checkpoints/
*.joblib
*.pkl
```

可提交小型 schema/profile 文档，例如：

```text
data/processed/onset_model_panel_full80_schema.json
data/processed/onset_model_panel_full80_profile.md
```

## Validation

放置数据后运行：

```bash
python scripts/list_required_data.py
```

然后运行 smoke test：

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --data-path data/processed/onset_model_panel_full80.parquet
```
