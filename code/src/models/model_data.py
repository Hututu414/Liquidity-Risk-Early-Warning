"""Shared data loading and transformations for core model scripts."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from config import paths


MARKET_VARIABLES = ["MarketLSI", "CrossStress", "IndexRet", "IndexRV", "MarketRelAmt"]


def load_time_split() -> dict[str, str]:
    with (paths.STAGE2_DIR / "time_split.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_label_thresholds() -> dict[str, float]:
    with (paths.STAGE2_DIR / "label_thresholds_train.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_market_context() -> pd.DataFrame:
    path = paths.STAGE2_DIR / "market_context.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing market context: {path}")
    df = pd.read_parquet(path)
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["date"] = df["datetime"].dt.date
    for col in MARKET_VARIABLES:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("datetime").reset_index(drop=True)


def add_period(df: pd.DataFrame, split: dict[str, str]) -> pd.DataFrame:
    out = df.copy()
    dates = pd.to_datetime(out["date"], errors="coerce")
    out["period"] = "unassigned"
    out.loc[(dates >= pd.Timestamp(split["train_start"])) & (dates <= pd.Timestamp(split["train_end"])), "period"] = "train"
    out.loc[
        (dates >= pd.Timestamp(split["validation_start"])) & (dates <= pd.Timestamp(split["validation_end"])),
        "period",
    ] = "validation"
    out.loc[(dates >= pd.Timestamp(split["test_start"])) & (dates <= pd.Timestamp(split["test_end"])), "period"] = "test"
    return out


def train_stats(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    train = df.loc[df["period"] == "train", cols]
    rows = []
    for col in cols:
        values = pd.to_numeric(train[col], errors="coerce").dropna()
        rows.append(
            {
                "variable": col,
                "mean": float(values.mean()),
                "std": float(values.std(ddof=0)),
                "median": float(values.median()),
                "q01": float(values.quantile(0.01)),
                "q99": float(values.quantile(0.99)),
                "n_train": int(len(values)),
            }
        )
    return pd.DataFrame(rows)


def standardize_with_train(df: pd.DataFrame, cols: list[str], stats: pd.DataFrame, prefix: str = "z_") -> pd.DataFrame:
    out = df.copy()
    for row in stats.itertuples(index=False):
        if row.variable not in cols:
            continue
        std = row.std if np.isfinite(row.std) and row.std > 1.0e-12 else 1.0
        clipped = pd.to_numeric(out[row.variable], errors="coerce").clip(row.q01, row.q99)
        out[f"{prefix}{row.variable}"] = (clipped - row.mean) / std
    return out


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
