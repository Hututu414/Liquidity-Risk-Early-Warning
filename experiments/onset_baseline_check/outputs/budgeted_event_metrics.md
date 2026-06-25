# Budgeted event-level onset metrics

Signals are selected within each trading day by descending model score. Event matching uses the corrected pressure-episode logic and trading-minute `slot` windows.

| Horizon | Budget | Signals/day | Daily false alarms | Label recall | Practical recall | Avg lead | Median lead | FA/detected event | Detected/Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H5 | Top 20/day | 20.00 | 15.81 | 2.13% | 3.70% | 7.49 | 8.00 | 5.38 | 426/20018 |
| H5 | Top 50/day | 50.00 | 40.50 | 4.04% | 7.25% | 7.63 | 8.00 | 7.27 | 808/20018 |
| H5 | Top 100/day | 100.00 | 82.64 | 6.76% | 11.87% | 7.71 | 8.00 | 8.85 | 1354/20018 |
| H5 | Top 200/day | 200.00 | 167.95 | 11.32% | 19.59% | 7.82 | 8.00 | 10.75 | 2266/20018 |
| H5 | Top 0.5%/day | 84.02 | 69.06 | 5.97% | 10.52% | 7.71 | 8.00 | 8.38 | 1195/20018 |
| H5 | Top 1.0%/day | 167.60 | 139.99 | 9.96% | 17.28% | 7.78 | 8.00 | 10.18 | 1994/20018 |
| H5 | Top 2.0%/day | 334.66 | 284.99 | 16.05% | 26.93% | 7.88 | 9.00 | 12.86 | 3213/20018 |
| H5 | Top 5.0%/day | 835.83 | 736.59 | 28.15% | 43.66% | 8.03 | 9.00 | 18.95 | 5635/20018 |
| H10 | Top 20/day | 20.00 | 13.38 | 3.98% | 7.81% | 9.92 | 10.00 | 3.13 | 620/15585 |
| H10 | Top 50/day | 50.00 | 34.63 | 7.94% | 15.01% | 10.09 | 10.00 | 4.06 | 1237/15585 |
| H10 | Top 100/day | 100.00 | 71.21 | 12.61% | 22.49% | 10.37 | 11.00 | 5.25 | 1966/15585 |
| H10 | Top 200/day | 200.00 | 148.67 | 18.89% | 31.26% | 10.64 | 11.00 | 7.32 | 2944/15585 |
| H10 | Top 0.5%/day | 81.19 | 57.05 | 11.21% | 20.12% | 10.26 | 11.00 | 4.73 | 1747/15585 |
| H10 | Top 1.0%/day | 161.91 | 119.09 | 16.68% | 28.38% | 10.55 | 11.00 | 6.64 | 2600/15585 |
| H10 | Top 2.0%/day | 323.35 | 248.81 | 23.76% | 37.68% | 10.88 | 12.00 | 9.74 | 3703/15585 |
| H10 | Top 5.0%/day | 807.68 | 662.46 | 36.25% | 52.33% | 11.33 | 13.00 | 17.00 | 5650/15585 |

The CSV also includes practical-window false alarms, practical lead time, practical detected events, and total pressure episode counts.
