# Liquidity Risk Early Warning

本仓库用于展示 A 股分钟级流动性压力 onset 预警项目的核心代码、配置、必要结果图和复现实验步骤。研究主题是：基于 A 股 1 分钟 OHLCV 与成交额数据，预警未来 5 或 10 分钟短时流动性压力 onset。

本仓库不是论文压缩包，也不包含论文 TeX 源文件、论文 PDF、Word 文件或写作材料包。

## Repository Contents

- `code/`: 数据检查、LSI 构造、标签生成、RGARCH-CARR-SK、QVAR、SMARTBoost、可视化和测试代码。
- `scripts/`: 环境检查、数据契约扫描、云端运行辅助脚本。
- `experiments/onset_baseline_check/`: onset baseline 实验代码、配置和小型结果输出。
- `figures/`: 保留给评阅者查看的核心结果图片。
- `docs/`: 数据契约、复现步骤、项目结构和清理审计文档。
- `.github/workflows/`: smoke test 与手动 onset baseline 工作流。
- `.devcontainer/`: GitHub Codespaces 配置。

## Data Files

默认数据文件路径：

```text
data/processed/onset_model_panel_full80.parquet
```

该 parquet 文件不提交 Git。原因是文件体积较大，包含分钟级研究面板数据，不适合进入公开代码仓库，也会超过 GitHub 对大文件的常规限制。复现时请在本地或 Codespaces 中手动放置该文件。

数据字段契约见 [docs/data_contract.md](docs/data_contract.md)。

## Environment

推荐 Python 3.10 或以上版本。

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

主要依赖包括 `pandas`、`pyarrow`、`scikit-learn`、`matplotlib`、`PyYAML`、`joblib` 和 `lightgbm`。

## Reproduction Steps

完整步骤见 [docs/reproduction_steps.md](docs/reproduction_steps.md)。最小流程：

```bash
python scripts/prepare_environment.py
python scripts/list_required_data.py
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke
```

## Smoke Test

smoke test 用于快速检查代码、依赖和数据契约：

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --data-path data/processed/onset_model_panel_full80.parquet
```

如果没有放置数据文件，GitHub Actions 的 smoke workflow 会跳过数据依赖型运行，只保留静态检查和编译检查。

## Onset Baseline

运行 bounded 检查：

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode bounded --resume --data-path data/processed/onset_model_panel_full80.parquet
```

运行 full 检查：

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode full --resume --max-stock-codes null --bootstrap 500 --threshold-quantile 0.90 --gap 5 --lookback-clean 10 --data-path data/processed/onset_model_panel_full80.parquet
```

结果写入：

```text
experiments/onset_baseline_check/outputs/
```

`checkpoints/` 和 `logs/` 仅用于本地或云端续跑，不进入 Git。

## Main Scripts

- `scripts/prepare_environment.py`: 检查目录、依赖和运行环境。
- `scripts/list_required_data.py`: 扫描候选数据文件和字段契约。
- `experiments/onset_baseline_check/run_onset_baseline.py`: onset baseline 训练、评价和小型图表输出。
- `code/src/data/00_verify_preprocessed_inputs.py`: 检查预处理输入。
- `code/src/data/01_make_model_ready_panel.py`: 构造模型就绪面板。
- `code/src/data/02_make_stress_components.py`: 构造流动性压力组成变量。
- `code/src/data/03_make_stress_index_and_labels.py`: 构造 LSI 与 onset 标签。
- `code/src/models/05_rgarch_carr_sk.py`: RGARCH-CARR-SK 模型。
- `code/src/models/06_qvar_tail_transmission.py`: QVAR tail 状态分析。
- `code/src/models/07_smartboost_forecasting.py`: SMARTBoost 训练与预测。
- `code/src/visualization/`: 图表生成脚本。

## Generate Figures

onset baseline 图表由实验脚本自动生成：

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode bounded --resume --data-path data/processed/onset_model_panel_full80.parquet
```

核心展示图已保存在：

```text
figures/
```

图片清单见 [docs/figure_inventory.md](docs/figure_inventory.md)。

## Git Policy

本仓库不提交：

```text
*.parquet
*.joblib
*.pkl
checkpoints/
data/raw/
data_inbox/
data_intermediate/
report/latex_project/
08_report/latex_project/
paper/
agent_workspaces/
```

提交前请检查：

```bash
git status --short
git diff --cached --name-only
```
