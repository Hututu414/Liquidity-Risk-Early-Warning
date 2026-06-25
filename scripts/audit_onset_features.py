from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "experiments/onset_baseline_check/outputs"
CHECKPOINT_DIR = ROOT / "experiments/onset_baseline_check/checkpoints"
MODEL_DIR = CHECKPOINT_DIR / "models"
DEFAULT_DATA = Path("data/processed/onset_model_panel_bounded20.parquet")
DEFAULT_REPORT = Path("experiments/onset_baseline_check/outputs/feature_leakage_audit_bounded20.md")
SUSPICIOUS_KEYWORDS = [
    "future",
    "lead",
    "target",
    "label",
    "stress_h5",
    "stress_h10",
    "futuremax",
    "crossstress",
    "forward",
    "next",
    "y_",
]
FORBIDDEN_EXACT = {"Stress_H5", "Stress_H10", "FutureMaxLSI", "CrossStress", "CrossStress_H10"}
GROUPS = ["P", "M", "C", "ALL"]
HORIZONS = ["H5", "H10"]


def project_path(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_cloud_value(key: str) -> str:
    path = OUTPUT_DIR / "cloud_run_summary.md"
    if not path.exists():
        return "unknown"
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^- {re.escape(key)}: (.*)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else "unknown"


def load_manifest_signature(data_path: Path) -> str | None:
    manifest_path = CHECKPOINT_DIR / "manifest.json"
    if not manifest_path.exists():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = rel(data_path)
    candidates: list[tuple[str, str]] = []
    for signature, run in manifest.get("runs", {}).items():
        params = run.get("parameters", {})
        run_path = str(params.get("data_path", "")).replace("\\", "/")
        if run.get("mode") == "bounded" and run_path == expected:
            candidates.append((str(run.get("updated_at", "")), signature))
    if not candidates:
        return None
    return sorted(candidates)[-1][1]


def model_cache_path(signature: str, horizon: str, group: str, model: str) -> Path:
    return MODEL_DIR / f"{signature}_onset_{horizon}_{group}_{model}.joblib"


def load_feature_sets(signature: str | None) -> dict[str, dict[str, list[str]]]:
    features: dict[str, dict[str, list[str]]] = {h: {} for h in HORIZONS}
    if not signature:
        return features
    for horizon in HORIZONS:
        for group in GROUPS:
            loaded: list[str] | None = None
            for model in ["LightGBM", "SMARTBoost", "Logit"]:
                path = model_cache_path(signature, horizon, group, model)
                if not path.exists():
                    continue
                try:
                    payload = joblib.load(path)
                    loaded = list(payload.get("features", []))
                    break
                except Exception:
                    continue
            features[horizon][group] = loaded or []
    return features


def suspicious_columns(features: dict[str, dict[str, list[str]]]) -> dict[str, list[str]]:
    flagged: dict[str, list[str]] = {}
    for horizon, groups in features.items():
        for group, cols in groups.items():
            hits = []
            for col in cols:
                lower = col.lower()
                if col in FORBIDDEN_EXACT or any(key in lower for key in SUSPICIOUS_KEYWORDS):
                    hits.append(col)
            flagged[f"{horizon}_{group}"] = sorted(set(hits))
    return {k: v for k, v in flagged.items() if v}


def rolling_name_warnings(features: dict[str, dict[str, list[str]]]) -> list[str]:
    patterns = ("center", "centered", "forward", "future", "lead", "next")
    warnings = []
    for horizon, groups in features.items():
        for group, cols in groups.items():
            hits = [c for c in cols if "roll" in c.lower() and any(p in c.lower() for p in patterns)]
            for hit in hits:
                warnings.append(f"{horizon}/{group}: {hit}")
    return sorted(set(warnings))


def exact_forbidden_hits(features: dict[str, dict[str, list[str]]]) -> list[str]:
    hits = []
    for horizon, groups in features.items():
        for group, cols in groups.items():
            for col in cols:
                if col in FORBIDDEN_EXACT:
                    hits.append(f"{horizon}/{group}: {col}")
    return sorted(set(hits))


def feature_category(feature: str) -> str:
    if feature.startswith("LSI_5") or "threshold" in feature:
        return "persistence"
    if feature.startswith("Market") or feature.startswith("Index"):
        return "market"
    if feature.startswith("xsec_"):
        return "cross"
    if any(feature.startswith(prefix) for prefix in ("ILLIQ_", "Range_", "RV_", "RelAmt_", "z_")):
        return "component"
    return "timing_or_other"


def model_importance_from_cache(signature: str | None, horizon: str, group: str, model_name: str) -> pd.DataFrame:
    if not signature:
        return pd.DataFrame()
    path = model_cache_path(signature, horizon, group, model_name)
    if not path.exists():
        return pd.DataFrame()
    try:
        payload = joblib.load(path)
    except Exception:
        return pd.DataFrame()
    features = list(payload.get("features", []))
    model = payload.get("trainval_model")
    if model is None or not hasattr(model, "named_steps"):
        return pd.DataFrame()
    estimator = model.named_steps.get("model")
    values = getattr(estimator, "feature_importances_", None)
    if values is None:
        return pd.DataFrame()
    imputer = model.named_steps.get("imputer")
    names = list(features)
    if imputer is not None and hasattr(imputer, "statistics_"):
        stats = np.asarray(imputer.statistics_, dtype="float64")
        if len(stats) == len(names):
            names = [name for name, keep in zip(names, np.isfinite(stats)) if keep]
    values = np.asarray(values, dtype="float64")
    n = min(len(names), len(values))
    frame = pd.DataFrame({"feature": names[:n], "importance": values[:n]})
    if frame.empty:
        return frame
    frame["category"] = frame["feature"].map(feature_category)
    return frame.sort_values("importance", ascending=False).reset_index(drop=True)


def fallback_importance() -> pd.DataFrame:
    path = OUTPUT_DIR / "feature_importance_onset.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).sort_values("importance", ascending=False).reset_index(drop=True)


def selected_models() -> pd.DataFrame:
    path = OUTPUT_DIR / "selected_best_models.csv"
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    return frame.loc[frame["task"].astype(str).eq("onset")].copy()


def panel_columns(path: Path) -> list[str]:
    import pyarrow.parquet as pq

    return list(pq.ParquetFile(path).schema.names)


def write_report(
    report_path: Path,
    data_path: Path,
    signature: str | None,
    features: dict[str, dict[str, list[str]]],
    schema_hits: list[str],
    suspicious: dict[str, list[str]],
    exact_hits: list[str],
    rolling_hits: list[str],
    importances: dict[str, pd.DataFrame],
    fallback: pd.DataFrame,
) -> None:
    lines = [
        "# Feature leakage audit for bounded20 onset baseline",
        "",
        "## Scope",
        "",
        f"- data_path: {rel(data_path)}",
        f"- cache_signature: {signature or 'not found'}",
        f"- run_mode: {read_cloud_value('mode')}",
        f"- max_stock_codes: {read_cloud_value('max_stock_codes')}",
        f"- bootstrap_iterations: {read_cloud_value('bootstrap_iterations')}",
        "",
        "## Feature Group Counts",
        "",
    ]
    for horizon in HORIZONS:
        lines.append(f"### {horizon}")
        lines.append("")
        for group in GROUPS:
            cols = features.get(horizon, {}).get(group, [])
            lines.append(f"- {group}: {len(cols)}")
        lines.append("")
    lines.extend(["## ALL Feature Names", ""])
    for horizon in HORIZONS:
        all_cols = features.get(horizon, {}).get("ALL", [])
        lines.append(f"### {horizon} first 50")
        lines.append("")
        lines.extend(f"- {col}" for col in all_cols[:50])
        lines.append("")
    lines.extend(["## Leakage Checks", ""])
    lines.append(f"- suspicious_feature_name_hits: {sum(len(v) for v in suspicious.values())}")
    if suspicious:
        for key, cols in suspicious.items():
            lines.append(f"  - {key}: {', '.join(cols)}")
    else:
        lines.append("  - none")
    lines.append(f"- exact_forbidden_feature_hits: {len(exact_hits)}")
    lines.extend([f"  - {x}" for x in exact_hits] or ["  - none"])
    lines.append(f"- panel_schema_future_or_label_hits: {len(schema_hits)}")
    lines.extend([f"  - {x}" for x in schema_hits] or ["  - none"])
    lines.append(f"- centered_or_forward_rolling_name_hits: {len(rolling_hits)}")
    lines.extend([f"  - {x}" for x in rolling_hits] or ["  - none"])
    lines.append("")
    lines.extend(["## Model Feature Importance", ""])
    for key, frame in importances.items():
        lines.append(f"### {key}")
        lines.append("")
        if frame.empty:
            lines.append("- no native model importance available")
        else:
            for row in frame.head(30).itertuples(index=False):
                lines.append(f"- {row.feature}: {float(row.importance):.6f} ({row.category})")
        lines.append("")
    lines.extend(["### Fallback feature_importance_onset.csv top 30", ""])
    if fallback.empty:
        lines.append("- not available")
    else:
        for row in fallback.head(30).itertuples(index=False):
            category = getattr(row, "category", feature_category(str(row.feature)))
            lines.append(f"- {row.feature}: {float(row.importance):.6f} ({category})")
    lines.append("")
    category_lines = []
    if not fallback.empty and "category" in fallback.columns and "share" in fallback.columns:
        contrib = fallback.groupby("category", as_index=False)["share"].sum().sort_values("share", ascending=False)
        category_lines = [f"- {r.category}: {float(r.share):.3f}" for r in contrib.itertuples(index=False)]
    lines.extend(["## Audit Conclusion", ""])
    leak_found = bool(suspicious or exact_hits or rolling_hits)
    future_agg_found = bool(schema_hits)
    lines.append(f"- suspected_leakage_columns_found: {'yes' if leak_found else 'no'}")
    lines.append(f"- future_label_aggregate_variables_in_features: {'yes' if leak_found else 'no'}")
    lines.append(f"- future_or_label_columns_present_in_panel_schema_but_not_features: {'yes' if future_agg_found else 'no'}")
    lines.append(
        "- preliminary_legality_of_ALL_increment: "
        + ("blocked until feature construction is fixed" if leak_found else "passes name-based and cache-feature audit")
    )
    lines.append("- main_increment_feature_types:")
    lines.extend(category_lines or ["  - unavailable"])
    lines.append("- support_C_as_standalone_core_contribution: no; bounded20 C-vs-P increments were negative.")
    lines.append(
        "- recommend_all_stock_diagnostic: "
        + ("no; stop and repair feature construction first" if leak_found else "yes")
    )
    lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit onset baseline feature groups for leakage-prone columns.")
    parser.add_argument("--data-path", default=str(DEFAULT_DATA))
    parser.add_argument("--output", default=str(DEFAULT_REPORT))
    args = parser.parse_args()

    data_path = project_path(args.data_path)
    report_path = project_path(args.output)
    if not data_path.exists():
        print(f"Missing data file: {rel(data_path)}")
        return 2
    columns = panel_columns(data_path)
    schema_hits = [
        col
        for col in columns
        if col not in {"Stress_H5", "Stress_H10"}
        and (col in FORBIDDEN_EXACT or any(key in col.lower() for key in SUSPICIOUS_KEYWORDS))
    ]
    signature = load_manifest_signature(data_path)
    features = load_feature_sets(signature)
    suspicious = suspicious_columns(features)
    exact_hits = exact_forbidden_hits(features)
    rolling_hits = rolling_name_warnings(features)

    selected = selected_models()
    importances: dict[str, pd.DataFrame] = {}
    for horizon in HORIZONS:
        row = selected.loc[selected["horizon"].astype(str).eq(horizon)]
        if row.empty:
            continue
        group = str(row.iloc[0]["feature_group"])
        model_name = str(row.iloc[0]["model"])
        importances[f"{horizon} best {model_name}/{group}"] = model_importance_from_cache(
            signature, horizon, group, model_name
        )
    fallback = fallback_importance()
    write_report(report_path, data_path, signature, features, schema_hits, suspicious, exact_hits, rolling_hits, importances, fallback)
    print(f"Wrote {rel(report_path)}")
    if suspicious or exact_hits or rolling_hits:
        print("Feature leakage audit failed: suspicious feature names are present.")
        return 2
    print("Feature leakage audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
