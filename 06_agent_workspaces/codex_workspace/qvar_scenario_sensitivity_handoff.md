# Handoff: qvar_scenario_sensitivity

Date: 2026-05-22
Status: COMPLETE

## Figures produced

- `05_outputs/figures/07_robustness/qvar_scenario_sensitivity/qvar_sensitivity_shock_size_cum_abs_q095.png`
- `05_outputs/figures/07_robustness/qvar_scenario_sensitivity/qvar_sensitivity_quantile_cum_abs_shock2.png`
- `05_outputs/figures/07_robustness/qvar_scenario_sensitivity/qvar_sensitivity_fixed_horizon_signed_direction.png`
- `05_outputs/figures/07_robustness/qvar_scenario_sensitivity/qvar_sensitivity_direction_stability_heatmap.png`

## Tables produced

- `05_outputs/tables/07_robustness/qvar_scenario_sensitivity/qvar_scenario_sensitivity_paths.csv`
- `05_outputs/tables/07_robustness/qvar_scenario_sensitivity/qvar_scenario_sensitivity_summary.csv`
- `05_outputs/tables/07_robustness/qvar_scenario_sensitivity/qvar_scenario_direction_stability.csv`
- `05_outputs/tables/07_robustness/qvar_scenario_sensitivity/qvar_scenario_original_path_comparison.csv`

## Figure registry updated

NO. These are candidate sensitivity outputs only.

## CrossStress leak check

CLEAN for task scope. This task only reads QVAR coefficients and scenario-path outputs; it does not alter SMARTBoost features.

## Audit script result

PASS. The script ran with the fixed project Python interpreter and wrote all requested candidate outputs.

## Next steps

If updating the paper later, prefer the quantile cumulative absolute response figure as the replacement for the current QVAR robustness figure.
