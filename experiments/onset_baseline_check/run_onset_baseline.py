from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import subprocess
import sys
import traceback
import gc
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, precision_recall_curve, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

LGBMClassifier: Any | None = None
LIGHTGBM_AVAILABLE: bool | None = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = EXPERIMENT_DIR / "config_onset_baseline.yaml"
HORIZONS = [5, 10]
TASKS = {"onset": "Y_onset_H{h}", "continuation": "Stress_H{h}"}
TOP_FRACS = [0.01, 0.05, 0.10, 0.20]
ACTIVE_LOG_PATH: Path | None = None

COMPONENT_FEATURES = [
    "ILLIQ_5",
    "Range_5",
    "RV_5",
    "RelAmt_5",
    "ILLIQ_10",
    "Range_10",
    "RV_10",
    "RelAmt_10",
    "ILLIQ_20",
    "Range_20",
    "RV_20",
    "RelAmt_20",
]
Z_COMPONENT_FEATURES = [f"z_{c}" for c in COMPONENT_FEATURES]
MARKET_BASE = ["MarketLSI", "IndexRet", "IndexRV", "MarketRelAmt"]
FORBIDDEN_FEATURE_PARTS = [
    "Stress_H",
    "future_max",
    "FutureMax",
    "CrossStress",
    "Y_onset",
    "label",
    "target",
]


@dataclass
class FitResult:
    task: str
    horizon: int
    feature_group: str
    model: str
    feature_cols: list[str]
    train_model: Any | None
    trainval_model: Any | None
    status: str
    error: str = ""


