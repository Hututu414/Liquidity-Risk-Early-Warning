# Revised event-level onset metrics

This script recomputes event-level metrics from cached models only. It does not fit, refit, or update model checkpoints.

Event hits are evaluated by same stock, same trading date, and trading-minute `slot`.
The label-aligned window is `s-(gap+H-1) <= t <= s-gap`; the practical window is H5 `[s-20,s-5]` and H10 `[s-30,s-5]`.

| Horizon | Model | Group | Top5 threshold | Label recall | Practical recall | Avg lead | Median lead | Daily false alarms | Signals/day | Events/day | FA/detected event |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H5 | LightGBM | ALL | 0.707098 | 28.40% | 44.09% | 8.06 | 9.00 | 733.17 | 835.35 | 149.51 | 18.70 |
| H10 | LightGBM | ALL | 0.711206 | 36.93% | 52.96% | 11.39 | 13.00 | 654.70 | 807.23 | 115.01 | 16.50 |

Additional columns in the CSV include total pressure episodes, eligible-event denominators, top5 signal counts, minute-level top5 hits, practical-window daily false alarms, and scored-row counts.
