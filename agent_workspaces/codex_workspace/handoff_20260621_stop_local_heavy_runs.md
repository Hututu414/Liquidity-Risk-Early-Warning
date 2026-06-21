# Handoff: stop local heavy runs

Date: 2026-06-21

## Current Policy

The local Windows machine is unstable and is now restricted to lightweight management:

- code edits;
- git checks;
- documentation;
- `py_compile`;
- dry-run checks;
- very small smoke runs only.

Do not run local bounded, local full, local full80 panel construction, local full shard merging, or local large bootstrap.

## Current Full Run Status

- The local final full run was interrupted and must not be resumed locally.
- No live heavy Python process was found at the final stop check.
- Logs were preserved under `experiments/onset_baseline_check/logs/`.
- Checkpoints and existing outputs were preserved under `experiments/onset_baseline_check/checkpoints/` and `experiments/onset_baseline_check/outputs/`.
- The allowed local smoke verification produced `run_20260621_161307.log` and refreshed top-level files in `experiments/onset_baseline_check/outputs/`; do not interpret those refreshed top-level files as final full results.

## Reliable Results Already Available

- `bounded20` run completed earlier and remains available in the local outputs/checkpoints.
- all-stock diagnostic completed earlier on the full80 panel.
- feature leakage audit was completed.
- corrected event-level evaluation was implemented and diagnostic recomputation completed.
- budgeted event evaluation has been wired into the final full runner and diagnostic budgeted outputs were generated locally before the local-heavy ban. Full-run budgeted evaluation is not complete.

## Not Completed

- final full run;
- full bootstrap-500 final evaluation;
- full budget-constrained event evaluation;
- final full result digest;
- final full archive;
- any paper reconstruction based on final full.

## Next Cloud Tasks

In Codespaces or GitHub Actions:

```bash
export CLOUD_RUN=1

python scripts/prepare_environment.py
python scripts/list_required_data.py

python experiments/onset_baseline_check/run_onset_baseline.py \
  --mode full \
  --max-stock-codes null \
  --bootstrap 500 \
  --threshold-quantile 0.90 \
  --gap 5 \
  --lookback-clean 10 \
  --data-path data/processed/onset_model_panel_full80.parquet \
  --resume
```

If only corrected event metrics need recomputation after cloud model outputs exist:

```bash
python scripts/recompute_event_metrics.py \
  --data-path data/processed/onset_model_panel_full80.parquet \
  --predictions-dir experiments/onset_baseline_check/checkpoints \
  --outputs-dir experiments/onset_baseline_check/outputs \
  --mode full \
  --bootstrap 500 \
  --threshold-quantile 0.90 \
  --gap 5 \
  --lookback-clean 10 \
  --budgeted
```

## Do Not Run Locally

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode bounded
python experiments/onset_baseline_check/run_onset_baseline.py --mode full
python scripts/build_onset_model_panel.py --output data/processed/onset_model_panel_full80.parquet
python scripts/build_onset_model_panel.py --output data/processed/onset_model_panel.parquet
python scripts/run_bounded_onset_cloud_ready.py --execute
```
