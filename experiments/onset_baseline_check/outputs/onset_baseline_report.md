# Onset baseline independent experiment report

## Purpose

This experiment checks whether short-horizon warning performance is incremental to naive LSI persistence after using an onset label with a clean lookback window and a prediction gap.

## Run Settings

- mode: smoke
- gap: 5
- lookback_clean: 10
- threshold_quantile: 0.9
- max_stock_codes: 3
- bootstrap_iterations: 10

## Training Samples

- onset H5 train: rows=180, event_rate=50.00%
- onset H5 train_plus_validation: rows=240, event_rate=50.00%
- onset H10 train: rows=180, event_rate=50.00%
- onset H10 train_plus_validation: rows=240, event_rate=50.00%
- continuation H5 train: rows=180, event_rate=50.00%
- continuation H5 train_plus_validation: rows=240, event_rate=50.00%
- continuation H10 train: rows=180, event_rate=50.00%
- continuation H10 train_plus_validation: rows=240, event_rate=50.00%

## Selected Onset Results

- H5: validation selected Logit / ALL; test PR-AUC=0.0665; Delta PR-AUC vs naive=0.0045; Top5 lift=0.9623; Delta Top5 lift vs naive=0.8554.
- H10: validation selected Logit / ALL; test PR-AUC=0.1120; Delta PR-AUC vs naive=0.0204; Top5 lift=1.1762; Delta Top5 lift vs naive=0.8625.

See `model_comparison_summary.csv` for the H5/H10 model comparison table and `feature_group_increment_table.csv` for P/M/C/ALL increments.

## Daily Bootstrap CIs

- H5 best_vs_naive / PR_AUC: delta=0.0045, 95% CI=[-0.0044, 0.0118], rows=3999
- H5 best_vs_naive / Top5_lift: delta=0.8554, 95% CI=[0.3019, 1.3535], rows=3999
- H5 M_vs_P_same_model / PR_AUC: delta=-0.0062, 95% CI=[-0.0102, -0.0031], rows=3999
- H5 M_vs_P_same_model / Top5_lift: delta=0.2139, 95% CI=[0.0234, 0.4161], rows=3999
- H5 C_vs_P_same_model / PR_AUC: delta=-0.0067, 95% CI=[-0.0118, -0.0009], rows=3999
- H5 C_vs_P_same_model / Top5_lift: delta=0.7485, 95% CI=[0.2410, 0.8863], rows=3999
- H5 ALL_vs_P_same_model / PR_AUC: delta=0.0049, 95% CI=[0.0017, 0.0099], rows=3999
- H5 ALL_vs_P_same_model / Top5_lift: delta=0.9623, 95% CI=[0.3659, 1.4233], rows=3999
- H10 best_vs_naive / PR_AUC: delta=0.0204, 95% CI=[0.0107, 0.0279], rows=3999
- H10 best_vs_naive / Top5_lift: delta=0.8625, 95% CI=[0.2820, 1.4756], rows=3999
- H10 M_vs_P_same_model / PR_AUC: delta=-0.0170, 95% CI=[-0.0356, -0.0126], rows=3999
- H10 M_vs_P_same_model / Top5_lift: delta=-0.4705, 95% CI=[-0.8008, 0.1171], rows=3999
- H10 C_vs_P_same_model / PR_AUC: delta=0.0088, 95% CI=[0.0018, 0.0168], rows=3999
- H10 C_vs_P_same_model / Top5_lift: delta=-0.3136, 95% CI=[-0.7468, 0.4745], rows=3999
- H10 ALL_vs_P_same_model / PR_AUC: delta=0.0067, 95% CI=[-0.0094, 0.0187], rows=3999
- H10 ALL_vs_P_same_model / Top5_lift: delta=-0.4705, 95% CI=[-0.7688, 0.2231], rows=3999

## Event-Level Metrics

- H10: events=255, recall=5.88%, mean lead=22.0000 minutes, daily false alarms=2.0556
- H5: events=187, recall=0.00%, mean lead=NA minutes, daily false alarms=2.3529

## Feature Contribution Summary

- component: 0.00%
- cross: 0.00%
- market: 0.00%
- other: 0.00%
- persistence: 0.00%

## Robustness Grid

See `robustness_grid_summary.csv` for rows, event counts, and event rates under alternative gap, lookback, and threshold settings.

## Excluded Leakage-Prone Variables

- Stress_H5
- Stress_H10
- future_max_LSI_5_H5
- future_max_LSI_5_H10
- CrossStress
- CrossStress_H10
- Y_onset_H5
- Y_onset_H10
