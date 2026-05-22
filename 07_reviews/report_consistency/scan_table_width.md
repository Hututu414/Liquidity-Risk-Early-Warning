# scan_table_width

- Project root: `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only`
- Python expected by project: `D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe`
- TeX files scanned: 20
- Tabular-like environments found: 14

## Table Scan

| file | line | env | columns | booktabs | wrappers | risks |
|---|---:|---|---:|---|---|---|
| `08_report/latex_project/sections/02_literature.tex` | 35 | tabularx | 0 | yes | tabularx | ok |
| `08_report/latex_project/tables/tab_label_distribution.tex` | 7 | tabular | 3 | yes | - | ok |
| `08_report/latex_project/tables/tab_model_framework.tex` | 7 | tabularx | 0 | yes | tabularx | ok |
| `08_report/latex_project/tables/tab_qvar_pinball.tex` | 6 | tabular | 4 | yes | - | ok |
| `08_report/latex_project/tables/tab_qvar_scenarios.tex` | 7 | tabularx | 0 | yes | tabularx | ok |
| `08_report/latex_project/tables/tab_rgarch_fit_loss.tex` | 7 | tabular | 4 | yes | - | ok |
| `08_report/latex_project/tables/tab_rgarch_fit_loss.tex` | 30 | tabular | 4 | yes | - | ok |
| `08_report/latex_project/tables/tab_robustness_summary.tex` | 7 | tabularx | 0 | yes | tabularx | ok |
| `08_report/latex_project/tables/tab_robustness_summary.tex` | 30 | tabularx | 0 | yes | tabularx | ok |
| `08_report/latex_project/tables/tab_sample_cleaning.tex` | 7 | tabularx | 0 | yes | tabularx | ok |
| `08_report/latex_project/tables/tab_smartboost_leakage.tex` | 7 | tabularx | 0 | yes | tabularx | ok |
| `08_report/latex_project/tables/tab_smartboost_metrics.tex` | 8 | tabular | 8 | yes | - | many columns, may need width wrapper |
| `08_report/latex_project/tables/tab_smartboost_topk.tex` | 7 | tabular | 4 | yes | - | ok |
| `08_report/latex_project/tables/tab_variable_definition.tex` | 7 | tabularx | 0 | yes | tabularx | ok |

## Long Cell Examples

- None detected.

## Suggested Actions

- Use `booktabs` for formal paper tables.
- Use `tabularx` for text-heavy tables and `adjustbox` only for slight overflow.
- Use `sidewaystable` or split the table when many columns make text unreadable.
- Move large raw CSV-style material to appendix or external data outputs.
