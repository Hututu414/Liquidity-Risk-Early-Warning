# Local heavy run stop report

Date: 2026-06-21

## Status

- Local heavy task found at final check: no live heavy Python process was found.
- Checked process patterns: `run_onset_baseline.py`, `build_onset_model_panel.py`, bounded/full/bootstrap/full-shard related Python commands.
- Stop method: no active process required termination at the final stop check. Earlier local final-full attempts had already exited unexpectedly before this report was written.
- Stage at stop/interruption: final full data-preparation stage. The most recent local full attempt reached shard preparation and did not complete model training, bootstrap, corrected full event metrics, or archive generation.

## Preserved Evidence

- Run logs: `experiments/onset_baseline_check/logs/run_20260621_151407.log`, `experiments/onset_baseline_check/logs/run_20260621_152601.log`, `experiments/onset_baseline_check/logs/run_20260621_152944.log`, `experiments/onset_baseline_check/logs/run_20260621_155732.log`.
- Process stdout/stderr: `experiments/onset_baseline_check/outputs/final_full_stdout.txt`, `experiments/onset_baseline_check/outputs/final_full_stderr.txt`.
- Checkpoints: `experiments/onset_baseline_check/checkpoints/`.
- Existing outputs: `experiments/onset_baseline_check/outputs/`.
- Note: `run_20260621_161307.log` and the top-level files updated at `2026-06-21 16:14` are from the allowed local smoke verification, not from final full.

## Integrity Notes

- No data files were deleted.
- No parquet, checkpoint, joblib, raw minute data, or large output artifacts were staged or committed.
- No damaged intermediate file was identified during the stop check.
- The local Windows machine is now treated as lightweight-only. Do not resume final full locally.

## Cloud Continuation Required

The following tasks must move to Codespaces, GitHub Actions, or another cloud runtime:

- final full onset baseline run;
- bootstrap 500 evaluation;
- full corrected event-level recomputation;
- full budgeted event metrics;
- final full result digest and archive.
