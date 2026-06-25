from __future__ import annotations

import json
import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from config import paths
from src.common.config_loader import load_project_config, load_schema_config
from src.common.io_utils import write_json, write_markdown
from src.common.logging_utils import setup_logger, write_failure
from src.common.time_utils import build_slot_map


STAGE = "stage0_verify_input"


def _dtype_family(dtype: pa.DataType) -> str:
    if pa.types.is_string(dtype) or pa.types.is_large_string(dtype):
        return "string"
    if pa.types.is_boolean(dtype):
        return "bool"
    if pa.types.is_timestamp(dtype):
        return "timestamp"
    if pa.types.is_date(dtype):
        return "date"
    if pa.types.is_integer(dtype) or pa.types.is_floating(dtype) or pa.types.is_decimal(dtype):
        return "numeric"
    return str(dtype)


def verify_python_runtime() -> None:
    expected = paths.PYTHON_EXE.resolve()
    actual = Path(sys.executable).resolve()
    if actual != expected:
        raise RuntimeError(f"Python runtime mismatch. Expected {expected}, got {actual}")


def verify_preprocessed_layout(config: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    root = paths.PREPROCESSED_ROOT
    if not root.exists():
        raise FileNotFoundError(f"Preprocessed root is missing: {root}")
    for name in config["inputs"]["required_subdirs"]:
        path = root / name
        rows.append({"path": str(path.relative_to(paths.PROJECT_ROOT)), "exists": path.exists(), "is_dir": path.is_dir()})
        if not path.is_dir():
            raise FileNotFoundError(f"Required preprocessed subdir is missing: {path}")
    if not paths.RAW_PANEL_PATH.exists():
        raise FileNotFoundError(f"Raw panel parquet is missing: {paths.RAW_PANEL_PATH}")
    return rows


def verify_schema(pf: pq.ParquetFile, schema_config: dict) -> tuple[list[dict[str, object]], list[str]]:
    actual_schema = pf.schema_arrow
    actual_columns = set(actual_schema.names)
    rows: list[dict[str, object]] = []
    errors: list[str] = []
    required = schema_config["raw_minute_panel"]["required_columns"]
    for col, spec in required.items():
        exists = col in actual_columns
        actual_type = str(actual_schema.field(col).type) if exists else None
        actual_family = _dtype_family(actual_schema.field(col).type) if exists else None
        expected_family = spec["dtype_family"]
        ok = exists and (actual_family == expected_family)
        rows.append(
            {
                "column": col,
                "exists": exists,
                "expected_family": expected_family,
                "actual_family": actual_family,
                "actual_type": actual_type,
                "ok": ok,
            }
        )
        if not ok:
            errors.append(f"{col}: expected {expected_family}, got {actual_type}")
    return rows, errors


def sample_profile(raw_path: Path, required_columns: list[str]) -> dict[str, object]:
    sample = pd.read_parquet(raw_path, columns=required_columns).head(1000)
    null_counts = {col: int(sample[col].isna().sum()) for col in required_columns}
    return {
        "sample_rows": int(len(sample)),
        "sample_null_counts": null_counts,
        "sample_first_datetime": str(sample["datetime"].min()) if "datetime" in sample else None,
        "sample_last_datetime": str(sample["datetime"].max()) if "datetime" in sample else None,
        "sample_codes": sorted(map(str, sample["code"].dropna().unique()))[:10] if "code" in sample else [],
    }


def build_audit_text(profile: dict[str, object], schema_errors: list[str]) -> str:
    status = "PASS" if not schema_errors else "FAIL"
    return "\n".join(
        [
            "# Stage0 杈撳叆鏍搁獙瀹¤",
            "",
            f"- 鐘舵€侊細{status}",
            f"- 鍘熷 parquet锛歚{paths.RAW_PANEL_PATH.relative_to(paths.PROJECT_ROOT)}`",
            f"- 琛屾暟锛歿profile['rows']:,}",
            f"- row groups锛歿profile['row_groups']}",
            f"- 瀛楁鏁帮細{len(profile['columns'])}",
            f"- slot 瑙勫垯鏁伴噺锛歿profile['slot_count']}",
            "",
            "## Schema 閿欒",
            "",
            *(f"- {item}" for item in schema_errors),
            "" if schema_errors else "- 鏃?,
            "",
            "## 璇存槑",
            "",
            "鏈樁娈靛彧鏍搁獙棰勫鐞嗗師濮嬮潰鏉垮瓨鍦ㄦ€с€佺洰褰曠粨鏋勩€乸arquet metadata銆佸瓧娈垫棌涓庡皬鏍锋湰鍙鎬э紱涓嶄慨鏀?`data_inbox/preprocessed/`銆?,
            "",
        ]
    )


def run() -> None:
    logger = setup_logger(STAGE)
    paths.ensure_runtime_dirs()
    verify_python_runtime()
    config = load_project_config()
    schema_config = load_schema_config()
    build_slot_map(config)
    layout = verify_preprocessed_layout(config)

    pf = pq.ParquetFile(paths.RAW_PANEL_PATH)
    schema_rows, schema_errors = verify_schema(pf, schema_config)
    required_columns = list(schema_config["raw_minute_panel"]["required_columns"].keys())
    sample = sample_profile(paths.RAW_PANEL_PATH, required_columns)
    slot_count = len(build_slot_map(config))

    profile = {
        "raw_panel": str(paths.RAW_PANEL_PATH.relative_to(paths.PROJECT_ROOT)),
        "rows": int(pf.metadata.num_rows),
        "row_groups": int(pf.num_row_groups),
        "columns": pf.schema_arrow.names,
        "schema": [{"name": f.name, "type": str(f.type)} for f in pf.schema_arrow],
        "layout": layout,
        "schema_check": schema_rows,
        "sample_profile": sample,
        "slot_count": slot_count,
    }
    write_json(profile, paths.STAGE0_PROFILE_DIR / "input_profile.json")
    pd.DataFrame(schema_rows).to_csv(paths.STAGE0_PROFILE_DIR / "schema_check.csv", index=False, encoding="utf-8-sig")
    write_markdown(build_audit_text(profile, schema_errors), paths.DATA_AUDIT_DIR / "stage0_input_audit.md")

    if schema_errors:
        raise RuntimeError("Raw panel schema verification failed: " + "; ".join(schema_errors))
    logger.info("Stage0 completed: rows=%s row_groups=%s", f"{pf.metadata.num_rows:,}", pf.num_row_groups)


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        paths.ensure_runtime_dirs()
        failure_path = write_failure(STAGE, exc, paths.REVIEWS_DIR / "stage_failures")
        print(f"{STAGE} failed. See {failure_path}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