@dataclass
class NaiveScorer:
    quantiles: np.ndarray

    @classmethod
    def fit(cls, scores: pd.Series) -> "NaiveScorer":
        values = pd.to_numeric(scores, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
        if values.size == 0:
            values = np.array([0.0], dtype="float64")
        values = np.sort(values.astype("float64"))
        return cls(values)

    def predict(self, scores: pd.Series) -> np.ndarray:
        values = pd.to_numeric(scores, errors="coerce").to_numpy(dtype="float64")
        fill = float(np.nanmedian(self.quantiles)) if self.quantiles.size else 0.0
        values = np.where(np.isfinite(values), values, fill)
        ranks = np.searchsorted(self.quantiles, values, side="right") / max(len(self.quantiles), 1)
        return np.clip(ranks, 0.0, 1.0).astype("float32")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the onset baseline experiment.")
    parser.add_argument("--mode", choices=["smoke", "bounded", "full"], default="bounded")
    parser.add_argument("--max-stock-codes", default=None, help="Stock-code cap; use null for the complete pool.")
    parser.add_argument("--bootstrap", type=int, default=None, help="Bootstrap iterations.")
    parser.add_argument("--threshold-quantile", type=float, default=None)
    parser.add_argument("--gap", type=int, default=None)
    parser.add_argument("--lookback-clean", type=int, default=None)
    parser.add_argument("--resume", action="store_true", help="Read existing checkpoint markers when available.")
    parser.add_argument("--dry-run", action="store_true", help="Validate configuration and data presence without fitting models.")
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Path to the YAML configuration file.")
    parser.add_argument("--data-path", default=None, help="Optional modeling panel parquet path.")
    return parser.parse_args(argv)


def parse_nullable_int(value: Any) -> int | None:
    if value in (None, "null", "None", ""):
        return None
    return int(value)


def cache_signature(config: dict[str, Any]) -> str:
    payload = {
        "mode": config.get("run_mode"),
        "data_path": config.get("paths", {}).get("data_path"),
        "gap": config.get("main_label", {}).get("gap"),
        "lookback_clean": config.get("main_label", {}).get("lookback_clean"),
        "threshold_quantile": config.get("main_label", {}).get("threshold_quantile"),
        "max_stock_codes": config.get("sampling", {}).get("max_stock_codes"),
        "bootstrap": config.get("bootstrap", {}).get("iterations"),
        "train_cap": config.get("sampling", {}).get("train_max_per_class_per_code"),
        "trainval_cap": config.get("sampling", {}).get("trainval_max_per_class_per_code"),
        "eval_cap": config.get("sampling", {}).get("eval_max_rows_per_task_horizon_period"),
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_config(config_path: Path | str | None = None) -> dict[str, Any]:
    path = Path(config_path) if config_path is not None else CONFIG_PATH
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def apply_run_mode(config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    cfg = copy.deepcopy(config)
    cfg["run_mode"] = args.mode
    cfg["resume"] = bool(args.resume)
    cfg["dry_run"] = bool(args.dry_run)
    cfg.setdefault("paths", {})
    cfg["paths"].setdefault("data_path", "data/processed/onset_model_panel.parquet")

    if args.mode == "smoke":
        cfg["sampling"]["max_stock_codes"] = 3
        cfg["sampling"]["train_max_per_class_per_code"] = min(int(cfg["sampling"]["train_max_per_class_per_code"]), 30)
        cfg["sampling"]["trainval_max_per_class_per_code"] = min(int(cfg["sampling"]["trainval_max_per_class_per_code"]), 40)
        cfg["sampling"]["eval_max_rows_per_task_horizon_period"] = 4000
        cfg["sampling"]["event_eval_full_test"] = False
        cfg["bootstrap"]["iterations"] = 10
        cfg["bootstrap"]["max_rows"] = min(int(cfg["bootstrap"].get("max_rows", 250000)), 10000)
        cfg["robustness_grid"]["gaps"] = [int(cfg["main_label"]["gap"])]
        cfg["robustness_grid"]["lookback_clean"] = [int(cfg["main_label"]["lookback_clean"])]
        cfg["robustness_grid"]["threshold_quantiles"] = [float(cfg["main_label"]["threshold_quantile"])]
        cfg["models"]["lightgbm"]["n_estimators"] = min(int(cfg["models"]["lightgbm"]["n_estimators"]), 20)
        cfg["models"]["smartboost"]["max_iter"] = min(int(cfg["models"]["smartboost"]["max_iter"]), 20)
        cfg["models"]["logit"]["max_iter"] = min(int(cfg["models"]["logit"]["max_iter"]), 150)
    elif args.mode == "bounded":
        cfg["sampling"]["max_stock_codes"] = 20
        cfg["sampling"]["eval_max_rows_per_task_horizon_period"] = cfg["sampling"].get(
            "eval_max_rows_per_task_horizon_period", 80000
        )
        cfg["sampling"]["event_eval_full_test"] = False
        cfg["bootstrap"]["iterations"] = 200
    elif args.mode == "full":
        cfg["sampling"]["max_stock_codes"] = None
        cfg["sampling"]["eval_max_rows_per_task_horizon_period"] = None
        cfg["sampling"]["event_eval_full_test"] = True
        cfg["bootstrap"]["iterations"] = 500

    if args.max_stock_codes is not None:
        cfg["sampling"]["max_stock_codes"] = parse_nullable_int(args.max_stock_codes)
    if args.bootstrap is not None:
        cfg["bootstrap"]["iterations"] = int(args.bootstrap)
    if args.threshold_quantile is not None:
        cfg["main_label"]["threshold_quantile"] = float(args.threshold_quantile)
        if float(args.threshold_quantile) not in [float(x) for x in cfg["robustness_grid"]["threshold_quantiles"]]:
            cfg["robustness_grid"]["threshold_quantiles"] = sorted(
                set([*map(float, cfg["robustness_grid"]["threshold_quantiles"]), float(args.threshold_quantile)])
            )
    if args.gap is not None:
        cfg["main_label"]["gap"] = int(args.gap)
        if int(args.gap) not in [int(x) for x in cfg["robustness_grid"]["gaps"]]:
            cfg["robustness_grid"]["gaps"] = sorted(set([*map(int, cfg["robustness_grid"]["gaps"]), int(args.gap)]))
    if args.lookback_clean is not None:
        cfg["main_label"]["lookback_clean"] = int(args.lookback_clean)
        if int(args.lookback_clean) not in [int(x) for x in cfg["robustness_grid"]["lookback_clean"]]:
            cfg["robustness_grid"]["lookback_clean"] = sorted(
                set([*map(int, cfg["robustness_grid"]["lookback_clean"]), int(args.lookback_clean)])
            )
    if args.data_path is not None:
        cfg["paths"]["data_path"] = args.data_path
        cfg["paths"]["data_path_explicit"] = args.data_path != "data/processed/onset_model_panel.parquet"
    else:
        cfg["paths"]["data_path_explicit"] = False
    cfg["cache_signature"] = cache_signature(cfg)
    return cfg


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def flush_log(output_dir: Path, log: list[str]) -> None:
    text = "\n".join(log) + "\n"
    write_text(output_dir / "run_log.txt", text)
    if ACTIVE_LOG_PATH is not None:
        write_text(ACTIVE_LOG_PATH, text)


def log_line(log: list[str], message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.append(f"[{stamp}] {message}")


def runtime_name() -> str:
    if os.getenv("GITHUB_ACTIONS") == "true":
        return "GitHub Actions"
    if os.getenv("CODESPACES"):
        return "Codespaces"
    return "local"


def git_commit_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def memory_hint() -> str:
    try:
        import psutil

        vm = psutil.virtual_memory()
        return f"available={vm.available / (1024 ** 3):.2f}GB,total={vm.total / (1024 ** 3):.2f}GB"
    except Exception:
        return "unavailable"


def checkpoint_path(output_dir: Path, name: str) -> Path:
    return output_dir.parent / "checkpoints" / f"{name}.json"


def write_checkpoint(output_dir: Path, name: str, payload: dict[str, Any]) -> None:
    path = checkpoint_path(output_dir, name)
    data = {
        "checkpoint": name,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        **payload,
    }
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def existing_checkpoints(output_dir: Path) -> list[str]:
    ckpt_dir = output_dir.parent / "checkpoints"
    if not ckpt_dir.exists():
        return []
    return sorted(p.stem for p in ckpt_dir.glob("*.json"))


def cache_manifest_path(output_dir: Path) -> Path:
    return output_dir.parent / "checkpoints" / "manifest.json"


def load_cache_manifest(output_dir: Path) -> dict[str, Any]:
    path = cache_manifest_path(output_dir)
    if not path.exists():
        return {"runs": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"runs": {}, "corrupt": True}


def save_cache_manifest(output_dir: Path, manifest: dict[str, Any]) -> None:
    write_text(cache_manifest_path(output_dir), json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def update_cache_stage(output_dir: Path, config: dict[str, Any], stage: str, files: list[Path] | None = None) -> None:
    manifest = load_cache_manifest(output_dir)
    sig = str(config.get("cache_signature", "unknown"))
    run = manifest.setdefault("runs", {}).setdefault(sig, {"stages": {}, "created_at": datetime.now().isoformat(timespec="seconds")})
    run["updated_at"] = datetime.now().isoformat(timespec="seconds")
    run["mode"] = config.get("run_mode")
    run["parameters"] = {
        "gap": config["main_label"]["gap"],
        "lookback_clean": config["main_label"]["lookback_clean"],
        "threshold_quantile": config["main_label"]["threshold_quantile"],
        "max_stock_codes": config["sampling"].get("max_stock_codes"),
        "bootstrap": config["bootstrap"]["iterations"],
        "data_path": config["paths"].get("data_path"),
    }
    run["stages"][stage] = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "files": [rel(p) for p in files or []],
    }
    save_cache_manifest(output_dir, manifest)


def cache_stage_available(output_dir: Path, config: dict[str, Any], stage: str, files: list[Path]) -> bool:
    manifest = load_cache_manifest(output_dir)
    run = manifest.get("runs", {}).get(str(config.get("cache_signature", "unknown")), {})
    if stage not in run.get("stages", {}):
        return False
    return all(path.exists() for path in files)


def write_cloud_run_summary(
    output_dir: Path,
    config: dict[str, Any],
    status: str,
    generated: list[Path],
    started_at: datetime,
    ended_at: datetime,
    error: str | None = None,
    manifest: pd.DataFrame | None = None,
    split: dict[str, str] | None = None,
) -> Path:
    elapsed = (ended_at - started_at).total_seconds()
    stock_count = "unknown"
    if manifest is not None and "is_index" in manifest:
        stock_count = str(int((~manifest["is_index"].astype(bool)).sum()))
    data_range = "unknown"
    if split:
        data_range = f"{split.get('train_start', '?')} to {split.get('test_end', '?')}"
    data_source = config.get("_data_source")
    data_path = config.get("_data_path_used")
    if status == "OK_REUSED":
        data_source = data_source or "cached_reports"
        data_path = data_path or config.get("paths", {}).get("data_path", "unknown")
    lines = [
        "# Cloud run summary",
        "",
        f"- status: {status}",
        f"- mode: {config.get('run_mode', 'unknown')}",
        f"- runtime: {runtime_name()}",
        f"- git_commit: {git_commit_hash()}",
        f"- python: {sys.version.split()[0]}",
        f"- data_source: {data_source or 'unknown'}",
        f"- data_path: {data_path or 'unknown'}",
        f"- data_rows: {config.get('_data_rows', 'unknown')}",
        f"- data_columns: {config.get('_data_columns', 'unknown')}",
        f"- started_at: {started_at.isoformat(timespec='seconds')}",
        f"- ended_at: {ended_at.isoformat(timespec='seconds')}",
        f"- elapsed_seconds: {elapsed:.1f}",
        f"- resume: {config.get('resume', False)}",
        f"- dry_run: {config.get('dry_run', False)}",
        f"- memory: {memory_hint()}",
        f"- stock_count_after_cap: {stock_count}",
        f"- manifest_rows_after_cap: {len(manifest) if manifest is not None else 'unknown'}",
        f"- data_range: {data_range}",
        f"- gap: {config['main_label']['gap']}",
        f"- lookback_clean: {config['main_label']['lookback_clean']}",
        f"- threshold_quantile: {config['main_label']['threshold_quantile']}",
        f"- max_stock_codes: {config['sampling'].get('max_stock_codes')}",
        f"- bootstrap_iterations: {config['bootstrap']['iterations']}",
        f"- checkpoints_read: {', '.join(config.get('_checkpoints_read', [])) or 'none'}",
        f"- stages_recomputed: {', '.join(config.get('_stages_recomputed', [])) or 'none'}",
    ]
    next_gate = "full-ready requires successful bounded run with real cloud data and matching checkpoints"
    if config.get("run_mode") == "smoke" and status == "OK":
        next_gate = "bounded-ready if the same data source is available in Codespaces or GitHub Actions"
    elif config.get("run_mode") == "bounded" and status == "OK":
        next_gate = "full-ready after reviewing bounded artifacts, runtime, memory, and data completeness"
    lines.append(f"- next_run_readiness: {next_gate}")
    risks = []
    if status == "OK_REUSED":
        risks.append("cached report reuse; data metadata was not reloaded in this fast path")
    elif config.get("_data_source") != "model_panel":
        risks.append("model panel was not used; runner fell back to stage2 shards")
    if config.get("run_mode") == "full":
        risks.append("full mode can exceed Actions runtime or memory limits")
    if config["bootstrap"]["iterations"] >= 500:
        risks.append("bootstrap may be slow")
    lines.extend(["", "## Risk Notes", ""])
    lines.extend([f"- {x}" for x in risks] or ["- none"])
    if error:
        lines.extend(["", "## Error", "", error])
    lines.extend(["", "## Output Files", ""])
    lines.extend([f"- {rel(path)}" for path in generated] or ["- none"])
    path = output_dir / "cloud_run_summary.md"
    write_text(path, "\n".join(lines) + "\n")
    return path


def apply_stock_code_cap(manifest: pd.DataFrame, config: dict[str, Any], log: list[str]) -> pd.DataFrame:
    cap = config.get("sampling", {}).get("max_stock_codes")
    if cap in (None, "null"):
        return manifest
    cap = int(cap)
    stock = manifest.loc[~manifest["is_index"]].copy()
    if cap <= 0 or len(stock) <= cap:
        return manifest
    positions = np.unique(np.linspace(0, len(stock) - 1, cap).round().astype(int))
    capped_stock = stock.iloc[positions].copy()
    log.append(f"Applied deterministic stock-code cap: {len(capped_stock)}/{len(stock)} stock shards")
    return capped_stock.reset_index(drop=True)


def setup_style(dpi: int) -> None:
    plt.rcParams.update(
        {
            "figure.dpi": dpi,
            "savefig.dpi": dpi,
            "savefig.bbox": "tight",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "axes.labelsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7,
            "axes.linewidth": 0.8,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "grid.linewidth": 0.5,
            "grid.color": "0.88",
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def despine(ax: plt.Axes, grid: bool = True) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.spines["left"].set_position(("outward", 4))
    ax.spines["bottom"].set_position(("outward", 4))
    if grid:
        ax.grid(axis="y", color="0.88", linewidth=0.5)
        ax.grid(axis="x", visible=False)
    else:
        ax.grid(False)


def colors() -> dict[str, str]:
    return {
        "primary": "#4477AA",
        "negative": "#EE6677",
        "positive": "#228833",
        "third": "#CCBB44",
        "purple": "#AA3377",
        "forecast": "#66CCEE",
        "baseline": "#BBBBBB",
        "dark": "#333333",
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def parquet_columns(path: Path) -> list[str]:
    try:
        import pyarrow.parquet as pq

        return list(pq.ParquetFile(path).schema.names)
    except Exception:
        return list(pd.read_parquet(path, nrows=0).columns)  # type: ignore[call-arg]


def normalize_panel_columns(df: pd.DataFrame) -> pd.DataFrame:
    aliases = {"stock_code": "code", "symbol": "code", "timestamp": "datetime", "LSI5": "LSI_5", "lsi5": "LSI_5"}
    rename = {src: dst for src, dst in aliases.items() if src in df.columns and dst not in df.columns}
    if rename:
        df = df.rename(columns=rename)
    return df


def required_contract_missing(columns: list[str]) -> list[str]:
    available = set(columns)
    groups = {
        "code/symbol": {"code", "stock_code", "symbol"},
        "date": {"date", "trading_date", "trade_date"},
        "datetime/timestamp": {"datetime", "timestamp", "minute_timestamp"},
        "LSI_5/LSI5": {"LSI_5", "LSI5", "lsi5"},
        "MarketLSI": {"MarketLSI", "market_lsi"},
        "IndexRet": {"IndexRet", "index_ret"},
        "IndexRV": {"IndexRV", "index_rv"},
        "MarketRelAmt": {"MarketRelAmt", "market_rel_amt"},
    }
    return [name for name, aliases in groups.items() if available.isdisjoint(aliases)]


def read_source_frame(row: pd.Series, columns: list[str] | None = None) -> pd.DataFrame:
    path = project_path(str(row["output_path"]))
    source_type = str(row.get("source_type", "shard"))
    available = parquet_columns(path)
    read_cols = [c for c in (columns or available) if c in available]
    missing = [c for c in (columns or []) if c not in available]
    if read_cols:
        try:
            if source_type == "panel":
                df = pd.read_parquet(path, columns=read_cols, filters=[("code", "==", row["code"])])
            else:
                df = pd.read_parquet(path, columns=read_cols)
        except Exception:
            df = pd.read_parquet(path, columns=read_cols)
    else:
        df = pd.read_parquet(path)
    df = normalize_panel_columns(df)
    if source_type == "panel" and "code" in df.columns:
        df = df.loc[df["code"].astype(str).eq(str(row["code"]))].copy()
    for col in missing:
        df[col] = np.nan
    if "is_index" not in df.columns:
        df["is_index"] = False
    return df


def make_panel_manifest(data_path: Path, log: list[str]) -> pd.DataFrame:
    columns = parquet_columns(data_path)
    missing = required_contract_missing(columns)
    if missing:
        raise RuntimeError(f"Model panel does not satisfy data contract. Missing groups: {', '.join(missing)}")
    code_col = "code" if "code" in columns else ("stock_code" if "stock_code" in columns else "symbol")
    read_cols = [code_col]
    if "is_index" in columns:
        read_cols.append("is_index")
    codes = pd.read_parquet(data_path, columns=read_cols)
    codes = normalize_panel_columns(codes)
    if "is_index" not in codes.columns:
        codes["is_index"] = False
    rows = codes.groupby(["code", "is_index"], dropna=False).size().reset_index(name="rows")
    rel_path = str(data_path.relative_to(PROJECT_ROOT)) if data_path.is_relative_to(PROJECT_ROOT) else str(data_path)
    rows["output_path"] = rel_path
    rows["source_type"] = "panel"
    log_line(log, f"Using model panel data source: {rel_path}; codes={rows['code'].nunique()}, rows={int(rows['rows'].sum())}")
    return rows[["code", "output_path", "rows", "is_index", "source_type"]]


def load_inputs(config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, str], dict[str, float]]:
    data_path_value = config["paths"].get("data_path")
    data_path = project_path(data_path_value) if data_path_value else None
    split_path = PROJECT_ROOT / config["paths"]["time_split"]
    threshold_path = PROJECT_ROOT / config["paths"]["existing_label_thresholds"]
    if not split_path.exists():
        raise FileNotFoundError(f"Missing split file: {split_path}")
    split = load_json(split_path)
    thresholds = load_json(threshold_path) if threshold_path.exists() else {}
    log_stub: list[str] = []
    if data_path is not None and data_path.exists():
        manifest = make_panel_manifest(data_path, log_stub)
        config["_data_source"] = "model_panel"
        config["_data_path_used"] = rel(data_path)
        config["_data_columns"] = len(parquet_columns(data_path))
    else:
        if config["paths"].get("data_path_explicit"):
            raise FileNotFoundError(f"Requested --data-path does not exist: {data_path}")
        manifest_path = PROJECT_ROOT / config["paths"]["lsi_manifest"]
        if not manifest_path.exists():
            searched = [str(data_path), str(manifest_path)]
            raise FileNotFoundError("No usable data source found. Searched: " + "; ".join(searched))
        manifest = pd.read_csv(manifest_path)
        manifest["source_type"] = "shard"
        config["_data_source"] = "stage2_shards"
        config["_data_path_used"] = rel(manifest_path)
        config["_data_columns"] = "per-shard"
    manifest = manifest.loc[manifest["rows"].fillna(0).astype(int) > 0].copy()
    manifest["is_index"] = manifest["is_index"].astype(bool)
    config["_data_rows"] = int(manifest["rows"].sum()) if "rows" in manifest else "unknown"
    return manifest, split, {str(k): float(v) for k, v in thresholds.items()}


def period_from_dates(dates: pd.Series, split: dict[str, str]) -> pd.Series:
    values = pd.to_datetime(dates, errors="coerce")
    period = pd.Series("unassigned", index=dates.index, dtype="object")
    period.loc[(values >= pd.Timestamp(split["train_start"])) & (values <= pd.Timestamp(split["train_end"]))] = "train"
    period.loc[
        (values >= pd.Timestamp(split["validation_start"])) & (values <= pd.Timestamp(split["validation_end"]))
    ] = "validation"
    period.loc[(values >= pd.Timestamp(split["test_start"])) & (values <= pd.Timestamp(split["test_end"]))] = "test"
    return period


def systematic_sample(df: pd.DataFrame, n: int | None) -> pd.DataFrame:
    if n is None or n <= 0 or len(df) <= n:
        return df.copy()
    step = max(1, int(math.floor(len(df) / n)))
    return df.iloc[::step].head(n).copy()


def stratified_binary_sample(df: pd.DataFrame, target: str, max_per_class: int) -> pd.DataFrame:
    valid = df.loc[df[target].notna()].copy()
    if valid.empty:
        return valid
    pos = valid.loc[valid[target] >= 0.5]
    neg = valid.loc[valid[target] < 0.5]
    return pd.concat(
        [systematic_sample(pos, max_per_class), systematic_sample(neg, max_per_class)],
        ignore_index=True,
    )


def build_cross_context(
    manifest: pd.DataFrame,
    split: dict[str, str],
    main_thresholds: dict[int, float],
    robustness_quantiles: list[float],
    log: list[str],
) -> tuple[pd.DataFrame, dict[float, float]]:
    series_parts = []
    date_map: pd.Series | None = None
    train_value_parts = []
    stock_manifest = manifest.loc[~manifest["is_index"]].copy()
    for idx, row in stock_manifest.iterrows():
        df = read_source_frame(row, columns=["datetime", "date", "LSI_5"])
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        df["LSI_5"] = pd.to_numeric(df["LSI_5"], errors="coerce").astype("float32")
        df = df.loc[df["datetime"].notna()].drop_duplicates("datetime")
        if date_map is None:
            date_map = df.set_index("datetime")["date"]
        period = period_from_dates(df["date"], split)
        train_values = df.loc[period.eq("train"), "LSI_5"].dropna().to_numpy(dtype="float32")
        if train_values.size:
            train_value_parts.append(train_values)
        series_parts.append(pd.Series(df["LSI_5"].to_numpy(dtype="float32"), index=df["datetime"], name=str(row["code"])))
        if (idx + 1) % 20 == 0:
            log.append(f"Loaded cross-section LSI shard {idx + 1}/{len(stock_manifest)}")
    if not series_parts:
        raise RuntimeError("No stock LSI shards are available for cross-sectional context.")
    wide = pd.concat(series_parts, axis=1).sort_index()
    if not train_value_parts:
        raise RuntimeError("No train-period LSI values are available for thresholds.")
    train_values = np.concatenate(train_value_parts).astype("float64")
    direct_thresholds = {float(q): float(np.nanquantile(train_values, float(q))) for q in robustness_quantiles}

    context = pd.DataFrame({"datetime": wide.index})
    context["xsec_lsi_mean"] = wide.mean(axis=1, skipna=True).to_numpy(dtype="float32")
    context["xsec_lsi_median"] = wide.median(axis=1, skipna=True).to_numpy(dtype="float32")
    context["xsec_lsi_std"] = wide.std(axis=1, skipna=True).to_numpy(dtype="float32")
    context["xsec_lsi_skew"] = wide.skew(axis=1, skipna=True).to_numpy(dtype="float32")
    context["xsec_stock_count"] = wide.count(axis=1).to_numpy(dtype="float32")
    context["xsec_lsi_q90"] = wide.quantile(0.90, axis=1, interpolation="linear").to_numpy(dtype="float32")
    for horizon, threshold in main_thresholds.items():
        pressure = wide.ge(float(threshold))
        valid_count = wide.notna().sum(axis=1).replace(0, np.nan)
        pressure_count = pressure.sum(axis=1)
        context[f"xsec_pressure_count_H{horizon}"] = pressure_count.to_numpy(dtype="float32")
        context[f"xsec_pressure_breadth_H{horizon}"] = (pressure_count / valid_count).to_numpy(dtype="float32")

    context = context.sort_values("datetime").reset_index(drop=True)
    if date_map is None:
        context["date"] = pd.to_datetime(context["datetime"]).dt.date
    else:
        context["date"] = pd.Series(date_map.reindex(pd.to_datetime(context["datetime"])).to_numpy(), index=context.index)
    for horizon in main_thresholds:
        breadth_col = f"xsec_pressure_breadth_H{horizon}"
        by_date = context.groupby("date", sort=False)[breadth_col]
        context[f"{breadth_col}_lag1"] = by_date.shift(1)
        context[f"{breadth_col}_rollmean_10"] = (
            by_date.rolling(10, min_periods=1).mean().reset_index(level=0, drop=True)
        )
    for col in context.columns:
        if col not in {"datetime", "date"}:
            context[col] = pd.to_numeric(context[col], errors="coerce").astype("float32")
    log.append(f"Built cross-sectional context for {len(context):,} minute timestamps")
    return context.drop(columns=["date"]), direct_thresholds


def future_window_any(series: pd.Series, gap: int, horizon: int) -> tuple[pd.Series, pd.Series]:
    shifted = [series.shift(-k) for k in range(int(gap), int(gap) + int(horizon))]
    values = pd.concat(shifted, axis=1)
    return values.max(axis=1), values.notna().sum(axis=1)


def make_onset_label(df: pd.DataFrame, threshold: float, gap: int, horizon: int, lookback_clean: int) -> pd.Series:
    threshold = float(threshold)
    gap = int(gap)
    horizon = int(horizon)
    window = int(lookback_clean) + 1
    result = np.full(len(df), np.nan, dtype="float32")

    def trailing_sum(values: np.ndarray, width: int) -> np.ndarray:
        out = np.full(values.size, -1, dtype="int32")
        if values.size < width:
            return out
        csum = np.concatenate(([0], np.cumsum(values.astype("int32"))))
        out[width - 1 :] = csum[width:] - csum[:-width]
        return out

    def forward_sum(values: np.ndarray, start_gap: int, width: int) -> np.ndarray:
        out = np.full(values.size, -1, dtype="int32")
        if values.size < start_gap + width:
            return out
        csum = np.concatenate(([0], np.cumsum(values.astype("int32"))))
        starts = np.arange(values.size, dtype="int32") + start_gap
        ends = starts + width
        valid = ends <= values.size
        out[valid] = csum[ends[valid]] - csum[starts[valid]]
        return out

    lsi_all = pd.to_numeric(df["LSI_5"], errors="coerce").to_numpy(dtype="float64")
    for _, positions in df.groupby(["code", "date"], sort=False).indices.items():
        idx = np.asarray(positions, dtype=np.intp)
        lsi = lsi_all[idx]
        observed = np.isfinite(lsi)
        pressure = observed & (lsi >= threshold)
        clean_count = trailing_sum(observed, window)
        prior_pressure_count = trailing_sum(pressure, window)
        future_observed_count = forward_sum(observed, gap, horizon)
        future_pressure_count = forward_sum(pressure, gap, horizon)
        valid = (clean_count == window) & (future_observed_count == horizon)
        onset = (prior_pressure_count == 0) & (future_pressure_count > 0)
        out = onset.astype("float32")
        out[~valid] = np.nan
        result[idx] = out
    return pd.Series(result, index=df.index, dtype="float32")


def make_onset_label_pandas_reference(
    df: pd.DataFrame, threshold: float, gap: int, horizon: int, lookback_clean: int
) -> pd.Series:
    def one_day(values: pd.Series) -> pd.Series:
        lsi = pd.to_numeric(values, errors="coerce")
        pressure = (lsi >= float(threshold)).where(lsi.notna(), np.nan).astype("float32")
        pressure_zero = pressure.fillna(0.0)
        clean_count = lsi.notna().rolling(int(lookback_clean) + 1, min_periods=int(lookback_clean) + 1).sum()
        prior_any = pressure_zero.rolling(int(lookback_clean) + 1, min_periods=int(lookback_clean) + 1).max()
        future_any, future_count = future_window_any(pressure, int(gap), int(horizon))
        valid = (clean_count == int(lookback_clean) + 1) & (future_count == int(horizon))
        label = ((prior_any < 0.5) & (future_any >= 0.5)).astype("float32")
        label.loc[~valid] = np.nan
        return label

    return df.groupby(["code", "date"], sort=False)["LSI_5"].transform(one_day).astype("float32")


def validate_onset_label_equivalence(
    manifest: pd.DataFrame,
    main_thresholds: dict[int, float],
    config: dict[str, Any],
    log: list[str],
    max_codes: int = 2,
    max_days: int = 3,
) -> None:
    stock_manifest = manifest.loc[~manifest["is_index"]].head(max_codes).copy()
    gap = int(config["main_label"]["gap"])
    lookback = int(config["main_label"]["lookback_clean"])
    mismatches: list[pd.DataFrame] = []
    for _, row in stock_manifest.iterrows():
        path = PROJECT_ROOT / str(row["output_path"])
        df = pd.read_parquet(path, columns=["code", "is_index", "date", "slot", "LSI_5"])
        df = df.loc[~df["is_index"].astype(bool)].copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        keep_days = list(pd.Series(df["date"].dropna().unique()).head(max_days))
        df = df.loc[df["date"].isin(keep_days)].sort_values(["code", "date", "slot"]).reset_index(drop=True)
        for horizon in HORIZONS:
            threshold = float(main_thresholds[horizon])
            ref = make_onset_label_pandas_reference(df, threshold, gap, horizon, lookback)
            fast = make_onset_label(df, threshold, gap, horizon, lookback)
            same = (ref.isna().to_numpy() == fast.isna().to_numpy()) & (
                np.nan_to_num(ref.to_numpy(), nan=-1.0) == np.nan_to_num(fast.to_numpy(), nan=-1.0)
            )
            if not bool(np.all(same)):
                bad = df.loc[~same, ["code", "date", "slot", "LSI_5"]].copy()
                bad["horizon"] = f"H{horizon}"
                bad["reference"] = ref.loc[~same].to_numpy()
                bad["fast"] = fast.loc[~same].to_numpy()
                mismatches.append(bad.head(20))
    if mismatches:
        mismatch = pd.concat(mismatches, ignore_index=True).head(20)
        log.append("Onset label equivalence validation failed; first mismatches:")
        log.extend(mismatch.to_string(index=False).splitlines())
        raise RuntimeError("NumPy onset label implementation differs from pandas reference.")
    log.append("Onset label equivalence validation passed.")


def embargo_mask(df: pd.DataFrame, split: dict[str, str], embargo: int) -> pd.Series:
    mask = pd.Series(False, index=df.index)
    date_values = pd.to_datetime(df["date"], errors="coerce").dt.date.astype(str)
    slot = pd.to_numeric(df["slot"], errors="coerce")
    for date_key, side in [
        (split["train_end"], "tail"),
        (split["validation_start"], "head"),
        (split["validation_end"], "tail"),
        (split["test_start"], "head"),
    ]:
        date_mask = date_values.eq(str(date_key))
        if not date_mask.any():
            continue
        if side == "head":
            min_slot = slot.loc[date_mask].min()
            mask.loc[date_mask & (slot <= min_slot + embargo - 1)] = True
        else:
            max_slot = slot.loc[date_mask].max()
            mask.loc[date_mask & (slot >= max_slot - embargo + 1)] = True
    return mask


def add_regime_columns(df: pd.DataFrame) -> pd.DataFrame:
    dates = pd.to_datetime(df["date"], errors="coerce")
    df["reg_stage_1"] = ((dates >= pd.Timestamp("2023-05-15")) & (dates <= pd.Timestamp("2024-10-07"))).astype("int8")
    df["reg_stage_2"] = ((dates >= pd.Timestamp("2024-10-08")) & (dates <= pd.Timestamp("2025-07-06"))).astype("int8")
    df["reg_stage_3"] = ((dates >= pd.Timestamp("2025-07-07")) & (dates <= pd.Timestamp("2026-05-13"))).astype("int8")
    return df


def prepare_shard(
    row: pd.Series,
    split: dict[str, str],
    cross_context: pd.DataFrame,
    main_thresholds: dict[int, float],
    label_cfg: dict[str, Any],
) -> pd.DataFrame:
    read_cols = [
        "code",
        "is_index",
        "datetime",
        "date",
        "slot",
        "ret_1m",
        "amount",
        "valid_minutes",
        *COMPONENT_FEATURES,
        *Z_COMPONENT_FEATURES,
        "LSI_5",
        "LSI_10",
        "LSI_20",
        "MarketLSI",
        "IndexRet",
        "IndexRV",
        "MarketRelAmt",
        "Stress_H5",
        "Stress_H10",
    ]
    df = read_source_frame(row, columns=read_cols)
    df = df.loc[~df["is_index"].astype(bool)].copy()
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df = df.sort_values(["code", "date", "slot"]).reset_index(drop=True)
    df = df.merge(cross_context, on="datetime", how="left", validate="many_to_one")
    df["period"] = period_from_dates(df["date"], split)

    numeric_cols = [
        "slot",
        "ret_1m",
        "amount",
        "valid_minutes",
        *COMPONENT_FEATURES,
        *Z_COMPONENT_FEATURES,
        "LSI_5",
        "LSI_10",
        "LSI_20",
        "MarketLSI",
        "IndexRet",
        "IndexRV",
        "MarketRelAmt",
        "Stress_H5",
        "Stress_H10",
    ]
    numeric_cols.extend([c for c in df.columns if c.startswith("xsec_")])
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    by_day = df.groupby(["code", "date"], sort=False)
    for lag in [1, 2, 5]:
        df[f"LSI_5_lag{lag}"] = by_day["LSI_5"].shift(lag)
    for col in ["LSI_10", "LSI_20"]:
        df[f"{col}_lag1"] = by_day[col].shift(1)
    for window in [5, 10, 20]:
        df[f"LSI_5_rollmean_{window}"] = (
            by_day["LSI_5"].rolling(window, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        )
        df[f"LSI_5_rollmax_{window}"] = (
            by_day["LSI_5"].rolling(window, min_periods=1).max().reset_index(level=[0, 1], drop=True)
        )
        df[f"ret_sum_{window}"] = (
            by_day["ret_1m"].rolling(window, min_periods=1).sum().reset_index(level=[0, 1], drop=True)
        )
    for col in MARKET_BASE:
        df[f"{col}_lag1"] = by_day[col].shift(1)
        df[f"{col}_rollmean_10"] = by_day[col].rolling(10, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        if col in {"MarketLSI", "MarketRelAmt", "IndexRV"}:
            df[f"{col}_rollmax_20"] = by_day[col].rolling(20, min_periods=1).max().reset_index(level=[0, 1], drop=True)

    df["cum_ret_open"] = by_day["ret_1m"].cumsum()
    df["cum_amount_log_so_far"] = np.log1p(by_day["amount"].cumsum().clip(lower=0))
    slot = pd.to_numeric(df["slot"], errors="coerce").astype("float64")
    df["slot_sin"] = np.sin(2.0 * np.pi * slot / 240.0)
    df["slot_cos"] = np.cos(2.0 * np.pi * slot / 240.0)
    df["is_open_10m"] = (slot <= 10).astype("int8")
    df["is_afternoon_open_10m"] = ((slot >= 122) & (slot <= 131)).astype("int8")
    df["is_tail_10m"] = (slot >= 230).astype("int8")
    df = add_regime_columns(df)

    gap = int(label_cfg["gap"])
    lookback = int(label_cfg["lookback_clean"])
    for horizon, threshold in main_thresholds.items():
        df[f"LSI_5_minus_threshold_H{horizon}"] = df["LSI_5"] - float(threshold)
        df[f"Y_onset_H{horizon}"] = make_onset_label(df, threshold, gap, int(horizon), lookback)
        df[f"embargo_H{horizon}"] = embargo_mask(df, split, gap + int(horizon)).astype("bool")
    return df


def build_feature_groups(horizon: int, available_cols: set[str]) -> dict[str, list[str]]:
    p = [
        "LSI_5",
        "LSI_5_lag1",
        "LSI_5_lag2",
        "LSI_5_lag5",
        "LSI_5_rollmean_5",
        "LSI_5_rollmean_10",
        "LSI_5_rollmax_5",
        "LSI_5_rollmax_10",
        "LSI_5_rollmax_20",
        f"LSI_5_minus_threshold_H{horizon}",
    ]
    market = [
        "MarketLSI",
        "MarketLSI_lag1",
        "MarketLSI_rollmean_10",
        "MarketLSI_rollmax_20",
        "IndexRet",
        "IndexRet_lag1",
        "IndexRet_rollmean_10",
        "IndexRV",
        "IndexRV_lag1",
        "IndexRV_rollmean_10",
        "IndexRV_rollmax_20",
        "MarketRelAmt",
        "MarketRelAmt_lag1",
        "MarketRelAmt_rollmean_10",
        "MarketRelAmt_rollmax_20",
    ]
    cross = [
        "xsec_lsi_mean",
        "xsec_lsi_median",
        "xsec_lsi_q90",
        "xsec_lsi_std",
        "xsec_lsi_skew",
        "xsec_stock_count",
        f"xsec_pressure_count_H{horizon}",
        f"xsec_pressure_breadth_H{horizon}",
        f"xsec_pressure_breadth_H{horizon}_lag1",
        f"xsec_pressure_breadth_H{horizon}_rollmean_10",
    ]
    extra = [
        *COMPONENT_FEATURES,
        *Z_COMPONENT_FEATURES,
        "LSI_10",
        "LSI_20",
        "LSI_10_lag1",
        "LSI_20_lag1",
        "ret_1m",
        "ret_sum_5",
        "ret_sum_10",
        "ret_sum_20",
        "cum_ret_open",
        "cum_amount_log_so_far",
        "slot",
        "slot_sin",
        "slot_cos",
        "is_open_10m",
        "is_afternoon_open_10m",
        "is_tail_10m",
        "reg_stage_1",
        "reg_stage_2",
        "reg_stage_3",
    ]
    groups = {
        "P": p,
        "M": [*p, *market],
        "C": [*p, *market, *cross],
        "ALL": [*p, *market, *cross, *extra],
    }
    clean_groups = {}
    for name, cols in groups.items():
        deduped = []
        for col in cols:
            if col in available_cols and col not in deduped and not any(part in col for part in FORBIDDEN_FEATURE_PARTS):
                deduped.append(col)
        clean_groups[name] = deduped
    return clean_groups


def collect_datasets(
    manifest: pd.DataFrame,
    split: dict[str, str],
    cross_context: pd.DataFrame,
    main_thresholds: dict[int, float],
    direct_thresholds: dict[float, float],
    config: dict[str, Any],
    log: list[str],
    output_dir: Path | None = None,
) -> tuple[
    dict[tuple[str, int], pd.DataFrame],
    dict[tuple[str, int], pd.DataFrame],
    dict[tuple[str, int, str], pd.DataFrame],
    pd.DataFrame,
    set[str],
]:
    stock_manifest = manifest.loc[~manifest["is_index"]].copy()
    train_parts: dict[tuple[str, int], list[pd.DataFrame]] = {(task, h): [] for task in TASKS for h in HORIZONS}
    trainval_parts: dict[tuple[str, int], list[pd.DataFrame]] = {(task, h): [] for task in TASKS for h in HORIZONS}
    eval_parts: dict[tuple[str, int, str], list[pd.DataFrame]] = {
        (task, h, period): [] for task in TASKS for h in HORIZONS for period in ["validation", "test"]
    }
    robustness_rows: list[dict[str, Any]] = []
    available_cols: set[str] = set()

    per_code_train = int(config["sampling"]["train_max_per_class_per_code"])
    per_code_trainval = int(config["sampling"]["trainval_max_per_class_per_code"])
    eval_cap = config["sampling"].get("eval_max_rows_per_task_horizon_period")
    per_code_eval = None if eval_cap in (None, "null") else max(100, int(eval_cap) // max(1, len(stock_manifest)))
    stream_full_eval = eval_cap in (None, "null")

    for idx, row in stock_manifest.reset_index(drop=True).iterrows():
        log.append(f"Preparing shard {idx + 1}/{len(stock_manifest)}: {row['code']}")
        if output_dir is not None:
            flush_log(output_dir, log)
        df = prepare_shard(row, split, cross_context, main_thresholds, config["main_label"])
        available_cols.update(df.columns)
        for task, template in TASKS.items():
            for horizon in HORIZONS:
                target = template.format(h=horizon)
                valid = df.loc[df[target].notna() & ~df[f"embargo_H{horizon}"]].copy()
                train = valid.loc[valid["period"].eq("train")]
                trainval = valid.loc[valid["period"].isin(["train", "validation"])]
                train_parts[(task, horizon)].append(stratified_binary_sample(train, target, per_code_train))
                trainval_parts[(task, horizon)].append(stratified_binary_sample(trainval, target, per_code_trainval))
                if not stream_full_eval:
                    for period in ["validation", "test"]:
                        eval_df = valid.loc[valid["period"].eq(period)]
                        eval_parts[(task, horizon, period)].append(systematic_sample(eval_df, per_code_eval))

        if config["robustness_grid"].get("enabled", True):
            embargo_cache: dict[tuple[int, int], pd.Series] = {}
            period_series = df["period"]
            for gap in config["robustness_grid"]["gaps"]:
                gap_int = int(gap)
                for lookback in config["robustness_grid"]["lookback_clean"]:
                    lookback_int = int(lookback)
                    for q in config["robustness_grid"]["threshold_quantiles"]:
                        q_float = float(q)
                        threshold = direct_thresholds[q_float]
                        for horizon in HORIZONS:
                            horizon_int = int(horizon)
                            emb_key = (gap_int, horizon_int)
                            if emb_key not in embargo_cache:
                                embargo_cache[emb_key] = embargo_mask(df, split, gap_int + horizon_int).astype("bool")
                            label = make_onset_label(df, threshold, gap_int, horizon_int, lookback_int)
                            valid = label.notna() & ~embargo_cache[emb_key]
                            for period in ["train", "validation", "test"]:
                                period_mask = valid & period_series.eq(period)
                                rows_count = int(period_mask.sum())
                                event_count = float(label.loc[period_mask].sum()) if rows_count else 0.0
                                robustness_rows.append(
                                    {
                                        "gap": gap_int,
                                        "lookback_clean": lookback_int,
                                        "threshold_quantile": q_float,
                                        "threshold": float(threshold),
                                        "horizon": f"H{horizon_int}",
                                        "period": period,
                                        "rows": rows_count,
                                        "events": event_count,
                                    }
                                )
                            del label, valid
        del df
        gc.collect()
        if output_dir is not None and (idx + 1) % 5 == 0:
            log.append(f"Collected training/robustness shard {idx + 1}/{len(stock_manifest)}")
            flush_log(output_dir, log)

    train_samples = {
        key: pd.concat(parts, ignore_index=True) if parts else pd.DataFrame() for key, parts in train_parts.items()
    }
    trainval_samples = {
        key: pd.concat(parts, ignore_index=True) if parts else pd.DataFrame() for key, parts in trainval_parts.items()
    }
    eval_samples = {
        key: pd.concat(parts, ignore_index=True) if parts else pd.DataFrame() for key, parts in eval_parts.items()
    }
    robustness = pd.DataFrame(robustness_rows)
    if not robustness.empty:
        group_cols = ["gap", "lookback_clean", "threshold_quantile", "threshold", "horizon", "period"]
        robustness = (
            robustness.groupby(group_cols, as_index=False)
            .agg(rows=("rows", "sum"), events=("events", "sum"))
            .sort_values(["horizon", "period", "gap", "lookback_clean", "threshold_quantile"])
            .reset_index(drop=True)
        )
        robustness["event_rate"] = np.where(
            robustness["rows"] > 0,
            robustness["events"] / robustness["rows"],
            np.nan,
        )
    return train_samples, trainval_samples, eval_samples, robustness, available_cols


def clean_xy(df: pd.DataFrame, target: str, features: list[str]) -> tuple[pd.DataFrame, np.ndarray]:
    cols = [c for c in features if c in df.columns]
    out = df.loc[df[target].notna(), [*cols, target]].copy()
    out = out.replace([np.inf, -np.inf], np.nan)
    y = out[target].astype("int8").to_numpy()
    return out[cols].astype("float32"), y


def balanced_weights(y: np.ndarray) -> np.ndarray:
    n = len(y)
    pos = max(int((y == 1).sum()), 1)
    neg = max(int((y == 0).sum()), 1)
    return np.where(y == 1, n / (2.0 * pos), n / (2.0 * neg)).astype("float32")


def get_lgbm_classifier() -> Any | None:
    global LGBMClassifier, LIGHTGBM_AVAILABLE
    if LIGHTGBM_AVAILABLE is None:
        try:
            from lightgbm import LGBMClassifier as _LGBMClassifier

            LGBMClassifier = _LGBMClassifier
            LIGHTGBM_AVAILABLE = True
        except Exception:
            LGBMClassifier = None
            LIGHTGBM_AVAILABLE = False
    return LGBMClassifier


def make_model(model_name: str, config: dict[str, Any], seed: int) -> Pipeline:
    if model_name == "Logit":
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=int(config["models"]["logit"]["max_iter"]),
                        class_weight=config["models"]["logit"].get("class_weight", "balanced"),
                        solver="lbfgs",
                        n_jobs=1,
                        random_state=seed,
                    ),
                ),
            ]
        )
    if model_name == "LightGBM":
        lgbm_classifier = get_lgbm_classifier()
        if lgbm_classifier is None:
            raise RuntimeError("LightGBM is not available")
        params = config["models"]["lightgbm"]
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    lgbm_classifier(
                        objective="binary",
                        n_estimators=int(params["n_estimators"]),
                        learning_rate=float(params["learning_rate"]),
                        num_leaves=int(params["num_leaves"]),
                        min_child_samples=int(params["min_child_samples"]),
                        subsample=float(params["subsample"]),
                        colsample_bytree=float(params["colsample_bytree"]),
                        class_weight="balanced",
                        random_state=seed,
                        n_jobs=-1,
                        verbosity=-1,
                    ),
                ),
            ]
        )
    if model_name == "SMARTBoost":
        params = config["models"]["smartboost"]
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    HistGradientBoostingClassifier(
                        loss="log_loss",
                        learning_rate=float(params["learning_rate"]),
                        max_iter=int(params["max_iter"]),
                        max_leaf_nodes=int(params["max_leaf_nodes"]),
                        min_samples_leaf=int(params["min_samples_leaf"]),
                        l2_regularization=float(params["l2_regularization"]),
                        early_stopping=False,
                        random_state=seed,
                    ),
                ),
            ]
        )
    raise ValueError(model_name)


