# Handoff: RGARCH dynamic skew/kurtosis refined axis adjustment

## Read Files

- `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\.agents\skills\academic-finance-visualization-cn\SKILL.md`
- `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\05_outputs\tables\04_rgarch\rgarch_carr_sk_adapted_conditional_paths.csv`
- `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\05_outputs\tables\04_rgarch\rgarch_carr_sk_adapted_oos_losses.csv`
- `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\07_reviews\figure_audit\rgarch_figure_issue_2_kurtosis_jump_check.md`
- `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\07_reviews\figure_audit\rgarch_figure_issue_3_skewness_kurtosis_jump_check.md`

## Modified Files

- Added `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\04_code\src\visualization\update_rgarch_skew_kurtosis_refined_axis.py`
- Regenerated `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\05_outputs\figures\04_rgarch\fig_rgarch_dynamic_skew_kurtosis_refined.png`
- Regenerated `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\08_report\latex_project\figures\fig_rgarch_dynamic_skew_kurtosis_refined.png`
- Added `D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\07_reviews\figure_audit\rgarch_dynamic_skew_kurtosis_refined_axis_adjustment.md`

## Generated Outputs

- Target PNG rebuilt at 300 dpi with dimensions `2887 x 1807`.
- The lower `k_t` panel now uses a narrow actual-value y-axis around `3.0000` to `3.0014`, with four-decimal tick labels.
- The script selects `RGARCH-CARR-SK-RMAD` from the lowest test-period `R2LOG`; plotted `k_t` range is `3.0001000000` to `3.0012741979`.

## Unresolved Issues

- The lower panel is no longer visually flat, but the source data still have only two unique `k_t` values. It remains a boundary-adjacent diagnostic path, not evidence of a large tail-risk regime shift.
- `08_report/latex_project/figure_table_map.md` still records this figure as not entering the正文 or appendix. This was left unchanged because the request only targeted the image.

## Next Agent

- If the figure should be used in the paper, update the relevant LaTeX include and `figure_table_map.md` deliberately, preserving the conservative interpretation boundary for dynamic kurtosis.
