# Cloud run summary

- status: OK
- mode: smoke
- runtime: local
- git_commit: 30c4aa1
- python: 3.11.9
- data_source: stage2_shards
- data_path: data_intermediate\stage2_lsi_labels\lsi_labels_manifest.csv
- data_rows: 14536695
- data_columns: per-shard
- started_at: 2026-06-21T16:13:07
- ended_at: 2026-06-21T16:14:15
- elapsed_seconds: 68.0
- resume: False
- dry_run: False
- memory: unavailable
- stock_count_after_cap: 3
- manifest_rows_after_cap: 3
- data_range: 2023-05-15 to 2026-05-13
- gap: 5
- lookback_clean: 10
- threshold_quantile: 0.9
- max_stock_codes: 3
- bootstrap_iterations: 10
- checkpoints_read: none
- stages_recomputed: model:onset:H5:P:Logit, model:onset:H5:P:LightGBM, model:onset:H5:P:SMARTBoost, model:onset:H5:M:Logit, model:onset:H5:M:LightGBM, model:onset:H5:M:SMARTBoost, model:onset:H5:C:Logit, model:onset:H5:C:LightGBM, model:onset:H5:C:SMARTBoost, model:onset:H5:ALL:Logit, model:onset:H5:ALL:LightGBM, model:onset:H5:ALL:SMARTBoost, model:onset:H10:P:Logit, model:onset:H10:P:LightGBM, model:onset:H10:P:SMARTBoost, model:onset:H10:M:Logit, model:onset:H10:M:LightGBM, model:onset:H10:M:SMARTBoost, model:onset:H10:C:Logit, model:onset:H10:C:LightGBM, model:onset:H10:C:SMARTBoost, model:onset:H10:ALL:Logit, model:onset:H10:ALL:LightGBM, model:onset:H10:ALL:SMARTBoost, model:continuation:H5:P:Logit, model:continuation:H5:P:LightGBM, model:continuation:H5:P:SMARTBoost, model:continuation:H5:M:Logit, model:continuation:H5:M:LightGBM, model:continuation:H5:M:SMARTBoost, model:continuation:H5:C:Logit, model:continuation:H5:C:LightGBM, model:continuation:H5:C:SMARTBoost, model:continuation:H5:ALL:Logit, model:continuation:H5:ALL:LightGBM, model:continuation:H5:ALL:SMARTBoost, model:continuation:H10:P:Logit, model:continuation:H10:P:LightGBM, model:continuation:H10:P:SMARTBoost, model:continuation:H10:M:Logit, model:continuation:H10:M:LightGBM, model:continuation:H10:M:SMARTBoost, model:continuation:H10:C:Logit, model:continuation:H10:C:LightGBM, model:continuation:H10:C:SMARTBoost, model:continuation:H10:ALL:Logit, model:continuation:H10:ALL:LightGBM, model:continuation:H10:ALL:SMARTBoost
- next_run_readiness: bounded-ready if the same data source is available in Codespaces or GitHub Actions

## Risk Notes

- model panel was not used; runner fell back to stage2 shards

## Output Files

- experiments\onset_baseline_check\outputs\bootstrap_ci.csv
- experiments\onset_baseline_check\outputs\onset_metrics.csv
- experiments\onset_baseline_check\outputs\continuation_metrics.csv
- experiments\onset_baseline_check\outputs\model_comparison_summary.csv
- experiments\onset_baseline_check\outputs\topk_lift_table.csv
- experiments\onset_baseline_check\outputs\delta_vs_persistence.csv
- experiments\onset_baseline_check\outputs\feature_group_increment_table.csv
- experiments\onset_baseline_check\outputs\robustness_grid_summary.csv
- experiments\onset_baseline_check\outputs\training_sample_summary.csv
- experiments\onset_baseline_check\outputs\selected_best_models.csv
- experiments\onset_baseline_check\outputs\event_level_metrics.csv
- experiments\onset_baseline_check\outputs\feature_importance_onset.csv
- experiments\onset_baseline_check\outputs\feature_group_contribution_onset.csv
- experiments\onset_baseline_check\outputs\fig_pr_curves_onset.png
- experiments\onset_baseline_check\outputs\fig_topk_lift_onset.png
- experiments\onset_baseline_check\outputs\fig_feature_importance_onset.png
- experiments\onset_baseline_check\outputs\fig_pr_curves_onset.pdf
- experiments\onset_baseline_check\outputs\fig_topk_lift_onset.pdf
- experiments\onset_baseline_check\outputs\fig_feature_importance_onset.pdf
- experiments\onset_baseline_check\outputs\onset_baseline_report.md
- experiments\onset_baseline_check\outputs\inclusion_decision_note.md
- experiments\onset_baseline_check\outputs\run_log.txt
