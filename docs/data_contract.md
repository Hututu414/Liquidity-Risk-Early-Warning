# Data contract for `experiments/onset_baseline_check`

This document describes the minimum schema expected by the onset baseline experiment. The experiment can run in `smoke`, `bounded`, or `full` mode, but all real-data modes depend on the same stage-2 LSI-label data contract.

## Required Control Files

- `data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv`
- `data_intermediate/stage2_lsi_labels/time_split.json`
- `data_intermediate/stage2_lsi_labels/label_thresholds_train.json`

The manifest must contain at least:

- `code`
- `output_path`
- `rows`
- `is_index`

## Required Per-Code Shard Columns

The runner reads per-code parquet shards listed in `lsi_labels_manifest.csv`. Required columns are:

- `code`: stock code or symbol.
- `is_index`: boolean flag; stock rows are used and index rows are excluded from stock-level training.
- `date`: trading date.
- `datetime`: minute timestamp.
- `slot`: intraday minute slot.
- `ret_1m`: one-minute return.
- `amount`: traded amount.
- `valid_minutes`: valid minute count or coverage marker.
- `LSI_5`, `LSI_10`, `LSI_20`: liquidity stress index values.
- `MarketLSI`: market-level LSI.
- `IndexRet`: index return state.
- `IndexRV`: index realized volatility state.
- `MarketRelAmt`: market relative amount state.
- `Stress_H5`, `Stress_H10`: original continuation labels, if available.

The current feature specification also expects component features:

- `ILLIQ_5`, `Range_5`, `RV_5`, `RelAmt_5`
- `ILLIQ_10`, `Range_10`, `RV_10`, `RelAmt_10`
- `ILLIQ_20`, `Range_20`, `RV_20`, `RelAmt_20`

and standardized component features:

- `z_ILLIQ_5`, `z_Range_5`, `z_RV_5`, `z_RelAmt_5`
- `z_ILLIQ_10`, `z_Range_10`, `z_RV_10`, `z_RelAmt_10`
- `z_ILLIQ_20`, `z_Range_20`, `z_RV_20`, `z_RelAmt_20`

## Time Split Fields

`time_split.json` must define:

- `train_start`
- `train_end`
- `validation_start`
- `validation_end`
- `test_start`
- `test_end`

The experiment applies a `gap + horizon` embargo around split boundaries to avoid future-window leakage.

## Label Threshold Fields

`label_thresholds_train.json` should define:

- `H5`
- `H10`

If those thresholds are unavailable and the configuration allows fallback, thresholds are derived from train-period `LSI_5` quantiles.

## Data Not Stored in Git

Large parquet/csv.gz/csv data files should not be committed. Place them in the expected folders in a cloud runtime before launching a real experiment, or restore them from an external artifact/source.

## Validation Helper

Run:

```bash
python scripts/list_required_data.py
```

The script scans candidate data files without reading full large files, reports schemas, and flags files that appear to satisfy the minimum onset experiment contract.
