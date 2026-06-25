# Handoff: bounded20 onset baseline run

Date: 2026-06-21

## Files read

- `scripts/build_onset_model_panel.py`
- `scripts/run_bounded_onset_cloud_ready.py`
- `scripts/list_required_data.py`
- `experiments/onset_baseline_check/run_onset_baseline.py`
- `experiments/onset_baseline_check/outputs/*.csv`
- `experiments/onset_baseline_check/outputs/cloud_run_summary.md`
- `data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv`

## Files modified

- `scripts/build_onset_model_panel.py`
- `scripts/run_bounded_onset_cloud_ready.py`

## Artifacts generated

- `data/processed/onset_model_panel_bounded20.parquet`
- `data/processed/onset_model_panel_bounded20_schema.json`
- `data/processed/onset_model_panel_bounded20_profile.md`
- `experiments/onset_baseline_check/outputs/bounded20_result_digest.md`
- `experiments/onset_baseline_check/outputs/model_comparison_summary.csv`
- `experiments/onset_baseline_check/outputs/delta_vs_persistence.csv`
- `experiments/onset_baseline_check/outputs/topk_lift_table.csv`
- `experiments/onset_baseline_check/outputs/bootstrap_ci.csv`
- `experiments/onset_baseline_check/outputs/event_level_metrics.csv`
- `experiments/onset_baseline_check/outputs/cloud_run_summary.md`
- `experiments/onset_baseline_check/checkpoints/manifest.json`
- `experiments/onset_baseline_check/logs/bounded20_retry_exit.json`

## Unresolved issues

- The first bounded20 attempt reached `bootstrap_complete` but exited before report files were written. A second run with the same bounded command and `--resume` completed with exit code 0.
- `ret_1m`, `ret_sum_*`, `cum_ret_open`, and `cum_amount_log_so_far` were unavailable in the bounded20 panel and triggered sklearn median-imputation warnings. The run completed, but these missing auxiliary return features should be considered when interpreting ALL/M/C increments.
- The bounded20 parquet, checkpoints, joblib files, and logs are local/ignored artifacts and should not be committed.

## Next steps

- Review `experiments/onset_baseline_check/outputs/bounded20_result_digest.md`.
- If proceeding, run full only in a dedicated follow-up after checking cloud memory/runtime budget.
- Do not write bounded20 results into LaTeX paper text without a separate manuscript-integration task.