def fit_pipeline(pipe: Pipeline, x: pd.DataFrame, y: np.ndarray, model_name: str) -> Pipeline:
    if model_name in {"LightGBM", "SMARTBoost"}:
        pipe.fit(x, y, model__sample_weight=balanced_weights(y))
    else:
        pipe.fit(x, y)
    return pipe


def train_models(
    train_samples: dict[tuple[str, int], pd.DataFrame],
    trainval_samples: dict[tuple[str, int], pd.DataFrame],
    feature_groups_by_h: dict[int, dict[str, list[str]]],
    config: dict[str, Any],
    log: list[str],
    output_dir: Path | None = None,
) -> tuple[list[FitResult], dict[tuple[str, int], NaiveScorer], pd.DataFrame]:
    seed = int(config["seed"])
    fit_results: list[FitResult] = []
    naive: dict[tuple[str, int], NaiveScorer] = {}
    sample_rows = []
    for task in TASKS:
        for horizon in HORIZONS:
            target = TASKS[task].format(h=horizon)
            train_df = train_samples[(task, horizon)]
            trainval_df = trainval_samples[(task, horizon)]
            naive[(task, horizon)] = NaiveScorer.fit(train_df.get("LSI_5_rollmax_20", pd.Series(dtype="float64")))
            sample_rows.append(
                {
                    "task": task,
                    "horizon": f"H{horizon}",
                    "sample": "train",
                    "rows": int(len(train_df)),
                    "event_rate": float(train_df[target].mean()) if target in train_df and len(train_df) else np.nan,
                }
            )
            sample_rows.append(
                {
                    "task": task,
                    "horizon": f"H{horizon}",
                    "sample": "train_plus_validation",
                    "rows": int(len(trainval_df)),
                    "event_rate": float(trainval_df[target].mean()) if target in trainval_df and len(trainval_df) else np.nan,
                }
            )
            for group, features in feature_groups_by_h[horizon].items():
                for model_name in ["Logit", "LightGBM", "SMARTBoost"]:
                    try:
                        if not features:
                            raise RuntimeError("No available feature columns")
                        x_train, y_train = clean_xy(train_df, target, features)
                        x_trainval, y_trainval = clean_xy(trainval_df, target, features)
                        if len(np.unique(y_train)) < 2 or len(np.unique(y_trainval)) < 2:
                            raise RuntimeError("Training sample has fewer than two classes")
                        model_cache = None
                        if output_dir is not None:
                            cache_dir = output_dir.parent / "checkpoints" / "models"
                            cache_dir.mkdir(parents=True, exist_ok=True)
                            sig = str(config.get("cache_signature", "nosig"))
                            stem = f"{sig}_{task}_H{horizon}_{group}_{model_name}"
                            model_cache = cache_dir / f"{stem}.joblib"
                        reused_model = False
                        if (
                            output_dir is not None
                            and config.get("resume")
                            and model_cache is not None
                            and model_cache.exists()
                        ):
                            try:
                                cached = joblib.load(model_cache)
                                if cached.get("signature") != config.get("cache_signature"):
                                    raise RuntimeError("cache signature mismatch")
                                train_model = cached["train_model"]
                                trainval_model = cached["trainval_model"]
                                config.setdefault("_checkpoints_read", []).append(rel(model_cache))
                                log.append(f"Fit {task} H{horizon} {group} {model_name}: reused model checkpoint")
                                reused_model = True
                            except Exception as cache_exc:
                                log.append(
                                    f"Fit {task} H{horizon} {group} {model_name}: model checkpoint unreadable; recomputing ({cache_exc})"
                                )
                        else:
                            cache_exc = None
                        if not reused_model:
                            train_model = fit_pipeline(make_model(model_name, config, seed), x_train, y_train, model_name)
                            trainval_model = fit_pipeline(make_model(model_name, config, seed), x_trainval, y_trainval, model_name)
                            config.setdefault("_stages_recomputed", []).append(f"model:{task}:H{horizon}:{group}:{model_name}")
                            if model_cache is not None:
                                joblib.dump(
                                    {
                                        "signature": config.get("cache_signature"),
                                        "features": features,
                                        "train_model": train_model,
                                        "trainval_model": trainval_model,
                                    },
                                    model_cache,
                                )
                        fit_results.append(
                            FitResult(task, horizon, group, model_name, features, train_model, trainval_model, "OK")
                        )
                        if not reused_model:
                            log.append(f"Fit {task} H{horizon} {group} {model_name}: OK")
                    except Exception as exc:
                        fit_results.append(FitResult(task, horizon, group, model_name, features, None, None, "FAIL", str(exc)))
                        log.append(f"Fit {task} H{horizon} {group} {model_name}: FAIL - {exc}")
    return fit_results, naive, pd.DataFrame(sample_rows)


