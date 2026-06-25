# bounded20 archive manifest

## Data and Run

- bounded20_data_file: data\processed\onset_model_panel_bounded20.parquet
- stock_count: 20
- rows: 3473937
- date_range: 2023-05-15 to 2026-05-13
- mode: bounded
- gap: 5
- lookback_clean: 10
- threshold_quantile: 0.9
- max_stock_codes: 20
- bootstrap_iterations: 200
- elapsed_seconds: 308.4

## H5 / H10 Key Results

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

## Safety Notes

- final_full_run: not run
- paper_body_modified: no
- final_tex_modified: no
- archive_policy: files were copied, not moved, so resume artifacts remain in place.

## Archived Files

- experiments\onset_baseline_check\outputs\bounded20_result_digest.md
- experiments\onset_baseline_check\outputs\cloud_run_summary.md
- experiments\onset_baseline_check\outputs\onset_baseline_report.md
- experiments\onset_baseline_check\outputs\inclusion_decision_note.md
- experiments\onset_baseline_check\outputs\model_comparison_summary.csv
- experiments\onset_baseline_check\outputs\delta_vs_persistence.csv
- experiments\onset_baseline_check\outputs\topk_lift_table.csv
- experiments\onset_baseline_check\checkpoints\manifest.json
- experiments/onset_baseline_check/logs/bounded20_process.json
- experiments/onset_baseline_check/logs/bounded20_retry_combined.log
- experiments/onset_baseline_check/logs/bounded20_retry_exit.json
- experiments/onset_baseline_check/logs/bounded20_stderr.log
- experiments/onset_baseline_check/logs/bounded20_stdout.log
- experiments/onset_baseline_check/logs/run_20260621_102109.log
- experiments/onset_baseline_check/logs/run_20260621_102139.log
- experiments/onset_baseline_check/logs/run_20260621_104544.log
- experiments/onset_baseline_check/logs/run_20260621_110616.log
- experiments/onset_baseline_check/logs/run_20260621_110744.log
- experiments/onset_baseline_check/logs/run_20260621_110954.log
- experiments/onset_baseline_check/logs/run_20260621_111054.log
- experiments/onset_baseline_check/logs/run_20260621_114804.log
- experiments/onset_baseline_check/logs/run_20260621_115350.log

## Missing Files

- none
