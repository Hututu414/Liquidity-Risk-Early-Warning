"""Time split utilities. Splits are date-ordered and never randomized."""

from __future__ import annotations

from datetime import date
from typing import Iterable

import pandas as pd


def normalize_dates(dates: Iterable[object]) -> list[date]:
    values = pd.to_datetime(pd.Series(list(dates), dtype="object"), errors="coerce").dropna()
    normalized = sorted({v.date() for v in values})
    if not normalized:
        raise ValueError("No valid dates are available for time split construction.")
    return normalized


def make_time_split(
    dates: Iterable[object],
    train_fraction: float,
    validation_fraction: float,
) -> dict[str, object]:
    """Return deterministic train/validation/test boundaries."""

    ordered = normalize_dates(dates)
    n = len(ordered)
    if n < 5:
        raise ValueError(f"At least 5 trading dates are required, got {n}.")
    if not (0 < train_fraction < 1):
        raise ValueError("train_fraction must be between 0 and 1.")
    if not (0 <= validation_fraction < 1):
        raise ValueError("validation_fraction must be between 0 and 1.")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("train_fraction + validation_fraction must be less than 1.")

    train_end_idx = max(0, int(n * train_fraction) - 1)
    valid_end_idx = max(train_end_idx + 1, int(n * (train_fraction + validation_fraction)) - 1)
    valid_end_idx = min(valid_end_idx, n - 2)

    return {
        "n_dates": n,
        "first_date": ordered[0].isoformat(),
        "last_date": ordered[-1].isoformat(),
        "train_start": ordered[0].isoformat(),
        "train_end": ordered[train_end_idx].isoformat(),
        "validation_start": ordered[train_end_idx + 1].isoformat(),
        "validation_end": ordered[valid_end_idx].isoformat(),
        "test_start": ordered[valid_end_idx + 1].isoformat(),
        "test_end": ordered[-1].isoformat(),
    }


def period_mask(dates: pd.Series, start: str, end: str) -> pd.Series:
    values = pd.to_datetime(dates, errors="coerce")
    return (values >= pd.Timestamp(start)) & (values <= pd.Timestamp(end))
