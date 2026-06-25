from pathlib import Path
import sys

CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import pandas as pd

from src.common.features import add_future_lsi_targets, assign_stress_labels


def test_future_label_does_not_cross_date():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"] * 4 + ["2024-01-02"] * 4).date,
            "LSI_5": [0.0, 1.0, 5.0, 2.0, 10.0, 0.0, 0.0, 0.0],
        }
    )
    out = add_future_lsi_targets(df, "LSI_5", [2])
    assert out.loc[2, "future_max_LSI_5_H2"] != 10.0
    assert pd.isna(out.loc[3, "future_max_LSI_5_H2"])


def test_assign_stress_labels_threshold():
    df = pd.DataFrame({"future_max_LSI_5_H5": [0.1, 2.0, None]})
    out = assign_stress_labels(df, {"H5": 1.0}, "LSI_5")
    assert out["Stress_H5"].tolist()[0] == 0.0
    assert out["Stress_H5"].tolist()[1] == 1.0
    assert pd.isna(out["Stress_H5"].tolist()[2])
