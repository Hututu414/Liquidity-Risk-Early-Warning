"""Trading-session and intraday slot helpers."""

from __future__ import annotations

from datetime import datetime, time, timedelta

import pandas as pd


def _parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M:%S").time()


def _time_range(start: str, end: str) -> list[str]:
    current = datetime.combine(datetime.today().date(), _parse_time(start))
    final = datetime.combine(datetime.today().date(), _parse_time(end))
    values: list[str] = []
    while current <= final:
        values.append(current.strftime("%H:%M:%S"))
        current += timedelta(minutes=1)
    return values


def build_slot_map(config: dict) -> dict[str, int]:
    session = config["trading_session"]
    morning = _time_range(session["morning_start"], session["morning_end"])
    afternoon = _time_range(session["afternoon_start"], session["afternoon_regular_end"])
    terminal = session.get("afternoon_terminal_close")
    times = [*morning, *afternoon]
    if terminal and terminal not in times:
        times.append(terminal)
    slot_map = {value: idx + 1 for idx, value in enumerate(times)}
    expected = int(session.get("expected_slots", len(slot_map)))
    if len(slot_map) != expected:
        raise ValueError(f"Slot map has {len(slot_map)} slots, expected {expected}.")
    return slot_map


def filter_and_add_slot(df: pd.DataFrame, slot_map: dict[str, int]) -> pd.DataFrame:
    out = df.copy()
    out["time"] = out["time"].astype(str)
    out = out.loc[out["time"].isin(slot_map)].copy()
    out["slot"] = out["time"].map(slot_map).astype("int16")
    return out
