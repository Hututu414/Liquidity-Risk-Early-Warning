# Liquidity Risk Early Warning

This repository is a research workspace for testing whether A-share one-minute OHLCV and trading-amount data can warn of short-horizon liquidity pressure over the next 5 or 10 minutes.

The formal paper pipeline centers on three models:

1. RGARCH-CARR-SK
2. QVAR
3. SMARTBoost

The `experiments/onset_baseline_check/` experiment is an additional diagnostic for checking whether warning performance mainly reflects LSI persistence or provides incremental onset-warning value.

## What Is Tracked

Tracked files should include source code, configuration, small result summaries, Markdown reports, and paper-ready figures/tables when their size is reasonable.

Large raw and intermediate data files are intentionally not meant to be committed to GitHub. Restore them in the expected folders before running data-dependent experiments.

## Repository Layout

- `code/`: existing data, model, visualization, and report scripts.
- `src/liquidity_risk/`: lightweight package namespace for future shared helpers.
- `experiments/onset_baseline_check/`: isolated onset baseline experiment.
- `scripts/`: cloud/local validation helpers.
- `docs/`: project audit, data contract, and administrative documentation.
- `.devcontainer/`: GitHub Codespaces configuration.
- `.github/workflows/`: GitHub Actions workflows.
- `report/latex_project/`: LaTeX paper sources and compiled paper assets.
- `outputs/`: existing figures and tables.
- `data_inbox/`, `data_intermediate/`: local data staging and generated intermediate data; large files are ignored by Git.

## Local Setup

On Windows for local research runs, follow the project-specific Python interpreter documented in `AGENTS.md`. Do not hard-code local absolute interpreter paths into repository files.

For generic Linux/macOS/Codespaces use:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/prepare_environment.py
python scripts/list_required_data.py
```

## Data Placement

The onset experiment expects the stage-2 LSI label contract documented in:

```text
docs/data_contract.md
```

The main required files are:

```text
data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv
data_intermediate/stage2_lsi_labels/time_split.json
data_intermediate/stage2_lsi_labels/label_thresholds_train.json
data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet
```

Do not commit large parquet/csv.gz/csv raw or intermediate data files. Place them into the workspace manually, through a private artifact, or through another secure data-transfer process before running real experiments.

## Codespaces

Open the repository in GitHub Codespaces. The devcontainer installs `requirements.txt` automatically.

After startup:

```bash
python scripts/prepare_environment.py
python scripts/list_required_data.py
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke
```

Codespaces does not automatically run the full experiment.

## Onset Experiment Modes

Run from the repository root:

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke
python experiments/onset_baseline_check/run_onset_baseline.py --mode bounded
python experiments/onset_baseline_check/run_onset_baseline.py --mode full --resume
```

Modes:

- `smoke`: small sample, small bootstrap, meant to finish quickly and validate the pipeline.
- `bounded`: default diagnostic mode, 20 stock-code cap and 200 bootstrap iterations.
- `full`: complete stock pool and 500 bootstrap iterations; use only for formal paper-grade output and run it manually.

Useful overrides:

```bash
python experiments/onset_baseline_check/run_onset_baseline.py \
  --mode bounded \
  --max-stock-codes 20 \
  --bootstrap 200 \
  --threshold-quantile 0.90 \
  --gap 5 \
  --lookback-clean 10 \
  --resume
```

Outputs are written to:

```text
experiments/onset_baseline_check/outputs/
experiments/onset_baseline_check/logs/
experiments/onset_baseline_check/checkpoints/
```

## GitHub Actions

Two workflows are provided:

- `Smoke test`: runs on push, pull request, or manual dispatch. It installs dependencies, checks the environment, scans data contracts, compiles core scripts, and only runs onset smoke mode when the required stage-2 manifest is present.
- `Onset baseline`: manual `workflow_dispatch` only. It accepts mode, stock cap, bootstrap, threshold, gap, and lookback parameters, then uploads outputs/logs/checkpoints as artifacts even if the run fails.

To run manually:

1. Open the repository on GitHub.
2. Go to `Actions`.
3. Choose `Onset baseline`.
4. Click `Run workflow`.
5. Select `smoke`, `bounded`, or `full`.
6. Download artifacts from the completed workflow run.

The full experiment is never triggered automatically by push or pull request.

## Resume Interrupted Runs

Use:

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode full --resume
```

Run logs are written under `experiments/onset_baseline_check/logs/`. Checkpoint markers are written under `experiments/onset_baseline_check/checkpoints/`. Large binary checkpoint files are ignored by Git, while small JSON markers can be retained.

## Common Failure Causes

- Stage-2 LSI manifest or parquet shards are missing in the cloud runtime.
- Large data files were not restored after cloning the repository.
- Required Python packages were not installed.
- Full mode exceeds available memory or runtime.
- A previous local run left only process logs but not complete outputs.

Read:

```text
experiments/onset_baseline_check/outputs/cloud_run_summary.md
experiments/onset_baseline_check/outputs/run_log.txt
```

for concrete failure context.

## Paper Safety

The cloud scaffolding and onset experiment do not automatically modify LaTeX paper body files. Any integration into `report/latex_project/` should be done in a separate manuscript-editing task.