def top_metrics(y: np.ndarray, p: np.ndarray, frac: float) -> tuple[float, float]:
    n = len(y)
    if n == 0:
        return np.nan, np.nan
    top_n = max(1, int(math.ceil(n * float(frac))))
    order = np.argsort(-p, kind="mergesort")[:top_n]
    hit_rate = float(np.mean(y[order] == 1))
    base = float(np.mean(y == 1))
    lift = hit_rate / base if base > 0 else np.nan
    return hit_rate, lift


def evaluate_arrays(y_raw: pd.Series, p_raw: np.ndarray) -> tuple[dict[str, float], list[dict[str, float]], np.ndarray, np.ndarray]:
    y = pd.to_numeric(y_raw, errors="coerce").to_numpy(dtype="float64")
    p = np.asarray(p_raw, dtype="float64")
    mask = np.isfinite(y) & np.isfinite(p)
    y = y[mask].astype("int8")
    p = np.clip(p[mask], 0.0, 1.0)
    row: dict[str, float] = {
        "rows": int(len(y)),
        "event_rate": float(np.mean(y)) if len(y) else np.nan,
        "PR_AUC": np.nan,
        "ROC_AUC": np.nan,
        "Brier": np.nan,
    }
    if len(y):
        row["Brier"] = float(brier_score_loss(y, p))
    if len(np.unique(y)) >= 2:
        row["PR_AUC"] = float(average_precision_score(y, p))
        row["ROC_AUC"] = float(roc_auc_score(y, p))
    top_rows = []
    for frac in TOP_FRACS:
        hit, lift = top_metrics(y, p, frac)
        top_rows.append({"top_frac": frac, "hit_rate": hit, "lift": lift})
        row[f"Top{int(frac * 100)}_hit_rate"] = hit
        row[f"Top{int(frac * 100)}_lift"] = lift
    return row, top_rows, y, p.astype("float32")


def predict_with_fit(fit: FitResult, df: pd.DataFrame, period: str) -> np.ndarray:
    model = fit.train_model if period == "validation" else fit.trainval_model
    if model is None:
        return np.full(len(df), np.nan, dtype="float32")
    x = df[fit.feature_cols].replace([np.inf, -np.inf], np.nan).astype("float32")
    return model.predict_proba(x)[:, 1].astype("float32")


def evaluate_models(
    eval_samples: dict[tuple[str, int, str], pd.DataFrame],
    fit_results: list[FitResult],
    naive: dict[tuple[str, int], NaiveScorer],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[tuple[int, str, str], dict[str, np.ndarray]]]:
    metric_rows: list[dict[str, Any]] = []
    top_rows: list[dict[str, Any]] = []
    onset_test_cache: dict[tuple[int, str, str], dict[str, np.ndarray]] = {}
    fits = [f for f in fit_results if f.status == "OK"]
    groups = ["P", "M", "C", "ALL"]
    for (task, horizon, period), df in eval_samples.items():
        target = TASKS[task].format(h=horizon)
        if df.empty:
            continue
        for group in groups:
            p = naive[(task, horizon)].predict(df["LSI_5_rollmax_20"] if "LSI_5_rollmax_20" in df else df["LSI_5"])
            metrics, tops, y_arr, p_arr = evaluate_arrays(df[target], p)
            row = {
                "task": task,
                "horizon": f"H{horizon}",
                "period": period,
                "feature_group": group,
                "model": "Naive",
                "status": "OK",
                **metrics,
            }
            metric_rows.append(row)
            for top in tops:
                top_rows.append({**{k: row[k] for k in ["task", "horizon", "period", "feature_group", "model"]}, **top})
            if task == "onset" and period == "test" and group == "P":
                onset_test_cache[(horizon, "P", "Naive")] = {
                    "y": y_arr.astype("int8"),
                    "p": p_arr,
                    "date": pd.to_datetime(df.loc[df[target].notna(), "date"], errors="coerce").to_numpy(),
                }
        for fit in [x for x in fits if x.task == task and x.horizon == horizon]:
            p = predict_with_fit(fit, df, period)
            metrics, tops, y_arr, p_arr = evaluate_arrays(df[target], p)
            row = {
                "task": task,
                "horizon": f"H{horizon}",
                "period": period,
                "feature_group": fit.feature_group,
                "model": fit.model,
                "status": fit.status,
                **metrics,
            }
            metric_rows.append(row)
            for top in tops:
                top_rows.append({**{k: row[k] for k in ["task", "horizon", "period", "feature_group", "model"]}, **top})
            if task == "onset" and period == "test":
                onset_test_cache[(horizon, fit.feature_group, fit.model)] = {
                    "y": y_arr.astype("int8"),
                    "p": p_arr,
                    "date": pd.to_datetime(df.loc[df[target].notna(), "date"], errors="coerce").to_numpy(),
                }
    metrics_df = pd.DataFrame(metric_rows)
    top_df = pd.DataFrame(top_rows)
    return add_deltas(metrics_df), top_df, onset_test_cache


def _append_prediction_store(
    store: dict[tuple[str, int, str, str, str], dict[str, list[np.ndarray]]],
    key: tuple[str, int, str, str, str],
    y: pd.Series,
    p: np.ndarray,
    dates: pd.Series | None = None,
) -> None:
    bucket = store.setdefault(key, {"y": [], "p": [], "date": []})
    bucket["y"].append(pd.to_numeric(y, errors="coerce").to_numpy(dtype="float32"))
    bucket["p"].append(np.asarray(p, dtype="float32"))
    if dates is not None:
        bucket["date"].append(pd.to_datetime(dates, errors="coerce").to_numpy())


def evaluate_models_streaming(
    manifest: pd.DataFrame,
    split: dict[str, str],
    cross_context: pd.DataFrame,
    main_thresholds: dict[int, float],
    config: dict[str, Any],
    fit_results: list[FitResult],
    naive: dict[tuple[str, int], NaiveScorer],
    output_dir: Path,
    log: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[tuple[int, str, str], dict[str, np.ndarray]]]:
    stores: dict[tuple[str, int, str, str, str], dict[str, list[np.ndarray]]] = {}
    fits = [f for f in fit_results if f.status == "OK"]
    groups = ["P", "M", "C", "ALL"]
    stock_manifest = manifest.loc[~manifest["is_index"]].copy()
    for idx, row in stock_manifest.reset_index(drop=True).iterrows():
        df = prepare_shard(row, split, cross_context, main_thresholds, config["main_label"])
        for task, template in TASKS.items():
            for horizon in HORIZONS:
                target = template.format(h=horizon)
                valid_base = df.loc[df[target].notna() & ~df[f"embargo_H{horizon}"]].copy()
                if valid_base.empty:
                    continue
                for period in ["validation", "test"]:
                    valid = valid_base.loc[valid_base["period"].eq(period)].copy()
                    if valid.empty:
                        continue
                    naive_score_col = "LSI_5_rollmax_20" if "LSI_5_rollmax_20" in valid else "LSI_5"
                    p_naive = naive[(task, horizon)].predict(valid[naive_score_col])
                    for group in groups:
                        _append_prediction_store(
                            stores,
                            (task, horizon, period, group, "Naive"),
                            valid[target],
                            p_naive,
                            valid["date"] if task == "onset" and period == "test" and group == "P" else None,
                        )
                    for fit in [x for x in fits if x.task == task and x.horizon == horizon]:
                        p = predict_with_fit(fit, valid, period)
                        _append_prediction_store(
                            stores,
                            (task, horizon, period, fit.feature_group, fit.model),
                            valid[target],
                            p,
                            valid["date"] if task == "onset" and period == "test" else None,
                        )
        if (idx + 1) % 10 == 0:
            log.append(f"Stream-evaluated full sample shard {idx + 1}/{len(stock_manifest)}")
            flush_log(output_dir, log)

    metric_rows: list[dict[str, Any]] = []
    top_rows: list[dict[str, Any]] = []
    onset_test_cache: dict[tuple[int, str, str], dict[str, np.ndarray]] = {}
    for (task, horizon, period, group, model), bucket in stores.items():
        y_raw = pd.Series(np.concatenate(bucket["y"]) if bucket["y"] else np.array([], dtype="float32"))
        p = np.concatenate(bucket["p"]) if bucket["p"] else np.array([], dtype="float32")
        metrics, tops, y_arr, p_arr = evaluate_arrays(y_raw, p)
        row = {
            "task": task,
            "horizon": f"H{horizon}",
            "period": period,
            "feature_group": group,
            "model": model,
            "status": "OK",
            **metrics,
        }
        metric_rows.append(row)
        for top in tops:
            top_rows.append({**{k: row[k] for k in ["task", "horizon", "period", "feature_group", "model"]}, **top})
        if task == "onset" and period == "test" and bucket["date"]:
            onset_test_cache[(horizon, group, model)] = {
                "y": y_arr.astype("int8"),
                "p": p_arr,
                "date": np.concatenate(bucket["date"]),
            }

    metrics_df = pd.DataFrame(metric_rows)
    top_df = pd.DataFrame(top_rows)
    return add_deltas(metrics_df), top_df, onset_test_cache


def add_deltas(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return metrics
    out = metrics.copy()
    out["Delta_PR_AUC_vs_persistence"] = np.nan
    out["Delta_Top5_lift_vs_persistence"] = np.nan
    out["Delta_Top10_lift_vs_persistence"] = np.nan
    base = out.loc[(out["model"] == "Naive") & (out["feature_group"] == "P")].copy()
    base = base.set_index(["task", "horizon", "period"])
    for idx, row in out.iterrows():
        key = (row["task"], row["horizon"], row["period"])
        if key not in base.index:
            continue
        b = base.loc[key]
        out.loc[idx, "Delta_PR_AUC_vs_persistence"] = row["PR_AUC"] - b["PR_AUC"]
        out.loc[idx, "Delta_Top5_lift_vs_persistence"] = row.get("Top5_lift", np.nan) - b.get("Top5_lift", np.nan)
        out.loc[idx, "Delta_Top10_lift_vs_persistence"] = row.get("Top10_lift", np.nan) - b.get("Top10_lift", np.nan)
    return out


def select_best_models(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for horizon in ["H5", "H10"]:
        sub = metrics.loc[
            (metrics["task"] == "onset")
            & (metrics["horizon"] == horizon)
            & (metrics["period"] == "validation")
            & (metrics["status"] == "OK")
            & (metrics["model"] != "Naive")
        ].copy()
        sub = sub.sort_values(["PR_AUC", "Top5_lift"], ascending=False)
        if sub.empty:
            continue
        best = sub.iloc[0].to_dict()
        rows.append(best)
    return pd.DataFrame(rows)


def build_feature_group_increment_table(metrics: pd.DataFrame) -> pd.DataFrame:
    sub = metrics.loc[(metrics["task"] == "onset") & (metrics["period"] == "test") & (metrics["status"] == "OK")].copy()
    rows: list[dict[str, Any]] = []
    for (horizon, model), g in sub.groupby(["horizon", "model"], sort=True):
        p_ref = g.loc[g["feature_group"] == "P"]
        if p_ref.empty:
            continue
        p_row = p_ref.iloc[0]
        for _, row in g.sort_values("feature_group").iterrows():
            rows.append(
                {
                    "horizon": horizon,
                    "model": model,
                    "feature_group": row["feature_group"],
                    "event_rate": row["event_rate"],
                    "PR_AUC": row["PR_AUC"],
                    "Top5_hit_rate": row["Top5_hit_rate"],
                    "Top5_lift": row["Top5_lift"],
                    "Brier": row["Brier"],
                    "Delta_PR_AUC_vs_P_same_model": row["PR_AUC"] - p_row["PR_AUC"],
                    "Delta_Top5_lift_vs_P_same_model": row["Top5_lift"] - p_row["Top5_lift"],
                    "Delta_PR_AUC_vs_naive_persistence": row["Delta_PR_AUC_vs_persistence"],
                    "Delta_Top5_lift_vs_naive_persistence": row["Delta_Top5_lift_vs_persistence"],
                }
            )
    return pd.DataFrame(rows)


def save_dual(fig: plt.Figure, path_png: Path, save_pdf: bool) -> None:
    path_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path_png, dpi=300)
    if save_pdf:
        fig.savefig(path_png.with_suffix(".pdf"))
    plt.close(fig)


def plot_pr_curves(cache: dict[tuple[int, str, str], dict[str, np.ndarray]], best: pd.DataFrame, out_dir: Path, save_pdf: bool) -> None:
    c = colors()
    model_colors = {"Naive": c["baseline"], "Logit": c["primary"], "LightGBM": c["positive"], "SMARTBoost": c["negative"]}
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.5), constrained_layout=True)
    for ax, horizon in zip(axes, HORIZONS):
        plotted = set()
        key = (horizon, "P", "Naive")
        if key in cache and len(np.unique(cache[key]["y"])) >= 2:
            prec, rec, _ = precision_recall_curve(cache[key]["y"], cache[key]["p"])
            ax.plot(rec, prec, color=model_colors["Naive"], linestyle=":", linewidth=1.2, label="Naive")
            plotted.add("Naive")
        for model in ["Logit", "LightGBM", "SMARTBoost"]:
            sub = best.loc[(best["horizon"] == f"H{horizon}") & (best["model"] == model)]
            if sub.empty:
                candidates = [k for k in cache if k[0] == horizon and k[2] == model]
                if not candidates:
                    continue
                key = candidates[0]
            else:
                key = (horizon, str(sub.iloc[0]["feature_group"]), model)
            if key in cache and len(np.unique(cache[key]["y"])) >= 2 and model not in plotted:
                prec, rec, _ = precision_recall_curve(cache[key]["y"], cache[key]["p"])
                ax.plot(rec, prec, color=model_colors[model], linewidth=1.4, label=model)
                plotted.add(model)
        ax.set_xlabel(f"Recall (H{horizon})")
        ax.set_ylabel("Precision")
        ax.legend(loc="best", frameon=False)
        despine(ax, grid=True)
    save_dual(fig, out_dir / "fig_pr_curves_onset.png", save_pdf)


