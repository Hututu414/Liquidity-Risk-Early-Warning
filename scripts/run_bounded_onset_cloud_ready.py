from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PANEL = Path("data/processed/onset_model_panel.parquet")
CHECKPOINT_MANIFEST = Path("experiments/onset_baseline_check/checkpoints/manifest.json")
REQUIRED_GROUPS = {
    "code": {"code", "stock_code", "symbol", "ticker"},
    "date": {"date", "trading_date", "trade_date"},
    "datetime": {"datetime", "timestamp", "minute", "minute_timestamp", "minute_ts"},
    "LSI_5": {"LSI_5", "LSI5", "lsi_5", "lsi5"},
    "MarketLSI": {"MarketLSI", "market_lsi"},
    "IndexRet": {"IndexRet", "index_ret"},
    "IndexRV": {"IndexRV", "index_rv"},
    "MarketRelAmt": {"MarketRelAmt", "market_rel_amt"},
}
FORBIDDEN_PARTS = (
    "future",
    "lead",
    "target",
    "label",
    "max_future",
    "forward",
    "FutureMax",
    "CrossStress",
    "Y_onset",
)
ALLOWED_LABEL_COLUMNS = {"Stress_H5", "Stress_H10"}

LOCAL_HEAVY_REFUSAL = (
    "本地电脑已设置为轻量模式。当前命令属于重计算任务，已拒绝在本地运行。\n"
    "请在 GitHub Codespaces 或 GitHub Actions 中运行该任务。\n"
    "如确认是在云端环境，请设置环境变量 CLOUD_RUN=1。"
)


def project_path(path: Path | str) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def cloud_run_enabled() -> bool:
    return (
        os.environ.get("CLOUD_RUN") == "1"
        or os.environ.get("CODESPACES", "").lower() == "true"
        or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
    )


def local_windows_light_mode() -> bool:
    return sys.platform.startswith("win") and not cloud_run_enabled()


def local_heavy_override_confirmed(allow_local_heavy: bool) -> bool:
    if not allow_local_heavy:
        return False
    print("WARNING: --allow-local-heavy was requested on a local Windows machine.")
    print("This may crash or restart the local computer. Prefer Codespaces or GitHub Actions.")
    if not sys.stdin.isatty():
        print("Refusing override because no interactive confirmation is available.")
        return False
    reply = input("Type ALLOW_LOCAL_HEAVY to continue: ").strip()
    return reply == "ALLOW_LOCAL_HEAVY"


def same_project_path(left: Path, right: Path) -> bool:
    try:
        return project_path(left).resolve() == project_path(right).resolve()
    except OSError:
        return project_path(left).absolute() == project_path(right).absolute()


def local_heavy_reasons(panel: Path, execute: bool) -> list[str]:
    reasons: list[str] = []
    panel_text = str(panel).replace("\\", "/").lower()
    if execute:
        reasons.append("--execute would run bounded")
    if "full80" in panel_text:
        reasons.append("data path contains full80")
    if same_project_path(panel, DEFAULT_PANEL):
        reasons.append("data path is data/processed/onset_model_panel.parquet")
    return reasons


def enforce_local_light_mode(panel: Path, execute: bool, allow_local_heavy: bool) -> bool:
    if not local_windows_light_mode():
        return True
    reasons = local_heavy_reasons(panel, execute)
    if not reasons:
        return True
    if local_heavy_override_confirmed(allow_local_heavy):
        print("WARNING: local heavy-run guard overridden after explicit confirmation.")
        return True
    print(LOCAL_HEAVY_REFUSAL)
    print("Refusal reasons:")
    for reason in reasons:
        print(f"- {reason}")
    return False


def pick_column(columns: list[str], aliases: set[str]) -> str | None:
    for col in columns:
        if col in aliases:
            return col
    return None


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def future_information_columns(columns: list[str]) -> list[str]:
    flagged = []
    for col in columns:
        if col in ALLOWED_LABEL_COLUMNS:
            continue
        lower = col.lower()
        if any(part.lower() in lower for part in FORBIDDEN_PARTS):
            flagged.append(col)
    return flagged


