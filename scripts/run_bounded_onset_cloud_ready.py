from __future__ import annotations

import argparse
import json
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


def project_path(path: Path | str) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def parquet_info(path: Path) -> dict[str, Any]:
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(path)
    columns = list(pf.schema.names)
    available = {c.strip() for c in columns}
    missing = [
        group
        for group, aliases in REQUIRED_GROUPS.items()
        if available.isdisjoint(aliases)
    ]
    return {
        "rows": int(pf.metadata.num_rows),
        "columns": len(columns),
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
    args = parser.parse_args()

    panel = Path(args.data_path)
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
    if not args.execute:
        print("Dry check only. Re-run with --execute to run bounded.")
        return 0

    execute_command = [sys.executable, *command[1:]]
    completed = subprocess.run(execute_command, cwd=ROOT, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