def plot_topk_lift(metrics: pd.DataFrame, best: pd.DataFrame, out_dir: Path, save_pdf: bool) -> None:
    c = colors()
    rows = []
    for horizon in ["H5", "H10"]:
        naive = metrics.loc[
            (metrics["task"] == "onset")
            & (metrics["horizon"] == horizon)
            & (metrics["period"] == "test")
            & (metrics["feature_group"] == "P")
            & (metrics["model"] == "Naive")
        ]
        chosen = best.loc[best["horizon"] == horizon]
        if chosen.empty or naive.empty:
            continue
        test_best = metrics.loc[
            (metrics["task"] == "onset")
            & (metrics["horizon"] == horizon)
            & (metrics["period"] == "test")
            & (metrics["feature_group"] == chosen.iloc[0]["feature_group"])
            & (metrics["model"] == chosen.iloc[0]["model"])
        ]
        if test_best.empty:
            continue
        for frac in TOP_FRACS:
            col = f"Top{int(frac * 100)}_lift"
            rows.append({"horizon": horizon, "top": f"Top {int(frac * 100)}%", "series": f"{horizon} Naive", "lift": float(naive.iloc[0][col])})
            rows.append(
                {
                    "horizon": horizon,
                    "top": f"Top {int(frac * 100)}%",
                    "series": f"{horizon} Best",
                    "lift": float(test_best.iloc[0][col]),
                }
            )
    plot = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(7.0, 4.0), constrained_layout=True)
    if not plot.empty:
        x = np.arange(len(TOP_FRACS))
        width = 0.18
        series_order = ["H5 Naive", "H5 Best", "H10 Naive", "H10 Best"]
        palette = [c["baseline"], c["primary"], "#999999", c["negative"]]
        for i, series in enumerate(series_order):
            vals = []
            for frac in TOP_FRACS:
                label = f"Top {int(frac * 100)}%"
                match = plot.loc[(plot["top"] == label) & (plot["series"] == series), "lift"]
                vals.append(float(match.iloc[0]) if not match.empty else np.nan)
            ax.bar(x + (i - 1.5) * width, vals, width=width, color=palette[i], label=series, edgecolor="white", linewidth=0.4)
        ax.set_xticks(x)
        ax.set_xticklabels([f"Top {int(frac * 100)}%" for frac in TOP_FRACS])
    ax.set_ylabel("Lift")
    ax.legend(loc="best", frameon=False)
    despine(ax, grid=False)
    save_dual(fig, out_dir / "fig_topk_lift_onset.png", save_pdf)


def feature_category(feature: str) -> str:
    if feature.startswith("xsec_"):
        return "cross"
    if feature.startswith("Market") or feature.startswith("Index"):
        return "market"
    if feature.startswith("LSI_5"):
        return "persistence"
    if feature in COMPONENT_FEATURES or feature in Z_COMPONENT_FEATURES or feature.startswith("LSI_10") or feature.startswith("LSI_20"):
        return "component"
    return "other"


