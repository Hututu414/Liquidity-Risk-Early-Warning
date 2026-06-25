# all-stock diagnostic result digest

## Run Environment

- runtime: local
- git_commit: 30c4aa1
- python: 3.11.9
- run_mode: bounded
- diagnostic_type: all-stock diagnostic, not final full
- data_path: data\processed\onset_model_panel_full80.parquet
- elapsed_seconds: 882.9
- stock_count: 80
- rows: 13840730
- columns: 40
- date_range: 2023-05-15 to 2026-05-13
- panel_size_mb: 3275.410
- git_ignore: .gitignore:24:data/processed/**/*.parquet	data/processed/onset_model_panel_full80.parquet
- gap: 5
- lookback_clean: 10
- threshold_quantile: 0.9
- bootstrap_iterations: 200
- final_full_run: not run

## H5 / H10 Key Results

### H5

- event_rate: 3.00%
- naive_persistence: PR-AUC=0.051209, Top5_hit_rate=3.25%, Top5_lift=1.084237
- best_model: LightGBM / ALL, PR-AUC=0.153790, Top5_hit_rate=18.48%, Top5_lift=6.163470
- delta_vs_naive: Delta_PR_AUC=0.102581, Delta_Top5_lift=5.079233
- bootstrap_delta_PR_AUC_95CI: observed=0.102581, CI=[0.092759, 0.113503], iterations=200
- bootstrap_delta_Top5_lift_95CI: observed=5.079233, CI=[4.729868, 5.442228], iterations=200
- event_level: events=2398, recall=0.00%, daily_false_alarms=27.777778, mean_lead_minutes=nan
- bounded20_comparison: bounded20 Delta_PR_AUC=0.103517, all-stock Delta_PR_AUC=0.102581; bounded20 Delta_Top5_lift=4.938097, all-stock Delta_Top5_lift=5.079233

### H10

- event_rate: 3.40%
- naive_persistence: PR-AUC=0.067044, Top5_hit_rate=4.75%, Top5_lift=1.399116
- best_model: LightGBM / ALL, PR-AUC=0.181581, Top5_hit_rate=21.98%, Top5_lift=6.472754
- delta_vs_naive: Delta_PR_AUC=0.114537, Delta_Top5_lift=5.073638
- bootstrap_delta_PR_AUC_95CI: observed=0.114537, CI=[0.103319, 0.127849], iterations=200
- bootstrap_delta_Top5_lift_95CI: observed=5.073638, CI=[4.719070, 5.360597], iterations=200
- event_level: events=2716, recall=11.16%, daily_false_alarms=25.496552, mean_lead_minutes=28.805281
- bounded20_comparison: bounded20 Delta_PR_AUC=0.116207, all-stock Delta_PR_AUC=0.114537; bounded20 Delta_Top5_lift=4.587258, all-stock Delta_Top5_lift=5.073638

## P / M / C / ALL Feature Groups

- H5 selected model LightGBM: best_group=ALL
  - P: PR-AUC=0.118885, Top5_lift=5.170976, Delta_PR_AUC_vs_P=0.000000, Delta_Top5_lift_vs_P=0.000000
  - M: PR-AUC=0.112719, Top5_lift=5.221018, Delta_PR_AUC_vs_P=-0.006166, Delta_Top5_lift_vs_P=0.050042
  - C: PR-AUC=0.112400, Top5_lift=5.095913, Delta_PR_AUC_vs_P=-0.006484, Delta_Top5_lift_vs_P=-0.075063
  - ALL: PR-AUC=0.153790, Top5_lift=6.163470, Delta_PR_AUC_vs_P=0.034905, Delta_Top5_lift_vs_P=0.992494
- H10 selected model LightGBM: best_group=ALL
  - P: PR-AUC=0.146318, Top5_lift=5.559647, Delta_PR_AUC_vs_P=0.000000, Delta_Top5_lift_vs_P=0.000000
  - M: PR-AUC=0.137729, Top5_lift=5.449190, Delta_PR_AUC_vs_P=-0.008590, Delta_Top5_lift_vs_P=-0.110457
  - C: PR-AUC=0.139916, Top5_lift=5.419735, Delta_PR_AUC_vs_P=-0.006402, Delta_Top5_lift_vs_P=-0.139912
  - ALL: PR-AUC=0.181581, Top5_lift=6.472754, Delta_PR_AUC_vs_P=0.035263, Delta_Top5_lift_vs_P=0.913108

## Bootstrap Increment Checks

- H5 M_vs_P_same_model: observed=-0.006166, PR-AUC 95% CI=[-0.013438, 0.001395]
- H5 C_vs_P_same_model: observed=-0.006484, PR-AUC 95% CI=[-0.011735, -0.000609]
- H5 ALL_vs_P_same_model: observed=0.034905, PR-AUC 95% CI=[0.023210, 0.045779]
- H10 M_vs_P_same_model: observed=-0.008590, PR-AUC 95% CI=[-0.012508, -0.003650]
- H10 C_vs_P_same_model: observed=-0.006402, PR-AUC 95% CI=[-0.009700, -0.002590]
- H10 ALL_vs_P_same_model: observed=0.035263, PR-AUC 95% CI=[0.030258, 0.041792]

## Feature Contribution Types

- component: 0.491
- market: 0.160
- other: 0.134
- persistence: 0.131
- cross: 0.083

## Bounded20 Direction Consistency

- Direction is consistent with bounded20: best-vs-naive Delta PR-AUC remains positive for H5 and H10, and ALL remains better than P for both horizons.
- H5/H10 Delta PR-AUC are close to bounded20, not materially weaker. H5 event-level recall is weaker and should be treated as a diagnostic caution.

## Decision

all-stock diagnostic 支持继续进入最终 full run。

当前证据仍不支持将横截面状态单独作为核心贡献。

扩展历史状态特征在剥离持续性后仍具有增量预警含量，值得进入最终 full run 检验。

- recommend_final_full: yes
- recommend_paper_body_now: no
- recommend_restructure_now: no
- paper_note: 不建议现在重构文章或写入正文；需要等待最终 full 结果。
- final_full_note: 本轮没有运行最终 full。
## Output Files

- experiments/onset_baseline_check/outputs/allstock_diagnostic_result_digest.md
- experiments/onset_baseline_check/outputs/model_comparison_summary.csv
- experiments/onset_baseline_check/outputs/delta_vs_persistence.csv
- experiments/onset_baseline_check/outputs/topk_lift_table.csv
- experiments/onset_baseline_check/outputs/bootstrap_ci.csv
- experiments/onset_baseline_check/outputs/event_level_metrics.csv
- experiments/onset_baseline_check/outputs/feature_group_increment_table.csv
- experiments/onset_baseline_check/outputs/feature_leakage_audit_full80.md
- experiments/onset_baseline_check/outputs/cloud_run_summary.md
- experiments/onset_baseline_check/checkpoints/manifest.json
- experiments/onset_baseline_check/logs/
