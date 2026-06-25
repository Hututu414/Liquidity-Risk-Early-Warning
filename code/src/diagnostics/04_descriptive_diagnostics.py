from __future__ import annotations

import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from config import paths
from src.common.config_loader import load_project_config
from src.common.io_utils import write_markdown
from src.common.logging_utils import setup_logger, write_failure
from src.visualization.plot_style import apply_cn_academic_style


STAGE = "stage3_descriptive_diagnostics"


def _read_manifest() -> pd.DataFrame:
    path = paths.STAGE2_DIR / "lsi_labels_manifest.csv"
    if not path.exists():
        raise FileNotFoundError(f"Stage2 final manifest is missing: {path}")
    manifest = pd.read_csv(path)
    if manifest.empty:
        raise RuntimeError("Stage2 final manifest is empty.")
    return manifest


def _add_group(left: pd.DataFrame | None, right: pd.DataFrame) -> pd.DataFrame:
    if left is None:
        return right.copy()
    return left.add(right, fill_value=0)


def _plot_intraday(slot_stats: pd.DataFrame, figure_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(slot_stats["slot"], slot_stats["LSI_5_mean"], linewidth=1.4, label="LSI_5 (Mean)")
    if "LSI_5_q25" in slot_stats.columns and "LSI_5_q75" in slot_stats.columns:
        ax.fill_between(
            slot_stats["slot"],
            slot_stats["LSI_5_q25"],
            slot_stats["LSI_5_q75"],
            alpha=0.2,
            label="LSI_5 (25%-75%)"
        )
    ax.set_xlabel("鏃ュ唴 slot")
    ax.set_ylabel("LSI_5")
    ax.set_title("娴佸姩鎬у帇鍔涙寚鏁版棩鍐呮ā寮?)
    ax.legend()
    fig.savefig(figure_path)
    plt.close(fig)


def _plot_stress_rate(date_stats: pd.DataFrame, figure_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    dates = pd.to_datetime(date_stats["date"])
    ax.plot(dates, date_stats["Stress_H5_mean"], linewidth=1.0, label="Stress_H5 Rate", alpha=0.7)
    ax.set_xlabel("鏃ユ湡")
    ax.set_ylabel("鍘嬪姏姣斾緥")
    ax.set_title("鏍锋湰鍐呭悇鏃ユ祦鍔ㄦ€у帇鍔涙爣绛炬瘮渚?)
    ax.legend()
    fig.savefig(figure_path)
    plt.close(fig)


def _plot_market_context(market: pd.DataFrame, figure_path: Path, max_points: int) -> None:
    plot_df = market.sort_values("datetime")
    if len(plot_df) > max_points:
        step = max(1, len(plot_df) // max_points)
        plot_df = plot_df.iloc[::step].copy()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    times = pd.to_datetime(plot_df["datetime"])

    ax1.plot(times, plot_df["MarketLSI"], linewidth=0.8, color="tab:blue")
    ax1.set_ylabel("MarketLSI")
    ax1.set_title("甯傚満鍏卞悓鍘嬪姏鎸囨暟 (MarketLSI)")

    ax2.plot(times, plot_df["CrossStress"], linewidth=0.8, color="tab:red")
    ax2.set_ylabel("CrossStress")
    ax2.set_title("甯傚満鎴潰鍘嬪姏姣斾緥 (CrossStress)")

    ax2.set_xlabel("鏃堕棿")
    fig.savefig(figure_path)
    plt.close(fig)


def _plot_coverage_heatmap(coverage_df: pd.DataFrame, figure_path: Path) -> None:
    """Plot data coverage heatmap (date vs code)."""
    # coverage_df should be index=code, columns=date
    if coverage_df.empty:
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(coverage_df.values, aspect="auto", cmap="YlGn", interpolation="nearest")

    # Labeling
    ax.set_yticks(np.arange(len(coverage_df.index)))
    ax.set_yticklabels(coverage_df.index, fontsize=6)

    # Only show some date labels to avoid clutter
    n_dates = len(coverage_df.columns)
    indices = np.linspace(0, n_dates - 1, 10, dtype=int)
    ax.set_xticks(indices)
    ax.set_xticklabels([coverage_df.columns[i] for i in indices], rotation=45, fontsize=8)

    ax.set_title("鏍锋湰璇佸埜鏁版嵁瑕嗙洊鐑姏鍥?(缁胯壊琛ㄧず鏈夋暟鎹?")
    plt.colorbar(im, label="鏄惁鍙敤")
    fig.savefig(figure_path)
    plt.close(fig)


def build_audit_text(total_rows: int, n_codes: int, outputs: list[str]) -> str:
    output_lines = [f"- `{item}`" for item in outputs]
    return "\n".join(
        [
            "# Stage3 鎻忚堪鎬ц瘖鏂璁?,
            "",
            "- 鐘舵€侊細PASS",
            f"- 璇诲彇鏈€缁堝彉閲忎笌鏍囩琛屾暟锛歿total_rows:,}",
            f"- 璇佸埜 shard 鏁帮細{n_codes}",
            "",
            "## 杈撳嚭",
            "",
            *output_lines,
            "",
            "## 璇存槑",
            "",
            "鏈樁娈电敓鎴愭牱鏈鐩栥€丩SI 鏃ュ唴妯″紡銆佸帇鍔涙爣绛炬瘮渚嬩笌甯傚満鍏卞悓鍘嬪姏鐨勬弿杩版€ц〃鏍煎拰鍥惧舰銆?,
            "鏂板锛氳鐩栫儹鍔涘浘銆丆rossStress 瓒嬪娍鍥俱€丩SI 鏃ュ唴鍒嗕綅甯︺€?,
            "",
        ]
    )


def run() -> None:
    logger = setup_logger(STAGE)
    paths.ensure_runtime_dirs()
    config = load_project_config()
    diagnostics_cfg = config["diagnostics"]
    apply_cn_academic_style(int(diagnostics_cfg["figure_dpi"]))

    manifest = _read_manifest()
    paths.TABLE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths.FIGURE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, object]] = []
    total_rows = 0

    all_dates = set()
    coverage_data = {} # code -> list of dates

    # To calculate quantiles for LSI_5 per slot, we need to collect data
    # Given the size, we'll collect a sample or use a more memory-efficient way
    # For 84 codes, we can probably aggregate by slot fairly easily
    slot_lsi_data = {} # slot -> list of LSI_5 values (sampled if too large)

    read_cols = [
        "code", "is_index", "datetime", "date", "slot",
        "LSI_5", "Stress_H5", "MarketLSI", "CrossStress"
    ]

    market_context_full = []

    for idx, row in enumerate(manifest.itertuples(index=False), start=1):
        code = str(row.code)
        logger.info("Processing diagnostics for %s (%d/%d)", code, idx, len(manifest))
        df = pd.read_parquet(paths.PROJECT_ROOT / str(row.output_path), columns=read_cols)
        total_rows += int(len(df))

        stock = df.loc[~df["is_index"].astype(bool)].copy()
        if stock.empty:
            continue

        unique_dates = stock["date"].unique()
        all_dates.update(unique_dates)
        coverage_data[code] = set(unique_dates)

        summary_rows.append({
            "code": code,
            "rows": int(len(stock)),
            "date_count": int(len(unique_dates)),
            "LSI_5_mean": float(stock["LSI_5"].mean()),
            "LSI_5_std": float(stock["LSI_5"].std()),
            "Stress_H5_rate": float(stock["Stress_H5"].mean()),
        })

        # Sample for intraday quantiles to save memory
        # Take 10% of rows
        sample_stock = stock.sample(frac=0.1, random_state=42) if len(stock) > 1000 else stock
        for slot, group in sample_stock.groupby("slot"):
            if slot not in slot_lsi_data:
                slot_lsi_data[slot] = []
            slot_lsi_data[slot].extend(group["LSI_5"].dropna().tolist())

        # Collect market context from the first stock (or better, aggregate)
        # Since MarketLSI is same for all stocks at same datetime, we just take it once
        if idx == 1:
            market_context_full.append(df[["datetime", "date", "MarketLSI", "CrossStress"]].drop_duplicates("datetime"))

    if not summary_rows:
        raise RuntimeError("No stock data found for diagnostics.")

    # 1. Summary Table
    summary = pd.DataFrame(summary_rows)
    summary_path = paths.TABLE_OUTPUT_DIR / "summary_statistics_by_code.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    # 2. Coverage Heatmap
    sorted_dates = sorted(list(all_dates))
    coverage_matrix = pd.DataFrame(0, index=summary["code"].tolist(), columns=sorted_dates)
    for code, dates in coverage_data.items():
        coverage_matrix.loc[code, list(dates)] = 1

    fig_coverage = paths.FIGURE_OUTPUT_DIR / "fig_coverage_heatmap.png"
    _plot_coverage_heatmap(coverage_matrix, fig_coverage)

    # 3. Intraday Stats
    intraday_rows = []
    for slot in sorted(slot_lsi_data.keys()):
        vals = slot_lsi_data[slot]
        if vals:
            intraday_rows.append({
                "slot": slot,
                "LSI_5_mean": np.mean(vals),
                "LSI_5_q25": np.percentile(vals, 25),
                "LSI_5_q50": np.percentile(vals, 50),
                "LSI_5_q75": np.percentile(vals, 75)
            })
    slot_stats = pd.DataFrame(intraday_rows)
    slot_path = paths.TABLE_OUTPUT_DIR / "lsi_intraday_stats.csv"
    slot_stats.to_csv(slot_path, index=False)

    fig_intraday = paths.FIGURE_OUTPUT_DIR / "fig_lsi_intraday.png"
    _plot_intraday(slot_stats, fig_intraday)

    # 4. Market Context & Stress Rate
    market_df = pd.concat(market_context_full).sort_values("datetime").drop_duplicates("datetime")
    market_path = paths.TABLE_OUTPUT_DIR / "market_context_diagnostics.csv"
    market_df.to_csv(market_path, index=False)

    fig_market = paths.FIGURE_OUTPUT_DIR / "fig_market_stress_combined.png"
    _plot_market_context(market_df, fig_market, int(diagnostics_cfg["max_market_plot_points"]))

    # Stress rate by date
    date_stress = market_df.groupby("date")["CrossStress"].mean().reset_index()
    date_stress.columns = ["date", "Stress_H5_mean"]
    fig_stress = paths.FIGURE_OUTPUT_DIR / "fig_stress_rate_timeseries.png"
    _plot_stress_rate(date_stress, fig_stress)

    outputs = [
        str(summary_path.relative_to(paths.PROJECT_ROOT)),
        str(slot_path.relative_to(paths.PROJECT_ROOT)),
        str(market_path.relative_to(paths.PROJECT_ROOT)),
        str(fig_coverage.relative_to(paths.PROJECT_ROOT)),
        str(fig_intraday.relative_to(paths.PROJECT_ROOT)),
        str(fig_market.relative_to(paths.PROJECT_ROOT)),
        str(fig_stress.relative_to(paths.PROJECT_ROOT)),
    ]
    write_markdown(build_audit_text(total_rows, len(manifest), outputs), paths.DATA_AUDIT_DIR / "stage3_descriptive_diagnostics.md")
    logger.info("Stage3 completed: total_rows=%s", f"{total_rows:,}")


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
