from pathlib import Path
import sys

CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import pandas as pd

from src.common.features import compute_standardization_params


def test_standardization_params_use_train_mask_only():
    df = pd.DataFrame(
        {
            "code": ["000001.SZ"] * 4,
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]).date,
            "slot": [1, 1, 1, 1],
            "ILLIQ_5": [1.0, 3.0, 1000.0, 2000.0],
        }
    )
    train_mask = pd.Series([True, True, False, False])
    params = compute_standardization_params(df, ["ILLIQ_5"], train_mask, epsilon=1.0e-12)
    row = params.loc[(params["slot"] == 1) & (params["variable"] == "ILLIQ_5")].iloc[0]
    assert row["median"] == 2.0
    assert row["n_train"] == 2
