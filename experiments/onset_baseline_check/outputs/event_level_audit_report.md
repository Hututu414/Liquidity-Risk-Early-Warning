# Event-level evaluation audit

## Scope

- Scope: all-stock diagnostic event-level audit only.
- Training: no model was retrained; cached `trainval_model` objects were loaded from `checkpoints/models`.
- Final full: not run.
- Paper body/final TeX: not modified.
- Data path: `data/processed/onset_model_panel_full80.parquet`.
- Cache signature: `4c603e3151d66306`.
- Runtime seconds: 263.2.

## Main finding

The original event-level implementation is time-window misaligned for onset labels. It builds events from rows where `Y_onset_H >= 0.5`, so the label time `t` is treated as the event start. Onset labels are designed to occur before the true pressure episode start `s`, so the original code then searches for signals before an already-early label time. This can drive H5 event recall to zero even when minute-level Top5 hit and lift are high.

The original code also used wall-clock minute differences between datetimes. The revised metrics use same-stock, same-date trading `slot` distances, matching the label construction by intraday row shifts.

## Window definitions

- gap: 5.
- lookback_clean: 10.
- threshold_quantile: 0.90.
- label-aligned hit rule: `s-(gap+H-1) <= t <= s-gap`.
- practical windows: H5 `s-20` to `s-5`; H10 `s-30` to `s-5`.
- Original code windows: H5 `5..20` minutes before the derived label-event; H10 `10..30` minutes before the derived label-event.

## Thresholds

- H5: LSI_5 threshold = 7.972218.
- H10: LSI_5 threshold = 9.606480.

## Horizon diagnostics

### H5

- Cached model: `LightGBM` / `ALL` from `experiments\onset_baseline_check\checkpoints\models\4c603e3151d66306_onset_H5_ALL_LightGBM.joblib`.
- Onset positive rows: 69,569.
- Pressure episodes: 21,679.
- Top5 signals: 121,126.
- Top5 minute-level hits: 20,882 (17.24%).
- Label-aligned eligible events: 20,018; detected: 5,686; recall: 28.40%.
- Practical eligible events: 20,281; detected: 8,942; recall: 44.09%.
- Label-aligned daily false alarms: 733.17.
- Practical-window daily false alarms: 595.14.
- Positive-label lead distribution: count=69,569, median=5.00, p10=2.00, p90=9.00, within label window=62.65%.
- Top5-signal future event lead distribution: count=81,952, median=18.00, p10=2.00, p90=86.00, within label window=14.99%, within practical window=34.18%.

### H10

- Cached model: `LightGBM` / `ALL` from `experiments\onset_baseline_check\checkpoints\models\4c603e3151d66306_onset_H10_ALL_LightGBM.joblib`.
- Onset positive rows: 81,011.
- Pressure episodes: 16,676.
- Top5 signals: 117,049.
- Top5 minute-level hits: 25,508 (21.79%).
- Label-aligned eligible events: 15,585; detected: 5,755; recall: 36.93%.
- Practical eligible events: 15,654; detected: 8,290; recall: 52.96%.
- Label-aligned daily false alarms: 654.70.
- Practical-window daily false alarms: 521.34.
- Positive-label lead distribution: count=81,011, median=8.00, p10=2.00, p90=13.00, within label window=73.71%.
- Top5-signal future event lead distribution: count=78,176, median=20.00, p10=2.00, p90=90.00, within label window=22.68%, within practical window=42.96%.

## Interpretation

The revised event-level metrics do not change PR-AUC or TopK lift because those are minute-level ranking metrics computed from the same labels and scores. They only replace the event aggregation denominator and prewarning-window matching logic.

Conclusion: event-level evaluation should use the revised episode-start logic in any later final full run.
