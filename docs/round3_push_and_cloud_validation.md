# Round 3 Push and Cloud Validation

## Pre-Commit Safety Check

Commands run before editing this round:

```bash
git status --short
git diff --stat
git diff --name-only
```

Observed summary:

- The working tree was heavily dirty before this round.
- `git diff --stat` reported 885 files changed, 200 insertions, and 39,438 deletions.
- The staging area initially contained unrelated `AD` entries, including large data/report artifacts and final-named TeX candidates.
- A non-destructive unstaging pass was run:

```bash
git restore --staged -- .
```

This did not delete or revert files. It only cleared the index so this round can selectively stage the intended cloud-readiness files.

## Final TeX Cleanliness

Checked protected files:

- `report/latex_project/main.tex`: clean
- `report/latex_project/main_v2_final.tex`: clean
- `report/latex_project/main_v2_final_parameter_tables_significance.tex`: clean

Additional final-named TeX candidates existed in the dirty worktree outside the target protected paths before unstaging. They are not part of this round's planned commit and must not be staged.

## Planned Commit Files

Stage only these paths, if present:

- `.gitignore`
- `.github/workflows/smoke-test.yml`
- `.github/workflows/onset-baseline.yml`
- `.devcontainer/devcontainer.json`
- `requirements.txt`
- `pyproject.toml`
- `README.md`
- `docs/project_audit.md`
- `docs/data_contract.md`
- `docs/git_push_checklist.md`
- `docs/cloud_run_guide.md`
- `docs/data_transfer_to_cloud.md`
- `docs/resume_validation_report.md`
- `docs/round3_push_and_cloud_validation.md`
- `scripts/prepare_environment.py`
- `scripts/list_required_data.py`
- `scripts/build_onset_model_panel.py`
- `scripts/run_bounded_onset_cloud_ready.py`
- `experiments/onset_baseline_check/README.md`
- `experiments/onset_baseline_check/config_onset_baseline.yaml`
- `experiments/onset_baseline_check/run_onset_baseline.py`
- `data/processed/onset_model_panel_schema.json`
- `data/processed/onset_model_panel_profile.md`
- `agent_workspaces/codex_workspace/handoff_20260621_github_cloud_round2.md`
- `agent_workspaces/codex_workspace/handoff_20260621_github_cloud_round3.md`

## Explicit Non-Commit Files

Do not stage or commit:

- `data/processed/*.parquet`
- `data/raw/`
- `data_intermediate/**/*.parquet`
- `data_intermediate/**/*.csv`
- `data_intermediate/**/*.json`
- `experiments/**/checkpoints/**/*.parquet`
- `experiments/**/checkpoints/**/*.joblib`
- raw minute data
- final TeX files
- unrelated deleted legacy directories shown by `git status`

## Large File Risk

Large-file risk was present in the pre-existing dirty index before unstaging. The current `.gitignore` rules are intended to keep model panel parquet files, stage-2 data artifacts, checkpoint parquet files, and joblib model files out of Git.

## Windows Absolute Path Check

No local Windows absolute paths should be committed. Before committing, run a targeted content scan over the planned files and confirm that no drive-letter path, user profile path, token, or local interpreter path remains.

## Branch and Commit Readiness

It is safe to create or switch to `codex/cloud-readiness-round3` only after:

- the index remains clean before selective staging;
- protected final TeX files remain unstaged;
- large parquet/joblib/checkpoint files are ignored or unstaged;
- `git diff --cached --name-only` contains only the planned files above.

## Push and Actions Notes

If push fails, do not retry repeatedly. Use:

```bash
git push -u origin codex/cloud-readiness-round3
```

Then inspect the failure message. If GitHub CLI is not installed or authenticated, manually inspect Actions in the GitHub web UI:

1. Open the repository.
2. Go to `Actions`.
3. Select `Smoke test`.
4. Open the latest run.
5. Download artifacts.
6. Inspect logs and `cloud_run_summary.md`.

## Round 3 Result

- Branch: `codex/cloud-readiness-round3` created locally.
- Local environment check: passed.
- Model panel dry-run: passed and did not write the full panel.
- Sample5 panel build: passed.
- Sample5 panel:
  - path: `data/processed/onset_model_panel_sample5.parquet`
  - size: 126.983 MB
  - rows: 521,754
  - columns: 40
  - non-index stock count: 3
  - date range: 2023-05-15 to 2026-05-13
  - git ignore: yes, matched by `data/processed/**/*.parquet`
- Data contract scan: sample5 was listed first as `[OK]`.
- Sample5 smoke: passed after fixing feature-importance alignment for all-null optional features.
- First successful sample5 smoke elapsed: 33.158 seconds.
- Cached resume elapsed: 1.441 seconds.
- Resume result: `Resume completed from cached reports`; report-level cache reuse skipped recomputation.
- Large file check: sample5 parquet, full panel parquet, checkpoint parquet, and joblib model files are ignored.
- Windows absolute path scan: passed after removing local interpreter path from `README.md`.
- Bounded wrapper: created; default mode does not run bounded. It currently reports bounded is not ready until the full model panel exists at `data/processed/onset_model_panel.parquet`.
- Commit: local commit created with message `Prepare cloud onset baseline workflow`.
- Push: failed because this local repository has no configured `origin` remote.
- GitHub Actions smoke: not triggered because push did not reach GitHub.

Manual push commands after confirming the intended remote:

```bash
git remote add origin https://github.com/Hututu414/Liquidity-Risk-Early-Warning.git
git push -u origin codex/cloud-readiness-round3
```

After the push succeeds, inspect GitHub Actions manually:

1. Open the repository.
2. Go to `Actions`.
3. Select `Smoke test`.
4. Open the newest run for `codex/cloud-readiness-round3`.
5. Confirm dependency install, environment check, data contract scan, py_compile, optional smoke logic, and artifact upload.
