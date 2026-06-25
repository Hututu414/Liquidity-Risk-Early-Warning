# bounded20 onset baseline result digest

## Run Environment

- runtime: local
- git_commit: 30c4aa1
- python: 3.11.9
- mode: bounded
- data_path: data\processed\onset_model_panel_bounded20.parquet
- bounded_success_elapsed_seconds: 308.4
- retry_shell_elapsed_seconds: 310.1
- first_attempt_note: first bounded20 attempt reached bootstrap_complete but exited before reports; reran the same bounded command with --resume and exit_code=0.
- full_run: not run

## Panel Profile

- panel_generated: yes
- panel_size_mb: 830.841
- rows: 3473937
- columns: 40
- stock_count: 20
- date_range: 2023-05-15 to 2026-05-13
- git_ignore: .gitignore:24:data/processed/**/*.parquet	data/processed/onset_model_panel_bounded20.parquet
- schema: data/processed/onset_model_panel_bounded20_schema.json
- profile: data/processed/onset_model_panel_bounded20_profile.md

## H5 / H10 Results

### H5

- onset event_rate: 3.53%
- naive persistence: PR-AUC=0.054260, Top5_hit_rate=2.15%, Top5_lift=0.608419
- selected best model: LightGBM / ALL, PR-AUC=0.157776, Top5_hit_rate=19.60%, Top5_lift=5.546516
- Delta vs naive: Delta_PR_AUC=0.103517, Delta_Top5_lift=4.938097
- bootstrap PR-AUC delta CI: observed=0.103517, 95% CI=[0.094774, 0.116197], iterations=200
- bootstrap Top5 lift delta CI: observed=4.938097, 95% CI=[4.591551, 5.346080], iterations=200
- event-level: events=2462, recall=19.54%, daily_false_alarms=24.840580, mean_lead_minutes=10.376299

### H10

- onset event_rate: 4.51%
- naive persistence: PR-AUC=0.076567, Top5_hit_rate=3.90%, Top5_lift=0.864266
- selected best model: SMARTBoost / ALL, PR-AUC=0.192774, Top5_hit_rate=24.60%, Top5_lift=5.451524
- Delta vs naive: Delta_PR_AUC=0.116207, Delta_Top5_lift=4.587258
- bootstrap PR-AUC delta CI: observed=0.116207, 95% CI=[0.106682, 0.127804], iterations=200
- bootstrap Top5 lift delta CI: observed=4.587258, 95% CI=[4.193186, 4.860992], iterations=200
- event-level: events=2209, recall=20.01%, daily_false_alarms=24.242857, mean_lead_minutes=21.934389

## P / M / C / ALL Feature Groups

- H5 selected-model feature groups (LightGBM): best=ALL
  - P: PR-AUC=0.131827, Top5_lift=4.909798, Delta_PR_AUC_vs_P=0.000000, Delta_Top5_lift_vs_P=0.000000
  - M: PR-AUC=0.121524, Top5_lift=4.810753, Delta_PR_AUC_vs_P=-0.010303, Delta_Top5_lift_vs_P=-0.099045
  - C: PR-AUC=0.119219, Top5_lift=4.506544, Delta_PR_AUC_vs_P=-0.012608, Delta_Top5_lift_vs_P=-0.403254
  - ALL: PR-AUC=0.157776, Top5_lift=5.546516, Delta_PR_AUC_vs_P=0.025949, Delta_Top5_lift_vs_P=0.636717
- H10 selected-model feature groups (SMARTBoost): best=ALL
  - P: PR-AUC=0.182318, Top5_lift=5.329640, Delta_PR_AUC_vs_P=0.000000, Delta_Top5_lift_vs_P=0.000000
  - M: PR-AUC=0.152800, Top5_lift=4.908587, Delta_PR_AUC_vs_P=-0.029518, Delta_Top5_lift_vs_P=-0.421053
  - C: PR-AUC=0.152096, Top5_lift=4.847645, Delta_PR_AUC_vs_P=-0.030222, Delta_Top5_lift_vs_P=-0.481994
  - ALL: PR-AUC=0.192774, Top5_lift=5.451524, Delta_PR_AUC_vs_P=0.010456, Delta_Top5_lift_vs_P=0.121884

## Bootstrap Increment Checks

- H5 M_vs_P_same_model PR-AUC: observed=-0.010303, 95% CI=[-0.016140, -0.003251]
- H5 C_vs_P_same_model PR-AUC: observed=-0.012608, 95% CI=[-0.020095, -0.004984]
- H5 ALL_vs_P_same_model PR-AUC: observed=0.025949, 95% CI=[0.016526, 0.035247]
- H10 M_vs_P_same_model PR-AUC: observed=-0.029518, 95% CI=[-0.035828, -0.022350]
- H10 C_vs_P_same_model PR-AUC: observed=-0.030222, 95% CI=[-0.037465, -0.022730]
- H10 ALL_vs_P_same_model PR-AUC: observed=0.010456, 95% CI=[0.001524, 0.022299]

## Decision

bounded20 结果支持继续进入 full run。

当前 bounded20 结果暂不支持将横截面状态作为核心贡献。

横截面或扩展状态变量可能提供了持续性之外的增量预警信息，建议在 full run 中重点检验。

- full recommendation: yes, proceed to full only after reviewing bounded artifacts and ensuring memory/runtime budget.
- paper-body recommendation: no direct paper-body insertion yet; bounded20 is diagnostic and should not be treated as final-paper evidence.
- full run was not executed in this round.

## Output Files

- experiments/onset_baseline_check/outputs/model_comparison_summary.csv
- experiments/onset_baseline_check/outputs/delta_vs_persistence.csv
- experiments/onset_baseline_check/outputs/topk_lift_table.csv
- experiments/onset_baseline_check/outputs/bootstrap_ci.csv
- experiments/onset_baseline_check/outputs/event_level_metrics.csv
- experiments/onset_baseline_check/outputs/feature_group_increment_table.csv
- experiments/onset_baseline_check/outputs/onset_baseline_report.md
- experiments/onset_baseline_check/outputs/inclusion_decision_note.md
- experiments/onset_baseline_check/outputs/cloud_run_summary.md
- experiments/onset_baseline_check/outputs/bounded20_result_digest.md
- experiments/onset_baseline_check/checkpoints/manifest.json
- experiments/onset_baseline_check/logs/
