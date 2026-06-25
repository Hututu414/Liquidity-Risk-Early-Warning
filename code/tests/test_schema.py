from pathlib import Path
import sys

CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from src.common.config_loader import load_schema_config


def test_raw_schema_declares_required_key_columns():
    schema = load_schema_config()
    required = schema["raw_minute_panel"]["required_columns"]
    for col in ["code", "datetime", "date", "time", "open", "high", "low", "close", "volume", "amount"]:
        assert col in required


def test_model_ready_schema_contains_return_and_slot():
    schema = load_schema_config()
    required = set(schema["model_ready_panel"]["required_columns"])
    assert {"slot", "ret_1m", "valid_minutes"}.issubset(required)
