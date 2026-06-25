# Data Transfer to Cloud

`data/processed/onset_model_panel.parquet` is intentionally ignored by Git. Do not commit the full model panel, raw minute data, checkpoint parquet files, or joblib model files to the repository.

## 本地轻量模式与云端重计算规则

- Local Windows is limited to code edits, git checks, documentation, `py_compile`, and very small smoke tests.
- Do not build or merge `full80` panels locally.
- Do not run `bounded` or `full` locally.
- Do not run large bootstrap jobs or full shard scans locally.
- Run heavy recomputation in Codespaces, GitHub Actions, or another cloud runtime.
- Set `CLOUD_RUN=1` before cloud-side bounded/full commands.
- Confirm Codespaces with `echo "$CODESPACES"`; it should print `true`.
- Use `git check-ignore -v data/processed/onset_model_panel_full80.parquet` and `git status --short` before committing.
- If local Windows is unstable, never run local `--resume` full.

## Recommended Order

1. Codespaces manual upload for bounded or full runs.
2. Private URL or release asset download for GitHub Actions bounded runs.
3. Codespaces-only or Actions-based real experiments, with local Windows used only for lightweight checks.

## Scheme A: Codespaces Manual Upload

Use this for bounded and full runs when data is private or large.

1. Obtain the panel from a cloud-side build, private artifact, or trusted manual upload source.
2. Do not commit the parquet file.
3. Open GitHub Codespaces for the repository.
4. Upload the parquet file into:

```text
data/processed/onset_model_panel.parquet
```

5. In Codespaces, mark the job as cloud-side and run bounded only after smoke checks pass:

```bash
export CLOUD_RUN=1
python scripts/prepare_environment.py
python scripts/list_required_data.py
python experiments/onset_baseline_check/run_onset_baseline.py --mode bounded --max-stock-codes 20 --bootstrap 200 --data-path data/processed/onset_model_panel.parquet --resume
```

If GitHub CLI is installed and authenticated, `gh codespace cp` can also copy the file into a Codespace. This is optional and depends on the user's local GitHub CLI setup.

## Scheme B: Private URL or Release Asset Download

Use this for GitHub Actions bounded runs when a private, access-controlled data URL is available.

The manual `Onset baseline` workflow supports optional inputs:

- `data_url`
- `data_sha256`

If `data_url` is non-empty, the workflow downloads the file to:

```text
data/processed/onset_model_panel.parquet
```

If `data_sha256` is non-empty, the workflow validates the downloaded file with `sha256sum --check`. A mismatch fails the run with a clear error. The repository does not hard-code URLs or tokens.

Recommended manual workflow settings:

- `mode=bounded`
- `max_stock_codes=20`
- `bootstrap=200`
- `threshold_quantile=0.90`
- `gap=5`
- `lookback_clean=10`
- leave `data_path` empty unless you want an explicit hard-fail path
- set `data_url` only in the workflow dispatch form
- set `data_sha256` when the source provides a stable checksum

## Scheme C: Actions Smoke Only

Use this when data is too large or too sensitive for GitHub-hosted runners.

In this scheme:

- GitHub Actions runs only environment checks, data-contract scanning, py_compile, and optional smoke behavior.
- Real bounded and full experiments run in Codespaces or another cloud runtime after the panel has been uploaded.
- This is the most conservative data-security option.

## Safety Notes

- Do not commit `data/processed/*.parquet`.
- Do not commit `data_intermediate` parquet, CSV, or JSON data artifacts.
- Do not commit experiment checkpoint parquet or joblib model files.
- Do not place secrets or tokens in workflow YAML, scripts, docs, or command history.
- Do not run full until smoke and bounded both pass on the intended data source.
