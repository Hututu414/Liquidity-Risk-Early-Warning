# Git push checklist

Date: 2026-06-21

## Current Git Status Summary

At the time this checklist was written, the relevant working tree changes were:

- Modified: `.gitignore`
- Added/modified: `README.md`
- Added: `.devcontainer/`
- Added/modified: `.github/workflows/`
- Added/modified: `docs/`
- Added/modified: `scripts/`
- Added: `src/liquidity_risk/`
- Added/modified: `experiments/onset_baseline_check/`
- Added: `requirements.txt`
- Added: `pyproject.toml`

No automatic `git push` was performed.

## Files That Should Be Committed

- `README.md`
- `.gitignore`
- `requirements.txt`
- `pyproject.toml`
- `.devcontainer/devcontainer.json`
- `.github/workflows/smoke-test.yml`
- `.github/workflows/onset-baseline.yml`
- `docs/project_audit.md`
- `docs/data_contract.md`
- `docs/cloud_run_guide.md`
- `docs/git_push_checklist.md`
- `scripts/prepare_environment.py`
- `scripts/list_required_data.py`
- `scripts/build_onset_model_panel.py`
- `src/liquidity_risk/*.py`
- `experiments/onset_baseline_check/README.md`
- `experiments/onset_baseline_check/config_onset_baseline.yaml`
- `experiments/onset_baseline_check/run_onset_baseline.py`
- Small Markdown/CSV/PNG/PDF experiment summaries under `experiments/onset_baseline_check/outputs/`, if intentionally retained.
- Small JSON checkpoint manifest files, especially `experiments/onset_baseline_check/checkpoints/manifest.json`, if useful for audit.

## Files That Should Not Be Committed

- Raw data under `data/raw/`
- Large generated model panels such as `data/processed/onset_model_panel.parquet`
- Large preprocessed data under `data_inbox/preprocessed/panel/`
- Large intermediate parquet files under `data_intermediate/`
- Large checkpoint caches under `experiments/onset_baseline_check/checkpoints/`
- Model cache files such as `*.joblib`
- Pickle, feather, numpy, and parquet checkpoint files
- Local process files: `process_stdout.txt`, `process_stderr.txt`, `process.pid`
- Local temporary logs and pipeline logs
- Virtual environments and Python caches

## `.gitignore` Coverage

The current `.gitignore` covers:

- `data/raw/`
- `data/processed/**/*.parquet` and other large processed binary formats
- `data_inbox/preprocessed/panel/**/*.parquet`, `*.csv`, and `*.csv.gz`
- `data_intermediate/**/*.parquet`, `*.feather`, `*.pkl`, `*.pickle`, `*.joblib`
- `experiments/**/checkpoints/**/*.parquet`, `*.feather`, `*.pkl`, `*.pickle`, `*.joblib`, `*.npy`, `*.npz`
- `__pycache__/`
- `.venv/`, `venv/`, `env/`
- `*.pyc`
- `.ipynb_checkpoints/`
- local process files and temporary logs
- OS/editor cache files such as `.DS_Store` and `Thumbs.db`
- LaTeX build byproducts, while preserving source `.tex` and final `.pdf`

## Possible Large-File Risk

Known local large files include:

- `data_inbox/preprocessed/panel/minute_panel_preprocessed_raw.parquet`
- `data_inbox/preprocessed/panel/minute_panel_preprocessed_raw_by_year/*.parquet`
- `data_inbox/preprocessed/quality/preprocessed_duplicate_keys.csv`
- `data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet`

Recommendation: do not delete these local files, but keep them ignored. For cloud runs, restore them through a private artifact or build the smaller `data/processed/onset_model_panel.parquet` outside Git.

## Final Paper File Safety

The following protected final paper files should remain unmodified before push:

- `report/latex_project/main.tex`
- `report/latex_project/main_v2_final.tex`
- `report/latex_project/main_v2_final_parameter_tables_significance.tex`
- any final-version TeX file whose filename contains `final`

Current check result: no relevant `git status` entries were observed for these protected final TeX files during this maintenance pass.

## Recommended Pre-Push Commands

```bash
git status --short
python scripts/prepare_environment.py
python scripts/list_required_data.py
python scripts/build_onset_model_panel.py --dry-run
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --max-stock-codes 3 --bootstrap 10
```

Review all output paths before deciding whether to push.
