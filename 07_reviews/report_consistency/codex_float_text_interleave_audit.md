# Codex Float-Text Interleave Audit

## Scope

- Skill used: `.agents/skills/academic-latex-typesetting-cn/`
- Task: repair the final paper's float placement so the empirical sections read as “引出图表--展示图表--解释图表--过渡到下一图表”.
- No RGARCH-CARR-SK, QVAR, SMARTBoost model estimation was rerun.
- No original figure or model-output directory was moved.

## Files Modified

- `08_report/latex_project/main.tex`
- `08_report/latex_project/sections/05_empirical_results.tex`
- `08_report/latex_project/sections/06_robustness.tex`
- `08_report/latex_project/tables/tab_rgarch_fit_loss.tex`
- `08_report/latex_project/tables/tab_qvar_pinball.tex`
- `08_report/latex_project/tables/tab_qvar_scenarios.tex`
- `08_report/latex_project/tables/tab_smartboost_metrics.tex`
- `08_report/latex_project/tables/tab_smartboost_topk.tex`
- `08_report/latex_project/tables/tab_smartboost_leakage.tex`
- `08_report/latex_project/tables/tab_robustness_summary.tex`

## Float Placement Changes

- QVAR core tables and figures were changed to local `[H]` placement:
  - `tab:qvar-pinball`
  - `fig:qvar-response`
  - `tab:qvar-scenarios`
  - `fig:qvar-stress`
- SMARTBoost core tables and figures were changed to local `[H]` placement:
  - `tab:smartboost-metrics`
  - `fig:sb-pr`
  - `fig:sb-top5`
  - `tab:smartboost-topk`
  - `fig:sb-partial`
- Robustness core figures and summary tables were changed to local `[H]` placement:
  - `fig:robust-label`
  - `fig:rgarch-realized-dist`
  - `fig:qvar-tail-summary`
  - `fig:robust-topk`
  - `tab:smartboost-leakage`
  - `tab:robustness-design`
  - `tab:robustness-conclusions`
- RGARCH main figure `fig:rgarch-risk` uses `[!htbp]` rather than `[H]` to avoid a large blank at the start of Section 5.1 while still allowing here-placement.
- Repeated `\FloatBarrier` commands inside Section 6 were removed; a single section-end barrier remains.
- `\clearpage` was added between appendix figures and the bibliography to prevent appendix figures and references from sharing a page.

## QVAR Sequence Check

The final QVAR section now follows the required sequence:

1. QVAR role and interpretation boundary.
2. Table 8: QVAR MarketLSI equation sample-out pinball loss.
3. Explanation of Table 8, including:
   - \(q=0.95\) test pinball loss = 0.0231;
   - \(q=0.50\) test pinball loss = 0.0447;
   - tail quantile and median behavior differ;
   - loss comparison is not causal identification.
4. Figure 6: QVAR tail-quantile response.
5. Explanation of Figure 6, including median smoothness, tail asymmetry, tail heterogeneity, and the standardization boundary for shock/response wording.
6. Table 9: QVAR pressure-test scenario settings.
7. Explanation of Table 9, including IndexRet = -2, IndexRV = +2, MarketRelAmt = -2, and composite-pressure interpretation.
8. Figure 7: QVAR four-scenario pressure-test paths.
9. Explanation of Figure 7, emphasizing stronger volatility/composite-pressure response, weaker standalone market-drop response, and the role of transaction-bearing state.
10. Section conclusion and transition to SMARTBoost.

PDF text page-map check:

| item | detected pages |
|---|---|
| 表 8 | 18 |
| 图 6 | 18, 25 |
| 表 9 | 19 |
| 图 7 | 19, 20, 25 |

The repeated figure hits outside Section 5.2 are cross-references in robustness text, not misplaced figures. Visual contact-sheet review confirms Table 8 and Figure 6 are on page 18, while Table 9 and Figure 7 are on page 19.

## RGARCH Check

