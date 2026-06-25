from __future__ import annotations

import argparse
import importlib.util
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = PROJECT_ROOT / "experiments" / "onset_baseline_check" / "run_onset_baseline.py"
PYTHON_NOTICE = (
    "This script recomputes event-level metrics from cached models only. "
    "It does not fit, refit, or update model checkpoints."
)
DAILY_TOP_N_SIGNALS = [20, 50, 100, 200]
DAILY_TOP_PCT_SIGNALS = [0.005, 0.01, 0.02, 0.05]


@dataclass(frozen=True)
class CachedModel:
    horizon: int
    feature_group: str
    model_name: str
    score_model: Any
    features: list[str]
    model_path: Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recompute corrected event-level onset metrics from cached models.")
    parser.add_argument("--data-path", required=True)
    parser.add_argument("--predictions-dir", default="experiments/onset_baseline_check/checkpoints")
    parser.add_argument("--outputs-dir", default="experiments/onset_baseline_check/outputs")
    parser.add_argument("--mode", choices=["bounded", "full"], default="bounded")
    parser.add_argument("--gap", type=int, default=5)
    parser.add_argument("--lookback-clean", type=int, default=10)
    parser.add_argument("--threshold-quantile", type=float, default=0.90)
    parser.add_argument("--top-frac", type=float, default=0.05)
    parser.add_argument("--bootstrap", type=int, default=200)
    parser.add_argument("--budgeted", action="store_true", help="Also compute daily budget-constrained signals.")
    return parser.parse_args(argv)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("onset_baseline_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import runner from {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def configure_runner(runner: Any, args: argparse.Namespace) -> tuple[dict[str, Any], pd.DataFrame, dict[str, str], dict[int, float], pd.DataFrame]:
    runner_args = runner.parse_args(
        [
            "--mode",
            str(args.mode),
            "--max-stock-codes",
            "null",
            "--bootstrap",
            str(int(args.bootstrap)),
            "--threshold-quantile",
            str(float(args.threshold_quantile)),
            "--gap",
            str(int(args.gap)),
            "--lookback-clean",
            str(int(args.lookback_clean)),
            "--data-path",
            str(args.data_path),
            "--resume",
        ]
    )
    config = runner.apply_run_mode(runner.load_config(), runner_args)
    log: list[str] = []
    manifest, split, existing_thresholds = runner.load_inputs(config)
    manifest = runner.apply_stock_code_cap(manifest, config, log)
    robustness_q = [float(x) for x in config["robustness_grid"]["threshold_quantiles"]]
    prefer_existing = bool(config["main_label"].get("prefer_existing_thresholds_for_main", True))
    main_thresholds: dict[int, float] = {}
    for horizon in runner.HORIZONS:
        key = f"H{horizon}"
        main_thresholds[horizon] = (
            float(existing_thresholds[key]) if prefer_existing and key in existing_thresholds else float("nan")
        )
    cross_context, direct_thresholds = runner.build_cross_context(manifest, split, main_thresholds, robustness_q, log)
    for horizon in runner.HORIZONS:
        if not np.isfinite(main_thresholds[horizon]):
            main_thresholds[horizon] = float(direct_thresholds[float(config["main_label"]["threshold_quantile"])])
    return config, manifest, split, main_thresholds, cross_context


def read_best_models(outputs_dir: Path) -> dict[int, tuple[str, str]]:
    selected_path = outputs_dir / "selected_best_models.csv"
    if not selected_path.exists():
        raise FileNotFoundError(f"Missing selected best model table: {selected_path}")
    best = pd.read_csv(selected_path)
    if "task" in best.columns:
        best = best.loc[best["task"].astype(str).eq("onset")].copy()
    out: dict[int, tuple[str, str]] = {}
    for horizon in [5, 10]:
        rows = best.loc[best["horizon"].astype(str).eq(f"H{horizon}")]
        if rows.empty:
            raise RuntimeError(f"No selected onset best model found for H{horizon}")
        row = rows.iloc[0]
        out[horizon] = (str(row["feature_group"]), str(row["model"]))
    return out


def load_cached_models(config: dict[str, Any], args: argparse.Namespace, best_models: dict[int, tuple[str, str]]) -> dict[int, CachedModel]:
    checkpoint_dir = (PROJECT_ROOT / args.predictions_dir).resolve()
    model_dir = checkpoint_dir / "models"
    signature = str(config.get("cache_signature", "nosig"))
    cached: dict[int, CachedModel] = {}
    for horizon, (group, model_name) in best_models.items():
        model_path = model_dir / f"{signature}_onset_H{horizon}_{group}_{model_name}.joblib"
        if not model_path.exists():
            raise FileNotFoundError(
                "Missing cached model; refusing to retrain. Expected: "
                f"{rel(model_path)}"
            )
        payload = joblib.load(model_path)
        if str(payload.get("signature")) != signature:
            raise RuntimeError(f"Cached model signature mismatch: {rel(model_path)}")
        cached[horizon] = CachedModel(
            horizon=horizon,
            feature_group=group,
            model_name=model_name,
            score_model=payload["trainval_model"],
            features=list(payload["features"]),
            model_path=model_path,
        )
    return cached


def pressure_episodes(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    required = {"code", "date", "slot", "LSI_5"}
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError(f"Cannot compute pressure episodes; missing columns: {sorted(missing)}")
    work = df.loc[df["date"].notna()].copy()
    work["slot"] = pd.to_numeric(work["slot"], errors="coerce")
    work["LSI_5"] = pd.to_numeric(work["LSI_5"], errors="coerce")
    for (code, date_value), g in work.sort_values(["code", "date", "slot"]).groupby(["code", "date"], sort=False):
        slots = g["slot"].to_numpy(dtype="float64")
        lsi = g["LSI_5"].to_numpy(dtype="float64")
        pressure = np.isfinite(lsi) & (lsi >= float(threshold))
        if pressure.size == 0:
            continue
        prev_pressure = np.concatenate(([False], pressure[:-1]))
        prev_slot = np.concatenate(([np.nan], slots[:-1]))
        contiguous = np.isfinite(prev_slot) & np.isfinite(slots) & ((slots - prev_slot) == 1.0)
        starts = pressure & (~prev_pressure | ~contiguous)
        if not bool(starts.any()):
            continue
        start_positions = np.flatnonzero(starts)
        for pos in start_positions:
            rows.append(
                {
                    "code": str(code),
                    "date": date_value,
                    "start_slot": int(slots[pos]),
                    "event_start_datetime": pd.to_datetime(g.iloc[pos]["datetime"], errors="coerce")
                    if "datetime" in g.columns
                    else pd.NaT,
                }
            )
    return pd.DataFrame(rows)


def first_future_event_leads(preds: pd.DataFrame, events: pd.DataFrame, mask: np.ndarray) -> np.ndarray:
    if preds.empty or events.empty or not bool(mask.any()):
        return np.asarray([], dtype="float64")
    leads: list[np.ndarray] = []
    event_groups = {
        key: np.sort(group["start_slot"].to_numpy(dtype="int32"))
        for key, group in events.groupby(["code", "date"], sort=False)
    }
    selected = preds.loc[mask, ["code", "date", "slot"]].copy()
    selected["slot"] = pd.to_numeric(selected["slot"], errors="coerce").astype("float64")
    for key, g in selected.groupby(["code", "date"], sort=False):
        starts = event_groups.get(key)
        if starts is None or starts.size == 0:
            leads.append(np.full(len(g), np.nan, dtype="float64"))
            continue
        slots = g["slot"].to_numpy(dtype="float64")
        pos = np.searchsorted(starts, slots, side="right")
        out = np.full(slots.size, np.nan, dtype="float64")
        valid = pos < starts.size
        out[valid] = starts[pos[valid]] - slots[valid]
        leads.append(out)
    return np.concatenate(leads) if leads else np.asarray([], dtype="float64")


def summarize_leads(values: np.ndarray, gap: int, horizon: int, practical_max: int) -> dict[str, Any]:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return {
            "count": 0,
            "mean": np.nan,
            "median": np.nan,
            "p10": np.nan,
            "p90": np.nan,
            "within_label_window": 0,
            "within_label_window_rate": np.nan,
            "within_practical_window_rate": np.nan,
            "lt_gap_rate": np.nan,
            "gt_label_max_rate": np.nan,
        }
    label_max = int(gap) + int(horizon) - 1
    return {
        "count": int(finite.size),
        "mean": float(np.mean(finite)),
        "median": float(np.median(finite)),
        "p10": float(np.quantile(finite, 0.10)),
        "p90": float(np.quantile(finite, 0.90)),
        "within_label_window": int(((finite >= gap) & (finite <= label_max)).sum()),
        "within_label_window_rate": float(((finite >= gap) & (finite <= label_max)).mean()),
        "within_practical_window_rate": float(((finite >= gap) & (finite <= practical_max)).mean()),
        "lt_gap_rate": float((finite < gap).mean()),
        "gt_label_max_rate": float((finite > label_max).mean()),
    }


def empty_match_metrics() -> dict[str, Any]:
    return {
        "eligible_events": 0,
        "detected_events": 0,
        "event_recall": np.nan,
        "mean_lead": np.nan,
        "median_lead": np.nan,
        "daily_false_alarms": np.nan,
        "signals_per_day": np.nan,
        "events_per_day": 0.0,
        "false_alarms_per_detected_event": np.nan,
        "matched_signals": 0,
        "false_signals": 0,
    }


def build_match_context(preds: pd.DataFrame) -> dict[tuple[Any, Any], dict[str, np.ndarray]]:
    work = preds[["code", "date", "slot"]].copy()
    work["_row_id"] = np.arange(len(work), dtype="int64")
    context: dict[tuple[Any, Any], dict[str, np.ndarray]] = {}
    for key, group in work.groupby(["code", "date"], sort=False):
        sorted_group = group.sort_values("slot")
        context[key] = {
            "slots": sorted_group["slot"].to_numpy(dtype="int32"),
            "row_ids": sorted_group["_row_id"].to_numpy(dtype="int64"),
        }
    return context


def match_events_from_context(
    events: pd.DataFrame,
    match_context: dict[tuple[Any, Any], dict[str, np.ndarray]],
    signal_mask: np.ndarray,
    min_lead: int,
    max_lead: int,
    n_days: int,
) -> dict[str, Any]:
    if events.empty:
        return empty_match_metrics()
    event_count = int(len(events))
    eligible = 0
    detected = 0
    lead_values: list[float] = []
    matched_signals: set[int] = set()
    for key, ev_g in events.groupby(["code", "date"], sort=False):
        pred_g = match_context.get(key)
        if pred_g is None:
            continue
        pred_slots = pred_g["slots"]
        pred_ids = pred_g["row_ids"]
        local_signal = signal_mask[pred_ids]
        sig_slots = pred_slots[local_signal]
        sig_ids = pred_ids[local_signal]
        for start_slot in ev_g["start_slot"].to_numpy(dtype="int32"):
            lo = int(start_slot) - int(max_lead)
            hi = int(start_slot) - int(min_lead)
            pred_a = np.searchsorted(pred_slots, lo, side="left")
            pred_b = np.searchsorted(pred_slots, hi, side="right")
            if pred_b > pred_a:
                eligible += 1
            sig_a = np.searchsorted(sig_slots, lo, side="left")
            sig_b = np.searchsorted(sig_slots, hi, side="right")
            if sig_b > sig_a:
                detected += 1
                lead_values.append(float(start_slot - sig_slots[sig_a]))
                matched_signals.update(int(x) for x in sig_ids[sig_a:sig_b])
    signal_count = int(signal_mask.sum())
    false_signals = max(signal_count - len(matched_signals), 0)
    day_count = max(int(n_days), 1)
    return {
        "eligible_events": int(eligible),
        "detected_events": int(detected),
        "event_recall": float(detected / eligible) if eligible else np.nan,
        "mean_lead": float(np.mean(lead_values)) if lead_values else np.nan,
        "median_lead": float(np.median(lead_values)) if lead_values else np.nan,
        "daily_false_alarms": float(false_signals / day_count),
        "signals_per_day": float(signal_count / day_count),
        "events_per_day": float(event_count / day_count),
        "false_alarms_per_detected_event": float(false_signals / detected) if detected else np.nan,
        "matched_signals": int(len(matched_signals)),
        "false_signals": int(false_signals),
    }


def match_events(
    events: pd.DataFrame,
    preds: pd.DataFrame,
    signal_mask: np.ndarray,
    min_lead: int,
    max_lead: int,
    n_days: int,
) -> dict[str, Any]:
    return match_events_from_context(events, build_match_context(preds), signal_mask, min_lead, max_lead, n_days)


def daily_budget_mask(preds: pd.DataFrame, budget_type: str, budget_value: float) -> np.ndarray:
    scores = preds["score"].to_numpy(dtype="float64")
    mask = np.zeros(len(preds), dtype=bool)
    for _, positions in preds.groupby("date", sort=False).indices.items():
        pos = np.asarray(positions, dtype=np.int64)
        if pos.size == 0:
            continue
        if budget_type == "daily_top_n":
            keep = min(int(budget_value), int(pos.size))
        elif budget_type == "daily_top_pct":
            keep = min(max(1, int(math.ceil(float(pos.size) * float(budget_value)))), int(pos.size))
        else:
            raise ValueError(f"Unknown budget type: {budget_type}")
        order = np.argsort(-scores[pos], kind="mergesort")[:keep]
        mask[pos[order]] = True
    return mask


def compute_budgeted_rows(
    horizon: int,
    cached: CachedModel,
    preds: pd.DataFrame,
    events: pd.DataFrame,
    match_context: dict[tuple[Any, Any], dict[str, np.ndarray]],
    gap: int,
    practical_max: int,
    n_days: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    label_max = int(gap) + int(horizon) - 1
    budgets: list[tuple[str, float]] = [("daily_top_n", float(v)) for v in DAILY_TOP_N_SIGNALS]
    budgets.extend(("daily_top_pct", float(v)) for v in DAILY_TOP_PCT_SIGNALS)
    for budget_type, budget_value in budgets:
        signal_mask = daily_budget_mask(preds, budget_type, budget_value)
        label_metrics = match_events_from_context(events, match_context, signal_mask, gap, label_max, n_days)
        practical_metrics = match_events_from_context(events, match_context, signal_mask, gap, practical_max, n_days)
        rows.append(
            {
                "horizon": f"H{horizon}",
                "model": cached.model_name,
                "feature_group": cached.feature_group,
                "budget_type": budget_type,
                "budget_value": int(budget_value) if budget_type == "daily_top_n" else float(budget_value),
                "signals_per_day": label_metrics["signals_per_day"],
                "daily_false_alarms": label_metrics["daily_false_alarms"],
                "daily_false_alarms_practical": practical_metrics["daily_false_alarms"],
                "event_recall_label_aligned": label_metrics["event_recall"],
                "event_recall_practical": practical_metrics["event_recall"],
                "average_lead_time": label_metrics["mean_lead"],
                "median_lead_time": label_metrics["median_lead"],
                "practical_average_lead_time": practical_metrics["mean_lead"],
                "practical_median_lead_time": practical_metrics["median_lead"],
                "false_alarms_per_detected_event": label_metrics["false_alarms_per_detected_event"],
                "false_alarms_per_detected_event_practical": practical_metrics["false_alarms_per_detected_event"],
                "detected_events": label_metrics["detected_events"],
                "detected_events_practical": practical_metrics["detected_events"],
                "total_events": label_metrics["eligible_events"],
                "total_events_practical": practical_metrics["eligible_events"],
                "pressure_episodes": int(len(events)),
            }
        )
    return rows


def score_valid_rows(df: pd.DataFrame, cached: CachedModel, target: str) -> pd.DataFrame:
    valid = df.loc[df[target].notna() & ~df[f"embargo_H{cached.horizon}"]].copy()
    if valid.empty:
        return pd.DataFrame()
    missing = [col for col in cached.features if col not in valid.columns]
    if missing:
        raise RuntimeError(f"Cached model features missing for H{cached.horizon}: {missing[:8]}")
    x = valid[cached.features].replace([np.inf, -np.inf], np.nan).astype("float32")
    scores = cached.score_model.predict_proba(x)[:, 1].astype("float32")
    out = valid[["code", "date", "datetime", "slot", target, "LSI_5"]].copy()
    out = out.rename(columns={target: "y"})
    out["code"] = out["code"].astype(str)
    out["slot"] = pd.to_numeric(out["slot"], errors="coerce").astype("int32")
    out["y"] = pd.to_numeric(out["y"], errors="coerce").astype("float32")
    out["score"] = scores
    return out


def compute_event_metrics(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    runner = load_runner()
    outputs_dir = (PROJECT_ROOT / args.outputs_dir).resolve()
    outputs_dir.mkdir(parents=True, exist_ok=True)
    config, manifest, split, main_thresholds, cross_context = configure_runner(runner, args)
    best_models = read_best_models(outputs_dir)
    cached_models = load_cached_models(config, args, best_models)

    preds_by_h: dict[int, list[pd.DataFrame]] = {5: [], 10: []}
    events_by_h: dict[int, list[pd.DataFrame]] = {5: [], 10: []}
    stock_manifest = manifest.loc[~manifest["is_index"].astype(bool)].copy().reset_index(drop=True)
    for idx, row in stock_manifest.iterrows():
        df = runner.prepare_shard(row, split, cross_context, main_thresholds, config["main_label"])
        df_test = df.loc[df["period"].eq("test")].copy()
        for horizon, cached in cached_models.items():
            target = f"Y_onset_H{horizon}"
            preds = score_valid_rows(df_test, cached, target)
            if not preds.empty:
                preds_by_h[horizon].append(preds)
            events = pressure_episodes(df_test, main_thresholds[horizon])
            if not events.empty:
                events_by_h[horizon].append(events)
        if (idx + 1) % 10 == 0 or idx + 1 == len(stock_manifest):
            print(f"scored event metrics {idx + 1}/{len(stock_manifest)} stocks", flush=True)
    results: list[dict[str, Any]] = []
    budgeted_rows: list[dict[str, Any]] = []
    audits: dict[int, dict[str, Any]] = {}
    practical_max = {5: 20, 10: 30}
    gap = int(args.gap)
    for horizon, cached in cached_models.items():
        preds = pd.concat(preds_by_h[horizon], ignore_index=True) if preds_by_h[horizon] else pd.DataFrame()
        events = pd.concat(events_by_h[horizon], ignore_index=True) if events_by_h[horizon] else pd.DataFrame()
        if preds.empty:
            raise RuntimeError(f"No valid test predictions available for H{horizon}")
        n_days = int(pd.Series(preds["date"]).nunique())
        top_threshold = float(np.nanquantile(preds["score"].to_numpy(dtype="float64"), 1.0 - float(args.top_frac)))
        signal_mask = preds["score"].to_numpy(dtype="float64") >= top_threshold
        match_context = build_match_context(preds)
        label_window_max = gap + int(horizon) - 1
        label_metrics = match_events_from_context(events, match_context, signal_mask, gap, label_window_max, n_days)
        practical_metrics = match_events_from_context(events, match_context, signal_mask, gap, practical_max[horizon], n_days)
        label_leads = first_future_event_leads(preds, events, preds["y"].to_numpy(dtype="float64") >= 0.5)
        signal_leads = first_future_event_leads(preds, events, signal_mask)
        label_lead_summary = summarize_leads(label_leads, gap, horizon, practical_max[horizon])
        signal_lead_summary = summarize_leads(signal_leads, gap, horizon, practical_max[horizon])
        signal_count = int(signal_mask.sum())
        minute_hit_count = int(((preds["y"].to_numpy(dtype="float64") >= 0.5) & signal_mask).sum())
        pressure_episode_count = int(len(events))
        onset_positive_count = int((preds["y"].to_numpy(dtype="float64") >= 0.5).sum())
        result = {
            "horizon": f"H{horizon}",
            "model": cached.model_name,
            "feature_group": cached.feature_group,
            "topk_threshold": top_threshold,
            "top_frac": float(args.top_frac),
            "pressure_episodes": pressure_episode_count,
            "onset_positive_rows": onset_positive_count,
            "top5_signal_count": signal_count,
            "top5_signal_minute_hits": minute_hit_count,
            "top5_signal_minute_hit_rate": float(minute_hit_count / signal_count) if signal_count else np.nan,
            "label_window_min_lead": gap,
            "label_window_max_lead": label_window_max,
            "practical_window_min_lead": gap,
            "practical_window_max_lead": practical_max[horizon],
            "label_aligned_eligible_events": label_metrics["eligible_events"],
            "label_aligned_detected_events": label_metrics["detected_events"],
            "label_aligned_event_recall": label_metrics["event_recall"],
            "practical_eligible_events": practical_metrics["eligible_events"],
            "practical_detected_events": practical_metrics["detected_events"],
            "practical_window_event_recall": practical_metrics["event_recall"],
            "average_lead_time": label_metrics["mean_lead"],
            "median_lead_time": label_metrics["median_lead"],
            "practical_average_lead_time": practical_metrics["mean_lead"],
            "practical_median_lead_time": practical_metrics["median_lead"],
            "daily_false_alarms": label_metrics["daily_false_alarms"],
            "practical_daily_false_alarms": practical_metrics["daily_false_alarms"],
            "signals_per_day": label_metrics["signals_per_day"],
            "events_per_day": label_metrics["events_per_day"],
            "false_alarms_per_detected_event": label_metrics["false_alarms_per_detected_event"],
            "practical_false_alarms_per_detected_event": practical_metrics["false_alarms_per_detected_event"],
            "test_days": n_days,
            "scored_rows": int(len(preds)),
        }
        results.append(result)
        if args.budgeted:
            budgeted_rows.extend(
                compute_budgeted_rows(
                    horizon=horizon,
                    cached=cached,
                    preds=preds,
                    events=events,
                    match_context=match_context,
                    gap=gap,
                    practical_max=practical_max[horizon],
                    n_days=n_days,
                )
            )
        audits[horizon] = {
            "result": result,
            "label_lead_summary": label_lead_summary,
            "signal_lead_summary": signal_lead_summary,
            "model_path": rel(cached.model_path),
        }

    metrics = pd.DataFrame(results)
    metrics_path = outputs_dir / "event_level_metrics_revised.csv"
    metrics.to_csv(metrics_path, index=False, encoding="utf-8-sig", float_format="%.6f")
    markdown_path = outputs_dir / "event_level_metrics_revised.md"
    audit_path = outputs_dir / ("event_level_audit_report_final_full.md" if args.mode == "full" else "event_level_audit_report.md")
    digest_path = outputs_dir / (
        "final_full_event_revised_digest.md" if args.mode == "full" else "allstock_diagnostic_event_revised_digest.md"
    )
    write_event_metrics_markdown(markdown_path, metrics)
    write_audit_report(audit_path, audits, args, config, main_thresholds, elapsed=time.time() - started)
    write_digest(digest_path, metrics, audits, outputs_dir)
    budgeted = pd.DataFrame(budgeted_rows)
    budgeted_path = outputs_dir / "budgeted_event_metrics.csv"
    budgeted_markdown_path = outputs_dir / "budgeted_event_metrics.md"
    budgeted_digest_path = outputs_dir / "budgeted_event_metrics_diagnostic_digest.md"
    if args.budgeted:
        budgeted.to_csv(budgeted_path, index=False, encoding="utf-8-sig", float_format="%.6f")
        write_budgeted_markdown(budgeted_markdown_path, budgeted)
        budgeted_digest_path = outputs_dir / (
            "budgeted_event_metrics_final_digest.md"
            if args.mode == "full"
            else "budgeted_event_metrics_diagnostic_digest.md"
        )
        write_budgeted_digest(budgeted_digest_path, budgeted, metrics)
    return {
        "metrics": metrics,
        "budgeted": budgeted,
        "metrics_path": metrics_path,
        "markdown_path": markdown_path,
        "audit_path": audit_path,
        "digest_path": digest_path,
        "budgeted_path": budgeted_path if args.budgeted else None,
        "budgeted_markdown_path": budgeted_markdown_path if args.budgeted else None,
        "budgeted_digest_path": budgeted_digest_path if args.budgeted else None,
        "elapsed": time.time() - started,
        "config": config,
    }


def pct(value: Any) -> str:
    if pd.isna(value):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def num(value: Any, digits: int = 4) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def write_event_metrics_markdown(path: Path, metrics: pd.DataFrame) -> None:
    lines = [
        "# Revised event-level onset metrics",
        "",
        PYTHON_NOTICE,
        "",
        "Event hits are evaluated by same stock, same trading date, and trading-minute `slot`.",
        "The label-aligned window is `s-(gap+H-1) <= t <= s-gap`; the practical window is H5 `[s-20,s-5]` and H10 `[s-30,s-5]`.",
        "",
        "| Horizon | Model | Group | Top5 threshold | Label recall | Practical recall | Avg lead | Median lead | Daily false alarms | Signals/day | Events/day | FA/detected event |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics.itertuples(index=False):
        lines.append(
            "| {h} | {m} | {g} | {thr} | {lr} | {pr} | {avg} | {med} | {dfa} | {spd} | {epd} | {fae} |".format(
                h=row.horizon,
                m=row.model,
                g=row.feature_group,
                thr=num(row.topk_threshold, 6),
                lr=pct(row.label_aligned_event_recall),
                pr=pct(row.practical_window_event_recall),
                avg=num(row.average_lead_time, 2),
                med=num(row.median_lead_time, 2),
                dfa=num(row.daily_false_alarms, 2),
                spd=num(row.signals_per_day, 2),
                epd=num(row.events_per_day, 2),
                fae=num(row.false_alarms_per_detected_event, 2),
            )
        )
    lines.extend(
        [
            "",
            "Additional columns in the CSV include total pressure episodes, eligible-event denominators, top5 signal counts, minute-level top5 hits, practical-window daily false alarms, and scored-row counts.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def budget_label(row: pd.Series | Any) -> str:
    budget_type = str(row.budget_type)
    if budget_type == "daily_top_n":
        return f"Top {int(float(row.budget_value))}/day"
    return f"Top {100.0 * float(row.budget_value):.1f}%/day"


def write_budgeted_markdown(path: Path, budgeted: pd.DataFrame) -> None:
    lines = [
        "# Budgeted event-level onset metrics",
        "",
        "Signals are selected within each trading day by descending model score. Event matching uses the corrected pressure-episode logic and trading-minute `slot` windows.",
        "",
        "| Horizon | Budget | Signals/day | Daily false alarms | Label recall | Practical recall | Avg lead | Median lead | FA/detected event | Detected/Total |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if budgeted.empty:
        lines.append("| NA | NA | NA | NA | NA | NA | NA | NA | NA | NA |")
    else:
        for row in budgeted.itertuples(index=False):
            lines.append(
                "| {h} | {b} | {spd} | {dfa} | {lr} | {pr} | {avg} | {med} | {fae} | {det}/{tot} |".format(
                    h=row.horizon,
                    b=budget_label(row),
                    spd=num(row.signals_per_day, 2),
                    dfa=num(row.daily_false_alarms, 2),
                    lr=pct(row.event_recall_label_aligned),
                    pr=pct(row.event_recall_practical),
                    avg=num(row.average_lead_time, 2),
                    med=num(row.median_lead_time, 2),
                    fae=num(row.false_alarms_per_detected_event, 2),
                    det=int(row.detected_events),
                    tot=int(row.total_events),
                )
            )
    lines.extend(
        [
            "",
            "The CSV also includes practical-window false alarms, practical lead time, practical detected events, and total pressure episode counts.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def choose_budget_for_main_table(budgeted: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    if budgeted.empty:
        return "NA", budgeted
    grouped = (
        budgeted.groupby(["budget_type", "budget_value"], dropna=False)
        .agg(
            min_label_recall=("event_recall_label_aligned", "min"),
            min_practical_recall=("event_recall_practical", "min"),
            avg_label_recall=("event_recall_label_aligned", "mean"),
            avg_daily_false_alarms=("daily_false_alarms", "mean"),
            avg_signals_per_day=("signals_per_day", "mean"),
        )
        .reset_index()
    )
    acceptable = grouped.loc[(grouped["min_label_recall"] >= 0.10) & (grouped["min_practical_recall"] >= 0.20)].copy()
    if acceptable.empty:
        ranked = grouped.sort_values(["min_label_recall", "avg_daily_false_alarms"], ascending=[False, True])
    else:
        ranked = acceptable.sort_values(["avg_daily_false_alarms", "min_label_recall"], ascending=[True, False])
    chosen = ranked.iloc[0]
    label = budget_label(chosen)
    return label, grouped


def write_budgeted_digest(path: Path, budgeted: pd.DataFrame, unbudgeted: pd.DataFrame) -> None:
    chosen_label, grouped = choose_budget_for_main_table(budgeted)
    lines = [
        "# Budgeted event-level diagnostic digest",
        "",
        "## Scope",
        "",
        "- Source: current all-stock diagnostic or final-full cached models, depending on the cache mode used by the caller.",
        "- Training: no model refit is performed by this recomputation script.",
        "- Event logic: corrected pressure-episode start and trading-slot prewarning windows.",
        "",
        "## Baseline top-5% event metrics",
        "",
    ]
    for row in unbudgeted.itertuples(index=False):
        lines.append(
            f"- {row.horizon}: signals/day {num(row.signals_per_day, 2)}, daily false alarms {num(row.daily_false_alarms, 2)}, label recall {pct(row.label_aligned_event_recall)}, practical recall {pct(row.practical_window_event_recall)}."
        )
    lines.extend(["", "## Budget summary", ""])
    if grouped.empty:
        lines.append("- No budgeted metrics were available.")
    else:
        for row in grouped.sort_values(["budget_type", "budget_value"]).itertuples(index=False):
            lines.append(
                "- {b}: avg signals/day {spd}, avg daily false alarms {dfa}, min label recall {lr}, min practical recall {pr}.".format(
                    b=budget_label(row),
                    spd=num(row.avg_signals_per_day, 2),
                    dfa=num(row.avg_daily_false_alarms, 2),
                    lr=pct(row.min_label_recall),
                    pr=pct(row.min_practical_recall),
                )
            )
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"- Recommended main-table budget: {chosen_label}.",
            "- Recommended appendix budgets: report the full Top N and Top pct grid to show the recall/false-alarm tradeoff.",
            "- Effect on final full: budgeted event evaluation is an application diagnostic and does not change the PR-AUC/TopK decision to proceed to final full.",
            "- If the chosen budget keeps meaningful recall while sharply reducing false alarms, it can be used as supplemental evidence of practical monitoring value.",
            "",
            "Required judgment phrase:",
            "",
            "预算约束事件级评价可以作为实际监测价值的补充证据。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_report(
    path: Path,
    audits: dict[int, dict[str, Any]],
    args: argparse.Namespace,
    config: dict[str, Any],
    main_thresholds: dict[int, float],
    elapsed: float,
) -> None:
    run_note = (
        "Final full: already completed before this post-run recomputation."
        if args.mode == "full"
        else "Final full: not run."
    )
    lines = [
        "# Event-level evaluation audit",
        "",
        "## Scope",
        "",
        "- Scope: all-stock diagnostic event-level audit only.",
        "- Training: no model was retrained; cached `trainval_model` objects were loaded from `checkpoints/models`.",
        f"- {run_note}",
        "- Paper body/final TeX: not modified.",
        f"- Data path: `{args.data_path}`.",
        f"- Cache signature: `{config.get('cache_signature')}`.",
        f"- Runtime seconds: {elapsed:.1f}.",
        "",
        "## Main finding",
        "",
        "The original event-level implementation is time-window misaligned for onset labels. It builds events from rows where `Y_onset_H >= 0.5`, so the label time `t` is treated as the event start. Onset labels are designed to occur before the true pressure episode start `s`, so the original code then searches for signals before an already-early label time. This can drive H5 event recall to zero even when minute-level Top5 hit and lift are high.",
        "",
        "The original code also used wall-clock minute differences between datetimes. The revised metrics use same-stock, same-date trading `slot` distances, matching the label construction by intraday row shifts.",
        "",
        "## Window definitions",
        "",
        f"- gap: {int(args.gap)}.",
        f"- lookback_clean: {int(args.lookback_clean)}.",
        f"- threshold_quantile: {float(args.threshold_quantile):.2f}.",
        "- label-aligned hit rule: `s-(gap+H-1) <= t <= s-gap`.",
        "- practical windows: H5 `s-20` to `s-5`; H10 `s-30` to `s-5`.",
        "- Original code windows: H5 `5..20` minutes before the derived label-event; H10 `10..30` minutes before the derived label-event.",
        "",
        "## Thresholds",
        "",
    ]
    for horizon in sorted(main_thresholds):
        lines.append(f"- H{horizon}: LSI_5 threshold = {main_thresholds[horizon]:.6f}.")
    lines.extend(["", "## Horizon diagnostics", ""])
    for horizon in sorted(audits):
        result = audits[horizon]["result"]
        label_summary = audits[horizon]["label_lead_summary"]
        signal_summary = audits[horizon]["signal_lead_summary"]
        lines.extend(
            [
                f"### H{horizon}",
                "",
                f"- Cached model: `{result['model']}` / `{result['feature_group']}` from `{audits[horizon]['model_path']}`.",
                f"- Onset positive rows: {result['onset_positive_rows']:,}.",
                f"- Pressure episodes: {result['pressure_episodes']:,}.",
                f"- Top5 signals: {result['top5_signal_count']:,}.",
                f"- Top5 minute-level hits: {result['top5_signal_minute_hits']:,} ({pct(result['top5_signal_minute_hit_rate'])}).",
                f"- Label-aligned eligible events: {result['label_aligned_eligible_events']:,}; detected: {result['label_aligned_detected_events']:,}; recall: {pct(result['label_aligned_event_recall'])}.",
                f"- Practical eligible events: {result['practical_eligible_events']:,}; detected: {result['practical_detected_events']:,}; recall: {pct(result['practical_window_event_recall'])}.",
                f"- Label-aligned daily false alarms: {num(result['daily_false_alarms'], 2)}.",
                f"- Practical-window daily false alarms: {num(result['practical_daily_false_alarms'], 2)}.",
                f"- Positive-label lead distribution: count={label_summary['count']:,}, median={num(label_summary['median'], 2)}, p10={num(label_summary['p10'], 2)}, p90={num(label_summary['p90'], 2)}, within label window={pct(label_summary['within_label_window_rate'])}.",
                f"- Top5-signal future event lead distribution: count={signal_summary['count']:,}, median={num(signal_summary['median'], 2)}, p10={num(signal_summary['p10'], 2)}, p90={num(signal_summary['p90'], 2)}, within label window={pct(signal_summary['within_label_window_rate'])}, within practical window={pct(signal_summary['within_practical_window_rate'])}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "The revised event-level metrics do not change PR-AUC or TopK lift because those are minute-level ranking metrics computed from the same labels and scores. They only replace the event aggregation denominator and prewarning-window matching logic.",
            "",
            "Conclusion: event-level evaluation should use the revised episode-start logic in any later final full run.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_digest(path: Path, metrics: pd.DataFrame, audits: dict[int, dict[str, Any]], outputs_dir: Path) -> None:
    original_path = outputs_dir / "event_level_metrics.csv"
    original = pd.read_csv(original_path) if original_path.exists() else pd.DataFrame()
    lines = [
        "# All-stock diagnostic event-level revised digest",
        "",
        "## What changed",
        "",
        "The original digest is not overwritten. This note only revises the event-level aggregation.",
        "",
        "Original H5 event recall was zero because the event-level code treated onset label times as episode starts and then searched for signals before those label times. The corrected implementation defines events from true LSI pressure episode starts and matches signals in the label-aligned prewarning window.",
        "",
        "Minute-level PR-AUC and Top5 lift are unaffected by this correction.",
        "",
        "## Original event-level output",
        "",
    ]
    if original.empty:
        lines.append("- Original `event_level_metrics.csv` was not available.")
    else:
        for row in original.itertuples(index=False):
            lines.append(
                f"- {row.horizon}: original event recall {pct(row.event_recall)}, daily false alarms {num(row.daily_false_alarms, 2)}."
            )
    lines.extend(["", "## Revised event-level output", ""])
    for row in metrics.itertuples(index=False):
        lines.append(
            "- {h}: label-aligned recall {lr}, practical recall {pr}, label-aligned daily false alarms {dfa}, practical daily false alarms {pdfa}.".format(
                h=row.horizon,
                lr=pct(row.label_aligned_event_recall),
                pr=pct(row.practical_window_event_recall),
                dfa=num(row.daily_false_alarms, 2),
                pdfa=num(row.practical_daily_false_alarms, 2),
            )
        )
    h5 = metrics.loc[metrics["horizon"].astype(str).eq("H5")]
    h10 = metrics.loc[metrics["horizon"].astype(str).eq("H10")]
    h5_recall = float(h5["label_aligned_event_recall"].iloc[0]) if not h5.empty else float("nan")
    h10_recall = float(h10["label_aligned_event_recall"].iloc[0]) if not h10.empty else float("nan")
    if np.isfinite(h5_recall) and h5_recall > 0 and np.isfinite(h10_recall) and h10_recall > 0:
        decision = (
            "Event-level evaluation had a time-window misalignment; after correction, the event-level results are usable "
            "as diagnostics. Full run should use the revised event metrics."
        )
    else:
        decision = (
            "Minute-level high-risk ranking and event-level advance hit rate still diverge after correction; event-level "
            "claims need cautious wording and full-run confirmation."
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {decision}",
            "- Recommendation on final full: the corrected event metrics do not overturn the prior all-stock minute-level conclusion; proceed to final full only if the user explicitly asks, and use the revised event metrics.",
            "- Recommendation for paper body: do not write these event-level diagnostics into the paper yet; use them to guide the next full run design.",
            "- Paper body/final TeX: not modified.",
            "- Future full run should use the revised event-level logic.",
            "",
            "Required judgment phrase:",
            "",
            "事件级评价原实现存在时间窗口错位；修正后不影响分钟级 PR-AUC 与 TopK lift 结论，但 full run 应使用修正后的事件级指标。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    print(PYTHON_NOTICE, flush=True)
    result = compute_event_metrics(args)
    print("Revised event-level metrics written:", flush=True)
    for key in ["metrics_path", "markdown_path", "audit_path", "digest_path"]:
        print(rel(result[key]), flush=True)
    for key in ["budgeted_path", "budgeted_markdown_path", "budgeted_digest_path"]:
        if result.get(key) is not None:
            print(rel(result[key]), flush=True)
    print(f"elapsed_seconds={result['elapsed']:.1f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
