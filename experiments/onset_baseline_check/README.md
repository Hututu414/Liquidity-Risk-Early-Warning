# Onset Baseline Check

This isolated experiment tests whether short-horizon liquidity-pressure warnings mainly reflect LSI persistence or contain incremental onset-warning value beyond persistence.

The script first looks for the model-ready full80 panel at `data/processed/onset_model_panel_full80.parquet`. It can fall back to existing stage-2 LSI label shards for local compatibility. All outputs are written under this experiment directory, and the script does not modify the paper, final LaTeX files, existing paper figures, or the original data pipeline.

## Entry Point

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --data-path data/processed/onset_model_panel_full80.parquet
python experiments/onset_baseline_check/run_onset_baseline.py --mode bounded --data-path data/processed/onset_model_panel_full80.parquet
python experiments/onset_baseline_check/run_onset_baseline.py --mode full --resume --data-path data/processed/onset_model_panel_full80.parquet
```

## Modes

- `smoke`: very small stock cap, small bootstrap count, and reduced evaluation. Intended for CI and quick pipeline validation.
- `bounded`: default diagnostic mode. Uses a 20-stock cap and 200 bootstrap iterations.
- `full`: complete stock pool and 500 bootstrap iterations. Intended only for manual paper-grade runs.

The full mode is never run automatically by GitHub Actions.

## Key Arguments

```bash
--mode smoke|bounded|full
--max-stock-codes 5|20|null
--bootstrap 50|200|500
--threshold-quantile 0.85|0.90|0.95
--gap 5|10
--lookback-clean 5|10|20
--resume
--dry-run
--config experiments/onset_baseline_check/config_onset_baseline.yaml
--data-path data/processed/onset_model_panel_full80.parquet
```

## Outputs

- `outputs/onset_baseline_report.md`
- `outputs/inclusion_decision_note.md`
- `outputs/cloud_run_summary.md`
- `outputs/model_comparison_summary.csv`
- `outputs/feature_group_increment_table.csv`
- `outputs/bootstrap_ci.csv`
- `outputs/event_level_metrics.csv`
- `outputs/*.png`
- `logs/run_YYYYMMDD_HHMMSS.log`
- `checkpoints/*.json`

## Safeguards

- Reuses the existing train/validation/test split.
- Builds onset labels with a prediction gap and a clean lookback window.
- Keeps original `Stress_H5` and `Stress_H10` as continuation-task controls.
- Compares naive persistence ranking, Logit, LightGBM, and the existing project-style SMARTBoost Python adaptation.
- Excludes `Stress_H5`, `Stress_H10`, `future_max_*`, `CrossStress`, and other future-label fields from features.
- Uses deterministic stock-code caps for smoke and bounded modes.
- Runs a pandas-vs-NumPy onset-label equivalence check before full mode.

## Data Contract

See:

```text
docs/data_contract.md
```

Run:

```bash
python scripts/list_required_data.py
```

to inspect available candidate data without loading large files fully.
