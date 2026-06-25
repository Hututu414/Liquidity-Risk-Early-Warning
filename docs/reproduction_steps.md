# Reproduction Steps

本文件说明如何复现代码仓库中的 onset baseline 检查和核心展示结果。论文 TeX/PDF 不属于本仓库发布内容。

## 1. Clone And Install

```bash
git clone https://github.com/Hututu414/Liquidity-Risk-Early-Warning.git
cd Liquidity-Risk-Early-Warning
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Place Data

将模型就绪面板放到：

```text
data/processed/onset_model_panel_full80.parquet
```

该文件不提交 Git。若只查看代码和文档，可以不放置数据；若运行实验，必须放置。

## 3. Check Environment

```bash
python scripts/prepare_environment.py
python scripts/list_required_data.py
```

`list_required_data.py` 会扫描候选数据文件和字段，不应把大数据文件加入 Git。

## 4. Run Smoke Test

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --data-path data/processed/onset_model_panel_full80.parquet
```

smoke test 用于检查依赖、数据读取、标签构造、训练和输出写入链路。

## 5. Run Onset Baseline

bounded 检查：

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode bounded --resume --data-path data/processed/onset_model_panel_full80.parquet
```

full 检查：

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode full --resume --max-stock-codes null --bootstrap 500 --threshold-quantile 0.90 --gap 5 --lookback-clean 10 --data-path data/processed/onset_model_panel_full80.parquet
```

如果运行中断，使用同一命令加 `--resume` 继续。

## 6. Outputs

主要输出目录：

```text
experiments/onset_baseline_check/outputs/
```

可保留的小型结果文件包括：

```text
*.csv
*.md
*.png
```

不提交：

```text
experiments/onset_baseline_check/checkpoints/
experiments/onset_baseline_check/logs/
*.joblib
*.pkl
*.parquet
```

## 7. Generate Figures

onset baseline 图表由实验脚本自动生成。运行 bounded 或 full 后，检查：

```text
experiments/onset_baseline_check/outputs/fig_pr_curves_onset.png
experiments/onset_baseline_check/outputs/fig_feature_importance_onset.png
experiments/onset_baseline_check/outputs/fig_topk_lift_onset.png
```

本次代码发布保留的核心展示图位于：

```text
figures/
```

完整图片清单见：

```text
docs/figure_inventory.md
```

## 8. Git Safety Check Before Commit

提交前运行：

```bash
git status --short
git diff --cached --name-only
```

确认 staged 文件中没有：

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
