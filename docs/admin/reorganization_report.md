# Project Reorganization Report

Date: 2026-06-20

## Scope

This pass reorganized project paths and naming only. It did not change data-processing logic, model formulas, model parameters, output file names, or LaTeX paper content.

## Directory Rename Map

| Old path | New path |
|---|---|
| `00_admin/` | `docs/admin/` |
| `02_data_inbox/` | `data_inbox/` |
| `03_data_intermediate/` | `data_intermediate/` |
| `04_code/` | `code/` |
| `05_outputs/` | `outputs/` |
| `08_report/` | `report/` |
| `09_pipeline_logs/` | `pipeline_logs/` |
| `10_final_output/` | `final_output/` |
| `06_agent_workspaces/` | `agent_workspaces/` |
| `07_reviews/` | `reviews/` |

## Updated References

- Central paths: `code/config/paths.py`
- Project config: `code/config/project_config.yaml`
- Root stage runners: `run_stage0_verify_input.ps1` through `run_stage3_descriptive_diagnostics.ps1`
- Code and report helpers with hard-coded project-relative paths
- LaTeX final main file path reference from `../../outputs/...`
- Manifest CSV/JSON files containing project-relative paths
- Project documentation and admin registries

## Verification

- Python syntax check: `D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe -m compileall -q code`
- Unit tests: `D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe -m pytest code\tests`
- Test result: 8 passed.
- LaTeX compile: `latexmk -xelatex -interaction=nonstopmode -halt-on-error main_v2_final_parameter_tables_significance.tex`
- Final PDF: `report/latex_project/main_v2_final_parameter_tables_significance.pdf`
- Final log scan: no missing file, undefined control sequence, undefined references/citations, bibliography missing, LaTeX error, package error, emergency stop, or fatal error patterns.

## Cleanup

Generated `__pycache__`, `.pytest_cache`, and LaTeX auxiliary files were removed after verification.
