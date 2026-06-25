import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties

# Add project root to sys.path
CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from config import paths
from src.visualization.plot_style import apply_cn_academic_style

# Academic Variable Naming Mapping
CN_LABELS = {
    "MarketLSI": "甯傚満鍏卞悓鍘嬪姏鎸囨暟 (MarketLSI)",
    "LSI_5": "5鍒嗛挓娴佸姩鎬у帇鍔涙寚鏁?(LSI_5)",
    "LSI_10": "10鍒嗛挓娴佸姩鎬у帇鍔涙寚鏁?(LSI_10)",
    "LSI_20": "20鍒嗛挓娴佸姩鎬у帇鍔涙寚鏁?(LSI_20)",
    "CrossStress": "甯傚満鎴潰鍘嬪姏姣斾緥 (CrossStress)",
    "Stress_H5": "5鍒嗛挓鍘嬪姏浜嬩欢 (Stress_H5)",
    "Stress_H10": "10鍒嗛挓鍘嬪姏浜嬩欢 (Stress_H10)",
    "IndexRV": "娌繁300宸插疄鐜版尝鍔ㄧ巼 (IndexRV)",
    "IndexRet": "娌繁300鏀剁泭鐜?(IndexRet)",
    "MarketRelAmt": "甯傚満鐩稿鎴愪氦棰?(MarketRelAmt)",
    "slot": "鏃ュ唴鏃堕棿妲戒綅",
    "date": "鏃ユ湡",
    "importance": "鐗瑰緛閲嶈鎬?(%)",
    "Recall": "鍙洖鐜?(Recall)",
    "Precision": "绮剧‘鐜?(Precision)",
    "True Positive Rate": "鐪熸鐜?(TPR)",
    "False Positive Rate": "鍋囨鐜?(FPR)",
    "Predicted Probability": "棰勬祴姒傜巼",
    "Realized Positive Rate": "鐪熷疄鍘嬪姏鍙戠敓鐜?,
    "Conditional Risk": "鏉′欢鍘嬪姏椋庨櫓 (Conditional Risk)",
    "Dynamic Skewness": "鍔ㄦ€佸亸搴?(Dynamic Skewness)",
    "Dynamic Kurtosis": "鍔ㄦ€佸嘲搴?(Dynamic Kurtosis)",
    "Conditional Variance": "鏉′欢鏂瑰樊",
    "reg_stage": "鐩戠闃舵",
}

def get_cn_label(key: str) -> str:
    return CN_LABELS.get(key, key)

