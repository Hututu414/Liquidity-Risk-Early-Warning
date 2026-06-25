"""Feature, robust standardization, and label helpers."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


def add_minute_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add one-minute log returns without crossing code-date boundaries."""

    out = df.copy()
    close = pd.to_numeric(out["close"], errors="coerce")
    log_close = pd.Series(np.nan, index=out.index, dtype="float64")
    positive = close > 0
    log_close.loc[positive] = np.log(close.loc[positive])
    out["ret_1m"] = log_close.groupby(out["date"], sort=False).diff()
    return out


def _rolling_by_date(
    df: pd.DataFrame,
    source_col: str,
    window: int,
    method: str,
    min_periods: int | None = None,
) -> pd.Series:
    if min_periods is None:
        min_periods = window
    grouped = df.groupby("date", sort=False)[source_col]
    rolling = grouped.rolling(window=window, min_periods=min_periods)
    if method == "mean":
        values = rolling.mean()
    elif method == "sum":
        values = rolling.sum()
    else:
        raise ValueError(f"Unsupported rolling method: {method}")
    return values.reset_index(level=0, drop=True).astype("float64")


def compute_raw_components(
    df: pd.DataFrame,
    windows: Iterable[int],
    amount_scale: float,
    epsilon: float,
) -> tuple[pd.DataFrame, list[str]]:
    """Compute raw ILLIQ, Range, RV, and RelAmt windows for one code shard."""

    out = df.copy()
    amount = pd.to_numeric(out["amount"], errors="coerce").astype("float64")
    high = pd.to_numeric(out["high"], errors="coerce").astype("float64")
    low = pd.to_numeric(out["low"], errors="coerce").astype("float64")
    ret = pd.to_numeric(out["ret_1m"], errors="coerce").astype("float64")

    scaled_amount = amount / float(amount_scale)
    out["_illiq_base"] = np.where(scaled_amount > 0, ret.abs() / (scaled_amount + epsilon), np.nan)
    out["_range_base"] = np.where((high > 0) & (low > 0) & (high >= low), np.log(high / low), np.nan)
    out["_rv_base"] = ret.pow(2)
    out["_relamt_base"] = np.where(amount >= 0, np.log1p(amount), np.nan)

    component_cols: list[str] = []
    for window in windows:
        specs = {
            f"ILLIQ_{window}": ("_illiq_base", "mean"),
            f"Range_{window}": ("_range_base", "mean"),
            f"RV_{window}": ("_rv_base", "sum"),
            f"RelAmt_{window}": ("_relamt_base", "mean"),
        }
        for target, (source, method) in specs.items():
            out[target] = _rolling_by_date(out, source, int(window), method)
            component_cols.append(target)

    out = out.drop(columns=["_illiq_base", "_range_base", "_rv_base", "_relamt_base"])
    return out, component_cols


def compute_standardization_params(
    df: pd.DataFrame,
    component_cols: Iterable[str],
    train_mask: pd.Series,
    epsilon: float,
) -> pd.DataFrame:
    """Compute train-period code-slot median and MAD for component columns."""

    train = df.loc[train_mask, ["code", "slot", *component_cols]].copy()
    rows: list[dict[str, object]] = []
    code = str(df["code"].iloc[0]) if len(df) else ""
    fallback: dict[str, tuple[float, float, int]] = {}
    for col in component_cols:
        values = pd.to_numeric(train[col], errors="coerce").dropna()
        if len(values):
            median = float(values.median())
            mad = float((values - median).abs().median())
            if not np.isfinite(mad) or mad < epsilon:
                mad = 1.0
            fallback[col] = (median, mad, int(len(values)))
        else:
            fallback[col] = (0.0, 1.0, 0)

    for slot, group in train.groupby("slot", sort=True):
        for col in component_cols:
            values = pd.to_numeric(group[col], errors="coerce").dropna()
            if len(values):
                median = float(values.median())
                mad = float((values - median).abs().median())
                n_train = int(len(values))
                if not np.isfinite(mad) or mad < epsilon:
                    mad = fallback[col][1]
            else:
                median, mad, n_train = fallback[col]
            rows.append(
                {
                    "code": code,
                    "slot": int(slot),
                    "variable": col,
                    "median": median,
                    "mad": mad,
                    "n_train": n_train,
                }
            )
    return pd.DataFrame(rows)


def apply_robust_standardization(
    df: pd.DataFrame,
    params: pd.DataFrame,
    component_cols: Iterable[str],
    mad_scale: float,
    epsilon: float,
) -> pd.DataFrame:
    """Join code-slot train params and add z-scored component columns."""

    out = df.copy()
    for col in component_cols:
        sub = params.loc[params["variable"] == col, ["slot", "median", "mad"]].copy()
        sub = sub.rename(columns={"median": f"__median_{col}", "mad": f"__mad_{col}"})
        out = out.merge(sub, on="slot", how="left", validate="many_to_one")
        denom = out[f"__mad_{col}"].astype("float64") * float(mad_scale)
        denom = denom.where(np.isfinite(denom) & (denom > epsilon), 1.0)
        out[f"z_{col}"] = (pd.to_numeric(out[col], errors="coerce") - out[f"__median_{col}"]) / denom
        out = out.drop(columns=[f"__median_{col}", f"__mad_{col}"])
    return out


def add_lsi_columns(df: pd.DataFrame, windows: Iterable[int]) -> pd.DataFrame:
    out = df.copy()
    for window in windows:
        out[f"LSI_{window}"] = (
            out[f"z_ILLIQ_{window}"]
            + out[f"z_Range_{window}"]
            + out[f"z_RV_{window}"]
            - out[f"z_RelAmt_{window}"]
        )
    return out


def future_max_excluding_current(series: pd.Series, horizon: int) -> pd.Series:
    """Future rolling max over the next horizon rows, excluding current row."""

    reversed_future = series.iloc[::-1].shift(1)
    future_max = reversed_future.rolling(window=int(horizon), min_periods=int(horizon)).max()
    return future_max.iloc[::-1].reindex(series.index)


def add_future_lsi_targets(df: pd.DataFrame, source_col: str, horizons: Iterable[int]) -> pd.DataFrame:
    out = df.copy()
    for horizon in horizons:
        target = f"future_max_{source_col}_H{horizon}"
        out[target] = (
            out.groupby("date", sort=False)[source_col]
            .transform(lambda s, h=int(horizon): future_max_excluding_current(s, h))
            .astype("float64")
        )
    return out


def assign_stress_labels(df: pd.DataFrame, thresholds: dict[str, float], source_lsi_col: str) -> pd.DataFrame:
    out = df.copy()
    for key, threshold in thresholds.items():
        horizon = int(key.replace("H", ""))
        future_col = f"future_max_{source_lsi_col}_H{horizon}"
        label_col = f"Stress_H{horizon}"
        values = pd.to_numeric(out[future_col], errors="coerce")
        label = np.where(values.notna(), (values >= float(threshold)).astype("float32"), np.nan)
        out[label_col] = label.astype("float32")
    return out