- Section 5.1 now introduces Figure 5, places the risk-path figure near the first reference, explains it immediately, then introduces Table 6 and Table 7.
- Table 6 and Table 7 are both locally placed and appear directly after the realized pressure measure setup.
- Dynamic peakness/kurtosis figure remains excluded from the text body.
- The RGARCH sequence in the rendered PDF is now:
  - page 16: Section 5.1 introduction and Figure 5;
  - page 17: immediate explanation plus Table 6 and Table 7.

## SMARTBoost Check

The final Section 5.3 sequence is:

1. Table 10: validation/test metrics.
2. Explanation of PR-AUC, ROC-AUC, Top5 and Brier context.
3. Figure 8: PR curves.
4. Explanation of why PR curves are more informative for rare pressure events.
5. Figure 9: Top 5% realized pressure rate.
6. Explanation of lift around 10 times.
7. Table 11: Top-K hit rate and lift.
8. Explanation that lift declines as K expands because lower-risk samples enter the high-risk bucket.
9. Figure 10: Partial Effects.
10. Explanation that partial effects are local predictive responses, not causal effects.

PDF text page-map check:

| item | detected pages |
|---|---|
| 表 10 | 20 |
| 图 8 | 20, 21 |
| 图 9 | 21 |
| 表 11 | 22 |
| 图 10 | 22, 23 |

Visual review confirms there is no end-of-section float pile for SMARTBoost.

## Robustness Check

- Section 6.1: Figure 11 is placed directly after the label-threshold setup and followed by an interpretation paragraph.
- Section 6.2: Figure 12 is placed directly after the RGARCH realized-measure setup and followed by a conservative sensitivity interpretation.
- Section 6.3: Figure 13 is placed directly after the QVAR robustness setup and followed by text noting that some scenario responses are weak rather than treating this as a plotting error.
- Section 6.4: Figure 14 is placed directly after the Top-K robustness setup and followed by text explaining that lift decline as K expands is normal for a ranking model.
- Section 6.5: Table 12 appears before the leakage-boundary interpretation; Tables 13 and 14 appear as compact section-summary tables and are not stacked at the bottom of an unrelated float page.

PDF text page-map check:

| item | detected pages |
|---|---|
| 图 11 | 24 |
| 图 12 | 24, 25 |
| 图 13 | 25, 26 |
| 图 14 | 26, 27 |
| 表 12 | 27 |
| 表 13 | 28 |
| 表 14 | 28 |

## Mechanical Checks

- Built with `08_report/latex_project/build_report.ps1`.
- Final PDF: `08_report/latex_project/main.pdf`.
- Final page count: 33.
- `scan_overfull_log.py`:
  - Overfull hbox: 0
  - Underfull hbox: 0
  - Undefined references: 0
  - Missing files: 0
  - Citation warnings: 0
- `scan_tex_floats.py`:
  - Figures: 17
  - Tables parsed in section files: 1
  - `[H]` placements: 9
  - Missing captions: 0
  - Missing labels: 0
  - Unreferenced labels: 0
- `scan_figure_references.py`:
  - Includegraphics commands: 17
  - Missing files: 0
  - Absolute paths: 0
  - Outside figures directory: 0
- `scan_table_width.py`:
  - Most tables: ok
  - `tab_smartboost_metrics.tex` remains a compact many-column table; no overfull box appears and visual review shows it is readable.

## Visual Audit

- Rendered final PDF pages to `tmp/pdf_audit_interleave_20260520/`.
- Contact-sheet review found no consecutive two-page float block in the empirical or robustness sections.
- QVAR no longer has a full text page followed by delayed table/figure pages; Table 8/Figure 6 and Table 9/Figure 7 are now adjacent to their explanatory paragraphs.
- SMARTBoost no longer piles Table 10, Figures 8--10, and Table 11 at the end of the subsection.
- Robustness figures are attached to their respective robustness points.
- Appendix figures and references no longer share a page after adding `\clearpage`.

## Remaining Float Notes

- `scan_tex_floats.py` still reports consecutive float warnings inside `sections/appendix_figures.tex`. This is acceptable because the appendix intentionally groups three supplemental diagnostic figures and does not carry the main empirical argument.
- The bibliography starts on a separate page after the appendix figures.
