from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CODE_ROOT = PROJECT_ROOT / "code" / "src"

sys.dont_write_bytecode = True
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter


PATH_TABLE = PROJECT_ROOT / "outputs" / "tables" / "04_rgarch" / "rgarch_carr_sk_adapted_conditional_paths.csv"
LOSS_TABLE = PROJECT_ROOT / "outputs" / "tables" / "04_rgarch" / "rgarch_carr_sk_adapted_oos_losses.csv"
OUTPUT_PATHS = [
    PROJECT_ROOT / "outputs" / "figures" / "04_rgarch" / "fig_rgarch_dynamic_skew_kurtosis_refined.png",
    PROJECT_ROOT / "report" / "latex_project" / "figures" / "fig_rgarch_dynamic_skew_kurtosis_refined.png",
]
AUDIT_PATH = PROJECT_ROOT / "reviews" / "figure_audit" / "rgarch_dynamic_skew_kurtosis_refined_axis_adjustment.md"


def configure_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "axes.grid": True,
            "grid.alpha": 0.28,
            "grid.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": True,
            "legend.framealpha": 0.92,
        }
    )


def select_model(paths: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    losses = pd.read_csv(LOSS_TABLE)
    test_losses = losses.loc[losses["period"].eq("test")].copy()
    if test_losses.empty:
        model = "RGARCH-CARR-SK-RMAD"
    else:
        model = str(test_losses.sort_values("R2LOG").iloc[0]["model"])
    selected = paths.loc[paths["model"].eq(model)].copy()
    if selected.empty:
        raise RuntimeError(f"Selected model has no conditional path rows: {model}")
    selected["datetime"] = pd.to_datetime(selected["datetime"])
    selected = selected.sort_values("datetime")
    return model, selected


def add_period_spans(ax, df: pd.DataFrame, *, labels: bool = False) -> None:
    colors = {
        "train": "#EAF3FB",
        "validation": "#FBF3E2",
        "test": "#FCEEE8",
    }
    names = {
        "train": "训练期",
        "validation": "验证期",
        "test": "测试期",
    }
    for period in ["train", "validation", "test"]:
        part = df.loc[df["period"].eq(period)]
        if part.empty:
            continue
        start = part["datetime"].min()
        end = part["datetime"].max()
        ax.axvspan(start, end, color=colors[period], alpha=0.72, lw=0, zorder=0)
        if labels:
            mid = start + (end - start) / 2
            ax.text(
                mid,
                0.97,
                names[period],
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=10,
                color="#5F5F5F",
            )


def set_tight_kurtosis_axis(ax, k_values: pd.Series) -> None:
    k_min = float(np.nanmin(k_values))
    k_max = float(np.nanmax(k_values))
    if not np.isfinite(k_min) or not np.isfinite(k_max):
        return

    if k_max - k_min < 0.01:
        lower = min(3.0, k_min) - 0.00002
        upper = max(k_max, 3.0013) + 0.00008
        ticks = np.arange(3.0000, upper + 0.00001, 0.0003)
        ax.set_ylim(lower, upper)
        ax.set_yticks(ticks)
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.4f"))


def build_figure() -> dict[str, float | str | int]:
    configure_style()
    paths = pd.read_csv(PATH_TABLE)
    model, df = select_model(paths)

    fig, axes = plt.subplots(2, 1, figsize=(9.51, 5.91), sharex=True, constrained_layout=True)

    axes[0].plot(df["datetime"], df["s_t"], color="#D62728", linewidth=1.2, label="动态偏度 (s_t)")
    axes[0].set_title("RGARCH-CARR-SK 动态偏度 (s_t)", loc="left", fontsize=14, pad=10)
    axes[0].set_ylabel("偏度", fontsize=11)
    axes[0].legend(loc="upper right", fontsize=10)

    axes[1].plot(df["datetime"], df["k_t"], color="#1F6BBF", linewidth=1.35, label="动态峰度 (k_t)")
    axes[1].axhline(3.0001, color="#808080", linestyle="--", linewidth=0.8, alpha=0.75)
    axes[1].set_title("RGARCH-CARR-SK 动态峰度 (k_t)", loc="left", fontsize=14, pad=10)
    axes[1].set_ylabel("峰度", fontsize=11)
    axes[1].set_xlabel("日期", fontsize=11)
    axes[1].legend(loc="upper right", fontsize=10)
    set_tight_kurtosis_axis(axes[1], df["k_t"])

    spike = df.loc[df["k_t"].gt(df["k_t"].min() + 1e-8)]
    if not spike.empty:
        axes[1].scatter(spike["datetime"], spike["k_t"], s=18, color="#1F6BBF", zorder=3)

    for ax in axes:
        add_period_spans(ax, df)
        ax.set_axisbelow(True)
        ax.spines["left"].set_linewidth(0.9)
        ax.spines["bottom"].set_linewidth(0.9)
        ax.tick_params(axis="both", labelsize=10)

    axes[1].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 5, 9]))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    for path in OUTPUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, bbox_inches="tight", facecolor="white", dpi=300)
    plt.close(fig)

    return {
        "model": model,
        "nobs": int(len(df)),
        "s_min": float(df["s_t"].min()),
        "s_max": float(df["s_t"].max()),
        "k_min": float(df["k_t"].min()),
        "k_max": float(df["k_t"].max()),
        "k_std": float(df["k_t"].std(ddof=1)),
        "k_unique": int(df["k_t"].nunique()),
    }


def write_audit(stats: dict[str, float | str | int]) -> None:
    lines = [
        "# RGARCH Dynamic Skewness/Kurtosis Refined Axis Adjustment",
        "",
        "## Scope",
        "",
        "- Rebuilt `fig_rgarch_dynamic_skew_kurtosis_refined.png` from `rgarch_carr_sk_adapted_conditional_paths.csv`.",
        "- Adjusted only the lower kurtosis panel's y-axis scale and tick formatting.",
        "- Did not modify RGARCH-CARR-SK model outputs, source tables, LaTeX text, or empirical conclusions.",
        "",
        "## Data Used",
        "",
        f"- Selected model: `{stats['model']}`.",
        f"- Observations plotted: {stats['nobs']}.",
        f"- `s_t` range: {stats['s_min']:.10f} to {stats['s_max']:.10f}.",
        f"- `k_t` range: {stats['k_min']:.10f} to {stats['k_max']:.10f}.",
        f"- `k_t` std: {stats['k_std']:.10g}.",
        f"- `k_t` unique values: {stats['k_unique']}.",
        "",
        "## Visual Change",
        "",
        "- The lower panel now uses a narrow actual-value y-axis around `3.0000` to `3.0014`.",
        "- Tick labels are formatted to four decimals so the small boundary-adjacent movement is visible.",
        "- The dashed reference line marks the numerical lower bound near `3.0001`.",
        "",
        "## Interpretation Boundary",
        "",
        "The revised figure makes the lower-panel path readable, but the movement remains numerically tiny. It should still be described as a model-implied diagnostic path near the kurtosis lower stability bound, not as a large tail-risk regime shift.",
        "",
    ]
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    stats = build_figure()
    write_audit(stats)
    print(f"updated={OUTPUT_PATHS[1]}")
    print(f"model={stats['model']}")
    print(f"k_range={stats['k_min']:.10f},{stats['k_max']:.10f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