def parquet_info(path: Path) -> dict[str, Any]:
    import pyarrow.parquet as pq
    import pandas as pd

    pf = pq.ParquetFile(path)
    columns = list(pf.schema.names)
    available = {c.strip() for c in columns}
    missing = [
        group
        for group, aliases in REQUIRED_GROUPS.items()
        if available.isdisjoint(aliases)
    ]
    code_col = pick_column(columns, REQUIRED_GROUPS["code"])
    date_col = pick_column(columns, REQUIRED_GROUPS["date"])
    read_cols = [c for c in [code_col, date_col, "is_index"] if c is not None and c in columns]
    stock_count: int | None = None
    date_min: str | None = None
    date_max: str | None = None
    if read_cols:
        meta = pd.read_parquet(path, columns=read_cols)
        if code_col and code_col != "code":
            meta = meta.rename(columns={code_col: "code"})
        if date_col and date_col != "date":
            meta = meta.rename(columns={date_col: "date"})
        if "is_index" not in meta.columns:
            meta["is_index"] = False
        if "code" in meta.columns:
            non_index = meta.loc[~meta["is_index"].map(parse_bool)]
            stock_count = int(non_index["code"].astype(str).nunique())
        if "date" in meta.columns and len(meta):
            dates = pd.to_datetime(meta["date"], errors="coerce")
            if dates.notna().any():
                date_min = str(dates.min().date())
                date_max = str(dates.max().date())
    future_cols = future_information_columns(columns)
    return {
        "rows": int(pf.metadata.num_rows),
        "columns": len(columns),
        "stock_count": stock_count,
        "date_min": date_min,
        "date_max": date_max,
        "future_information_columns": future_cols,
        "missing_required_groups": missing,
        "satisfies_contract": not missing,
    }


def recommended_command(panel: Path) -> list[str]:
    return [
        "python",
        "experiments/onset_baseline_check/run_onset_baseline.py",
        "--mode",
        "bounded",
        "--max-stock-codes",
        "20",
        "--bootstrap",
        "200",
        "--threshold-quantile",
        "0.90",
        "--gap",
        "5",
        "--lookback-clean",
        "10",
        "--data-path",
        str(panel).replace("\\", "/"),
        "--resume",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check bounded onset cloud readiness without running bounded by default.")
    parser.add_argument("--data-path", default=str(DEFAULT_PANEL), help="Model-panel parquet path.")
    parser.add_argument("--execute", action="store_true", help="Actually run the bounded command.")
    parser.add_argument(
        "--allow-local-heavy",
        action="store_true",
        help="Override the local Windows heavy-run guard after an interactive confirmation.",
    )
    args = parser.parse_args()

    panel = Path(args.data_path)
    if not enforce_local_light_mode(panel, bool(args.execute), bool(args.allow_local_heavy)):
        return 2
    panel_abs = project_path(panel)
    manifest_abs = project_path(CHECKPOINT_MANIFEST)
    print(f"Panel path: {panel}")
    print(f"Panel exists: {panel_abs.exists()}")
    if not panel_abs.exists():
        print("Bounded is not ready: model panel parquet is missing.")
        print("Recommended command once data is available:")
        print(" ".join(recommended_command(panel)))
        return 2

    info = parquet_info(panel_abs)
    print("Panel contract:")
    print(json.dumps(info, ensure_ascii=False, indent=2))
    print(f"Checkpoint manifest: {CHECKPOINT_MANIFEST}")
    print(f"Checkpoint manifest exists: {manifest_abs.exists()}")

    command = recommended_command(panel)
    print("Recommended bounded command:")
    print(" ".join(command))
    if not info["satisfies_contract"]:
        print("Bounded is not ready: panel contract is incomplete.")
        return 2
    if info["future_information_columns"]:
        print("Bounded is not ready: future-information columns are present.")
        return 2
    if not args.execute:
        print("Dry check only. Re-run with --execute to run bounded.")
        return 0

    execute_command = [sys.executable, *command[1:]]
    completed = subprocess.run(execute_command, cwd=ROOT, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
