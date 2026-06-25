# Cloud run guide

This guide explains how to run smoke and bounded onset-baseline checks in GitHub Codespaces or GitHub Actions. Do not run `full` until the prerequisites below are satisfied.

## 本地轻量模式与云端重计算规则

The local Windows machine is now treated as lightweight-only infrastructure:

- Local work is limited to code edits, git checks, documentation, `py_compile`, data listing, dry-run checks, and very small smoke tests.
- Do not build or merge `full80` panels locally.
- Do not run `bounded` or `full` locally.
- Do not run large bootstrap, all-stock model training, or full shard scans locally.
- Run heavy recomputation only in GitHub Codespaces, GitHub Actions, or another cloud runtime.
- Set `CLOUD_RUN=1` before cloud-side bounded/full commands so local heavy-run guards know the job is intentional.
- In Codespaces, confirm the environment with `echo "$CODESPACES"`; it should print `true`.
- Keep parquet, checkpoint, joblib, raw minute data, logs, and large outputs out of Git. Verify with `git check-ignore -v data/processed/onset_model_panel_full80.parquet`.
- If the local Windows machine is unstable, never use it to `--resume` full.

## 1. Local Smoke Test

Commands are shown with portable `python`; on the local Windows research machine, replace `python` with the project interpreter specified by `AGENTS.md`.

```bash
python scripts/prepare_environment.py
python scripts/list_required_data.py
python scripts/build_onset_model_panel.py --dry-run
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --max-stock-codes 3 --bootstrap 10
```

On Linux/macOS/Codespaces:

```bash
python scripts/prepare_environment.py
python scripts/list_required_data.py
python scripts/build_onset_model_panel.py --dry-run
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --max-stock-codes 3 --bootstrap 10
```

## 2. Codespaces Smoke Test

1. Open the repository in GitHub Codespaces.
2. Wait for `.devcontainer/devcontainer.json` to install `requirements.txt`.
3. Run:

```bash
python scripts/prepare_environment.py
python scripts/list_required_data.py
python scripts/build_onset_model_panel.py --dry-run
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --max-stock-codes 3 --bootstrap 10
```

If data is missing, the scripts should report the missing files or missing fields explicitly.

## 3. GitHub Actions Smoke Test

The `Smoke test` workflow runs on:

- `push`
- `pull_request`
- `workflow_dispatch`

It installs dependencies, checks the environment, scans data, runs `py_compile`, performs an onset panel dry run, and only runs the data-dependent smoke experiment if the stage-2 manifest is present.

## 4. GitHub Actions Bounded Run

Use the manual `Onset baseline` workflow:

1. Open `Actions`.
2. Select `Onset baseline`.
3. Click `Run workflow`.
4. Choose:
   - `mode=bounded`
   - `max_stock_codes=20`
   - `bootstrap=200`
   - `threshold_quantile=0.90`
   - `gap=5`
   - `lookback_clean=10`
   - leave `data_path` empty to use the default preference order: `data/processed/onset_model_panel.parquet` if present, otherwise stage-2 shards.
   - set `data_path=data/processed/onset_model_panel.parquet` only if that file has been restored in the runtime and you want a hard failure when it is missing.
   - set `data_url` only when a private model-panel parquet URL is available.
   - set `data_sha256` only when the downloaded parquet should be checksum-verified.

The workflow uploads outputs, logs, checkpoint manifest, this guide, and the git push checklist as artifacts even if the run fails.

If `data_url` is provided, the workflow downloads it to:

```text
data/processed/onset_model_panel.parquet
```

If `data_sha256` is provided, the workflow verifies the downloaded parquet with `sha256sum --check`. URLs and tokens are not hard-coded in the repository.

## 5. Full Run Prerequisites

Run `full` only after:

- A local or cloud smoke run succeeds.
- A bounded run succeeds on the same cloud data source.
- `cloud_run_summary.md` confirms the intended data path, stock count, date range, and parameters.
- Runtime and memory are sufficient.
- Checkpoint parameters match the requested full run.
- You explicitly choose `mode=full` in the manual workflow.

Full mode is never triggered automatically.

For final full, run from cloud with:

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

## 6. Data Placement

Preferred cloud input:

```text
data/processed/onset_model_panel.parquet
```

Fallback input:

```text
data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv
data_intermediate/stage2_lsi_labels/time_split.json
data_intermediate/stage2_lsi_labels/label_thresholds_train.json
data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet
```

Large data files should be restored through a private artifact or secure upload process, not committed to Git.

## 7. Build `onset_model_panel.parquet`

Dry run:

```bash
python scripts/build_onset_model_panel.py --dry-run
```

Small build:

```bash
python scripts/build_onset_model_panel.py --max-stock-codes 5 --output data/processed/onset_model_panel.parquet
```

Full build:

```bash
python scripts/build_onset_model_panel.py --output data/processed/onset_model_panel.parquet
```

The parquet file is ignored by Git. The script writes:

- `data/processed/onset_model_panel_schema.json`
- `data/processed/onset_model_panel_profile.md`

## 8. Check Data Contract

```bash
python scripts/list_required_data.py
```

The onset runner also validates required field groups before reading the model panel.

## 9. Download Artifacts

After a GitHub Actions run:

1. Open the workflow run.
2. Scroll to `Artifacts`.
3. Download the artifact archive.
4. Inspect:
   - `experiments/onset_baseline_check/outputs/cloud_run_summary.md`
   - `experiments/onset_baseline_check/outputs/run_log.txt`
   - `experiments/onset_baseline_check/outputs/inclusion_decision_note.md`
   - `experiments/onset_baseline_check/checkpoints/manifest.json`

## 10. Resume

Use:

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode bounded --resume
```

Resume checks the parameter signature in `checkpoints/manifest.json`, reuses matching model checkpoints, and skips a fully completed matching report stage. If a cache is missing or the signature differs, the stage is recomputed and logged.

## 11. Deciding Whether to Enter Full

Proceed to full only if:

- smoke passed;
- bounded passed;
- data source and date range are correct;
- model panel or stage2 shards are complete;
- no protected paper files were modified;
- checkpoint manifest is consistent;
- runtime budget is realistic.

## 12. Recommended Order After Round 3

1. Push the cloud-readiness branch.
2. Verify GitHub Actions smoke.
3. Generate a local sample5 model panel.
4. Run sample5 smoke.
5. Run sample5 resume validation.
6. Put the full model panel into Codespaces.
7. Run Codespaces bounded.
8. Inspect artifacts.
9. Decide whether full is warranted.
10. Before full, confirm data, resume, bootstrap, storage, runtime, and logs are all available.

## 13. Common Failure Causes

- Data files were not uploaded or restored.
- Required fields are missing.
- Dependency installation failed.
- Linux path case differs from local Windows paths.
- Memory is insufficient.
- GitHub Actions reaches its time limit.
- Checkpoint parameters do not match the requested run.
- Bootstrap iterations are too slow.
