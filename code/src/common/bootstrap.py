"""Import bootstrap helpers for direct script execution."""

from __future__ import annotations

import sys
from pathlib import Path


def add_code_root(file_path: str | Path) -> Path:
    """Add code to sys.path and return it."""

    path = Path(file_path).resolve()
    for parent in path.parents:
        if parent.name == "code":
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError(f"Could not locate code above {path}")
