# Handoff: event-level onset evaluation audit

## Read

- `experiments/onset_baseline_check/run_onset_baseline.py`
- `experiments/onset_baseline_check/outputs/event_level_metrics.csv`
- `experiments/onset_baseline_check/outputs/selected_best_models.csv`
- `experiments/onset_baseline_check/outputs/cloud_run_summary.md`
- `experiments/onset_baseline_check/checkpoints/manifest.json`
- `data_intermediate/stage2_lsi_labels/label_thresholds_train.json`
- `data_intermediate/stage2_lsi_labels/time_split.json`

## Modified / Added

- Added `scripts/recompute_event_metrics.py`.
- Added `scripts/audit_event_level_evaluation.py`.
- Added this handoff file.

## Generated

- `experiments/onset_baseline_check/outputs/event_level_audit_report.md`
- `experiments/onset_baseline_check/outputs/event_level_metrics_revised.csv`
- `experiments/onset_baseline_check/outputs/event_level_metrics_revised.md`
- `experiments/onset_baseline_check/outputs/allstock_diagnostic_event_revised_digest.md`
- `experiments/onset_baseline_check/outputs/event_level_recompute_stdout.txt`
- `experiments/onset_baseline_check/outputs/event_level_recompute_stderr.txt`
- `experiments/onset_baseline_check/outputs/event_level_recompute.pid`

## Result

- Confirmed the original event-level logic is misaligned for onset labels: it treats positive onset label time `t` as event start and then searches before `t`.
- Recomputed event metrics without retraining, using cached `LightGBM / ALL` `trainval_model` joblib files for the all-stock diagnostic signature `4c603e3151d66306`.
- Corrected event matching uses true LSI pressure episode starts, same stock/date, and trading-minute `slot` windows.
- Revised H5 label-aligned event recall: 28.40%; practical-window recall: 44.09%.
- Revised H10 label-aligned event recall: 36.93%; practical-window recall: 52.96%.
- No final full run was executed.
- No paper body or final TeX file was modified.

## Unresolved / Next

- Future final full should use the revised event-level evaluation logic or run `scripts/audit_event_level_evaluation.py` after full model checkpoints are available.
- The main experiment runner still has its historical event-level output path; use the revised audit/recompute script for paper-grade event metrics unless the runner is later integrated with the corrected episode-start logic.
