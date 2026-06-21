# Codespaces Bounded Checklist

Use this checklist after the cloud-readiness branch is pushed and GitHub Actions smoke has passed. Do not run full until bounded has completed successfully and artifacts have been reviewed.

## 本地轻量模式与云端重计算规则

- Local Windows is for code edits, git checks, documentation, `py_compile`, and very small smoke tests only.
- Do not merge or build a `full80` panel locally.
- Do not run `bounded` or `full` locally.
- Do not run large bootstrap jobs, all-stock model training, or full shard scans locally.
- Run heavy jobs in Codespaces or GitHub Actions.
- In cloud, set `CLOUD_RUN=1` before running bounded/full.
- Confirm Codespaces with `echo "$CODESPACES"`; it should return `true`.
- Keep parquet, checkpoint, joblib, raw data, logs, and large output artifacts ignored and uncommitted.
- If local Windows is unstable, do not use local `--resume` full.

## 1. Open Codespaces

Open the repository branch:

```text
codex/cloud-readiness-round3
```

Wait for the devcontainer dependency installation to finish.

## 2. Basic Environment Checks

Run:

```bash
python scripts/prepare_environment.py
python scripts/list_required_data.py
```

Expected result:

- Python dependencies are available.
- Data-contract scan either finds the model panel or clearly reports that real data is missing.

## 3. Restore Complete Model Panel in Cloud

Do not generate the complete model panel on the unstable local Windows machine.
Restore it in Codespaces or GitHub Actions from a private artifact, manual upload,
or another cloud-side data source.

## 4. Move Data into Codespaces

Place the complete panel at:

```text
data/processed/onset_model_panel.parquet
```

Recommended options:

- manually upload the parquet to Codespaces;
- provide `data_url` and optional `data_sha256` to the manual GitHub Actions workflow;
- use GitHub CLI or Codespaces file transfer if already configured.

Do not write tokens, cookies, or private URLs into repository files.

## 5. Confirm Data Contract in Codespaces

Run:

```bash
python scripts/list_required_data.py
```

The full panel should appear as an `[OK]` candidate and satisfy the minimum onset model-panel contract.

## 6. Run Bounded Preflight Only

Before running bounded, run:

```bash
python scripts/run_bounded_onset_cloud_ready.py
```

This script should confirm:

- `data/processed/onset_model_panel.parquet` exists;
- required fields are present;
- checkpoint manifest status is visible;
- the recommended bounded command is printed.

The script does not execute bounded unless `--execute` is explicitly passed.

## 7. Bounded Command for Next Round

Only after the preflight passes, a later round may execute:

```bash
export CLOUD_RUN=1
python experiments/onset_baseline_check/run_onset_baseline.py --mode bounded --max-stock-codes 20 --bootstrap 200 --threshold-quantile 0.90 --gap 5 --lookback-clean 10 --data-path data/processed/onset_model_panel.parquet --resume
```

## 8. Artifacts to Review After Bounded

Inspect:

- `experiments/onset_baseline_check/outputs/model_comparison_summary.csv`
- `experiments/onset_baseline_check/outputs/delta_vs_persistence.csv`
- `experiments/onset_baseline_check/outputs/inclusion_decision_note.md`
- `experiments/onset_baseline_check/outputs/cloud_run_summary.md`
- `experiments/onset_baseline_check/logs/run_*.log`
- `experiments/onset_baseline_check/checkpoints/manifest.json`

## 9. Do Not Enter Full If

Do not proceed to full if any of the following holds:

- bounded failed;
- resume did not reuse cache where expected;
- Delta PR-AUC is unstable;
- bootstrap output is missing;
- event-level metrics are missing;
- artifacts did not upload or save correctly;
- runtime or memory usage is not controlled;
- the data source or date range is not the intended complete panel.

## 10. Guardrail

This checklist prepares bounded. It does not authorize running full.
