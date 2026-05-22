# scan_tex_floats

- Project root: `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only`
- Python expected by project: `D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe`
- Sections scanned: 8
- Figures: 18
- Tables: 1
- `[H]` placements: 12
- Missing captions: 0
- Missing labels: 0
- Labels not referenced by `\ref`-style commands: 0

## Float Details

| file | line | env | placement | caption | label | ref status |
|---|---:|---|---|---|---|---|
| `08_report/latex_project/sections/02_literature.tex` | 29 | table | `[tbp]` | yes | `tab:literature-map` | referenced |
| `08_report/latex_project/sections/04_data_descriptive.tex` | 11 | figure | `[tbp]` | yes | `fig:timeline` | referenced |
| `08_report/latex_project/sections/04_data_descriptive.tex` | 30 | figure | `[tbp]` | yes | `fig:coverage` | referenced |
| `08_report/latex_project/sections/04_data_descriptive.tex` | 43 | figure | `[tbp]` | yes | `fig:intraday` | referenced |
| `08_report/latex_project/sections/04_data_descriptive.tex` | 56 | figure | `[tbp]` | yes | `fig:marketlsi` | referenced |
| `08_report/latex_project/sections/05_empirical_results.tex` | 9 | figure | `[!htbp]` | yes | `fig:rgarch-risk` | referenced |
| `08_report/latex_project/sections/05_empirical_results.tex` | 20 | figure | `[!htbp]` | yes | `fig:rgarch_dynamic_skewness` | referenced |
| `08_report/latex_project/sections/05_empirical_results.tex` | 53 | figure | `[H]` | yes | `fig:qvar-response` | referenced |
| `08_report/latex_project/sections/05_empirical_results.tex` | 70 | figure | `[H]` | yes | `fig:qvar-stress` | referenced |
| `08_report/latex_project/sections/05_empirical_results.tex` | 95 | figure | `[H]` | yes | `fig:sb-pr` | referenced |
| `08_report/latex_project/sections/05_empirical_results.tex` | 106 | figure | `[H]` | yes | `fig:sb-top5` | referenced |
| `08_report/latex_project/sections/05_empirical_results.tex` | 123 | figure | `[H]` | yes | `fig:sb-partial` | referenced |
| `08_report/latex_project/sections/06_robustness.tex` | 9 | figure | `[H]` | yes | `fig:robust-label` | referenced |
| `08_report/latex_project/sections/06_robustness.tex` | 24 | figure | `[H]` | yes | `fig:rgarch-realized-dist` | referenced |
| `08_report/latex_project/sections/06_robustness.tex` | 37 | figure | `[H]` | yes | `fig:qvar-tail-summary` | referenced |
| `08_report/latex_project/sections/06_robustness.tex` | 52 | figure | `[H]` | yes | `fig:robust-topk` | referenced |
| `08_report/latex_project/sections/appendix_figures.tex` | 7 | figure | `[H]` | yes | `fig:app-event-rate` | referenced |
| `08_report/latex_project/sections/appendix_figures.tex` | 16 | figure | `[H]` | yes | `fig:app-corr` | referenced |
| `08_report/latex_project/sections/appendix_figures.tex` | 29 | figure | `[H]` | yes | `fig:app-sb-calibration` | referenced |

## Consecutive Float Warnings

- 08_report/latex_project/sections/appendix_figures.tex lines 7 and 16: adjacent floats with little explanatory prose.
- 08_report/latex_project/sections/appendix_figures.tex lines 16 and 29: adjacent floats with little explanatory prose.

## Suggested Actions

- Add captions and labels where missing.
- Reference every main-text figure and table in nearby prose.
- Replace excessive `[H]` with ordinary float placement or section-level `\FloatBarrier` when page breaks look poor.
- Add explanatory text between adjacent floats unless they form one deliberate multi-part evidence block.
