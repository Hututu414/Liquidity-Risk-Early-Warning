from __future__ import annotations

import os
import textwrap


def main() -> int:
    cloud_flag = os.environ.get("CLOUD_RUN") == "1"
    message = f"""
    # Cloud final full run instructions

    Local Windows is reserved for lightweight management only. Do not run final
    full, bounded, bootstrap-heavy, full80 panel construction, or full shard
    merges on the local machine.

    Current CLOUD_RUN=1: {cloud_flag}

    ## Recommended Codespaces workflow

    1. Open the repository in GitHub Codespaces on the intended branch.
    2. Restore or upload `data/processed/onset_model_panel_full80.parquet`.
    3. Confirm you are in Codespaces:

       ```bash
       echo "$CODESPACES"
       pwd
       ```

    4. Mark the run as cloud-side:

       ```bash
       export CLOUD_RUN=1
       ```

    5. Check the environment and data contract:

       ```bash
       python scripts/prepare_environment.py
       python scripts/list_required_data.py
       python scripts/run_bounded_onset_cloud_ready.py --data-path data/processed/onset_model_panel_full80.parquet
       ```

    ## Budgeted event evaluation

    The final full runner is wired to recompute corrected event-level metrics
    and budgeted event metrics after model outputs exist. If rerunning only the
    metric recomputation in cloud, use:

    ```bash
    python scripts/recompute_event_metrics.py \\
      --data-path data/processed/onset_model_panel_full80.parquet \\
      --predictions-dir experiments/onset_baseline_check/checkpoints \\
      --outputs-dir experiments/onset_baseline_check/outputs \\
      --mode full \\
      --bootstrap 500 \\
      --threshold-quantile 0.90 \\
      --gap 5 \\
      --lookback-clean 10 \\
      --budgeted
    ```

    ## Final full command

    ```bash
    export CLOUD_RUN=1

    python scripts/prepare_environment.py
    python scripts/list_required_data.py

    python experiments/onset_baseline_check/run_onset_baseline.py \\
      --mode full \\
      --max-stock-codes null \\
      --bootstrap 500 \\
      --threshold-quantile 0.90 \\
      --gap 5 \\
      --lookback-clean 10 \\
      --data-path data/processed/onset_model_panel_full80.parquet \\
      --resume
    ```

    Use the same command with `--resume` if the cloud job is interrupted.

    ## Data transfer

    - Do not commit parquet, checkpoint, joblib, raw minute data, logs, or large
      output artifacts to Git.
    - For Codespaces, upload `onset_model_panel_full80.parquet` manually or copy
      it with `gh codespace cp` if available.
    - Download `experiments/onset_baseline_check/outputs/`,
      `experiments/onset_baseline_check/logs/`, and selected artifacts after the
      run.

    ## GitHub Actions data inputs

    When using a workflow dispatch that supports private data download:

    - set `data_url` to the private parquet URL;
    - set `data_sha256` when a stable checksum is available;
    - never hard-code secrets, tokens, cookies, or private URLs in repository
      files.
    """
    print(textwrap.dedent(message).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
