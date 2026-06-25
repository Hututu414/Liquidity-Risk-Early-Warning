from pathlib import Path
import sys

CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import pandas as pd

from src.common.splits import make_time_split


def test_time_split_is_ordered_and_nonrandom():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    split = make_time_split(dates, train_fraction=0.6, validation_fraction=0.2)
    assert split["train_end"] == "2024-01-06"
    assert split["validation_start"] == "2024-01-07"
    assert split["test_start"] == "2024-01-09"
