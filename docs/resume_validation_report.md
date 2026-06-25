# Resume Validation Report

## Scope

This report validates only smoke-mode resume behavior using a small sample panel:

```text
data/processed/onset_model_panel_sample5.parquet
```

No bounded or full experiment is run in this validation.

## Command

```bash
python experiments/onset_baseline_check/run_onset_baseline.py --mode smoke --max-stock-codes 3 --bootstrap 10 --data-path data/processed/onset_model_panel_sample5.parquet --resume
```

## Results

- first_successful_run_elapsed_seconds: 33.158
- cached_resume_run_elapsed_seconds: 1.441
- checkpoint_read: yes, `experiments/onset_baseline_check/checkpoints/manifest.json`
- skipped_label_construction: yes on cached report resume
- skipped_feature_construction: yes on cached report resume
- reused_model_cache: yes; the successful run reused signature-matched model joblib checkpoints from the earlier interrupted attempt
- reused_prediction_or_bootstrap_result: report-level cache reuse succeeded; the cached resume skipped recomputation of prediction, bootstrap, figure, and report stages
- can_enter_bounded: yes, after the full model panel is available in `data/processed/onset_model_panel.parquet` or an explicit cloud `data_url` restores it

## Interpretation

The sample5 smoke path can complete on `data/processed/onset_model_panel_sample5.parquet`. Repeating the same command with `--resume` found completed reports for matching parameters and returned from cache in about 1.4 seconds.

One intermediate repeat exited with a Windows native code before entering the Python run log. The runner was adjusted to lazy-load LightGBM so cached report resume does not import that binary dependency before the early cache check. The subsequent cached resume completed normally.

This validates the smoke-level resume path. Bounded should still be run only after the full model panel is available and the bounded wrapper confirms the data contract.
