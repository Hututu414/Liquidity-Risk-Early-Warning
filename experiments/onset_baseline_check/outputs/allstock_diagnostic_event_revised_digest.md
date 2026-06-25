# All-stock diagnostic event-level revised digest

## What changed

The original digest is not overwritten. This note only revises the event-level aggregation.

Original H5 event recall was zero because the event-level code treated onset label times as episode starts and then searched for signals before those label times. The corrected implementation defines events from true LSI pressure episode starts and matches signals in the label-aligned prewarning window.

Minute-level PR-AUC and Top5 lift are unaffected by this correction.

## Original event-level output

- H10: original event recall 11.16%, daily false alarms 25.50.
- H5: original event recall 0.00%, daily false alarms 27.78.

## Revised event-level output

- H5: label-aligned recall 28.40%, practical recall 44.09%, label-aligned daily false alarms 733.17, practical daily false alarms 595.14.
- H10: label-aligned recall 36.93%, practical recall 52.96%, label-aligned daily false alarms 654.70, practical daily false alarms 521.34.

## Decision

- Event-level evaluation had a time-window misalignment; after correction, the event-level results are usable as diagnostics. Full run should use the revised event metrics.
- Recommendation on final full: the corrected event metrics do not overturn the prior all-stock minute-level conclusion; proceed to final full only if the user explicitly asks, and use the revised event metrics.
- Recommendation for paper body: do not write these event-level diagnostics into the paper yet; use them to guide the next full run design.
- Paper body/final TeX: not modified.
- Future full run should use the revised event-level logic.

Required judgment phrase:

事件级评价原实现存在时间窗口错位；修正后不影响分钟级 PR-AUC 与 TopK lift 结论，但 full run 应使用修正后的事件级指标。
