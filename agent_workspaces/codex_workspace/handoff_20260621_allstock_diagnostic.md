# Handoff: all-stock onset diagnostic

Date: 2026-06-21

## Files read

- `experiments/onset_baseline_check/outputs/bounded20_result_digest.md`
- `experiments/onset_baseline_check/outputs/cloud_run_summary.md`
- `experiments/onset_baseline_check/outputs/model_comparison_summary.csv`
- `experiments/onset_baseline_check/outputs/bootstrap_ci.csv`
- `experiments/onset_baseline_check/outputs/event_level_metrics.csv`
- `experiments/onset_baseline_check/outputs/feature_group_increment_table.csv`
- `experiments/onset_baseline_check/outputs/feature_importance_onset.csv`
- `experiments/onset_baseline_check/checkpoints/manifest.json`
- `data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv`

## Files modified

- `scripts/build_onset_model_panel.py`
- `scripts/run_bounded_onset_cloud_ready.py`
- `scripts/audit_onset_features.py`

## Artifacts generated

- `experiments/onset_baseline_check/archive/bounded20_20260621/archive_manifest.md`
- `experiments/onset_baseline_check/outputs/feature_leakage_audit_bounded20.md`
- `experiments/onset_baseline_check/outputs/feature_leakage_audit_full80.md`
- `data/processed/onset_model_panel_full80.parquet`
- `data/processed/onset_model_panel_full80_schema.json`
- `data/processed/onset_model_panel_full80_profile.md`
- `experiments/onset_baseline_check/outputs/allstock_diagnostic_result_digest.md`
- `experiments/onset_baseline_check/outputs/paper_restructure_waitlist.md`
- `experiments/onset_baseline_check/outputs/model_comparison_summary.csv`
- `experiments/onset_baseline_check/outputs/bootstrap_ci.csv`
- `experiments/onset_baseline_check/outputs/event_level_metrics.csv`
- `experiments/onset_baseline_check/outputs/cloud_run_summary.md`
- `experiments/onset_baseline_check/checkpoints/manifest.json`
- `experiments/onset_baseline_check/logs/allstock_diagnostic_process.json`

## Unresolved issues

- The all-stock diagnostic is not final full. It used `--mode bounded`, `--max-stock-codes null`, and bootstrap 200.
- H5 event-level recall is 0.00% in the all-stock diagnostic despite positive PR-AUC and Top5 lift; this should be treated as a diagnostic caution before any paper claim.
- `ret_1m`, `ret_sum_*`, `cum_ret_open`, and `cum_amount_log_so_far` remain unavailable and trigger sklearn imputation warnings.
- Generated parquet, checkpoints, joblib models, and large logs are local/ignored artifacts and should not be committed.

## Next steps

- Review `experiments/onset_baseline_check/outputs/allstock_diagnostic_result_digest.md`.
- If proceeding, run the final full only in a separate task with explicit approval.
- Do not restructure the paper or write diagnostic results into LaTeX until final full results are reviewed.
