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
import pandas as pd


PATH_TABLE = PROJECT_ROOT / "outputs" / "tables" / "04_rgarch" / "rgarch_carr_sk_adapted_conditional_paths.csv"
LOSS_TABLE = PROJECT_ROOT / "outputs" / "tables" / "04_rgarch" / "rgarch_carr_sk_adapted_oos_losses.csv"
OUTPUT_PATHS = [
    PROJECT_ROOT / "outputs" / "figures" / "04_rgarch" / "fig_rgarch_dynamic_skewness_refined.png",
    PROJECT_ROOT / "report" / "latex_project" / "figures" / "fig_rgarch_dynamic_skewness_refined.png",
]
AUDIT_PATH = PROJECT_ROOT / "reviews" / "figure_audit" / "rgarch_dynamic_skewness_refined_single_panel.md"


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
    model = str(test_losses.sort_values("R2LOG").iloc[0]["model"]) if not test_losses.empty else "RGARCH-CARR-SK-RMAD"
    selected = paths.loc[paths["model"].eq(model)].copy()
    if selected.empty:
        raise RuntimeError(f"Selected model has no conditional path rows: {model}")
    selected["datetime"] = pd.to_datetime(selected["datetime"])
    return model, selected.sort_values("datetime")


def add_period_spans(ax, df: pd.DataFrame) -> None:
    colors = {
        "train": "#EAF3FB",
        "validation": "#FBF3E2",
        "test": "#FCEEE8",
    }
    for period in ["train", "validation", "test"]:
        part = df.loc[df["period"].eq(period)]
        if part.empty:
            continue
        ax.axvspan(part["datetime"].min(), part["datetime"].max(), color=colors[period], alpha=0.72, lw=0, zorder=0)


def build_figure() -> dict[str, float | int | str]:
    configure_style()
    paths = pd.read_csv(PATH_TABLE)
    model, df = select_model(paths)

    fig, ax = plt.subplots(figsize=(9.51, 3.65), constrained_layout=True)
    add_period_spans(ax, df)
    ax.plot(df["datetime"], df["s_t"], color="#D62728", linewidth=1.25, label="动态偏度 (s_t)")
    ax.set_title("RGARCH-CARR-SK 动态偏度 (s_t)", loc="left", fontsize=15, pad=10)
    ax.set_ylabel("偏度", fontsize=11)
    ax.set_xlabel("日期", fontsize=11)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_axisbelow(True)
    ax.spines["left"].set_linewidth(0.9)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.tick_params(axis="both", labelsize=10)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 5, 9]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    for path in OUTPUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, bbox_inches="tight", facecolor="white", dpi=300)
    plt.close(fig)

    return {
        "model": model,
        "nobs": int(len(df)),
        "s_min": float(df["s_t"].min()),
        "s_max": float(df["s_t"].max()),
        "s_std": float(df["s_t"].std(ddof=1)),
    }


def write_audit(stats: dict[str, float | int | str]) -> None:
    lines = [
        "# RGARCH Dynamic Skewness Single-Panel Figure",
        "",
        "## Scope",
        "",
        "- Generated a single-panel dynamic skewness figure from the existing RGARCH-CARR-SK conditional path table.",
        "- Did not modify model outputs, empirical tables, LaTeX text, or the combined skewness/kurtosis figure.",
        "",
        "## Data Used",
        "",
        f"- Selected model: `{stats['model']}`.",
        f"- Observations plotted: {stats['nobs']}.",
        f"- `s_t` range: {stats['s_min']:.10f} to {stats['s_max']:.10f}.",
        f"- `s_t` std: {stats['s_std']:.10g}.",
        "",
        "## Outputs",
        "",
        "- `outputs/figures/04_rgarch/fig_rgarch_dynamic_skewness_refined.png`",
        "- `report/latex_project/figures/fig_rgarch_dynamic_skewness_refined.png`",
        "",
    ]
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    stats = build_figure()
    write_audit(stats)
    print(f"model={stats['model']}")
    print(f"s_range={stats['s_min']:.10f},{stats['s_max']:.10f}")
    print(f"updated={OUTPUT_PATHS[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
