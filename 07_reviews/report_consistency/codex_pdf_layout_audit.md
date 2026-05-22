# Codex PDF Layout Audit Before Repair

## 1. Current PDF

- PDF audited: `08_report/latex_project/main.pdf`
- Page count: 22
- Visual audit method: rendered all pages with `pdftoppm` to `tmp/pdf_audit_initial/` and reviewed a contact sheet plus focused table pages.

## 2. Current Main-Text Figure List

| label | figure | current decision | reason |
|---|---|---|---|
| `fig:timeline` | `figures/fig_timeline.png` | keep | Important for chronological split and no-leakage framing; currently unreferenced and should be cited in prose. |
| `fig:coverage` | `figures/fig_coverage.png` | keep | Data coverage diagnostic; dense labels are acceptable only as a coverage overview. |
| `fig:intraday` | `figures/fig_intraday.png` | keep | Core LSI intraday structure figure. |
| `fig:marketlsi` | `figures/fig_marketlsi.png` | keep | Core descriptive MarketLSI time-series figure. |
| `fig:event-rate` | `figures/fig_event_rate.png` | move to appendix | Useful descriptive diagnostic, but not necessary for the main evidence chain once label distribution is tabulated. |
| `fig:corr` | `figures/fig_corr.png` | move to appendix | Helpful background correlation diagnostic; not a main causal or predictive result. |
| `fig:rgarch-risk` | `figures/fig_rgarch_risk.png` | keep | RGARCH-CARR-SK main figure. |
| `fig:rgarch-realized` | `figures/fig_rgarch_realized.png` | move to appendix | Valid realized measure diagnostic, but secondary to the risk path and table evidence. |
| `fig:rgarch-loss` | `figures/fig_rgarch_loss.png` | remove from text | R2LOG scale compresses RMAD visually; table is clearer and less misleading. |
| `fig:qvar-response` | `figures/fig_qvar_response.png` | keep | QVAR main tail-response figure. |
| `fig:qvar-stress` | `figures/fig_qvar_stress.png` | keep | QVAR pressure-test main figure. |
| `fig:sb-pr` | `figures/fig_sb_pr.png` | keep | SMARTBoost main rare-event warning evidence; currently unreferenced and should be cited. |
| `fig:sb-top5` | `figures/fig_sb_top5.png` | keep | Key application result for high-risk group realized event rate. |
| `fig:sb-partial` | `figures/fig_sb_partial.png` | keep | Interpretable local-response evidence, if caption stays conservative. |
| `fig:robust-label` | `figures/fig_robust_label_threshold.png` | move to appendix | Useful robustness visualization, but not required in main text once robustness is summarized compactly. |
| `fig:robust-sb-topk` | `figures/fig_robust_sb_topk.png` | move to appendix | Useful robustness visualization; main text can keep concise table and prose. |

## 3. Current Main-Text Table List

| label | table file | current decision | reason |
|---|---|---|---|
| `tab:model-framework` | `tab_model_framework.tex` | keep and rebuild | Current table breaks `MarketLSI` as `Mar-ketLSI`; needs `tabularx` and shorter cells. |
| `tab:sample-cleaning` | `tab_sample_cleaning.tex` | keep and rebuild | Numeric fields should be clearer and notes should sit below table through `threeparttable`. |
| `tab:variables` | `tab_variable_definition.tex` | keep and rebuild | Core variable table is necessary, but text-heavy cells should use stable `tabularx` widths. |
| `tab:label-distribution` | `tab_label_distribution.tex` | keep and rebuild | Current note drifts to the right of the table; must use `threeparttable`. |
| `tab:rgarch-fit-loss` | `tab_rgarch_fit_loss.tex` | keep and rebuild | Contains both fit and loss evidence; should avoid `resizebox` and clarify R2LOG scale. |
| `tab:qvar-pinball` | `tab_qvar_pinball.tex` | keep | Compact and readable; minor caption/prose repair only. |
| `tab:qvar-scenarios` | `tab_qvar_scenarios.tex` | keep and rebuild | English shock strings cause wide layout and broken words; replace with three-column Chinese/variable design. |
| `tab:smartboost-leakage` | `tab_smartboost_leakage.tex` | keep | Important no-leakage audit table; can stay compact with `tabularx`. |
| `tab:smartboost-metrics` | `tab_smartboost_metrics.tex` | keep and rebuild | Many columns; should use validation/test grouping with stable widths rather than `resizebox`. |
| `tab:smartboost-topk` | `tab_smartboost_topk.tex` | keep | Core Top-K table; minor caption/prose repair only. |
| `tab:robustness-summary` | `tab_robustness_summary.tex` | split/rebuild | Current table is visually crowded and conclusion cells break vertically; split into design and conclusion tables. |

