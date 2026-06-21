# Handoff: GitHub Cloud Readiness Round 2

## Task

Continue repository maintenance for GitHub cloud readiness without modifying paper body or final TeX files. Focus on smoke/bounded/full workflow readiness, model panel dry-run support, data-path fallback, checkpoint reuse, and push safety.

## Files Read

- `AGENTS.md`
- `.gitignore`
- `.github/workflows/smoke-test.yml`
- `.github/workflows/onset-baseline.yml`
- `docs/cloud_run_guide.md`
- `docs/git_push_checklist.md`
- `scripts/prepare_environment.py`
- `scripts/list_required_data.py`
- `experiments/onset_baseline_check/run_onset_baseline.py`
- `experiments/onset_baseline_check/outputs/cloud_run_summary.md`
- `experiments/onset_baseline_check/outputs/run_log.txt`
- `data/processed/onset_model_panel_schema.json`
- `data/processed/onset_model_panel_profile.md`

## Files Modified or Added

- Modified `.gitignore`
  - Added ignore rules for `data/processed` parquet/binary artifacts.
  - Added ignore rules for top-level `data_intermediate` parquet/binary/CSV/JSON data artifacts.
  - Confirmed checkpoint parquet/joblib artifacts are ignored.
- Added `.github/workflows/smoke-test.yml`
  - Runs environment check, data contract scan, onset panel dry-run, py_compile, and optional data-dependent smoke run.
  - Uploads smoke logs and cloud-readiness artifacts.
- Added `.github/workflows/onset-baseline.yml`
  - Manual workflow for smoke/bounded/full onset baseline runs.
  - Supports `mode`, stock cap, bootstrap, gap, lookback, threshold quantile, optional `data_path`, and `--resume`.
  - Leaves `data_path` empty by default so runner can prefer `data/processed/onset_model_panel.parquet` when present and fall back to stage-2 shards when absent.
- Added `docs/git_push_checklist.md`
  - Documents what should and should not be committed.
  - Includes large-data and final-TeX safety checks.
- Added/updated `docs/cloud_run_guide.md`
  - Documents local, Codespaces, GitHub Actions smoke, bounded, and full run prerequisites.
  - Uses portable commands without local Windows absolute paths.
- Added `scripts/build_onset_model_panel.py`
  - Builds or dry-runs a model-ready onset panel from stage-2 LSI label shards.
  - Excludes forward/future/CrossStress leakage columns.
  - Writes schema/profile metadata; dry-run does not write the large parquet.
- Added `scripts/prepare_environment.py`
- Added `scripts/list_required_data.py`
- Modified `experiments/onset_baseline_check/run_onset_baseline.py`
  - Added default preference for `data/processed/onset_model_panel.parquet`, fallback to stage-2 shards, and explicit `--data-path`.
  - Added checkpoint manifest stages, model joblib cache, prediction/checkpoint artifacts, cloud summary fields, and label-equivalence validation for all modes.
  - Added enhanced cloud summary with data source/path, checkpoint reads, recomputed stages, and next-run readiness.

## Generated Outputs

- `data/processed/onset_model_panel_schema.json`
- `data/processed/onset_model_panel_profile.md`
- No `data/processed/onset_model_panel.parquet` was generated in this round; dry-run explicitly avoided writing it.
- `experiments/onset_baseline_check/outputs/cloud_run_summary.md`
- `experiments/onset_baseline_check/outputs/inclusion_decision_note.md`
- `experiments/onset_baseline_check/checkpoints/manifest.json`
- Ignored checkpoint artifacts under `experiments/onset_baseline_check/checkpoints/`, including model joblibs and bootstrap partial parquet.

## Validation Run

Used the project Python interpreter:

- `python -m py_compile experiments/onset_baseline_check/run_onset_baseline.py scripts/prepare_environment.py scripts/list_required_data.py scripts/build_onset_model_panel.py` passed.
- `python scripts/prepare_environment.py` passed.
- `python scripts/list_required_data.py` passed and found 84 files satisfying the minimum contract.
- `python scripts/build_onset_model_panel.py --dry-run` passed; retained 40 columns and excluded future/CrossStress leakage columns.
- `python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --max-stock-codes 3 --bootstrap 10` passed in about 30 seconds.
- Workflow YAML files parsed successfully with PyYAML.
- Content scan found no local Windows absolute path, user path, or forbidden legacy template terms in the files touched this round.
- Protected final TeX files were checked clean:
  - `report/latex_project/main.tex`
  - `report/latex_project/main_v2_final.tex`
  - `report/latex_project/main_v2_final_parameter_tables_significance.tex`

## Unresolved Issues or Cautions

- Runtime `--resume` behavior is implemented through signature-matched model/report checkpoints and manifest stages, but no extra `--resume` experiment was run because the requested command list was limited.
- Bootstrap partial output is written as an artifact, but draw-level mid-bootstrap continuation is not separately benchmarked in this round.
- The worktree contains many unrelated pre-existing staged/untracked/deleted entries. Do not push the whole worktree. Stage only the targeted cloud-readiness files after reviewing `git status`.
- Full and bounded GitHub Actions runs require data to be available in the runner through restored private data, generated `data/processed/onset_model_panel.parquet`, or stage-2 shards.

## Next Agent

If continuing, inspect only the targeted files above, not the broad dirty worktree. Recommended next step is a selective commit containing cloud-readiness code/docs/workflows plus small schema/profile metadata, while excluding raw/intermediate data and ignored checkpoint binaries.
