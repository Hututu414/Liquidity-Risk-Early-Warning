from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def relative_to_root(path: str | Path) -> str:
    root = project_root()
    value = Path(path)
    try:
        return str(value.resolve().relative_to(root))
    except Exception:
        return str(value)
