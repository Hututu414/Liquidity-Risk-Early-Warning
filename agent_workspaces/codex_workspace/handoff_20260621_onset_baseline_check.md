# Handoff: onset_baseline_check
Date: 2026-06-21
Status: COMPLETE

## Files read

- data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv
- data_intermediate/stage2_lsi_labels/time_split.json
- data_intermediate/stage2_lsi_labels/label_thresholds_train.json
- data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet
- code/src/models/07_smartboost_forecasting.py

## Files modified

- experiments/onset_baseline_check/config_onset_baseline.yaml
- experiments/onset_baseline_check/run_onset_baseline.py
- experiments/onset_baseline_check/README.md

## Artifacts generated

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
- experiments\onset_baseline_check\outputs\cloud_run_summary.md

## Unresolved issues

- none

## Next steps

- Review onset_baseline_report.md and inclusion_decision_note.md before making any separate LaTeX integration pass.
- Do not write these results into the paper automatically; update the manuscript only in a dedicated follow-up task.
