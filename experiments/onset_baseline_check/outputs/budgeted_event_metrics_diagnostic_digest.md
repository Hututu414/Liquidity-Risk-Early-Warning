# Budgeted event-level diagnostic digest

## Scope

- Source: current all-stock diagnostic or final-full cached models, depending on the cache mode used by the caller.
- Training: no model refit is performed by this recomputation script.
- Event logic: corrected pressure-episode start and trading-slot prewarning windows.

## Baseline top-5% event metrics

- H5: signals/day 835.35, daily false alarms 733.17, label recall 28.40%, practical recall 44.09%.
- H10: signals/day 807.23, daily false alarms 654.70, label recall 36.93%, practical recall 52.96%.

## Budget summary

- Top 20/day: avg signals/day 20.00, avg daily false alarms 14.59, min label recall 2.13%, min practical recall 3.70%.
- Top 50/day: avg signals/day 50.00, avg daily false alarms 37.57, min label recall 4.04%, min practical recall 7.25%.
- Top 100/day: avg signals/day 100.00, avg daily false alarms 76.93, min label recall 6.76%, min practical recall 11.87%.
- Top 200/day: avg signals/day 200.00, avg daily false alarms 158.31, min label recall 11.32%, min practical recall 19.59%.
- Top 0.5%/day: avg signals/day 82.61, avg daily false alarms 63.06, min label recall 5.97%, min practical recall 10.52%.
- Top 1.0%/day: avg signals/day 164.76, avg daily false alarms 129.54, min label recall 9.96%, min practical recall 17.28%.
- Top 2.0%/day: avg signals/day 329.01, avg daily false alarms 266.90, min label recall 16.05%, min practical recall 26.93%.
- Top 5.0%/day: avg signals/day 821.76, avg daily false alarms 699.52, min label recall 28.15%, min practical recall 43.66%.

## Recommendation

- Recommended main-table budget: Top 2.0%/day.
- Recommended appendix budgets: report the full Top N and Top pct grid to show the recall/false-alarm tradeoff.
- Effect on final full: budgeted event evaluation is an application diagnostic and does not change the PR-AUC/TopK decision to proceed to final full.
- If the chosen budget keeps meaningful recall while sharply reducing false alarms, it can be used as supplemental evidence of practical monitoring value.

Required judgment phrase:

预算约束事件级评价可以作为实际监测价值的补充证据。
