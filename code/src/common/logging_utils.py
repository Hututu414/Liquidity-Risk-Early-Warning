"""Logging helpers shared by stage scripts."""

from __future__ import annotations

import logging
import sys
import traceback
from pathlib import Path


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger


def write_failure(stage: str, exc: BaseException, failure_dir: Path) -> Path:
    failure_dir.mkdir(parents=True, exist_ok=True)
    path = failure_dir / f"{stage}_failure.txt"
    path.write_text("".join(traceback.format_exception(exc)), encoding="utf-8")
    return path
