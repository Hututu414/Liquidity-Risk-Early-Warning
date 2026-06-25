# Feature leakage audit for bounded20 onset baseline

## Scope

- data_path: data/processed/onset_model_panel_full80.parquet
- cache_signature: 4c603e3151d66306
- run_mode: bounded
- max_stock_codes: None
- bootstrap_iterations: 200

## Feature Group Counts

### H5

- P: 10
- M: 25
- C: 35
- ALL: 78

### H10

- P: 10
- M: 25
- C: 35
- ALL: 78

## ALL Feature Names

### H5 first 50

- LSI_5
- LSI_5_lag1
- LSI_5_lag2
- LSI_5_lag5
- LSI_5_rollmean_5
- LSI_5_rollmean_10
- LSI_5_rollmax_5
- LSI_5_rollmax_10
- LSI_5_rollmax_20
- LSI_5_minus_threshold_H5
- MarketLSI
- MarketLSI_lag1
- MarketLSI_rollmean_10
- MarketLSI_rollmax_20
- IndexRet
- IndexRet_lag1
- IndexRet_rollmean_10
- IndexRV
- IndexRV_lag1
- IndexRV_rollmean_10
- IndexRV_rollmax_20
- MarketRelAmt
- MarketRelAmt_lag1
- MarketRelAmt_rollmean_10
- MarketRelAmt_rollmax_20
- xsec_lsi_mean
- xsec_lsi_median
- xsec_lsi_q90
- xsec_lsi_std
- xsec_lsi_skew
- xsec_stock_count
- xsec_pressure_count_H5
- xsec_pressure_breadth_H5
- xsec_pressure_breadth_H5_lag1
- xsec_pressure_breadth_H5_rollmean_10
- ILLIQ_5
- Range_5
- RV_5
- RelAmt_5
- ILLIQ_10
- Range_10
- RV_10
- RelAmt_10
- ILLIQ_20
- Range_20
- RV_20
- RelAmt_20
- z_ILLIQ_5
- z_Range_5
- z_RV_5

### H10 first 50

- LSI_5
- LSI_5_lag1
- LSI_5_lag2
- LSI_5_lag5
- LSI_5_rollmean_5
- LSI_5_rollmean_10
- LSI_5_rollmax_5
- LSI_5_rollmax_10
- LSI_5_rollmax_20
- LSI_5_minus_threshold_H10
- MarketLSI
- MarketLSI_lag1
- MarketLSI_rollmean_10
- MarketLSI_rollmax_20
- IndexRet
- IndexRet_lag1
- IndexRet_rollmean_10
- IndexRV
- IndexRV_lag1
- IndexRV_rollmean_10
- IndexRV_rollmax_20
- MarketRelAmt
- MarketRelAmt_lag1
- MarketRelAmt_rollmean_10
- MarketRelAmt_rollmax_20
- xsec_lsi_mean
- xsec_lsi_median
- xsec_lsi_q90
- xsec_lsi_std
- xsec_lsi_skew
- xsec_stock_count
- xsec_pressure_count_H10
- xsec_pressure_breadth_H10
- xsec_pressure_breadth_H10_lag1
- xsec_pressure_breadth_H10_rollmean_10
- ILLIQ_5
- Range_5
- RV_5
- RelAmt_5
- ILLIQ_10
- Range_10
- RV_10
- RelAmt_10
- ILLIQ_20
- Range_20
- RV_20
- RelAmt_20
- z_ILLIQ_5
- z_Range_5
- z_RV_5

## Leakage Checks

- suspicious_feature_name_hits: 0
  - none
- exact_forbidden_feature_hits: 0
  - none
- panel_schema_future_or_label_hits: 0
  - none
- centered_or_forward_rolling_name_hits: 0
  - none

## Model Feature Importance

### H5 best LightGBM/ALL

