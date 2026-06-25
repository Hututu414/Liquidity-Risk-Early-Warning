"""Matplotlib style helpers for Chinese academic figures."""

from __future__ import annotations

import matplotlib.pyplot as plt


def apply_cn_academic_style(dpi: int = 300) -> None:
    plt.rcParams.update(
        {
            "figure.dpi": dpi,
            "savefig.dpi": dpi,
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
            "figure.autolayout": True,
        }
    )
