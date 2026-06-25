# Codex PDF Layout Fix Report

## Scope

This repair covered literature integration, BibTeX merge, figure selection, float placement, table rebuilding, caption cleanup, compile-log checks, and PDF visual review. It did not rerun the RGARCH-CARR-SK, QVAR, or SMARTBoost models and did not change empirical conclusions.

## Files Updated

- `08_report/latex_project/main.tex`
- `08_report/latex_project/sections/02_literature.tex`
- `08_report/latex_project/sections/03_data.tex`
- `08_report/latex_project/sections/05_descriptive.tex`
- `08_report/latex_project/sections/06_rgarch.tex`
- `08_report/latex_project/sections/07_qvar.tex`
- `08_report/latex_project/sections/08_smartboost.tex`
- `08_report/latex_project/sections/09_robustness_conclusion.tex`
- `08_report/latex_project/sections/appendix_figures.tex`
- `08_report/latex_project/refs.bib`
- `08_report/latex_project/figure_table_map.md`
- table files under `08_report/latex_project/tables/`

## Main Repairs

- Replaced the thin literature review with a three-subsection review built from `01_materials/literature/文献综述_编号引用_中文术语版.md`.
- Merged the markdown BibTeX draft into `refs.bib` without deleting existing project references.
- Added `threeparttable`, `placeins`, `longtable`, `pdflscape`, `adjustbox`, and a reusable `Y` column type to support cleaner tables and floats.
- Replaced rigid `[H]` figure placement with normal float placement and section-level `\FloatBarrier`.
- Removed the misleading RGARCH R2LOG bar chart from the main text; RGARCH loss evidence is now table-based.
- Moved non-core diagnostics to appendix: event-rate series, correlation heatmap, realized-measure comparison, calibration curve, and selected robustness figures.
- Kept the main-text figure set focused on the paper's evidence chain.

## Figures Kept in Main Text

- Sample split timeline
- Stock-month valid-minute coverage heatmap
- LSI intraday pattern
- MarketLSI time series
- RGARCH-CARR-SK conditional pressure risk path
- QVAR tail-quantile response
- QVAR pressure-test paths
- SMARTBoost out-of-sample PR curve
- SMARTBoost Top 5% realized pressure rate
- SMARTBoost partial effects

## Figures Moved to Appendix

- H5/H10 event-rate time series
- Core-variable correlation heatmap
- RGARCH realized pressure measure comparison
- SMARTBoost calibration curve
- Label-threshold robustness figure
- SMARTBoost Top-K robustness figure

## Figures Excluded

- RGARCH R2LOG bar chart: excluded because the shared linear scale makes RMAD visually misleading.
- Feature-importance all-zero figure: excluded from both main text and appendix.
- Dynamic skewness/kurtosis diagnostic figure: excluded from the paper body as a non-core diagnostic.
- Additional robustness figures not needed for the main argument were kept out of the TeX body.

## Tables Rebuilt or Split

- Table 1 framework table: rebuilt as a three-column `tabularx` table, removing hard word breaks.
- Sample cleaning table: rebuilt with concise notes and numeric alignment.
- Variable definition table: rebuilt with `tabularx` and a proper table note.
- Label distribution table: rebuilt with `threeparttable`, fixing the note that previously drifted to the side.
- RGARCH fit/loss table: split into a fit-criteria table and a sample-out loss table.
- QVAR scenario table: rewritten as `情景 / 标准化冲击 / 经济含义`, avoiding long English word breaks.
- SMARTBoost leakage table: rewritten to remove implementation-style wording from the paper.
- SMARTBoost Top-K table: given a unified table note.
- Robustness summary table: split into design and conclusion tables to avoid cramped vertical breaking.
- Literature-use table: compressed from the markdown 23-row table into a short three-column main-text table.

## Final Compile and Scan Status

- `08_report/latex_project/main.pdf` compiled successfully.
- Final PDF page count: 29.
- Final scan results:
  - overfull hbox: 0
  - underfull hbox: 0
  - undefined references: 0
  - missing files: 0
  - citation warnings: 0
  - absolute image paths: 0
  - missing figure files: 0
  - `[H]` figures: 0
- Final PDF pages were rendered and reviewed through contact sheets and focused page checks.

## Remaining Manual Checks

- SMARTBoost bibliographic metadata should be verified against the final source before formal submission; no unverified DOI or page range was added.
- Appendix figure grouping is visually acceptable, but a final human review can decide whether to keep all six supplemental figures.
- The SMARTBoost metrics table remains compact; it is readable in the final PDF and produces no overfull box, but it is the only table still flagged by the simple width scanner for having many columns.
