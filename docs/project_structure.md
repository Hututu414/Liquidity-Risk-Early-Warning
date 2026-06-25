# Project Structure

This repository is a clean code release for the A-share minute-level liquidity pressure onset early-warning project.

## Kept In Git

```text
README.md
requirements.txt
pyproject.toml
.gitignore
.devcontainer/
.github/workflows/
code/
src/
scripts/
experiments/onset_baseline_check/
figures/
docs/
data/processed/*_schema.json
data/processed/*_profile.md
```

## Directory Roles

`code/`

Core research pipeline code. It contains data preparation, liquidity stress component construction, LSI and label construction, RGARCH-CARR-SK, QVAR, SMARTBoost, visualization, and tests.

`src/liquidity_risk/`

Lightweight package namespace for shared helpers.

`scripts/`

Repository-level checks and cloud/local helper scripts.

`experiments/onset_baseline_check/`

Standalone onset baseline experiment. The release keeps code, configuration, README, and selected small outputs. Runtime checkpoints and logs are ignored.

`figures/`

Small PNG figures retained for result inspection.

`docs/`

Data contract, reproduction steps, figure inventory, cleanup inventory, and final repository check.

`data/processed/`

Only small schema/profile metadata is kept. The required parquet data file is local-only.

## Excluded From Git

```text
report/latex_project/
08_report/latex_project/
paper/
experiments/paper_material_pack/
agent_workspaces/
06_agent_workspaces/
07_reviews/
data/raw/
data_inbox/
data_intermediate/
outputs/
final_output/
pipeline_logs/
checkpoints/
*.parquet
*.joblib
*.pkl
*.tex
*.pdf
*.docx
*.doc
```

These exclusions keep the repository focused on code, compact result artifacts, and reproducibility notes rather than thesis packaging or local experiment caches.
