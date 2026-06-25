# Feature leakage audit for bounded20 onset baseline

## Scope

- data_path: data/processed/onset_model_panel_bounded20.parquet
- cache_signature: 48eca313c32c4033
- run_mode: bounded
- max_stock_codes: 20
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

- slot_cos: 119.000000 (timing_or_other)
- LSI_5_rollmax_10: 101.000000 (persistence)
- z_RelAmt_5: 76.000000 (component)
- z_Range_10: 75.000000 (component)
- slot: 72.000000 (timing_or_other)
- z_Range_20: 63.000000 (component)
- z_Range_5: 63.000000 (component)
- MarketLSI_rollmax_20: 58.000000 (market)
- LSI_5_rollmax_5: 56.000000 (persistence)
- ILLIQ_5: 56.000000 (component)
- LSI_5_rollmax_20: 53.000000 (persistence)
- IndexRet_rollmean_10: 48.000000 (market)
- IndexRV_lag1: 47.000000 (market)
- MarketLSI: 45.000000 (market)
- xsec_lsi_skew: 45.000000 (cross)
- slot_sin: 45.000000 (timing_or_other)
- LSI_20: 43.000000 (timing_or_other)
- z_RelAmt_20: 41.000000 (component)
- z_RelAmt_10: 41.000000 (component)
- MarketLSI_rollmean_10: 40.000000 (market)
- IndexRet: 40.000000 (market)
- RV_20: 35.000000 (component)
- z_RV_5: 35.000000 (component)
- xsec_lsi_q90: 35.000000 (cross)
- MarketLSI_lag1: 35.000000 (market)
- IndexRet_lag1: 33.000000 (market)
- RelAmt_20: 31.000000 (component)
- xsec_lsi_std: 27.000000 (cross)
- RelAmt_5: 27.000000 (component)
- LSI_5_lag5: 26.000000 (persistence)

### H10 best SMARTBoost/ALL

- no native model importance available

### Fallback feature_importance_onset.csv top 30

- slot_cos: 113.000000 (other)
- slot: 93.000000 (other)
- LSI_5_rollmax_10: 82.000000 (persistence)
- z_Range_20: 73.000000 (component)
- z_Range_5: 72.000000 (component)
- z_RelAmt_20: 72.000000 (component)
- LSI_5_rollmax_20: 60.000000 (persistence)
- LSI_20: 57.000000 (component)
- MarketLSI_rollmax_20: 57.000000 (market)
- MarketLSI_lag1: 53.000000 (market)
- MarketLSI: 53.000000 (market)
- z_RV_5: 49.000000 (component)
- MarketLSI_rollmean_10: 46.000000 (market)
- xsec_lsi_skew: 45.000000 (cross)
- RV_20: 41.000000 (component)
- RV_10: 40.000000 (component)
- RelAmt_20: 40.000000 (component)
- MarketRelAmt: 39.000000 (market)
- z_RelAmt_5: 37.000000 (component)
- IndexRV_lag1: 35.000000 (market)
- IndexRV_rollmax_20: 34.000000 (market)
- slot_sin: 33.000000 (other)
- IndexRet: 33.000000 (market)
- LSI_5_minus_threshold_H10: 33.000000 (persistence)
- Range_20: 32.000000 (component)
- z_Range_10: 32.000000 (component)
- RV_5: 31.000000 (component)
- z_RelAmt_10: 29.000000 (component)
- LSI_10: 28.000000 (component)
- LSI_20_lag1: 27.000000 (component)

## Audit Conclusion

- suspected_leakage_columns_found: no
- future_label_aggregate_variables_in_features: no
- future_or_label_columns_present_in_panel_schema_but_not_features: no
- preliminary_legality_of_ALL_increment: passes name-based and cache-feature audit
- main_increment_feature_types:
- component: 0.432
- market: 0.224
- persistence: 0.151
- other: 0.129
- cross: 0.064
- support_C_as_standalone_core_contribution: no; bounded20 C-vs-P increments were negative.
- recommend_all_stock_diagnostic: yes
