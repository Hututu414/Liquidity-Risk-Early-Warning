from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ["data", "processed", "data_inbox", "data_intermediate", "outputs", "experiments"]
EXTENSIONS = {".csv", ".gz", ".parquet", ".pkl", ".pickle", ".feather"}
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
OPTIONAL_GROUPS = {
    "Stress_H5": {"Stress_H5", "stress_h5"},
    "Stress_H10": {"Stress_H10", "stress_h10"},
}
SKIP_PARTS = {".git", "__pycache__", ".venv", "venv", "node_modules", "build", "dist"}


def is_candidate(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    if path.suffix.lower() in {".parquet", ".pkl", ".pickle", ".feather"}:
        return True
    return path.name.endswith(".csv") or path.name.endswith(".csv.gz")


def scan_files() -> list[Path]:
    files: list[Path] = []
    for name in SCAN_DIRS:
        base = ROOT / name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and is_candidate(path):
                files.append(path)
    def priority(path: Path) -> tuple[int, str]:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if rel.startswith("data/processed/onset_model_panel"):
            return (0, rel)
        if rel.startswith("data_intermediate/stage2_lsi_labels/lsi_labels_by_code/"):
            return (1, rel)
        if rel.startswith("data_intermediate/stage2_lsi_labels/"):
            return (2, rel)
        if rel.startswith("experiments/onset_baseline_check/"):
            return (3, rel)
        return (4, rel)

    return sorted(files, key=priority)


def parquet_schema(path: Path) -> tuple[list[str], int | None, str | None]:
    try:
        import pyarrow.parquet as pq

        pf = pq.ParquetFile(path)
        return list(pf.schema.names), int(pf.metadata.num_rows), None
    except Exception as exc:  # pragma: no cover - diagnostic path
        return [], None, str(exc)


def csv_schema(path: Path) -> tuple[list[str], int | None, str | None]:
    try:
        opener = gzip.open if path.name.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            columns = next(reader, [])
            row_count = None
            if path.stat().st_size < 25 * 1024 * 1024:
                row_count = sum(1 for _ in reader)
            return columns, row_count, None
    except UnicodeDecodeError:
        try:
            opener = gzip.open if path.name.endswith(".gz") else open
            with opener(path, "rt", encoding="gbk", newline="") as handle:
                reader = csv.reader(handle)
                columns = next(reader, [])
            return columns, None, None
        except Exception as exc:  # pragma: no cover
            return [], None, str(exc)
    except Exception as exc:  # pragma: no cover
        return [], None, str(exc)


def feather_schema(path: Path) -> tuple[list[str], int | None, str | None]:
    try:
        import pyarrow.feather as feather

        table = feather.read_table(path, memory_map=True)
        return list(table.column_names), int(table.num_rows), None
    except Exception as exc:  # pragma: no cover
        return [], None, str(exc)


def inspect_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        columns, rows, error = parquet_schema(path)
    elif path.name.endswith(".csv") or path.name.endswith(".csv.gz"):
        columns, rows, error = csv_schema(path)
    elif suffix == ".feather":
        columns, rows, error = feather_schema(path)
    else:
        columns, rows, error = [], None, "schema inspection skipped for pickle-like file"

    normalized = {c.strip() for c in columns}
    missing = [
        group
        for group, aliases in REQUIRED_GROUPS.items()
        if normalized.isdisjoint(aliases)
    ]
    optional_present = {
        group: not normalized.isdisjoint(aliases)
        for group, aliases in OPTIONAL_GROUPS.items()
    }
    return {
        "path": str(path.relative_to(ROOT)),
        "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
        "rows": rows,
        "columns": len(columns),
        "column_names": columns,
        "satisfies_min_contract": not missing,
        "missing_required_groups": missing,
        "optional_groups_present": optional_present,
        "error": error,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="List candidate data files for the onset baseline experiment.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a readable table.")
    parser.add_argument("--limit", type=int, default=200, help="Maximum files to inspect.")
    args = parser.parse_args()

    files = scan_files()[: max(args.limit, 1)]
    records = [inspect_file(path) for path in files]
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0

    print(f"Scanned candidate data files: {len(records)}")
    if not records:
        print("No candidate csv/parquet/pickle/feather files found under data, processed, outputs, or experiments.")
        return 0

    for record in records:
        status = "OK" if record["satisfies_min_contract"] else "MISSING"
        rows = "unknown" if record["rows"] is None else str(record["rows"])
        print(
            f"[{status}] {record['path']} | {record['size_mb']} MB | "
            f"rows={rows} | columns={record['columns']}"
        )
        if record["missing_required_groups"]:
            print(f"  missing required groups: {', '.join(record['missing_required_groups'])}")
        if record["error"]:
            print(f"  note: {record['error']}")
    matches = [r for r in records if r["satisfies_min_contract"]]
    print(f"Files satisfying minimum contract: {len(matches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
