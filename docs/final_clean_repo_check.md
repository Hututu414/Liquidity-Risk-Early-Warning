# Final Clean Repository Check

## Branch

```text
clean-code-release
```

## Staged File Summary

Staged changes contain:

- 103 added or modified files retained for the clean code release.
- 246 deletions removing legacy agent workspaces, review renders, and old thesis-package assets from Git.

Retained staged roots:

```text
.devcontainer/
.github/workflows/
.gitignore
README.md
requirements.txt
pyproject.toml
code/config/
code/src/common/
code/src/data/
code/src/diagnostics/
code/src/models/
code/src/robustness/
code/src/visualization/
code/tests/
src/liquidity_risk/
scripts/
data/processed/onset_model_panel_full80_schema.json
data/processed/onset_model_panel_full80_profile.md
docs/
experiments/onset_baseline_check/
figures/
```

Staged deletions remove from Git:

```text
06_agent_workspaces/
07_reviews/
08_report/latex_project/
AGENTS.md
CODEX.md
agent_workspaces/
old cloud/data-transfer docs
old generic onset_model_panel schema/profile files
```

## Added Or Modified Safety Checks

The added/modified staged set was checked with `git diff --cached --name-only --diff-filter=ACMR`.

| Check | Result |
| --- | --- |
| Contains thesis PDF | No |
| Contains thesis TeX | No |
| Contains parquet | No |
| Contains checkpoint directory/files | No |
| Contains joblib | No |
| Contains pkl | No |
| Contains raw data | No |
| Contains data_inbox or data_intermediate | No |
| Contains files larger than 50 MB | No |
| Contains files larger than 100 MB | No |
| Contains core code | Yes |
| Contains necessary result images | Yes |
| Contains reproduction steps | Yes |
| Can be pushed for teacher review | Yes |

`git diff --cached --check` passed after whitespace-only cleanup on newly tracked code files.

## Result Images Kept

```text
figures/fig_main_01_marketlsi_events.png
figures/fig_main_02_qvar_tail_response.png
figures/fig_main_03_qvar_tail_state_series.png
figures/fig_main_04_onset_pr_curve.png
figures/fig_main_05_delta_pr_auc.png
figures/fig_main_06_feature_group_increment.png
figures/fig_main_07_event_level_monitoring.png
figures/fig_main_08_budgeted_event_tradeoff.png
figures/fig_appendix_a2_topk_lift_curve.png
figures/fig_appendix_a3_calibration_curve.png
experiments/onset_baseline_check/outputs/fig_feature_importance_onset.png
experiments/onset_baseline_check/outputs/fig_pr_curves_onset.png
experiments/onset_baseline_check/outputs/fig_topk_lift_onset.png
```

## Reproduction Documents

```text
README.md
docs/data_contract.md
docs/reproduction_steps.md
docs/project_structure.md
docs/figure_inventory.md
docs/cleanup_inventory.md
```

## Protected Local Thesis Assets

The following protected local thesis source was not modified:

```text
report/latex_project/main_v2_final_parameter_tables_significance.tex
```

The clean release excludes thesis source/PDF assets from Git. Existing local thesis files remain local.

## Test Note

No local Python smoke test was run because the project-mandated local interpreter path was not present on this machine:

```text
D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe
```

The repository includes GitHub Actions smoke checks and reproducible commands in `README.md` and `docs/reproduction_steps.md`.
