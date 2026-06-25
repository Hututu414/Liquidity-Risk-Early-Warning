# Paper restructure waitlist

This file is a waitlist only. It records how the paper could be reorganized if the final full run confirms the diagnostic results. It does not modify the manuscript or any final TeX file.

## Candidate Subsection Titles

- Short-horizon onset warning beyond LSI persistence
- Incremental predictive content of extended historical state variables
- Diagnostic comparison with naive persistence
- Event-level warning tradeoff: recall and daily false alarms

## Existing Claims to Weaken or Replace

- Do not frame onset results as final evidence until the final full run is complete.
- Do not describe the exercise as a model horse race; keep RGARCH-CARR-SK, QVAR, and SMARTBoost as the main evidence chain.
- If final full confirms the diagnostic, weaken any statement that short-horizon warning is only descriptive and replace it with a limited predictive-diagnostic claim.
- Keep persistence as the baseline mechanism: all model gains should be stated relative to naive LSI persistence.

## Candidate Core Tables

- H5/H10 model comparison table: naive persistence, Logit, LightGBM, SMARTBoost across P/M/C/ALL.
- Feature group increment table: M vs P, C vs P, ALL vs P with PR-AUC and Top5 lift deltas.
- Bootstrap CI table: best-vs-naive and feature-group increments with daily bootstrap intervals.
- Event-level operating table: event recall, mean lead time, and daily false alarms.

## Candidate Core Figures

- Precision-recall curves for naive persistence and selected best models.
- Top-k lift comparison for H5 and H10.
- Feature importance by category: persistence, market, cross-section, components, timing/other.
- Optional robustness heatmap over gap, lookback_clean, and threshold_quantile.

## Diagnostic-Only Results for Now

- bounded20 and all-stock diagnostic outputs are not final paper evidence.
- all-stock diagnostic used `--mode bounded`, `--max-stock-codes null`, and bootstrap 200; it is not the final full run.
- H5 event-level recall in the all-stock diagnostic is weak and must not be overclaimed.
- Current diagnostics should not be written into LaTeX automatically.

## Results Waiting for Final Full

- Whether best-vs-naive Delta PR-AUC remains positive under final full settings.
- Whether Top5 lift gains remain stable after full-sample evaluation and final bootstrap settings.
- Whether ALL remains superior to P after final full.
- Whether event-level recall and daily false alarms are acceptable for a paper-grade warning claim.
- Whether robustness grids preserve the same direction across gap, lookback_clean, and threshold_quantile.

## Unsupported Claims

- Do not claim that cross-sectional C features alone provide a stable core contribution.
- Do not claim that all-stock diagnostics are final full-sample evidence.
- Do not claim that the paper already establishes a deployable early-warning system.
- Do not claim that the machine-learning contribution dominates LSI persistence without reporting naive persistence deltas.
