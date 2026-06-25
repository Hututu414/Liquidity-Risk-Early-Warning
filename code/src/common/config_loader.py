"""YAML configuration loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from config import paths


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


def load_project_config() -> dict[str, Any]:
    return load_yaml(paths.CONFIG_DIR / "project_config.yaml")


def load_schema_config() -> dict[str, Any]:
    return load_yaml(paths.CONFIG_DIR / "schema_minute_panel.yaml")


def load_variable_config() -> dict[str, Any]:
    return load_yaml(paths.CONFIG_DIR / "variable_config.yaml")