## 4. Skill Script Summary

- `scan_tex_floats`: 16 figures, all `[H]`; 4 unreferenced labels; adjacent RGARCH floats.
- `scan_table_width`: SMARTBoost metrics table has many columns; visual audit found additional text-heavy table issues.
- `scan_figure_references`: no missing or absolute image paths.
- `scan_overfull_log`: 0 overfull, 17 underfull, 0 undefined citations/references.
- `scan_for_bad_figures`: no referenced figure had static all-zero or missing-file risk; current feature-importance figure is not in text.
- `collect_latex_assets`: 16 referenced figures, 8 unused figure files, 11 table inputs.

## 5. Literature Review Problems

- Current `sections/02_literature.tex` is too thin and does not use the supplied three-part literature review.
- It cites only a small subset of references and leaves most microstructure, realized-measure, QVAR, and machine-learning warning literature out of the paper.
- It already uses `\cite{}` with BibTeX, so the new section should use BibTeX citation keys rather than raw numeric markers.

## 6. refs.bib Problems

- Current `refs.bib` contains only 5 entries.
- Existing `liu2025rgarch` is incomplete relative to the supplied markdown BibTeX draft.
- Existing Andersen and Barndorff-Nielsen entries overlap with fuller markdown entries under different keys.
- Existing SMARTBoost entry is present, but DOI is not provided; it should be retained without fabricating metadata and marked as final verification pending.

## 7. LaTeX Layout Problems

- The preamble lacks `threeparttable`, `placeins`, `longtable`, `pdflscape`, and `adjustbox`, which are useful for the requested table and appendix repairs.
- Heavy `[H]` placement makes page breaks brittle.
- Several figure/table captions are serviceable but too mechanical and need stronger economic context.
- Appendix routing is absent, so secondary diagnostics currently compete with core evidence in the main text.

## 8. Caption and Reference Problems

- `fig:timeline`, `fig:sb-pr`, `fig:robust-label`, and `fig:robust-sb-topk` are not referenced by `\ref`-style commands in current text.
- Captions generally avoid filenames, but some should better state sample split, horizon, or interpretation boundary.
- Table notes are implemented with manual `\vspace` and `\footnotesize`, causing visible placement issues.

## 9. Old or Low-Quality Figure Issues

- No old financial-engineering template figure is referenced.
- Feature-importance all-zero figure is not in the current main text and should remain excluded.
- Dynamic skew/kurtosis diagnostic is currently unused and should not become a core figure.
- R2LOG bar chart should be removed from the main text because RMAD is visually compressed by scale differences.

## 10. Repair Plan

1. Add needed layout packages and appendix inputs in `main.tex`.
2. Replace `sections/02_literature.tex` with a three-subsection LaTeX literature review based on `01_materials/literature/文献综述_编号引用_中文术语版.md`.
3. Merge markdown BibTeX entries into `refs.bib` without deleting existing project entries; mark duplicate keys and SMARTBoost verification status in audit.
4. Rebuild text-heavy tables with `tabularx` and `threeparttable`, especially tables 1, 4, 7, 8, and 11.
5. Reduce main-text figures to the core chain and move secondary diagnostics to `sections/appendix_figures.tex`.
6. Add `\FloatBarrier` at section boundaries and repair nearby prose references.
7. Compile with XeLaTeX/BibTeX until the PDF has no undefined citations, missing references, or missing files.