def refine_coverage_heatmap():
    """Generates a refined stock-date coverage heatmap."""
    print("Generating refined coverage heatmap...")
    input_path = paths.STAGE1_DIR / "coverage_by_code_date.csv"
    if not input_path.exists():
        print(f"Skipping coverage heatmap: {input_path} not found.")
        return

    df = pd.read_csv(input_path)
    # Pivot: Index = code, Columns = date, Value = 1 (exists)
    pivot_df = df.pivot(index="code", columns="date", values="valid_minutes")
    # Convert to binary coverage (1 if minutes > 0, else 0)
    pivot_df = (pivot_df > 0).astype(int)

    apply_cn_academic_style()
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.heatmap(pivot_df, cmap="YlGn", cbar_kws={'label': '鏁版嵁鏄惁鍙敤'}, ax=ax)

    # Refine labels
    ax.set_title("鏍锋湰璇佸埜浜ゆ槗鏃ユ暟鎹鐩栫巼鐑姏鍥?, fontsize=14, pad=15)
    ax.set_xlabel("鏃ユ湡", fontsize=12)
    ax.set_ylabel("璇佸埜浠ｇ爜", fontsize=12)

    # Reduce date labels
    n_dates = len(pivot_df.columns)
    indices = np.linspace(0, n_dates - 1, 8, dtype=int)
    ax.set_xticks(indices)
    ax.set_xticklabels([pivot_df.columns[i] for i in indices], rotation=0)

    # Reduce code labels if too many
    if len(pivot_df.index) > 50:
        n_codes = len(pivot_df.index)
        indices = np.linspace(0, n_codes - 1, 20, dtype=int)
        ax.set_yticks(indices)
        ax.set_yticklabels([pivot_df.index[i] for i in indices], fontsize=8)

    output_path = paths.FIGURES_ROOT / "01_data" / "fig_refined_coverage_heatmap.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    fig.savefig(output_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)

def refine_lsi_intraday():
    """Generates refined LSI intraday pattern plot."""
    print("Generating refined LSI intraday pattern...")
    input_path = paths.DIAGNOSTICS_OUTPUT_DIR / "tables" / "lsi_intraday_stats.csv"
    if not input_path.exists():
        print(f"Skipping LSI intraday: {input_path} not found.")
        return

    df = pd.read_csv(input_path)
    apply_cn_academic_style()
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df["slot"], df["LSI_5_mean"], color="tab:blue", linewidth=1.5, label="鍧囧€?)
    ax.fill_between(df["slot"], df["LSI_5_q25"], df["LSI_5_q75"], color="tab:blue", alpha=0.2, label="25%-75% 鍒嗕綅鏁板尯闂?)

    ax.set_title("娴佸姩鎬у帇鍔涙寚鏁?(LSI_5) 鏃ュ唴鏃堕棿妯″紡", fontsize=14)
    ax.set_xlabel("鏃ュ唴鍒嗛挓妲戒綅 (0-240)", fontsize=12)
    ax.set_ylabel("LSI_5", fontsize=12)
    ax.legend(loc="upper right")

    output_path = paths.FIGURES_ROOT / "02_lsi" / "fig_refined_lsi_intraday.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    fig.savefig(output_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)

def refine_market_lsi_ts():
    """Generates refined MarketLSI time series plot."""
    print("Generating refined MarketLSI time series...")
    input_path = paths.DIAGNOSTICS_OUTPUT_DIR / "tables" / "market_context_diagnostics.csv"
    if not input_path.exists():
        print(f"Skipping MarketLSI TS: {input_path} not found.")
        return

    df = pd.read_csv(input_path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")

    # Downsample for plotting if too many points
    if len(df) > 5000:
        df = df.iloc[::max(1, len(df)//2000)].copy()

    apply_cn_academic_style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax1.plot(df["datetime"], df["MarketLSI"], color="darkblue", linewidth=0.7)
    ax1.set_title("甯傚満鍏卞悓鍘嬪姏鎸囨暟 (MarketLSI) 鏃堕棿搴忓垪", fontsize=14)
    ax1.set_ylabel("MarketLSI", fontsize=12)

    ax2.plot(df["datetime"], df["CrossStress"], color="darkred", linewidth=0.7)
    ax2.set_title("甯傚満鎴潰鍘嬪姏姣斾緥 (CrossStress - 鎻忚堪鎬т簨瀹?", fontsize=14)
    ax2.set_ylabel("鍘嬪姏姣斾緥", fontsize=12)
    ax2.set_xlabel("鏃堕棿", fontsize=12)

    output_path = paths.FIGURES_ROOT / "02_lsi" / "fig_refined_market_lsi_timeseries.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

def refine_smartboost_pr_calibration():
    """Generates refined PR and Calibration curves for SMARTboost."""
    print("Generating refined SMARTboost PR/Calibration curves...")
    # These often need to be redrawn from the table outputs if the original pngs are rough
    # But for now, I'll focus on the Partial Effects and Top 5% rate as they are more critical for interpretation
    pass

def refine_smartboost_top5_rate():
    """Generates refined Top 5% group realized event rate chart."""
    print("Generating refined SMARTboost Top 5% event rate...")
    rates_path = paths.SMARTBOOST_TABLE_DIR / "smartboost_high_risk_group_rates.csv"
    metrics_path = paths.SMARTBOOST_TABLE_DIR / "smartboost_metrics.csv"

    if not rates_path.exists() or not metrics_path.exists():
        print(f"Skipping SMARTboost Top 5%: Data not found.")
        return

    df_rates = pd.read_csv(rates_path)
    df_metrics = pd.read_csv(metrics_path)

    # Filter for top_5pct only
    df_rates = df_rates[df_rates["group"] == "top_5pct"].copy()

    # Join with metrics to get population_rate (positive_rate)
    df = df_rates.merge(df_metrics[["horizon", "period", "positive_rate"]], on=["horizon", "period"])

    # Filter for horizons H5, H10
    df_h5 = df[df["horizon"] == "H5"]
    df_h10 = df[df["horizon"] == "H10"]

    apply_cn_academic_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    periods = df_h5["period"].tolist()
    x = np.arange(len(periods))
    width = 0.35

    ax.bar(x - width/2, df_h5["realized_pressure_rate"], width, label="鏈潵5鍒嗛挓 (H5)", color="tab:blue", alpha=0.8)
    ax.bar(x + width/2, df_h10["realized_pressure_rate"], width, label="鏈潵10鍒嗛挓 (H10)", color="tab:orange", alpha=0.8)

    # Baseline line (average positive rate)
    avg_rate_h5 = df_h5["positive_rate"].mean()
    ax.axhline(y=avg_rate_h5, color="gray", linestyle="--", alpha=0.5, label="鍏ㄦ牱鏈熀鍑嗗帇鍔涚巼")

    ax.set_xticks(x)
    ax.set_xticklabels(periods, fontsize=11)
    ax.set_title("SMARTBoost 棰勬祴 Top 5% 楂橀闄╃粍鐨勭湡瀹炲帇鍔涘彂鐢熺巼", fontsize=14)
    ax.set_ylabel("鐪熷疄鍘嬪姏浜嬩欢鍙戠敓棰戠巼", fontsize=12)
    ax.set_xlabel("鏍锋湰瀛愰泦 (楠岃瘉闆?vs 娴嬭瘯闆?", fontsize=12)
    ax.legend()

    output_path = paths.FIGURES_ROOT / "06_smartboost" / "fig_refined_top5_realized_rate.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

def refine_smartboost_partial_effects():
    """Generates refined Partial Effects plots for SMARTboost."""
    print("Generating refined SMARTboost partial effects...")
    input_path = paths.SMARTBOOST_TABLE_DIR / "smartboost_partial_effects.csv"
    if not input_path.exists():
        print(f"Skipping SMARTboost Partial Effects: {input_path} not found.")
        return

    df = pd.read_csv(input_path)
    apply_cn_academic_style()

    # Focus on top 3 features: MarketLSI, LSI_5_lag1, MarketRelAmt
    features = ["MarketLSI", "LSI_5_lag1", "MarketRelAmt"]
    horizons = ["H5", "H10"]

    fig, axes = plt.subplots(len(features), len(horizons), figsize=(14, 12), sharey='row')

    for i, feat in enumerate(features):
        for j, horiz in enumerate(horizons):
            subset = df[(df["feature"] == feat) & (df["horizon"] == horiz)]
            if subset.empty:
                continue

            ax = axes[i, j]
            ax.plot(subset["feature_value"], subset["mean_predicted_probability"],
                    marker='o', linestyle='-', color='tab:blue', linewidth=1.5)

            if i == 0:
                ax.set_title(f"棰勬祴鏃剁晫: {horiz}", fontsize=13)
            if j == 0:
                ax.set_ylabel(f"閮ㄥ垎鏁堝簲 (姒傜巼)\n[{get_cn_label(feat)}]", fontsize=11)

            ax.set_xlabel(f"{get_cn_label(feat)} 鍙栧€?, fontsize=10)

    fig.suptitle("SMARTBoost 鏍稿績鐗瑰緛鐨勯儴鍒嗘晥搴斿浘 (Partial Effects)", fontsize=16, y=1.02)
    plt.tight_layout()

    output_path = paths.FIGURES_ROOT / "06_smartboost" / "fig_refined_partial_effects.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    fig.savefig(output_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)

def refine_qvar_tail_response():
    """Generates refined QVAR tail quantile response plot."""
    print("Generating refined QVAR tail response...")
    input_path = paths.QVAR_TABLE_DIR / "qvar_tail_quantile_response.csv"
    if not input_path.exists():
        print(f"Skipping QVAR tail response: {input_path} not found.")
        return

    df = pd.read_csv(input_path)
    # Filter for the response of MarketLSI to shocks
    # Expect columns like: step, response_quantile, shock_variable, response_variable, value
    # Check actual columns
    if "step" not in df.columns:
        # If it's a different structure, we skip or adapt.
        # Assuming typical IRF structure.
        return

    apply_cn_academic_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    quantiles = sorted(df["response_quantile"].unique(), reverse=True)
    colors = sns.color_palette("rocket_r", n_colors=len(quantiles))

    for i, q in enumerate(quantiles):
        subset = df[df["response_quantile"] == q]
        ax.plot(subset["step"], subset["value"], label=f"鍒嗕綅鏁?q={q}", color=colors[i], linewidth=1.8)

    ax.set_title("QVAR 灏鹃儴椋庨櫓浼犲: MarketLSI 瀵瑰啿鍑荤殑鍝嶅簲", fontsize=14)
    ax.set_xlabel("鍐插嚮鍚庢闀?(鍒嗛挓)", fontsize=12)
    ax.set_ylabel("鍝嶅簲寮哄害", fontsize=12)
    ax.legend(title="鍝嶅簲鍒嗕綅鏁?)

    output_path = paths.FIGURES_ROOT / "05_qvar" / "fig_refined_qvar_tail_response.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

def refine_rgarch_risk_paths():
    """Redraw refined RGARCH-CARR-SK risk paths with academic labels."""
    print("Generating refined RGARCH risk paths...")
    input_path = paths.RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_conditional_paths.csv"
    if not input_path.exists():
        print(f"Skipping RGARCH risk paths: {input_path} not found.")
        return

    df = pd.read_csv(input_path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")

    apply_cn_academic_style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    ax1.plot(df["datetime"], df["lambda_t"], color="black", linewidth=0.8, label="鏉′欢鏂瑰樊 (Lambda)")
    ax1.set_title("RGARCH-CARR-SK 浼拌鐨?MarketLSI 鏉′欢椋庨櫓璺緞", fontsize=14)
    ax1.set_ylabel("鏉′欢鍘嬪姏椋庨櫓", fontsize=12)
    ax1.legend()

    ax2.plot(df["datetime"], df["s_t"], color="tab:red", linewidth=0.8, label="鍔ㄦ€佸亸搴?)
    ax2.plot(df["datetime"], df["k_t"], color="tab:green", linewidth=0.8, label="鍔ㄦ€佸嘲搴?)
    ax2.set_title("MarketLSI 鍔ㄦ€侀珮闃剁煩婕斿寲", fontsize=14)
    ax2.set_ylabel("鏁板€?, fontsize=12)
    ax2.set_xlabel("鏃堕棿", fontsize=12)
    ax2.legend()

    output_path = paths.FIGURES_ROOT / "04_rgarch" / "fig_refined_rgarch_risk_evolution.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

def main():
    paths.ensure_runtime_dirs()
    refine_coverage_heatmap()
    refine_lsi_intraday()
    refine_market_lsi_ts()
    refine_smartboost_top5_rate()
    refine_smartboost_partial_effects()
    refine_rgarch_risk_paths()
    refine_qvar_tail_response()
    print("Post-visualization refinement completed.")

if __name__ == "__main__":
    main()
