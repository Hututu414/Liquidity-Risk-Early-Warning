# Handoff: reorganize_paths
Date: 2026-06-20
Status: COMPLETE

## Read Files

- `code/config/paths.py`
- `code/config/project_config.yaml`
- `run_stage0_verify_input.ps1`
- `run_stage1_make_model_ready_panel.ps1`
- `run_stage2_make_lsi_labels.ps1`
- `run_stage3_descriptive_diagnostics.ps1`
- `code/tests/test_paths.py`
- `code/src/common/bootstrap.py`
- project docs and registries containing project-relative paths

## Changed Files And Directories

- Renamed numeric top-level directories to stable descriptive names:
  `data_inbox`, `data_intermediate`, `code`, `outputs`, `report`, `pipeline_logs`, `final_output`, and `docs/admin`.
- Updated project-relative path strings in code, configs, scripts, docs, CSV manifests, JSON manifests, and the final TeX file.
- Added `docs/admin/reorganization_report.md`.
- Added this handoff file.

## Generated Artifacts

- Recompiled final PDF: `report/latex_project/main_v2_final_parameter_tables_significance.pdf`

## Validation

- `compileall -q code`: PASS
- `pytest code\tests`: PASS, 8 tests passed
- `latexmk -xelatex ...`: PASS
- Old numeric directory-name search: no residual operational references outside the reorganization report and this handoff.

## Notes

- No model logic, data transformation logic, parameters, paper prose, figure contents, or table values were intentionally changed.
- Verification-created caches and LaTeX auxiliary files were removed.
- Next agent should use the new descriptive paths only.