- slot_cos: 154.000000 (timing_or_other)
- slot: 131.000000 (timing_or_other)
- z_Range_20: 124.000000 (component)
- z_Range_5: 123.000000 (component)
- z_RelAmt_5: 117.000000 (component)
- LSI_5_rollmax_10: 115.000000 (persistence)
- z_RelAmt_20: 114.000000 (component)
- xsec_lsi_median: 95.000000 (cross)
- IndexRet_rollmean_10: 90.000000 (market)
- z_Range_10: 88.000000 (component)
- LSI_5_rollmax_20: 76.000000 (persistence)
- z_RelAmt_10: 70.000000 (component)
- MarketLSI_rollmax_20: 57.000000 (market)
- LSI_20: 53.000000 (timing_or_other)
- MarketLSI_rollmean_10: 51.000000 (market)
- z_RV_5: 50.000000 (component)
- Range_20: 49.000000 (component)
- Range_10: 48.000000 (component)
- MarketLSI: 47.000000 (market)
- RelAmt_5: 43.000000 (component)
- z_ILLIQ_5: 43.000000 (component)
- RelAmt_20: 41.000000 (component)
- IndexRet: 41.000000 (market)
- ILLIQ_10: 37.000000 (component)
- xsec_pressure_breadth_H5_rollmean_10: 33.000000 (cross)
- ILLIQ_5: 32.000000 (component)
- LSI_5: 31.000000 (persistence)
- RelAmt_10: 31.000000 (component)
- xsec_lsi_q90: 29.000000 (cross)
- LSI_20_lag1: 29.000000 (timing_or_other)

### H10 best LightGBM/ALL

- slot: 153.000000 (timing_or_other)
- slot_cos: 143.000000 (timing_or_other)
- z_RelAmt_20: 142.000000 (component)
- LSI_5_rollmax_20: 116.000000 (persistence)
- z_Range_5: 110.000000 (component)
- z_RelAmt_5: 105.000000 (component)
- z_Range_20: 100.000000 (component)
- z_RelAmt_10: 97.000000 (component)
- z_Range_10: 96.000000 (component)
- LSI_5_rollmax_10: 90.000000 (persistence)
- MarketLSI_rollmax_20: 75.000000 (market)
- IndexRet_rollmean_10: 67.000000 (market)
- xsec_lsi_median: 67.000000 (cross)
- Range_5: 57.000000 (component)
- xsec_lsi_q90: 52.000000 (cross)
- RelAmt_5: 51.000000 (component)
- LSI_20: 49.000000 (timing_or_other)
- Range_10: 47.000000 (component)
- IndexRet: 47.000000 (market)
- MarketLSI: 44.000000 (market)
- LSI_20_lag1: 40.000000 (timing_or_other)
- RelAmt_20: 38.000000 (component)
- LSI_5: 36.000000 (persistence)
- xsec_lsi_std: 36.000000 (cross)
- RelAmt_10: 36.000000 (component)
- RV_20: 35.000000 (component)
- MarketLSI_rollmean_10: 34.000000 (market)
- Range_20: 33.000000 (component)
- z_ILLIQ_5: 32.000000 (component)
- z_RV_20: 31.000000 (component)

### Fallback feature_importance_onset.csv top 30

- slot: 153.000000 (other)
- slot_cos: 143.000000 (other)
- z_RelAmt_20: 142.000000 (component)
- LSI_5_rollmax_20: 116.000000 (persistence)
- z_Range_5: 110.000000 (component)
- z_RelAmt_5: 105.000000 (component)
- z_Range_20: 100.000000 (component)
- z_RelAmt_10: 97.000000 (component)
- z_Range_10: 96.000000 (component)
- LSI_5_rollmax_10: 90.000000 (persistence)
- MarketLSI_rollmax_20: 75.000000 (market)
- IndexRet_rollmean_10: 67.000000 (market)
- xsec_lsi_median: 67.000000 (cross)
- Range_5: 57.000000 (component)
- xsec_lsi_q90: 52.000000 (cross)
- RelAmt_5: 51.000000 (component)
- LSI_20: 49.000000 (component)
- Range_10: 47.000000 (component)
- IndexRet: 47.000000 (market)
- MarketLSI: 44.000000 (market)
- LSI_20_lag1: 40.000000 (component)
- RelAmt_20: 38.000000 (component)
- LSI_5: 36.000000 (persistence)
- xsec_lsi_std: 36.000000 (cross)
- RelAmt_10: 36.000000 (component)
- RV_20: 35.000000 (component)
- MarketLSI_rollmean_10: 34.000000 (market)
- Range_20: 33.000000 (component)
- z_ILLIQ_5: 32.000000 (component)
- z_RV_20: 31.000000 (component)

## Audit Conclusion

- suspected_leakage_columns_found: no
- future_label_aggregate_variables_in_features: no
- future_or_label_columns_present_in_panel_schema_but_not_features: no
- preliminary_legality_of_ALL_increment: passes name-based and cache-feature audit
- main_increment_feature_types:
- component: 0.491
- market: 0.160
- other: 0.134
- persistence: 0.131
- cross: 0.083
- support_C_as_standalone_core_contribution: no; bounded20 C-vs-P increments were negative.
- recommend_all_stock_diagnostic: yes