def plot_feature_importance(
    fit_results: list[FitResult],
    metrics: pd.DataFrame,
    out_dir: Path,
    save_pdf: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    lightgbm_metrics = metrics.loc[
        (metrics["task"] == "onset")
        & (metrics["period"] == "validation")
        & (metrics["model"] == "LightGBM")
        & (metrics["status"] == "OK")
    ].sort_values("PR_AUC", ascending=False)
    importance = pd.DataFrame()
    group_contrib = pd.DataFrame()
    if not lightgbm_metrics.empty:
        chosen = lightgbm_metrics.iloc[0]
        fit = next(
            (
                f
                for f in fit_results
                if f.task == "onset"
                and f.horizon == int(str(chosen["horizon"]).replace("H", ""))
                and f.feature_group == chosen["feature_group"]
                and f.model == "LightGBM"
                and f.status == "OK"
            ),
            None,
        )
        if fit is not None and fit.trainval_model is not None:
            feature_names = list(fit.feature_cols)
            imputer = fit.trainval_model.named_steps.get("imputer")
            if imputer is not None and hasattr(imputer, "statistics_"):
                stats = np.asarray(imputer.statistics_, dtype="float64")
                if len(stats) == len(feature_names):
                    feature_names = [name for name, keep in zip(feature_names, np.isfinite(stats)) if keep]
            estimator = fit.trainval_model.named_steps["model"]
            values = np.asarray(getattr(estimator, "feature_importances_", np.zeros(len(feature_names))), dtype="float64")
            if len(values) != len(feature_names):
                n = min(len(values), len(feature_names))
                feature_names = feature_names[:n]
                values = values[:n]
            importance = pd.DataFrame({"feature": feature_names, "importance": values})
            importance["category"] = importance["feature"].map(feature_category)
            total = importance["importance"].sum()
            if total > 0:
                importance["share"] = importance["importance"] / total
            else:
                importance["share"] = 0.0
            group_contrib = importance.groupby("category", as_index=False)["share"].sum().sort_values("share", ascending=False)
    fig, ax = plt.subplots(figsize=(7.0, 5.0), constrained_layout=True)
    if not importance.empty:
        plot = importance.sort_values("importance", ascending=False).head(20).sort_values("importance", ascending=True)
        cat_colors = {
            "persistence": colors()["baseline"],
            "market": colors()["primary"],
            "cross": colors()["negative"],
            "component": colors()["positive"],
            "other": colors()["third"],
        }
        ax.barh(
            plot["feature"],
            plot["importance"],
            color=[cat_colors.get(x, colors()["third"]) for x in plot["category"]],
            edgecolor="white",
            linewidth=0.4,
        )
        handles = [
            plt.Line2D([0], [0], color=color, lw=4, label=label)
            for label, color in [
                ("Persistence", cat_colors["persistence"]),
                ("Market", cat_colors["market"]),
                ("Cross-section", cat_colors["cross"]),
                ("Components", cat_colors["component"]),
                ("Other", cat_colors["other"]),
            ]
        ]
        ax.legend(handles=handles, loc="best", frameon=False)
    ax.set_xlabel("Importance")
    ax.set_ylabel("")
    despine(ax, grid=True)
    save_dual(fig, out_dir / "fig_feature_importance_onset.png", save_pdf)
    return importance, group_contrib


def bootstrap_ci_for_delta(
    cache: dict[tuple[int, str, str], dict[str, np.ndarray]],
    metrics: pd.DataFrame,
    best: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    rng = np.random.default_rng(int(config["seed"]))
    n_boot = int(config["bootstrap"]["iterations"])
    alpha = 1.0 - float(config["bootstrap"]["confidence_level"])
    max_rows = int(config["bootstrap"]["max_rows"])
    rows = []

    def sample_down(y: np.ndarray, p1: np.ndarray, p0: np.ndarray, dates: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        if len(y) <= max_rows:
            return y, p1, p0, dates
        idx = np.linspace(0, len(y) - 1, max_rows).astype(int)
        return y[idx], p1[idx], p0[idx], dates[idx]

    def metric_delta(y: np.ndarray, p1: np.ndarray, p0: np.ndarray, metric: str) -> float:
        if len(np.unique(y)) < 2:
            return np.nan
        if metric == "PR_AUC":
            return float(average_precision_score(y, p1) - average_precision_score(y, p0))
        if metric == "Top5_lift":
            return float(top_metrics(y, p1, 0.05)[1] - top_metrics(y, p0, 0.05)[1])
        return np.nan

    for horizon in HORIZONS:
        chosen = best.loc[best["horizon"] == f"H{horizon}"]
        if chosen.empty:
            continue
        key_best = (horizon, str(chosen.iloc[0]["feature_group"]), str(chosen.iloc[0]["model"]))
        key_naive = (horizon, "P", "Naive")
        if key_best not in cache or key_naive not in cache:
            continue
        y, p_best, p_naive, dates = sample_down(cache[key_best]["y"], cache[key_best]["p"], cache[key_naive]["p"], cache[key_best]["date"])
        valid_dates = pd.Series(pd.to_datetime(dates, errors="coerce")).dt.date.astype(str).to_numpy()
        unique_dates = np.array(sorted(pd.unique(valid_dates)))
        date_to_idx = {d: np.flatnonzero(valid_dates == d) for d in unique_dates}
        for metric in ["PR_AUC", "Top5_lift"]:
            observed = metric_delta(y, p_best, p_naive, metric)
            draws = []
            for _ in range(n_boot):
                picked = rng.choice(unique_dates, size=len(unique_dates), replace=True)
                idx = np.concatenate([date_to_idx[d] for d in picked])
                draws.append(metric_delta(y[idx], p_best[idx], p_naive[idx], metric))
            arr = np.asarray(draws, dtype="float64")
            rows.append(
                {
                    "comparison": f"H{horizon} best_vs_naive",
                    "metric": metric,
                    "observed_delta": observed,
                    "ci_low": float(np.nanquantile(arr, alpha / 2.0)),
                    "ci_high": float(np.nanquantile(arr, 1.0 - alpha / 2.0)),
                    "bootstrap_iterations": n_boot,
                    "rows_used": int(len(y)),
                }
            )

        model = str(chosen.iloc[0]["model"])
        key_p = (horizon, "P", model)
        for group in ["M", "C", "ALL"]:
            key_group = (horizon, group, model)
            if key_group not in cache or key_p not in cache:
                continue
            y2, p_group, p_p, dates2 = sample_down(cache[key_group]["y"], cache[key_group]["p"], cache[key_p]["p"], cache[key_group]["date"])
            valid_dates2 = pd.Series(pd.to_datetime(dates2, errors="coerce")).dt.date.astype(str).to_numpy()
            unique_dates2 = np.array(sorted(pd.unique(valid_dates2)))
            date_to_idx2 = {d: np.flatnonzero(valid_dates2 == d) for d in unique_dates2}
            for metric in ["PR_AUC", "Top5_lift"]:
                observed = metric_delta(y2, p_group, p_p, metric)
                draws = []
                for _ in range(n_boot):
                    picked = rng.choice(unique_dates2, size=len(unique_dates2), replace=True)
                    idx = np.concatenate([date_to_idx2[d] for d in picked])
                    draws.append(metric_delta(y2[idx], p_group[idx], p_p[idx], metric))
                arr = np.asarray(draws, dtype="float64")
                rows.append(
                    {
                        "comparison": f"H{horizon} {group}_vs_P_same_model",
                        "metric": metric,
                        "observed_delta": observed,
                        "ci_low": float(np.nanquantile(arr, alpha / 2.0)),
                        "ci_high": float(np.nanquantile(arr, 1.0 - alpha / 2.0)),
                        "bootstrap_iterations": n_boot,
                        "rows_used": int(len(y2)),
                    }
                )
    return pd.DataFrame(rows)


def collect_event_predictions(
    manifest: pd.DataFrame,
    split: dict[str, str],
    cross_context: pd.DataFrame,
    main_thresholds: dict[int, float],
    config: dict[str, Any],
    best: pd.DataFrame,
    fit_results: list[FitResult],
    naive: dict[tuple[str, int], NaiveScorer],
    log: list[str],
) -> pd.DataFrame:
    if not config["sampling"].get("event_eval_full_test", True):
        return pd.DataFrame()
    rows = []
    fit_lookup = {(f.horizon, f.feature_group, f.model): f for f in fit_results if f.task == "onset" and f.status == "OK"}
    stock_manifest = manifest.loc[~manifest["is_index"]].copy()
    for idx, row in stock_manifest.reset_index(drop=True).iterrows():
        df = prepare_shard(row, split, cross_context, main_thresholds, config["main_label"])
        df = df.loc[df["period"].eq("test")].copy()
        for horizon in HORIZONS:
            chosen = best.loc[best["horizon"] == f"H{horizon}"]
            if chosen.empty:
                continue
            fit = fit_lookup.get((horizon, str(chosen.iloc[0]["feature_group"]), str(chosen.iloc[0]["model"])))
            if fit is None:
                continue
            target = f"Y_onset_H{horizon}"
            valid = df.loc[df[target].notna() & ~df[f"embargo_H{horizon}"]].copy()
            if valid.empty:
                continue
            valid["score_best"] = predict_with_fit(fit, valid, "test")
            valid["score_naive"] = naive[("onset", horizon)].predict(valid["LSI_5_rollmax_20"] if "LSI_5_rollmax_20" in valid else valid["LSI_5"])
            valid["horizon"] = f"H{horizon}"
            rows.append(valid[["code", "datetime", "date", "horizon", target, "score_best", "score_naive"]].rename(columns={target: "y"}))
        if (idx + 1) % 20 == 0:
            log.append(f"Scored full-test event predictions {idx + 1}/{len(stock_manifest)}")
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def collect_sample_event_predictions(
    eval_samples: dict[tuple[str, int, str], pd.DataFrame],
    best: pd.DataFrame,
    fit_results: list[FitResult],
    naive: dict[tuple[str, int], NaiveScorer],
) -> pd.DataFrame:
    rows = []
    fit_lookup = {(f.horizon, f.feature_group, f.model): f for f in fit_results if f.task == "onset" and f.status == "OK"}
    for horizon in HORIZONS:
        chosen = best.loc[best["horizon"] == f"H{horizon}"]
        if chosen.empty:
            continue
        fit = fit_lookup.get((horizon, str(chosen.iloc[0]["feature_group"]), str(chosen.iloc[0]["model"])))
        if fit is None:
            continue
        df = eval_samples.get(("onset", horizon, "test"), pd.DataFrame()).copy()
        target = f"Y_onset_H{horizon}"
        if df.empty or target not in df:
            continue
        valid = df.loc[df[target].notna()].copy()
        valid["score_best"] = predict_with_fit(fit, valid, "test")
        valid["score_naive"] = naive[("onset", horizon)].predict(valid["LSI_5_rollmax_20"] if "LSI_5_rollmax_20" in valid else valid["LSI_5"])
        valid["horizon"] = f"H{horizon}"
        rows.append(valid[["code", "datetime", "date", "horizon", target, "score_best", "score_naive"]].rename(columns={target: "y"}))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def event_level_metrics(event_pred: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    if event_pred.empty:
        return pd.DataFrame()
    rows = []
    windows = {"H5": (5, 20), "H10": (10, 30)}
    for horizon, g_h in event_pred.groupby("horizon", sort=True):
        h_int = int(horizon.replace("H", ""))
        max_gap_minutes = h_int + int(config["main_label"]["gap"])
        low, high = windows[horizon]
        threshold = float(g_h["score_best"].quantile(0.95))
        signal = g_h.loc[g_h["score_best"] >= threshold, ["code", "datetime", "date", "score_best"]].copy()
        events = []
        for code, g in g_h.loc[g_h["y"] >= 0.5].sort_values(["code", "datetime"]).groupby("code", sort=False):
            prev_time = None
            for dt in pd.to_datetime(g["datetime"], errors="coerce"):
                if prev_time is None or (dt - prev_time).total_seconds() / 60.0 > max_gap_minutes:
                    events.append({"code": code, "start": dt})
                prev_time = dt
        if not events:
            rows.append({"horizon": horizon, "events": 0})
            continue
        event_df = pd.DataFrame(events)
        hit_count = 0
        lead_minutes = []
        matched_signal_idx = set()
        for ev in event_df.itertuples(index=False):
            sig = signal.loc[
                (signal["code"] == ev.code)
                & (pd.to_datetime(signal["datetime"]) >= ev.start - pd.Timedelta(minutes=high))
                & (pd.to_datetime(signal["datetime"]) <= ev.start - pd.Timedelta(minutes=low))
            ]
            if not sig.empty:
                hit_count += 1
                lead = (ev.start - pd.to_datetime(sig["datetime"]).min()).total_seconds() / 60.0
                lead_minutes.append(float(lead))
                matched_signal_idx.update(sig.index.tolist())
        signal_dates = pd.to_datetime(signal["date"], errors="coerce").dt.date
        n_days = max(int(signal_dates.nunique()), 1)
        false_signals = max(int(len(signal) - len(matched_signal_idx)), 0)
        rows.append(
            {
                "horizon": horizon,
                "events": int(len(event_df)),
                "event_recall": float(hit_count / len(event_df)),
                "mean_lead_minutes": float(np.mean(lead_minutes)) if lead_minutes else np.nan,
                "daily_false_alarms": float(false_signals / n_days),
                "top5_signal_event_coverage": float(hit_count / len(event_df)),
                "score_threshold_top5": threshold,
            }
        )
    return pd.DataFrame(rows)


def format_pct(x: Any) -> str:
    return "NA" if pd.isna(x) else f"{100 * float(x):.2f}%"


def format_num(x: Any) -> str:
    return "NA" if pd.isna(x) else f"{float(x):.4f}"


def _write_reports_legacy_unused(
    metrics: pd.DataFrame,
    topk: pd.DataFrame,
    robustness: pd.DataFrame,
    sample_summary: pd.DataFrame,
    best: pd.DataFrame,
    ci: pd.DataFrame,
    event_metrics: pd.DataFrame,
    importance_group: pd.DataFrame,
    excluded: list[str],
    config: dict[str, Any],
    output_dir: Path,
    log: list[str],
) -> None:
    test_main = metrics.loc[(metrics["task"] == "onset") & (metrics["period"] == "test")].copy()
    selected_lines = []
    decision_flags = []
    for _, row in best.iterrows():
        test_row = test_main.loc[
            (test_main["horizon"] == row["horizon"])
            & (test_main["feature_group"] == row["feature_group"])
            & (test_main["model"] == row["model"])
        ]
        if test_row.empty:
            continue
        tr = test_row.iloc[0]
        selected_lines.append(
            f"- {row['horizon']}：验证集选择 {row['model']} / {row['feature_group']}；测试集 PR-AUC={format_num(tr['PR_AUC'])}，"
            f"Delta PR-AUC={format_num(tr['Delta_PR_AUC_vs_persistence'])}，Top 5% lift={format_num(tr['Top5_lift'])}，"
            f"Delta Top 5% lift={format_num(tr['Delta_Top5_lift_vs_persistence'])}。"
        )
        decision_flags.append(float(tr["Delta_PR_AUC_vs_persistence"]) if pd.notna(tr["Delta_PR_AUC_vs_persistence"]) else np.nan)

    if decision_flags and np.nanmax(decision_flags) > 0:
        core_sentence = "高频状态变量在持续性之外可能存在增量预警含量，但是否足以进入正文需要结合置信区间和事件级覆盖率判断。"
    else:
        core_sentence = "当前预测能力主要来自 LSI 持续性，论文需要降低机器学习贡献表述，并将重点转向压力测度和状态识别。"

    ci_lines = [
        f"- {r.comparison} / {r.metric}: delta={format_num(r.observed_delta)}, 95% CI=[{format_num(r.ci_low)}, {format_num(r.ci_high)}], rows={int(r.rows_used)}"
        for r in ci.itertuples(index=False)
    ] or ["- 未能生成 bootstrap 置信区间。"]

    event_lines = [
        f"- {r.horizon}: events={int(r.events)}, recall={format_pct(r.event_recall)}, mean lead={format_num(r.mean_lead_minutes)} minutes, daily false alarms={format_num(r.daily_false_alarms)}"
        for r in event_metrics.itertuples(index=False)
    ] or ["- 事件级评价未生成。"]
    event_scope = (
        "事件级评价使用完整测试集逐 shard 评分。"
        if config["sampling"].get("event_eval_full_test", True)
        else "事件级评价使用确定性测试样本的简化版；由于采样会破坏部分相邻分钟连续性，事件数量、召回率和误报次数只作为方向性诊断。"
    )

    contrib_lines = [
        f"- {r.category}: {format_pct(r.share)}"
        for r in importance_group.itertuples(index=False)
    ] or ["- 未取得 LightGBM 特征重要性。"]

    sample_lines = [
        f"- {r.task} {r.horizon} {r.sample}: rows={int(r.rows)}, event_rate={format_pct(r.event_rate)}"
        for r in sample_summary.itertuples(index=False)
    ]
    capped = config["sampling"].get("max_stock_codes") not in (None, "null")
    stock_scope_line = (
        f"- stock-code cap: {config['sampling'].get('max_stock_codes')}；本次输出是有界诊断运行，若要作为最终正文证据，应将该值设为 null 并提高 evaluation/bootstrap caps 后重跑。"
        if capped
        else "- stock-code cap: none；本次使用完整股票池。验证集与测试集指标为完整样本评估，训练阶段仍按配置进行确定性分层抽样以控制模型拟合成本。"
    )

    report = "\n".join(
        [
            "# Onset baseline 独立实验报告",
            "",
            "## 1. 实验目的",
            "",
            "本实验检验 SMARTBoost 预警结果是否只是来自 LSI 自身持续性，还是在排除当前压力延续、设置预测空档期并控制 LSI 滞后项后，仍然存在增量预警能力。",
            "",
            "## 2. 为什么原始 Stress_H 可能混入持续性和窗口重叠",
            "",
            "原始 Stress_H 标签基于未来短窗口 LSI 是否超过训练期阈值。由于 LSI_5 是滚动 5 分钟指标，当前 LSI 与未来短窗口 LSI 存在机械重叠；若 t 时点已处于高压力状态，未来继续高压更可能是持续性，而不是提前预警。",
            "",
            "## 3. 新的 onset 标签定义",
            "",
            f"主实验使用 gap={config['main_label']['gap']}、lookback_clean={config['main_label']['lookback_clean']}、threshold_quantile={config['main_label']['threshold_quantile']}。"
            "仅当当前及回看窗口未处于压力状态，且未来 gap 后的预测窗口内出现压力，才记为 onset=1。",
            "",
            "## 4. 样本切分与时间边界",
            "",
            "样本切分沿用项目 stage2 的 time_split.json。训练、验证、测试边界附近按 gap+H 删除观测，避免未来窗口跨越样本区间。",
            "",
            "## 5. 模型与基线设置",
            "",
            "模型包括 Naive persistence ranking、Logit、LightGBM 与项目既有 SMARTBoost Python adaptation。验证集预测使用训练期模型，测试集预测使用训练+验证期模型。连续变量标准化、模型拟合和最终测试均不使用测试标签调参。",
            "",
            "抽样说明：",
            stock_scope_line,
            *sample_lines,
            "",
            "## 6. 主结果：onset task",
            "",
            *(selected_lines or ["- 未能选择有效的 onset 模型。"]),
            "",
            "Bootstrap 关键差异：",
            *ci_lines,
            "",
            "事件级评价：",
            "",
            event_scope,
            *event_lines,
            "",
            "## 7. 对照结果：continuation task",
            "",
            "Continuation task 使用原始 Stress_H5 / Stress_H10，仅作为压力持续性预测对照。完整指标见 continuation_metrics.csv。",
            "",
            "## 8. 模型是否显著超过 naive persistence",
            "",
            core_sentence,
            "",
            "## 9. 横截面状态是否带来增量价值",
            "",
            "特征组 C 在 P 与 M 的基础上加入 t 时点横截面压力广度和 LSI 横截面分布。C_vs_P 的 bootstrap 结果见 delta_vs_persistence.csv。LightGBM 特征重要性按类别汇总如下：",
            *contrib_lines,
            "",
            "## 10. 对论文主线的含义",
            "",
            "若 onset task 的增量为正且置信区间支持，可以考虑将其作为压力预警的核心稳健性证据；若增量不稳定或主要来自 P 组持续性特征，应降低机器学习增量贡献表述。",
            "",
            "## 排除变量清单",
            "",
            *(f"- {x}" for x in excluded),
            "",
            "## 稳健性参数网格",
            "",
            "稳健性网格已输出到 robustness_grid_summary.csv；该表报告不同 gap、lookback_clean 和 threshold_quantile 下的 onset 标签样本量与事件率。",
            "",
        ]
    )
    write_text(output_dir / "onset_baseline_report.md", report)

    # Decision note.
    best_test = test_main.loc[test_main["model"] != "Naive"].sort_values("Delta_PR_AUC_vs_persistence", ascending=False)
    best_ci_positive = False
    feature_increment_positive = False
    if not ci.empty:
        best_ci = ci.loc[(ci["comparison"].str.contains("best_vs_naive")) & (ci["metric"] == "PR_AUC")]
        best_ci_positive = bool((best_ci["ci_low"] > 0).any())
        fg_ci = ci.loc[
            (ci["comparison"].str.contains("M_vs_P|C_vs_P", regex=True))
            & (ci["metric"] == "PR_AUC")
        ]
        feature_increment_positive = bool((fg_ci["observed_delta"] > 0).any() and (fg_ci["ci_high"] > 0).any())
    event_ok = bool((event_metrics.get("event_recall", pd.Series(dtype="float64")) >= 0.10).any()) if not event_metrics.empty else False
    top5_positive = bool(not best_test.empty and best_test.iloc[0]["Delta_Top5_lift_vs_persistence"] > 0)
    if (
        not capped
        and not best_test.empty
        and best_test.iloc[0]["Delta_PR_AUC_vs_persistence"] > 0
        and top5_positive
        and best_ci_positive
        and feature_increment_positive
        and event_ok
    ):
        decision = "A. 强烈建议加入正文"
        reason = "onset task 相对 Naive persistence 存在正向增量，特征组增量和事件级覆盖率均满足正文纳入标准。"
    elif not best_test.empty and best_test.iloc[0]["PR_AUC"] > best_test.iloc[0]["event_rate"]:
        decision = "B. 建议作为稳健性或局限性加入"
        reason = "onset task 有一定预测能力，但特征组增量、bootstrap 区间或事件级证据未同时满足正文纳入标准。"
    else:
        decision = "C. 暂不加入正文"
        reason = "onset task 未显示稳定的增量预警能力，或样本/事件级结果不足以支撑正文主结论。"
    note = "\n".join(
        [
            "# Inclusion decision note",
            "",
            f"判定：{decision}",
            "",
            f"理由：{reason}",
            "",
            "判定依据：",
            *(selected_lines or ["- 无有效模型结果。"]),
            "",
            "置信区间摘要：",
            *ci_lines,
            "",
            "事件级摘要：",
            *event_lines,
            "",
        ]
    )
    write_text(output_dir / "inclusion_decision_note.md", note)
    log.append("Wrote onset_baseline_report.md and inclusion_decision_note.md")


def _write_reports_clean_legacy_unused(
    metrics: pd.DataFrame,
    topk: pd.DataFrame,
    robustness: pd.DataFrame,
    sample_summary: pd.DataFrame,
    best: pd.DataFrame,
    ci: pd.DataFrame,
    event_metrics: pd.DataFrame,
    importance_group: pd.DataFrame,
    excluded: list[str],
    config: dict[str, Any],
    output_dir: Path,
    log: list[str],
) -> None:
    del topk
    test_main = metrics.loc[(metrics["task"] == "onset") & (metrics["period"] == "test")].copy()
    selected_lines: list[str] = []
    decision_flags: list[float] = []
    for _, row in best.iterrows():
        test_row = test_main.loc[
            (test_main["horizon"] == row["horizon"])
            & (test_main["feature_group"] == row["feature_group"])
            & (test_main["model"] == row["model"])
        ]
        if test_row.empty:
            continue
        tr = test_row.iloc[0]
        selected_lines.append(
            f"- {row['horizon']}: validation selected {row['model']} / {row['feature_group']}; "
            f"test PR-AUC={format_num(tr['PR_AUC'])}, "
            f"Delta PR-AUC vs naive={format_num(tr['Delta_PR_AUC_vs_persistence'])}, "
            f"Top5 lift={format_num(tr['Top5_lift'])}, "
            f"Delta Top5 lift vs naive={format_num(tr['Delta_Top5_lift_vs_persistence'])}."
        )
        decision_flags.append(
            float(tr["Delta_PR_AUC_vs_persistence"]) if pd.notna(tr["Delta_PR_AUC_vs_persistence"]) else np.nan
        )

    if decision_flags and np.nanmax(decision_flags) > 0:
        core_sentence = (
            "onset task 在 naive persistence 之外存在正向增量信号；是否进入正文，取决于日度 "
            "bootstrap 置信区间、P/M/C/ALL 特征组增量和事件级召回是否同时支持。"
        )
    else:
        core_sentence = (
            "当前预测能力主要来自 LSI 持续性；论文应降低机器学习增量贡献表述，重点转向压力测度和状态识别。"
        )

    ci_lines = [
        f"- {r.comparison} / {r.metric}: delta={format_num(r.observed_delta)}, "
        f"95% CI=[{format_num(r.ci_low)}, {format_num(r.ci_high)}], rows={int(r.rows_used)}"
        for r in ci.itertuples(index=False)
    ] or ["- 未能生成 bootstrap 置信区间。"]

    event_lines = [
        f"- {r.horizon}: events={int(r.events)}, recall={format_pct(r.event_recall)}, "
        f"mean lead={format_num(r.mean_lead_minutes)} minutes, "
        f"daily false alarms={format_num(r.daily_false_alarms)}"
        for r in event_metrics.itertuples(index=False)
    ] or ["- 事件级评价未生成。"]
    event_scope = (
        "事件级评价使用完整测试集逐 shard 评分。"
        if config["sampling"].get("event_eval_full_test", True)
        else "事件级评价使用确定性测试样本的简化版本；事件数量、召回率和误报次数仅作方向性诊断。"
    )

    contrib_lines = [
        f"- {r.category}: {format_pct(r.share)}"
        for r in importance_group.itertuples(index=False)
    ] or ["- 未取得 LightGBM 特征重要性。"]

    sample_lines = [
        f"- {r.task} {r.horizon} {r.sample}: rows={int(r.rows)}, event_rate={format_pct(r.event_rate)}"
        for r in sample_summary.itertuples(index=False)
    ]
    capped = config["sampling"].get("max_stock_codes") not in (None, "null")
    stock_scope_line = (
        f"- stock-code cap: {config['sampling'].get('max_stock_codes')}; 本次输出是有界诊断运行，不能作为最终正文证据。"
        if capped
        else "- stock-code cap: none; 本次使用完整股票池。验证集和测试集指标为完整样本评价，训练阶段按配置做确定性分层抽样以控制拟合成本。"
    )

    main_robust = pd.DataFrame()
    if not robustness.empty:
        main_robust = robustness.loc[
            (robustness["gap"] == int(config["main_label"]["gap"]))
            & (robustness["lookback_clean"] == int(config["main_label"]["lookback_clean"]))
            & (np.isclose(robustness["threshold_quantile"], float(config["main_label"]["threshold_quantile"])))
        ].copy()
    robust_lines = [
        f"- {r.horizon} {r.period}: rows={int(r.rows)}, events={format_num(r.events)}, event_rate={format_pct(r.event_rate)}"
        for r in main_robust.itertuples(index=False)
    ] or ["- 主设定稳健性样本摘要未生成。"]

    report = "\n".join(
        [
            "# Onset baseline 独立实验报告",
            "",
            "## 1. 实验目的",
            "",
            "本实验检验 SMARTBoost 预警结果是否只是来自 LSI 自身持续性，还是在排除当前压力延续、设置预测空档期并控制 LSI 滞后项后，仍然存在增量预警能力。",
            "",
            "## 2. 原始 Stress_H 的问题",
            "",
            "原始 Stress_H 标签基于未来短窗口 LSI 是否超过训练期阈值。由于 LSI_5 是滚动 5 分钟指标，当前 LSI 与未来短窗口 LSI 可能存在机械重叠；若 t 时点已经处于高压力状态，未来继续高压更可能是持续性，而不是提前预警。",
            "",
            "## 3. onset 标签主设定",
            "",
            f"主实验使用 gap={config['main_label']['gap']}、lookback_clean={config['main_label']['lookback_clean']}、threshold_quantile={config['main_label']['threshold_quantile']}。仅当当前及回看窗口未处于压力状态，且未来 gap 后的预测窗口内出现压力，才记为 onset=1。",
            "",
            "## 4. 样本切分与边界",
            "",
            "样本切分沿用 stage2 的 time_split.json。训练、验证、测试边界附近按 gap+H 删除观测，避免未来窗口跨越样本区间。",
            "",
            "## 5. 模型与基线",
            "",
            "模型包括 Naive persistence ranking、Logit、LightGBM 与项目既有 SMARTBoost Python adaptation。验证集预测使用训练期模型，测试集预测使用训练+验证期模型；最终测试不使用测试标签调参。",
            "",
            "抽样说明：",
            stock_scope_line,
            *sample_lines,
            "",
            "## 6. 主结果：onset task",
            "",
            *(selected_lines or ["- 未能选择有效的 onset 模型。"]),
            "",
            "完整模型对照表见 model_comparison_summary.csv；P/M/C/ALL 特征组增量表见 feature_group_increment_table.csv。",
            "",
            "Bootstrap 关键差异：",
            *ci_lines,
            "",
            "事件级评价：",
            event_scope,
            *event_lines,
            "",
            "## 7. 对照结果：continuation task",
            "",
            "Continuation task 使用原始 Stress_H5 / Stress_H10，仅作为压力持续性预测对照。完整指标见 continuation_metrics.csv。",
            "",
            "## 8. 是否显著超过 naive persistence",
            "",
            core_sentence,
            "",
            "## 9. 横截面状态的增量价值",
            "",
            "特征组 C 在 P 与 M 的基础上加入 t 时点横截面压力广度和 LSI 横截面分布；相关 bootstrap 结果见 bootstrap_ci.csv。LightGBM 特征重要性按类别汇总如下：",
            *contrib_lines,
            "",
            "## 10. 主设定标签样本摘要",
            "",
            *robust_lines,
            "",
            "## 11. 对论文主线的含义",
            "",
            "若 onset task 的增量为正且日度 bootstrap 置信区间支持，可考虑将其作为压力预警的正文证据；若增量不稳定或主要来自 P 组持续性特征，应作为稳健性或局限性材料，而不是正文主表核心结论。",
            "",
            "## 排除变量清单",
            "",
            *(f"- {x}" for x in excluded),
            "",
            "## 稳健性参数网格",
            "",
            "稳健性网格已输出至 robustness_grid_summary.csv；该表报告不同 gap、lookback_clean 和 threshold_quantile 下的 onset 标签样本量、事件数与事件率。",
            "",
        ]
    )
    write_text(output_dir / "onset_baseline_report.md", report)

    best_test = test_main.loc[test_main["model"] != "Naive"].sort_values("Delta_PR_AUC_vs_persistence", ascending=False)
    best_ci_positive = False
    feature_increment_positive = False
    if not ci.empty:
        best_ci = ci.loc[(ci["comparison"].str.contains("best_vs_naive")) & (ci["metric"] == "PR_AUC")]
        best_ci_positive = bool((best_ci["ci_low"] > 0).any())
        fg_ci = ci.loc[
            (ci["comparison"].str.contains("M_vs_P|C_vs_P", regex=True))
            & (ci["metric"] == "PR_AUC")
        ]
        feature_increment_positive = bool((fg_ci["observed_delta"] > 0).any() and (fg_ci["ci_high"] > 0).any())
    event_ok = (
        bool((event_metrics.get("event_recall", pd.Series(dtype="float64")) >= 0.10).any())
        if not event_metrics.empty
        else False
    )
    top5_positive = bool(not best_test.empty and best_test.iloc[0]["Delta_Top5_lift_vs_persistence"] > 0)

    if (
        not capped
        and not best_test.empty
        and best_test.iloc[0]["Delta_PR_AUC_vs_persistence"] > 0
        and top5_positive
        and best_ci_positive
        and feature_increment_positive
        and event_ok
    ):
        decision = "A. 进入正文"
        recommendation = "建议进入正文主结果或正文稳健性段落。"
        reason = "onset task 相对 naive persistence 存在正向增量，P/M/C/ALL 特征组增量、bootstrap 区间和事件级覆盖率同时满足纳入标准。"
    elif not best_test.empty and best_test.iloc[0]["PR_AUC"] > best_test.iloc[0]["event_rate"]:
        decision = "B. 作为稳健性或局限性加入"
        recommendation = "建议放入稳健性/局限性讨论，不作为正文核心表格的主要证据。"
        reason = "onset task 有一定预测能力，但特征组增量、bootstrap 区间或事件级证据未同时满足正文纳入标准。"
    else:
        decision = "C. 暂不加入"
        recommendation = "建议暂不写入论文正文，最多作为内部诊断保留。"
        reason = "onset task 未显示稳定的增量预警能力，或样本/事件级结果不足以支撑论文主结论。"

    note = "\n".join(
        [
            "# Inclusion decision note",
            "",
            f"最终判断：{decision}",
            "",
            f"处理建议：{recommendation}",
            "",
            f"理由：{reason}",
            "",
            "判定依据：",
            *(selected_lines or ["- 无有效模型结果。"]),
            "",
            "置信区间摘要：",
            *ci_lines,
            "",
            "事件级摘要：",
            *event_lines,
            "",
            "备注：本文件只给出实验纳入判断；本次任务未修改 main.tex、main_v2_final.tex 或任何论文正文文件。",
            "",
        ]
    )
    write_text(output_dir / "inclusion_decision_note.md", note)
    log.append("Wrote clean onset_baseline_report.md and inclusion_decision_note.md")


def write_handoff(output_dir: Path, generated: list[Path], unresolved: list[str]) -> None:
    handoff_dir = PROJECT_ROOT / "agent_workspaces" / "codex_workspace"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    handoff = "\n".join(
        [
            "# Handoff: onset_baseline_check",
            "Date: 2026-06-21",
            "Status: COMPLETE",
            "",
            "## Files read",
            "",
            "- data_intermediate/stage2_lsi_labels/lsi_labels_manifest.csv",
            "- data_intermediate/stage2_lsi_labels/time_split.json",
            "- data_intermediate/stage2_lsi_labels/label_thresholds_train.json",
            "- data_intermediate/stage2_lsi_labels/lsi_labels_by_code/*.parquet",
            "- code/src/models/07_smartboost_forecasting.py",
            "",
            "## Files modified",
            "",
            "- experiments/onset_baseline_check/config_onset_baseline.yaml",
            "- experiments/onset_baseline_check/run_onset_baseline.py",
            "- experiments/onset_baseline_check/README.md",
            "",
            "## Artifacts generated",
            "",
            *(f"- {rel(p)}" for p in generated),
            "",
            "## Unresolved issues",
            "",
            *(f"- {x}" for x in unresolved),
            "",
            "## Next steps",
            "",
            "- Review onset_baseline_report.md and inclusion_decision_note.md before making any separate LaTeX integration pass.",
            "- Do not write these results into the paper automatically; update the manuscript only in a dedicated follow-up task.",
            "",
        ]
    )
    write_text(handoff_dir / "handoff_20260621_onset_baseline_check.md", handoff)


def _run_legacy_unused() -> int:
    config = load_config()
    output_dir = PROJECT_ROOT / config["paths"]["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_style(int(config["figures"]["dpi"]))
    log: list[str] = []
    generated: list[Path] = []
    unresolved: list[str] = []
    try:
        manifest, split, existing_thresholds = load_inputs(config)
        log_line(log, f"Data source={config.get('_data_source')} path={config.get('_data_path_used')} rows={config.get('_data_rows')}")
        manifest = apply_stock_code_cap(manifest, config, log)
        flush_log(output_dir, log)
        robustness_q = [float(x) for x in config["robustness_grid"]["threshold_quantiles"]]
        prefer_existing = bool(config["main_label"].get("prefer_existing_thresholds_for_main", True))
        main_thresholds: dict[int, float] = {}
        for horizon in HORIZONS:
            key = f"H{horizon}"
            if prefer_existing and key in existing_thresholds:
                main_thresholds[horizon] = float(existing_thresholds[key])
            else:
                main_thresholds[horizon] = np.nan
        cross_context, direct_thresholds = build_cross_context(manifest, split, main_thresholds, robustness_q, log)
        flush_log(output_dir, log)
        for horizon in HORIZONS:
            if not np.isfinite(main_thresholds[horizon]):
                main_thresholds[horizon] = direct_thresholds[float(config["main_label"]["threshold_quantile"])]
        log.append(f"Main thresholds: {main_thresholds}")

        train_samples, trainval_samples, eval_samples, robustness, available_cols = collect_datasets(
            manifest, split, cross_context, main_thresholds, direct_thresholds, config, log, output_dir
        )
        flush_log(output_dir, log)
        feature_groups_by_h = {h: build_feature_groups(h, available_cols) for h in HORIZONS}
        ckpt_dir = output_dir.parent / "checkpoints"
        cache_base_parts = [trainval_samples.get(("onset", 5), pd.DataFrame())]
        cache_base_parts.extend(eval_samples.get(("onset", 5, period), pd.DataFrame()) for period in ["validation", "test"])
        cache_base = pd.concat([x for x in cache_base_parts if not x.empty], ignore_index=True) if any(not x.empty for x in cache_base_parts) else pd.DataFrame()
        if not cache_base.empty:
            base_cols = [c for c in ["code", "datetime", "date", "period", "LSI_5", "MarketLSI", "IndexRet", "IndexRV", "MarketRelAmt", "Stress_H5", "Stress_H10"] if c in cache_base]
            processed_panel_cache = ckpt_dir / "processed_panel.parquet"
            cache_base[base_cols].to_parquet(processed_panel_cache, index=False)
            for group in ["P", "M", "C", "ALL"]:
                cols = sorted(set(feature_groups_by_h[5].get(group, []) + feature_groups_by_h[10].get(group, [])))
                keep = [c for c in ["code", "datetime", "date", "period"] if c in cache_base] + [c for c in cols if c in cache_base]
                (ckpt_dir / f"features_{group}.parquet").parent.mkdir(parents=True, exist_ok=True)
                cache_base[keep].to_parquet(ckpt_dir / f"features_{group}.parquet", index=False)
            write_text(
                ckpt_dir / "splits.json",
                json.dumps(
                    {
                        "signature": config.get("cache_signature"),
                        "split": split,
                        "rows_by_period": cache_base["period"].value_counts(dropna=False).to_dict() if "period" in cache_base else {},
                    },
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
                + "\n",
            )
            update_cache_stage(
                output_dir,
                config,
                "feature_matrices_complete",
                [
                    processed_panel_cache,
                    ckpt_dir / "features_P.parquet",
                    ckpt_dir / "features_M.parquet",
                    ckpt_dir / "features_C.parquet",
                    ckpt_dir / "features_ALL.parquet",
                    ckpt_dir / "splits.json",
                ],
            )
        excluded = [
            "Stress_H5",
            "Stress_H10",
            "future_max_LSI_5_H5",
            "future_max_LSI_5_H10",
            "CrossStress",
            "CrossStress_H10",
            "Y_onset_H5",
            "Y_onset_H10",
        ]

        fit_results, naive, sample_summary = train_models(train_samples, trainval_samples, feature_groups_by_h, config, log)
        flush_log(output_dir, log)
        if config["sampling"].get("eval_max_rows_per_task_horizon_period") in (None, "null"):
            metrics, topk, onset_test_cache = evaluate_models_streaming(
                manifest,
                split,
                cross_context,
                main_thresholds,
                config,
                fit_results,
                naive,
                output_dir,
                log,
            )
        else:
            metrics, topk, onset_test_cache = evaluate_models(eval_samples, fit_results, naive)
        flush_log(output_dir, log)
        best = select_best_models(metrics)
        ci = bootstrap_ci_for_delta(onset_test_cache, metrics, best, config)
        if config["sampling"].get("event_eval_full_test", True):
            event_pred = collect_event_predictions(
                manifest, split, cross_context, main_thresholds, config, best, fit_results, naive, log
            )
        else:
            event_pred = collect_sample_event_predictions(eval_samples, best, fit_results, naive)
        event_metrics = event_level_metrics(event_pred, config)

        importance, group_contrib = plot_feature_importance(
            fit_results, metrics, output_dir, bool(config["figures"].get("save_pdf", True))
        )
        plot_pr_curves(onset_test_cache, best, output_dir, bool(config["figures"].get("save_pdf", True)))
        plot_topk_lift(metrics, best, output_dir, bool(config["figures"].get("save_pdf", True)))

        onset_metrics = metrics.loc[metrics["task"] == "onset"].copy()
        continuation_metrics = metrics.loc[metrics["task"] == "continuation"].copy()
        feature_group_increment = build_feature_group_increment_table(metrics)
        summary = onset_metrics.loc[onset_metrics["period"] == "test"].copy()
        summary = summary[
            [
                "horizon",
                "model",
                "feature_group",
                "event_rate",
                "PR_AUC",
                "Top5_hit_rate",
                "Top5_lift",
                "Delta_PR_AUC_vs_persistence",
                "Delta_Top5_lift_vs_persistence",
                "Brier",
                "status",
            ]
        ]
        delta = metrics[
            [
                "task",
                "horizon",
                "period",
                "feature_group",
                "model",
                "Delta_PR_AUC_vs_persistence",
                "Delta_Top5_lift_vs_persistence",
                "Delta_Top10_lift_vs_persistence",
            ]
        ].copy()
        if not ci.empty:
            ci_path = output_dir / "bootstrap_ci.csv"
            ci.to_csv(ci_path, index=False, encoding="utf-8-sig", float_format="%.6f")
            generated.append(ci_path)
        for name, df in [
            ("onset_metrics.csv", onset_metrics),
            ("continuation_metrics.csv", continuation_metrics),
            ("model_comparison_summary.csv", summary),
            ("topk_lift_table.csv", topk),
            ("delta_vs_persistence.csv", pd.concat([delta, ci.assign(task="onset")], ignore_index=True, sort=False) if not ci.empty else delta),
            ("feature_group_increment_table.csv", feature_group_increment),
            ("robustness_grid_summary.csv", robustness),
            ("training_sample_summary.csv", sample_summary),
            ("selected_best_models.csv", best),
            ("event_level_metrics.csv", event_metrics),
            ("feature_importance_onset.csv", importance),
            ("feature_group_contribution_onset.csv", group_contrib),
        ]:
            path = output_dir / name
            df.to_csv(path, index=False, encoding="utf-8-sig", float_format="%.6f")
            generated.append(path)

        generated.extend(
            [
                output_dir / "fig_pr_curves_onset.png",
                output_dir / "fig_topk_lift_onset.png",
                output_dir / "fig_feature_importance_onset.png",
            ]
        )
        if config["figures"].get("save_pdf", True):
            generated.extend(
                [
                    output_dir / "fig_pr_curves_onset.pdf",
                    output_dir / "fig_topk_lift_onset.pdf",
                    output_dir / "fig_feature_importance_onset.pdf",
                ]
            )

        write_reports(
            metrics,
            topk,
            robustness,
            sample_summary,
            best,
            ci,
            event_metrics,
            group_contrib,
            excluded,
            config,
            output_dir,
            log,
        )
        generated.extend([output_dir / "onset_baseline_report.md", output_dir / "inclusion_decision_note.md"])
        write_text(output_dir / "run_log.txt", "\n".join(log) + "\n")
        generated.append(output_dir / "run_log.txt")
        write_handoff(output_dir, generated, unresolved or ["none"])
        print("Onset baseline experiment completed. Outputs:")
        for path in generated:
            print(rel(path))
        return 0
    except Exception as exc:
        unresolved.append(str(exc))
        log.append("FATAL: " + str(exc))
        log.append(traceback.format_exc())
        write_text(output_dir / "run_log.txt", "\n".join(log) + "\n")
        write_text(
            output_dir / "onset_baseline_report.md",
            "# Onset baseline 独立实验报告\n\n状态：BLOCKED\n\n"
            f"错误：{exc}\n\n请查看 run_log.txt，并确认必要数据字段与依赖包是否存在。\n",
        )
        write_text(
            output_dir / "inclusion_decision_note.md",
            "# Inclusion decision note\n\n判定：C. 暂不加入正文\n\n理由：实验未成功完成。\n",
        )
        write_text(
            output_dir / "onset_baseline_report.md",
            "# Onset baseline 独立实验报告\n\n状态：BLOCKED\n\n"
            f"错误：{exc}\n\n请查看 run_log.txt，并确认必要数据字段与依赖包是否存在。\n",
        )
        write_text(
            output_dir / "inclusion_decision_note.md",
            "# Inclusion decision note\n\n最终判断：C. 暂不加入\n\n理由：实验未成功完成。\n",
        )
        write_handoff(output_dir, [output_dir / "run_log.txt", output_dir / "onset_baseline_report.md"], unresolved)
        print(f"Onset baseline experiment failed: {exc}", file=sys.stderr)
        return 1


def write_reports(
    metrics: pd.DataFrame,
    topk: pd.DataFrame,
    robustness: pd.DataFrame,
    sample_summary: pd.DataFrame,
    best: pd.DataFrame,
    ci: pd.DataFrame,
    event_metrics: pd.DataFrame,
    importance_group: pd.DataFrame,
    excluded: list[str],
    config: dict[str, Any],
    output_dir: Path,
    log: list[str],
) -> None:
    del topk
    test_main = metrics.loc[(metrics["task"] == "onset") & (metrics["period"] == "test")].copy()
    selected_lines: list[str] = []
    for _, row in best.iterrows():
        test_row = test_main.loc[
            (test_main["horizon"] == row["horizon"])
            & (test_main["feature_group"] == row["feature_group"])
            & (test_main["model"] == row["model"])
        ]
        if test_row.empty:
            continue
        tr = test_row.iloc[0]
        selected_lines.append(
            f"- {row['horizon']}: validation selected {row['model']} / {row['feature_group']}; "
            f"test PR-AUC={format_num(tr['PR_AUC'])}; "
            f"Delta PR-AUC vs naive={format_num(tr['Delta_PR_AUC_vs_persistence'])}; "
            f"Top5 lift={format_num(tr['Top5_lift'])}; "
            f"Delta Top5 lift vs naive={format_num(tr['Delta_Top5_lift_vs_persistence'])}."
        )

    ci_lines = [
        f"- {r.comparison} / {r.metric}: delta={format_num(r.observed_delta)}, "
        f"95% CI=[{format_num(r.ci_low)}, {format_num(r.ci_high)}], rows={int(r.rows_used)}"
        for r in ci.itertuples(index=False)
    ] or ["- Bootstrap CI was not generated."]

    event_lines = [
        f"- {r.horizon}: events={int(r.events)}, recall={format_pct(r.event_recall)}, "
        f"mean lead={format_num(r.mean_lead_minutes)} minutes, daily false alarms={format_num(r.daily_false_alarms)}"
        for r in event_metrics.itertuples(index=False)
    ] or ["- Event-level evaluation was not generated."]

    sample_lines = [
        f"- {r.task} {r.horizon} {r.sample}: rows={int(r.rows)}, event_rate={format_pct(r.event_rate)}"
        for r in sample_summary.itertuples(index=False)
    ]

    contrib_lines = [
        f"- {r.category}: {format_pct(r.share)}"
        for r in importance_group.itertuples(index=False)
    ] or ["- LightGBM feature importance was not available."]

    capped = config["sampling"].get("max_stock_codes") not in (None, "null")
    best_test = test_main.loc[test_main["model"] != "Naive"].sort_values("Delta_PR_AUC_vs_persistence", ascending=False)
    best_ci_positive = False
    feature_increment_positive = False
    if not ci.empty:
        best_ci = ci.loc[(ci["comparison"].str.contains("best_vs_naive")) & (ci["metric"] == "PR_AUC")]
        best_ci_positive = bool((best_ci["ci_low"] > 0).any())
        fg_ci = ci.loc[(ci["comparison"].str.contains("M_vs_P|C_vs_P", regex=True)) & (ci["metric"] == "PR_AUC")]
        feature_increment_positive = bool((fg_ci["observed_delta"] > 0).any() and (fg_ci["ci_high"] > 0).any())
    event_ok = (
        bool((event_metrics.get("event_recall", pd.Series(dtype="float64")) >= 0.10).any())
        if not event_metrics.empty
        else False
    )
    top5_positive = bool(not best_test.empty and best_test.iloc[0]["Delta_Top5_lift_vs_persistence"] > 0)
    if (
        not capped
        and not best_test.empty
        and best_test.iloc[0]["Delta_PR_AUC_vs_persistence"] > 0
        and top5_positive
        and best_ci_positive
        and feature_increment_positive
        and event_ok
    ):
        decision = "A. Include in main text"
        reason = "Full-sample onset results pass the positive-delta, bootstrap, feature-increment, and event-recall gates."
    elif not best_test.empty and best_test.iloc[0]["PR_AUC"] > best_test.iloc[0]["event_rate"]:
        decision = "B. Use as robustness or limitation"
        reason = "The onset task has predictive content, but the full set of main-text gates is not satisfied."
    else:
        decision = "C. Do not include yet"
        reason = "The onset task does not provide stable enough incremental warning evidence."

    report = "\n".join(
        [
            "# Onset baseline independent experiment report",
            "",
            "## Purpose",
            "",
            "This experiment checks whether short-horizon warning performance is incremental to naive LSI persistence after using an onset label with a clean lookback window and a prediction gap.",
            "",
            "## Run Settings",
            "",
            f"- mode: {config.get('run_mode')}",
            f"- gap: {config['main_label']['gap']}",
            f"- lookback_clean: {config['main_label']['lookback_clean']}",
            f"- threshold_quantile: {config['main_label']['threshold_quantile']}",
            f"- max_stock_codes: {config['sampling'].get('max_stock_codes')}",
            f"- bootstrap_iterations: {config['bootstrap']['iterations']}",
            "",
            "## Training Samples",
            "",
            *sample_lines,
            "",
            "## Selected Onset Results",
            "",
            *(selected_lines or ["- No valid onset model was selected."]),
            "",
            "See `model_comparison_summary.csv` for the H5/H10 model comparison table and `feature_group_increment_table.csv` for P/M/C/ALL increments.",
            "",
            "## Daily Bootstrap CIs",
            "",
            *ci_lines,
            "",
            "## Event-Level Metrics",
            "",
            *event_lines,
            "",
            "## Feature Contribution Summary",
            "",
            *contrib_lines,
            "",
            "## Robustness Grid",
            "",
            "See `robustness_grid_summary.csv` for rows, event counts, and event rates under alternative gap, lookback, and threshold settings.",
            "",
            "## Excluded Leakage-Prone Variables",
            "",
            *(f"- {x}" for x in excluded),
            "",
        ]
    )
    write_text(output_dir / "onset_baseline_report.md", report)

    note = "\n".join(
        [
            "# Inclusion decision note",
            "",
            f"Final decision: {decision}",
            "",
            f"Reason: {reason}",
            "",
            "Evidence:",
            *(selected_lines or ["- No valid model result."]),
            "",
            "Bootstrap summary:",
            *ci_lines,
            "",
            "Event-level summary:",
            *event_lines,
            "",
            "Paper-body safety: this run did not modify LaTeX paper text.",
            "",
        ]
    )
    write_text(output_dir / "inclusion_decision_note.md", note)
    log.append("Wrote onset_baseline_report.md and inclusion_decision_note.md")


def run(argv: list[str] | None = None) -> int:
    global ACTIVE_LOG_PATH
    args = parse_args(argv)
    started_at = datetime.now()
    config = apply_run_mode(load_config(args.config), args)
    output_dir = PROJECT_ROOT / config["paths"]["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir.parent / "logs").mkdir(parents=True, exist_ok=True)
    (output_dir.parent / "checkpoints").mkdir(parents=True, exist_ok=True)
    ACTIVE_LOG_PATH = output_dir.parent / "logs" / f"run_{started_at.strftime('%Y%m%d_%H%M%S')}.log"
    setup_style(int(config["figures"]["dpi"]))
    log: list[str] = []
    generated: list[Path] = []
    unresolved: list[str] = []
    manifest: pd.DataFrame | None = None
    split: dict[str, str] | None = None
    try:
        log_line(log, f"Run mode={config['run_mode']} runtime={runtime_name()} memory={memory_hint()}")
        log_line(log, "Effective config: " + json.dumps(config, ensure_ascii=False, default=str))
        if config.get("resume"):
            log_line(log, "Resume requested; checkpoint markers: " + ", ".join(existing_checkpoints(output_dir)))
            complete_files = [
                output_dir / "cloud_run_summary.md",
                output_dir / "model_comparison_summary.csv",
                output_dir / "inclusion_decision_note.md",
            ]
            if cache_stage_available(output_dir, config, "reports_complete", complete_files):
                config.setdefault("_checkpoints_read", []).append(rel(cache_manifest_path(output_dir)))
                log_line(log, "Resume found completed reports for matching parameters; skipping recomputation.")
                generated.extend(complete_files)
                generated.append(output_dir / "run_log.txt")
                flush_log(output_dir, log)
                summary_path = write_cloud_run_summary(
                    output_dir, config, "OK_REUSED", generated, started_at, datetime.now(), manifest=None, split=None
                )
                print("Resume completed from cached reports. Outputs:")
                for path in [*generated, summary_path]:
                    print(rel(path))
                return 0

        manifest, split, existing_thresholds = load_inputs(config)
        manifest = apply_stock_code_cap(manifest, config, log)
        stock_count = int((~manifest["is_index"].astype(bool)).sum())
        log_line(log, f"Loaded manifest rows={len(manifest)} stock_count={stock_count}")
        write_checkpoint(
            output_dir,
            "data_read_complete",
            {"mode": config["run_mode"], "stock_count": stock_count, "manifest_rows": int(len(manifest))},
        )
        update_cache_stage(output_dir, config, "data_read_complete", [cache_manifest_path(output_dir)])
        flush_log(output_dir, log)

        if config.get("dry_run"):
            generated.append(output_dir / "run_log.txt")
            summary_path = write_cloud_run_summary(
                output_dir, config, "DRY_RUN_OK", generated, started_at, datetime.now(), manifest=manifest, split=split
            )
            generated.append(summary_path)
            flush_log(output_dir, log)
            print("Dry run completed. Outputs:")
            for path in generated:
                print(rel(path))
            return 0

        robustness_q = [float(x) for x in config["robustness_grid"]["threshold_quantiles"]]
        prefer_existing = bool(config["main_label"].get("prefer_existing_thresholds_for_main", True))
        main_thresholds: dict[int, float] = {}
        for horizon in HORIZONS:
            key = f"H{horizon}"
            main_thresholds[horizon] = float(existing_thresholds[key]) if prefer_existing and key in existing_thresholds else np.nan

        cross_context, direct_thresholds = build_cross_context(manifest, split, main_thresholds, robustness_q, log)
        for horizon in HORIZONS:
            if not np.isfinite(main_thresholds[horizon]):
                main_thresholds[horizon] = direct_thresholds[float(config["main_label"]["threshold_quantile"])]
        log_line(log, f"Main thresholds: {main_thresholds}")
        write_checkpoint(
            output_dir,
            "onset_thresholds_ready",
            {"main_thresholds": {f"H{k}": float(v) for k, v in main_thresholds.items()}},
        )
        update_cache_stage(output_dir, config, "onset_thresholds_ready")
        flush_log(output_dir, log)

        validate_onset_label_equivalence(manifest, main_thresholds, config, log)
        write_checkpoint(output_dir, "onset_label_equivalence_passed", {"mode": config["run_mode"]})
        update_cache_stage(output_dir, config, "onset_label_equivalence_passed")
        flush_log(output_dir, log)

        train_samples, trainval_samples, eval_samples, robustness, available_cols = collect_datasets(
            manifest, split, cross_context, main_thresholds, direct_thresholds, config, log, output_dir
        )
        write_checkpoint(
            output_dir,
            "labels_features_complete",
            {
                "available_feature_columns": len(available_cols),
                "train_sample_rows": {f"{k[0]}_H{k[1]}": int(len(v)) for k, v in train_samples.items()},
            },
        )
        update_cache_stage(output_dir, config, "labels_features_complete")
        flush_log(output_dir, log)

        feature_groups_by_h = {h: build_feature_groups(h, available_cols) for h in HORIZONS}
        excluded = [
            "Stress_H5",
            "Stress_H10",
            "future_max_LSI_5_H5",
            "future_max_LSI_5_H10",
            "CrossStress",
            "CrossStress_H10",
            "Y_onset_H5",
            "Y_onset_H10",
        ]

        fit_results, naive, sample_summary = train_models(train_samples, trainval_samples, feature_groups_by_h, config, log, output_dir)
        for fit in fit_results:
            write_checkpoint(
                output_dir,
                f"model_{fit.task}_H{fit.horizon}_{fit.feature_group}_{fit.model}",
                {"status": fit.status, "error": fit.error},
            )
        flush_log(output_dir, log)

        if config["sampling"].get("eval_max_rows_per_task_horizon_period") in (None, "null"):
            metrics, topk, onset_test_cache = evaluate_models_streaming(
                manifest, split, cross_context, main_thresholds, config, fit_results, naive, output_dir, log
            )
        else:
            metrics, topk, onset_test_cache = evaluate_models(eval_samples, fit_results, naive)
        write_checkpoint(output_dir, "evaluation_complete", {"metric_rows": int(len(metrics)), "topk_rows": int(len(topk))})
        update_cache_stage(output_dir, config, "evaluation_complete")
        flush_log(output_dir, log)

        best = select_best_models(metrics)
        ci = bootstrap_ci_for_delta(onset_test_cache, metrics, best, config)
        write_checkpoint(output_dir, "bootstrap_complete", {"rows": int(len(ci)), "iterations": int(config["bootstrap"]["iterations"])})
        bootstrap_cache = output_dir.parent / "checkpoints" / "bootstrap_partial_onset.parquet"
        if not ci.empty:
            ci.to_parquet(bootstrap_cache, index=False)
        update_cache_stage(output_dir, config, "bootstrap_complete", [bootstrap_cache] if bootstrap_cache.exists() else [])

        if config["sampling"].get("event_eval_full_test", True):
            event_pred = collect_event_predictions(manifest, split, cross_context, main_thresholds, config, best, fit_results, naive, log)
        else:
            event_pred = collect_sample_event_predictions(eval_samples, best, fit_results, naive)
        event_metrics = event_level_metrics(event_pred, config)

        importance, group_contrib = plot_feature_importance(fit_results, metrics, output_dir, bool(config["figures"].get("save_pdf", True)))
        plot_pr_curves(onset_test_cache, best, output_dir, bool(config["figures"].get("save_pdf", True)))
        plot_topk_lift(metrics, best, output_dir, bool(config["figures"].get("save_pdf", True)))
        write_checkpoint(output_dir, "figures_complete", {"save_pdf": bool(config["figures"].get("save_pdf", True))})
        update_cache_stage(output_dir, config, "figures_complete")

        onset_metrics = metrics.loc[metrics["task"] == "onset"].copy()
        continuation_metrics = metrics.loc[metrics["task"] == "continuation"].copy()
        feature_group_increment = build_feature_group_increment_table(metrics)
        summary = onset_metrics.loc[onset_metrics["period"] == "test"].copy()
        summary = summary[
            [
                "horizon",
                "model",
                "feature_group",
                "event_rate",
                "PR_AUC",
                "Top5_hit_rate",
                "Top5_lift",
                "Delta_PR_AUC_vs_persistence",
                "Delta_Top5_lift_vs_persistence",
                "Brier",
                "status",
            ]
        ]
        delta = metrics[
            [
                "task",
                "horizon",
                "period",
                "feature_group",
                "model",
                "Delta_PR_AUC_vs_persistence",
                "Delta_Top5_lift_vs_persistence",
                "Delta_Top10_lift_vs_persistence",
            ]
        ].copy()
        if not ci.empty:
            ci_path = output_dir / "bootstrap_ci.csv"
            ci.to_csv(ci_path, index=False, encoding="utf-8-sig", float_format="%.6f")
            generated.append(ci_path)
        prediction_dir = output_dir.parent / "checkpoints" / "predictions"
        prediction_dir.mkdir(parents=True, exist_ok=True)
        for (horizon, group, model), payload in onset_test_cache.items():
            pred_path = prediction_dir / f"predictions_onset_H{horizon}_{model}_{group}.parquet"
            pd.DataFrame({"y": payload["y"], "score": payload["p"], "date": payload.get("date")}).to_parquet(pred_path, index=False)
        for name, df in [
            ("onset_metrics.csv", onset_metrics),
            ("continuation_metrics.csv", continuation_metrics),
            ("model_comparison_summary.csv", summary),
            ("topk_lift_table.csv", topk),
            ("delta_vs_persistence.csv", pd.concat([delta, ci.assign(task="onset")], ignore_index=True, sort=False) if not ci.empty else delta),
            ("feature_group_increment_table.csv", feature_group_increment),
            ("robustness_grid_summary.csv", robustness),
            ("training_sample_summary.csv", sample_summary),
            ("selected_best_models.csv", best),
            ("event_level_metrics.csv", event_metrics),
            ("feature_importance_onset.csv", importance),
            ("feature_group_contribution_onset.csv", group_contrib),
        ]:
            path = output_dir / name
            df.to_csv(path, index=False, encoding="utf-8-sig", float_format="%.6f")
            generated.append(path)

        generated.extend(
            [output_dir / "fig_pr_curves_onset.png", output_dir / "fig_topk_lift_onset.png", output_dir / "fig_feature_importance_onset.png"]
        )
        if config["figures"].get("save_pdf", True):
            generated.extend(
                [output_dir / "fig_pr_curves_onset.pdf", output_dir / "fig_topk_lift_onset.pdf", output_dir / "fig_feature_importance_onset.pdf"]
            )

        write_reports(metrics, topk, robustness, sample_summary, best, ci, event_metrics, group_contrib, excluded, config, output_dir, log)
        generated.extend([output_dir / "onset_baseline_report.md", output_dir / "inclusion_decision_note.md"])
        generated.append(output_dir / "run_log.txt")
        flush_log(output_dir, log)
        summary_path = write_cloud_run_summary(output_dir, config, "OK", generated, started_at, datetime.now(), manifest=manifest, split=split)
        generated.append(summary_path)
        write_checkpoint(output_dir, "reports_complete", {"generated": [rel(p) for p in generated]})
        update_cache_stage(output_dir, config, "reports_complete", generated)
        write_handoff(output_dir, generated, unresolved or ["none"])
        print("Onset baseline experiment completed. Outputs:")
        for path in generated:
            print(rel(path))
        return 0
    except Exception as exc:
        unresolved.append(str(exc))
        log_line(log, "FATAL: " + str(exc))
        log.extend(traceback.format_exc().splitlines())
        flush_log(output_dir, log)
        report_path = output_dir / "onset_baseline_report.md"
        note_path = output_dir / "inclusion_decision_note.md"
        write_text(
            report_path,
            "# Onset baseline independent experiment report\n\nStatus: BLOCKED\n\n"
            f"Error: {exc}\n\nCheck `run_log.txt` and the timestamped log under `logs/`.\n",
        )
        write_text(
            note_path,
            "# Inclusion decision note\n\nFinal decision: C. Do not include yet\n\nReason: the experiment did not complete.\n",
        )
        generated.extend([output_dir / "run_log.txt", report_path, note_path])
        summary_path = write_cloud_run_summary(
            output_dir, config, "FAILED", generated, started_at, datetime.now(), error=str(exc), manifest=manifest, split=split
        )
        generated.append(summary_path)
        write_handoff(output_dir, generated, unresolved)
        print(f"Onset baseline experiment failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
