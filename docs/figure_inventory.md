# Figure Inventory

This clean code release keeps only small PNG figures needed to show experiment results and reproduction checks. Thesis TeX/PDF assets under `report/latex_project/` are not modified and are not part of the release.

## Kept Figures

| File | Source | Purpose |
| --- | --- | --- |
| `figures/fig_main_01_marketlsi_events.png` | `experiments/paper_material_pack/figures_main/` | MarketLSI event illustration and stress episode check. |
| `figures/fig_main_02_qvar_tail_response.png` | `experiments/paper_material_pack/figures_main/` | QVAR tail response summary. |
| `figures/fig_main_03_qvar_tail_state_series.png` | `experiments/paper_material_pack/figures_main/` | QVAR high-tail state time-series check. |
| `figures/fig_main_04_onset_pr_curve.png` | `experiments/paper_material_pack/figures_main/` | Onset baseline precision-recall curve. |
| `figures/fig_main_05_delta_pr_auc.png` | `experiments/paper_material_pack/figures_main/` | Delta PR-AUC against persistence baseline. |
| `figures/fig_main_06_feature_group_increment.png` | `experiments/paper_material_pack/figures_main/` | Feature-group incremental value. |
| `figures/fig_main_07_event_level_monitoring.png` | `experiments/paper_material_pack/figures_main/` | Event-level monitoring result. |
| `figures/fig_main_08_budgeted_event_tradeoff.png` | `experiments/paper_material_pack/figures_main/` | Budgeted event-warning tradeoff. |
| `figures/fig_appendix_a2_topk_lift_curve.png` | `experiments/paper_material_pack/figures_appendix/` | Top-K lift reproduction check. |
| `figures/fig_appendix_a3_calibration_curve.png` | `experiments/paper_material_pack/figures_appendix/` | Calibration reproduction check. |

## Not Kept In The Clean Release

The following local figure groups are intentionally excluded from Git:

```text
report/latex_project/figures/
08_report/latex_project/figures/
outputs/figures/
experiments/paper_material_pack/
07_reviews/report_consistency/**/*render*/
```

Reasons:

- They are thesis build assets, writing material packs, render audits, or legacy intermediate figures.
- Many duplicate the kept PNGs.
- The clean repository is for code, compact reproducible outputs, and review-facing figures, not for paper packaging.

## PDF Figure Policy

No figure PDFs are staged in this clean release. Small PDF versions exist locally in paper/output folders, but they are ignored to avoid mixing paper-package assets with the code release.
