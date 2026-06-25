# Project audit

Date: 2026-06-21

## Current Directory Summary

- `code/`: existing project code, including data preparation, common utilities, model scripts, visualization scripts, and tests.
- `data_inbox/`: local input data inbox. It currently contains large preprocessed minute panel files and quality reports.
- `data_intermediate/`: generated intermediate model-ready and LSI-label data. This includes many per-code parquet shards and split metadata.
- `docs/`: project documentation and administrative registries.
- `experiments/onset_baseline_check/`: isolated onset-label baseline experiment and generated reports/figures.
- `outputs/`: existing figures, tables, descriptive diagnostics, and paper-ready outputs.
- `report/latex_project/`: LaTeX paper source, tables, figures, bibliography, and compiled PDFs.
- `final_output/`: intended final delivery folder.
- `agent_workspaces/`: handoff notes from agent runs.

## Core Code Files

- `code/src/data/00_verify_preprocessed_inputs.py`
- `code/src/data/01_make_model_ready_panel.py`
- `code/src/data/02_make_stress_components.py`
- `code/src/data/03_make_stress_index_and_labels.py`
- `code/src/models/05_rgarch_carr_sk.py`
- `code/src/models/06_qvar_tail_transmission.py`
- `code/src/models/06b_qvar_stress_test.py`
- `code/src/models/07_smartboost_forecasting.py`
- `code/src/models/07_smartboost_verification.py`
- `code/src/models/08_core_model_no_lookahead_audit.py`
- `experiments/onset_baseline_check/run_onset_baseline.py`

## Core Paper Files

- `report/latex_project/main_v2_final_parameter_tables_significance.tex`
- `report/latex_project/main_v2_final_parameter_tables_significance.pdf`
- `report/latex_project/refs.bib`
- `report/latex_project/tables/*.tex`
- `report/latex_project/figures/*.png`

No paper body files were modified during this audit.

## Data Locations

- Raw/preprocessed input panel: `data_inbox/preprocessed/panel/`
- Stage 1 model-ready metadata: `data_intermediate/stage1_model_ready/`
- Stage 2 LSI labels and per-code shards: `data_intermediate/stage2_lsi_labels/`
- Existing model and paper outputs: `outputs/`
- Onset experiment outputs: `experiments/onset_baseline_check/outputs/`

## Large Files Observed

- `data_inbox/preprocessed/panel/minute_panel_preprocessed_raw.parquet` is about 371 MB.
- Year-partitioned preprocessed parquet files under `data_inbox/preprocessed/panel/minute_panel_preprocessed_raw_by_year/` are about 79-124 MB each.
- `data_inbox/preprocessed/quality/preprocessed_duplicate_keys.csv` is about 57 MB.
- Many per-code parquet shards under `data_intermediate/stage2_lsi_labels/lsi_labels_by_code/` are about 50-56 MB each.

These files should not be committed to GitHub. They should be staged in Codespaces/Actions through external storage, release assets, GitHub artifact downloads, or manual upload, not through Git.

## Possible Duplicate Outputs

- `outputs/figures/99_paper_ready/` contains finalized paper-ready figures.
- `report/latex_project/figures/` contains copied or renamed paper figures used by LaTeX.
- `experiments/onset_baseline_check/outputs/` contains isolated onset experiment outputs and aborted local process logs.
- `pipeline_logs/` contains local pipeline logs.

No duplicate output was deleted during this audit.

## Current Experiment Entrypoints

- Main onset experiment: `experiments/onset_baseline_check/run_onset_baseline.py`
- Project data/model pipeline scripts: `code/src/data/*.py`, `code/src/models/*.py`
- Windows stage wrappers: `run_stage0_verify_input.ps1` through `run_stage3_descriptive_diagnostics.ps1`

## Dependency Sources

- There was no root `requirements.txt` before this cleanup pass.
- `run_onset_baseline.py` imports pandas, numpy, matplotlib, PyYAML, scikit-learn, and optionally LightGBM.
- Parquet schema inspection needs `pyarrow`.
- Environment and memory reporting can use `psutil` when available.

## Cloud Failure Risks

- Large local data files are not suitable for normal Git commits and will not be present in a fresh GitHub clone unless explicitly supplied.
- The original root README contained mojibake and local Windows-specific setup text.
- The prior `.gitignore` ignored all `*.csv`, which would also hide small result tables that should remain trackable.
- Full onset runs are long and should only be triggered manually.
- Local Windows interpreter paths must not be assumed in Codespaces or GitHub Actions.
- Interrupted full runs need logs and checkpoint markers under `experiments/onset_baseline_check/`.

## File Handling Recommendation

Keep:

- Paper source/PDF files under `report/latex_project/`.
- Core code under `code/` and `experiments/onset_baseline_check/`.
- Small CSV summaries, Markdown reports, and paper-ready PNG/PDF figures.
- Metadata JSON/YAML files needed to understand splits and thresholds.

Move only after separate review:

- Repeated paper figure copies between `outputs/figures/99_paper_ready/` and `report/latex_project/figures/`.
- Old local process logs in experiment output folders.

Ignore in Git:

- Large raw/preprocessed data.
- Large parquet/feather/pickle/joblib/numpy checkpoints.
- Local logs and local process stdout/stderr/pid files.

Delete:

- Nothing in the audit phase.
