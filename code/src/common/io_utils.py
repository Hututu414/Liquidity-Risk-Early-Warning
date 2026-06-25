"""I/O helpers for parquet shards and manifests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd


def clean_dir(path: Path) -> None:
    """Remove and recreate a generated directory."""

    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def sanitize_code(code: str) -> str:
    return code.replace(".", "_").replace("/", "_").replace("\\", "_")


def write_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, default=str)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_markdown(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def to_parquet(df: pd.DataFrame, path: Path, compression: str = "zstd") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(path, index=False, engine="pyarrow", compression=compression)
    except Exception:
        if compression != "snappy":
            df.to_parquet(path, index=False, engine="pyarrow", compression="snappy")
        else:
            raise
