# 后续 agent 应生成的代码结构

本文件只是预期结构说明，不是代码。

```text
code/
  config/
    paths.py
    project_config.yaml
    schema_minute_panel.yaml
    variable_config.yaml
    model_config.yaml

  src/
    data/
      00_verify_preprocessed_inputs.py
      01_make_model_ready_panel.py
      02_make_stress_components.py
      03_make_stress_index_and_labels.py

    diagnostics/
      04_descriptive_diagnostics.py
      04b_zero_return_process.py
      04c_intraday_pattern.py

    models/
      05_rgarch_carr_sk.py
      05b_rgarch_carr_sk_simplified.py
      06_qvar_tail_transmission.py
      06b_qvar_stress_test.py
      07_smartboost_forecasting.py
      07b_smartboost_verification_gate.py

    robustness/
      08_robustness_and_phases.py

    visualization/
      plot_style.py
      plot_data_coverage.py
      plot_lsi_intraday.py
      plot_cross_stress.py
      plot_rgarch_risk.py
      plot_qvar_irf.py
      plot_smartboost_evaluation.py

    report/
      09_collect_paper_outputs.py
      export_tables.py
      build_report_inputs.py
      semantic_residue_scan.py

  tests/
    test_paths.py
    test_schema.py
    test_no_lookahead.py
    test_label_construction.py
    test_time_split.py
```

说明：这些文件应由 Codex 生成，而不是由本工作区预置。
