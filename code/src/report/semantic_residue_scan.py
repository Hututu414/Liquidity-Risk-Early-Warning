from __future__ import annotations

import argparse
import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import pandas as pd

from config import paths


BANNED_TERMS = [
    "套期保值",
    "期货",
    "IF 主力",
    "沪深300ETF",
    "510300",
    "价格发现",
    "VECM",
    "Hasbrouck",
    "Gonzalo-Granger",
    "统计套利",
    "配对交易",
    "Kalman 动态价差",
    "OU 半衰期",
    "DCC-GARCH",
    "Bayesian SSM",
    "Markov regime filter",
    "金融工程课堂大作业",
]


DEFAULT_SCAN_DIRS = ["code", "outputs", "report", "final_output"]
TEXT_SUFFIXES = {".md", ".tex", ".py", ".yaml", ".yml", ".txt", ".csv"}


def scan_file(path: Path) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    rows: list[dict[str, object]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for term in BANNED_TERMS:
            if term in line:
                rows.append(
                    {
                        "file": str(path.relative_to(paths.PROJECT_ROOT)),
                        "line": line_no,
                        "term": term,
                        "snippet": line.strip()[:300],
                    }
                )
    return rows


def run(scan_dirs: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for name in scan_dirs:
        root = paths.PROJECT_ROOT / name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                rows.extend(scan_file(path))
    return pd.DataFrame(rows, columns=["file", "line", "term", "snippet"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-dir", action="append", dest="scan_dirs", default=None)
    parser.add_argument("--output", default=str(paths.FINAL_PACKAGE_AUDIT_DIR / "semantic_residue_scan.csv"))
    args = parser.parse_args()

    paths.ensure_runtime_dirs()
    result = run(args.scan_dirs or DEFAULT_SCAN_DIRS)
    output = Path(args.output)
    if not output.is_absolute():
        output = paths.PROJECT_ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"semantic residue matches: {len(result)}")
    return 1 if len(result) else 0


if __name__ == "__main__":
    raise SystemExit(main())

