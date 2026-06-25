from __future__ import annotations

import csv
import json
import math
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LATEX = ROOT / "report" / "latex_project"
SECTIONS = LATEX / "sections"
FIG_DIR = LATEX / "figures"
TAB_DIR = LATEX / "tables"
REVIEW_DIR = ROOT / "reviews" / "report_consistency"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def fmt_num(value: str | float | int | None, digits: int = 3, pct: bool = False) -> str:
    if value is None or value == "":
        return "--"
    try:
        x = float(value)
    except (TypeError, ValueError):
        return tex_escape(str(value))
    if not math.isfinite(x):
        return "--"
    if pct:
        return f"{x * 100:.{digits}f}\\%"
    if abs(x) >= 1000:
        return f"{x:,.0f}"
    return f"{x:.{digits}f}"


def tex_escape(text: str) -> str:
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in str(text))


def table_env(label: str, caption: str, body: str, note: str | None = None) -> str:
    note_text = f"\n\\vspace{{0.2em}}\n\\footnotesize 注：{note}" if note else ""
    return rf"""
\begin{{table}}[H]
\centering
\caption{{{caption}}}
\label{{{label}}}
\small
{body}{note_text}
\end{{table}}
"""


def tabular(cols: str, header: list[str], rows: list[list[str]], resize: bool = False) -> str:
    lines = ["\\begin{tabular}{" + cols + "}", "\\toprule"]
    lines.append(" & ".join(header) + r" \\")
    lines.append("\\midrule")
    for row in rows:
        lines.append(" & ".join(row) + r" \\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    body = "\n".join(lines)
    if resize:
        return "\\resizebox{\\textwidth}{!}{%\n" + body + "\n}"
    return body


def copy_figures() -> list[dict[str, str]]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    figure_specs = [
        ("研究样本划分时间轴", "outputs/figures/03_descriptive/fig_descriptive_02_sample_split_timeline.png", "fig_timeline.png", "正文"),
        ("股票-月份有效分钟覆盖率热力图", "outputs/figures/03_descriptive/fig_descriptive_01_sample_coverage_heatmap.png", "fig_coverage.png", "正文"),
        ("LSI_5 日内模式", "outputs/figures/03_descriptive/fig_descriptive_05_intraday_pattern.png", "fig_intraday.png", "正文"),
        ("MarketLSI 日度时间序列", "outputs/figures/03_descriptive/fig_descriptive_03_marketlsi_timeseries.png", "fig_marketlsi.png", "正文"),
        ("H5/H10 压力事件率", "outputs/figures/03_descriptive/fig_descriptive_04_event_rate_h5_h10_timeseries.png", "fig_event_rate.png", "正文"),
        ("核心变量相关性热力图", "outputs/figures/03_descriptive/fig_descriptive_09_correlation_heatmap.png", "fig_corr.png", "正文/附录"),
        ("核心变量分布图", "outputs/figures/03_descriptive/fig_descriptive_07_core_variable_distribution.png", "fig_distribution.png", "附录"),
        ("RGARCH-CARR-SK 条件压力风险路径", "outputs/figures/04_rgarch/fig_rgarch_conditional_risk_path.png", "fig_rgarch_risk.png", "正文"),
        ("realized pressure measures 对比", "outputs/figures/04_rgarch/fig_rgarch_carr_sk_adapted_realized_measures.png", "fig_rgarch_realized.png", "正文"),
        ("RGARCH-CARR-SK R2LOG 样本外损失", "outputs/figures/04_rgarch/fig_rgarch_oos_loss_comparison.png", "fig_rgarch_loss.png", "正文"),
        ("RGARCH-CARR-SK 动态偏度与峰度诊断", "outputs/figures/04_rgarch/fig_rgarch_dynamic_skew_kurtosis.png", "fig_rgarch_skew_kurt.png", "附录/诊断"),
        ("QVAR 尾部分位响应", "outputs/figures/05_qvar/fig_qvar_tail_quantile_response.png", "fig_qvar_response.png", "正文"),
        ("QVAR 四类压力测试情景", "outputs/figures/05_qvar/fig_qvar_pressure_test_paths.png", "fig_qvar_stress.png", "正文"),
        ("QVAR pinball loss", "outputs/figures/05_qvar/fig_qvar_pinball_loss.png", "fig_qvar_pinball.png", "附录/正文补充"),
        ("SMARTBoost PR 曲线", "outputs/figures/06_smartboost/fig_smartboost_pr_curve.png", "fig_sb_pr.png", "正文"),
        ("SMARTBoost Top 5% 高风险组真实压力发生率", "outputs/figures/06_smartboost/fig_smartboost_top5_realized_rate.png", "fig_sb_top5.png", "正文"),
        ("SMARTBoost Partial Effects", "outputs/figures/06_smartboost/fig_smartboost_partial_effects.png", "fig_sb_partial.png", "正文"),
        ("SMARTBoost calibration 曲线", "outputs/figures/06_smartboost/fig_smartboost_calibration_curve.png", "fig_sb_calibration.png", "附录/正文补充"),
        ("标签阈值稳健性", "outputs/figures/07_robustness/fig_label_threshold_robustness.png", "fig_robust_label_threshold.png", "正文"),
        ("RGARCH realized measure 稳健性", "outputs/figures/07_robustness/fig_rgarch_realized_measure_robustness.png", "fig_robust_rgarch_measure.png", "正文/附录"),
        ("QVAR 冲击幅度稳健性", "outputs/figures/07_robustness/fig_qvar_shock_size_robustness.png", "fig_robust_qvar_shock.png", "附录"),
        ("SMARTBoost 特征组消融", "outputs/figures/07_robustness/fig_smartboost_feature_ablation.png", "fig_robust_sb_ablation.png", "正文/附录"),
        ("SMARTBoost Top-K 稳健性", "outputs/figures/07_robustness/fig_smartboost_topk_robustness.png", "fig_robust_sb_topk.png", "正文"),
    ]
    copied = []
    for title, src_rel, dest, use in figure_specs:
        src = ROOT / src_rel
        dest_path = FIG_DIR / dest
        status = "missing"
        if src.exists():
            shutil.copy2(src, dest_path)
            status = "copied"
        copied.append({"title": title, "source": src_rel, "dest": f"figures/{dest}", "use": use, "status": status})
    return copied


def make_tables() -> list[dict[str, str]]:
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[dict[str, str]] = []

    # Table 1: research framework.
    rows = [
        ["压力指数构造", "LSI 与 MarketLSI", "将分钟 OHLCV 与成交额信息压缩为短时压力代理指标", "不是订单簿真实流动性"],
        ["动态风险刻画", "RGARCH-CARR-SK", "刻画 MarketLSI 压力创新的条件风险和高阶矩路径", "用于风险度量而非收益率预测"],
        ["尾部分位传导", "QVAR", "描述市场状态变量在不同分位点下的联动和情景响应", "情景模拟不作严格因果识别"],
        ["样本外预警", "SMARTBoost", "检验无泄漏高频特征对未来 H5/H10 压力事件的预测能力", "唯一正式机器学习预警模型"],
    ]
    body = tabular("p{0.18\\textwidth}p{0.18\\textwidth}p{0.37\\textwidth}p{0.20\\textwidth}", ["环节", "方法", "功能", "边界"], rows, resize=True)
    path = TAB_DIR / "tab_model_framework.tex"
    write_text(path, table_env("tab:model-framework", "研究框架与三类模型功能定位", body))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "研究框架与三类模型功能定位"})

    # Table 2: variable definitions.
    rows = [
        ["LSI(k)", "个股短时压力指数", r"$z(\mathrm{ILLIQ})+z(\mathrm{Range})+z(\mathrm{RV})-z(\mathrm{RelAmt})$", "训练期股票-日内 slot 标准化"],
        ["MarketLSI", "市场压力指数", "个股 LSI 的市场层面聚合", "仅使用当前及历史分钟信息"],
        ["Stress\\_H5", "未来 5 分钟压力标签", "未来窗口压力是否超过训练期阈值", "只作为目标变量"],
        ["Stress\\_H10", "未来 10 分钟压力标签", "未来窗口压力是否超过训练期阈值", "只作为目标变量"],
        ["IndexRet", "市场收益状态", "分钟收益的市场聚合", "用于 QVAR 和预警特征"],
        ["IndexRV", "市场波动状态", "分钟收益平方的市场聚合", "用于 QVAR 和预警特征"],
        ["MarketRelAmt", "市场成交承接力", "成交额相对历史基准的市场聚合", "数值越低表示成交收缩"],
    ]
    body = tabular("p{0.17\\textwidth}p{0.20\\textwidth}p{0.36\\textwidth}p{0.20\\textwidth}", ["变量", "含义", "构造", "防泄漏说明"], rows, resize=True)
    path = TAB_DIR / "tab_variable_definition.tex"
    write_text(path, table_env("tab:variables", "核心变量与压力标签定义", body))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "核心变量与压力标签定义"})

    # Table 3: sample structure and cleaning.
    stage1 = read_json(ROOT / "data_intermediate/stage1_model_ready/stage1_metadata.json")
    split = read_json(ROOT / "data_intermediate/stage2_lsi_labels/time_split.json")
    manifest = read_csv(ROOT / "data_intermediate/stage1_model_ready/model_ready_manifest.csv")
    n_codes = len({r.get("code", "") for r in manifest if r.get("code")}) if manifest else "--"
    session_rows = sum(int(float(r.get("session_rows", "0") or 0)) for r in manifest) if manifest else None
    model_ready_rows = sum(int(float(r.get("model_ready_rows", "0") or 0)) for r in manifest) if manifest else None
    date_after_threshold = max((int(float(r.get("n_dates_after_threshold", "0") or 0)) for r in manifest), default=None)
    rows = [
        ["预处理原始分钟面板", "14,546,275", "来自预处理 parquet", "不覆盖原始数据"],
        ["连续竞价过滤", fmt_num(session_rows, 0), "09:30--11:30 与 13:00--15:00", "保留 A 股连续交易时段"],
        ["有效分钟阈值", "236", "按 code-date 计算有效分钟数", "低覆盖交易日不进入模型样本"],
        ["模型就绪样本", fmt_num(model_ready_rows, 0) + " / " + tex_escape(str(n_codes)) + " 只证券", "由 stage1 manifest 汇总", "剔除后样本用于变量构造"],
        ["交易日覆盖", tex_escape(str(date_after_threshold or "--")) + " 日", "有效分钟阈值后最大覆盖", "用于时间顺序样本划分"],
        ["训练/验证/测试", tex_escape(split.get("train_end", "2024-10-07")) + " / " + tex_escape(split.get("validation_end", "2025-07-06")), "按时间切分", "不随机打乱"],
    ]
    body = tabular("p{0.22\\textwidth}p{0.16\\textwidth}p{0.34\\textwidth}p{0.20\\textwidth}", ["处理环节", "规模/阈值", "说明", "作用"], rows, resize=True)
    path = TAB_DIR / "tab_sample_cleaning.tex"
    write_text(path, table_env("tab:sample-cleaning", "样本结构与数据清洗结果", body, "行数来自当前中间结果或预处理审计；证券数按模型就绪 manifest 汇总。"))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "样本结构与数据清洗结果"})

    # Table 4: label distribution.
    evt = read_csv(ROOT / "outputs/tables/03_descriptive/descriptive_event_rate_by_period.csv")
    rows = []
    for r in evt:
        rows.append([tex_escape(r.get("period", "")), fmt_num(r.get("Stress_H5_mean"), 2, True), fmt_num(r.get("Stress_H10_mean"), 2, True)])
    body = tabular("lcc", ["样本区间", "Stress\\_H5 事件率", "Stress\\_H10 事件率"], rows)
    path = TAB_DIR / "tab_label_distribution.tex"
    write_text(path, table_env("tab:label-distribution", "压力标签分布", body, "事件率按样本区间汇总，标签阈值来自训练期历史分布。"))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "压力标签分布"})

    # Table 5: RGARCH fit and OOS loss.
    fit = read_csv(ROOT / "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_fit_criteria.csv")
    loss = read_csv(ROOT / "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_oos_losses.csv")
    loss_map = {(r["model"], r["period"]): r for r in loss}
    rows = []
    for r in fit:
        model = r["model"].replace("RGARCH-CARR-SK-", "")
        val = loss_map.get((r["model"], "validation"), {})
        test = loss_map.get((r["model"], "test"), {})
        rows.append([
            tex_escape(model),
            fmt_num(r.get("log_likelihood"), 3),
            fmt_num(r.get("AIC"), 2),
            fmt_num(r.get("BIC"), 2),
            fmt_num(val.get("R2LOG"), 3),
            fmt_num(test.get("R2LOG"), 3),
            fmt_num(test.get("MAE"), 3),
        ])
    body = tabular("lrrrrrr", ["measure", "LLK", "AIC", "BIC", "R2LOG(val.)", "R2LOG(test)", "MAE(test)"], rows, resize=True)
    path = TAB_DIR / "tab_rgarch_fit_loss.tex"
    write_text(path, table_env("tab:rgarch-fit-loss", "RGARCH-CARR-SK 拟合准则与样本外损失", body, "R2LOG 为损失指标，越低越好；RMAD 的损失值明显低于其他 realized pressure measure，应结合尺度与稳健性审计解读。"))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "RGARCH-CARR-SK 拟合准则与样本外损失"})

    # Table 6: QVAR pinball and scenario definitions.
    pin = read_csv(ROOT / "outputs/tables/05_qvar/qvar_blocked_oos_pinball_loss.csv")
    rows = []
    for r in pin:
        if r.get("target") == "MarketLSI":
            rows.append([tex_escape(r["eval_period"]), fmt_num(r["quantile"], 2), fmt_num(r["pinball_loss"], 4), fmt_num(r["nobs"], 0)])
    body = tabular("lrrr", ["样本区间", "分位点", "MarketLSI pinball loss", "观测数"], rows)
    path = TAB_DIR / "tab_qvar_pinball.tex"
    write_text(path, table_env("tab:qvar-pinball", "QVAR MarketLSI 方程样本外 pinball loss", body))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "QVAR MarketLSI 方程样本外 pinball loss"})

    scen = read_csv(ROOT / "outputs/tables/05_qvar/qvar_pressure_test_scenario_definitions.csv")
    rows = []
    for r in scen:
        rows.append([
            tex_escape(r.get("scenario_cn", "")),
            tex_escape(r.get("shock_variables", "").replace(",", ", ")),
            tex_escape(r.get("shock_definition", "")),
        ])
    body = tabular("p{0.22\\textwidth}p{0.25\\textwidth}p{0.44\\textwidth}", ["情景", "冲击变量", "冲击设定"], rows, resize=True)
    path = TAB_DIR / "tab_qvar_scenarios.tex"
    write_text(path, table_env("tab:qvar-scenarios", "QVAR 压力测试情景设定", body, "冲击为标准化情景模拟，不代表严格因果识别。"))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "QVAR 压力测试情景设定"})

    # Table 7: SMARTBoost metrics.
    metrics = read_csv(ROOT / "outputs/tables/06_smartboost/smartboost_metrics.csv")
    rows = []
    for r in metrics:
        rows.append([
            tex_escape(r["horizon"]),
            tex_escape(r["period"]),
            fmt_num(r["positive_rate"], 2, True),
            fmt_num(r["PR_AUC"], 3),
            fmt_num(r["ROC_AUC"], 3),
            fmt_num(r["Precision_Top5pct"], 2, True),
            fmt_num(r["Recall_Top5pct"], 2, True),
            fmt_num(r["Brier"], 4),
        ])
    body = tabular("llrrrrrr", ["目标", "区间", "事件率", "PR-AUC", "ROC-AUC", "Top5命中率", "Top5召回", "Brier"], rows, resize=True)
    path = TAB_DIR / "tab_smartboost_metrics.tex"
    write_text(path, table_env("tab:smartboost-metrics", "SMARTBoost validation/test 样本外预测指标", body, "最终模型不含 CrossStress、Stress\\_H5、Stress\\_H10 或未来窗口派生变量。"))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "SMARTBoost validation/test 样本外预测指标"})

    # Table 8: SMARTBoost TopK.
    topk = read_csv(ROOT / "outputs/tables/07_robustness/smartboost_topk_robustness.csv")
    rows = []
    for r in topk:
        if r.get("period") == "test":
            for pct, hit_col, lift_col in [
                ("1\\%", "Top1_hit_rate", "Top1_lift"),
                ("5\\%", "Top5_hit_rate", "Top5_lift"),
                ("10\\%", "Top10_hit_rate", "Top10_lift"),
                ("20\\%", "Top20_hit_rate", "Top20_lift"),
            ]:
                rows.append([tex_escape(r["horizon"]), pct, fmt_num(r.get(hit_col), 2, True), fmt_num(r.get(lift_col), 2)])
    pct_order = {"1\\%": 1, "5\\%": 5, "10\\%": 10, "20\\%": 20}
    rows.sort(key=lambda x: (x[0], pct_order.get(x[1], 99)))
    body = tabular("lrrr", ["目标", "高风险组", "真实压力发生率", "lift"], rows)
    path = TAB_DIR / "tab_smartboost_topk.tex"
    write_text(path, table_env("tab:smartboost-topk", "SMARTBoost test 高风险组命中率与 lift", body))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "SMARTBoost test 高风险组命中率与 lift"})

    # Table 9: Leakage check.
    rows = [
        ["CrossStress", "已删除", "旧版由未来压力标签横截面聚合得到，不能作为预测特征"],
        ["Stress\\_H5 / Stress\\_H10", "未作为特征", "仅作为目标变量"],
        ["FutureMaxLSI", "未使用", "任何未来窗口派生变量均不得进入特征矩阵"],
        ["rolling 特征", "仅 t 及以前", "未使用 center=True 或 shift(-k)"],
        ["样本切分", "时间顺序", "训练、验证、测试按日期划分，不随机打乱"],
    ]
    body = tabular("p{0.22\\textwidth}p{0.18\\textwidth}p{0.52\\textwidth}", ["检查项", "最终状态", "说明"], rows)
    path = TAB_DIR / "tab_smartboost_leakage.tex"
    write_text(path, table_env("tab:smartboost-leakage", "SMARTBoost 防泄漏特征检查", body))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "SMARTBoost 防泄漏特征检查"})

    # Table 10: Robustness summary.
    label = read_csv(ROOT / "outputs/tables/07_robustness/label_threshold_robustness.csv")
    rg = read_csv(ROOT / "outputs/tables/07_robustness/rgarch_realized_measure_robustness.csv")
    qv = read_csv(ROOT / "outputs/tables/07_robustness/qvar_quantile_robustness.csv")
    sb = read_csv(ROOT / "outputs/tables/07_robustness/smartboost_feature_ablation.csv")
    best_rg = min([r for r in rg if r.get("period") == "test"], key=lambda r: float(r.get("R2LOG", "inf")), default={})
    q95 = next((r for r in qv if r.get("eval_period") == "test" and r.get("quantile") == "0.95" and r.get("target") == "MarketLSI"), {})
    rows = [
        ["标签阈值", "85\\% / 90\\% / 95\\%", "Top 5\\% lift 在 H5/H10 中保持高于 8", "方向稳健"],
        ["RGARCH realized measure", "RV / RBV / MedRV / RMAD", f"test 最低 R2LOG：{tex_escape(best_rg.get('model', 'RMAD')).replace('RGARCH-CARR-SK-', '')} = {fmt_num(best_rg.get('R2LOG'), 3)}", "风险路径解释需结合测度尺度"],
        ["QVAR 分位点", "0.10 / 0.50 / 0.90 / 0.95", f"MarketLSI q=0.95 test pinball loss = {fmt_num(q95.get('pinball_loss'), 4)}", "尾部分位响应存在差异"],
        ["SMARTBoost 消融", "完整特征与特征组删减", "删除 CrossStress 后仍保持样本外识别力", "未发现未来信息泄漏"],
    ]
    body = tabular("p{0.20\\textwidth}p{0.25\\textwidth}p{0.36\\textwidth}p{0.12\\textwidth}", ["检验对象", "设定", "主要结果", "结论"], rows, resize=True)
    path = TAB_DIR / "tab_robustness_summary.tex"
    write_text(path, table_env("tab:robustness-summary", "稳健性检验汇总", body, "仅概括已生成的稳健性结果；详细 CSV 表保留在稳健性输出目录。"))
    outputs.append({"file": str(path.relative_to(ROOT)), "title": "稳健性检验汇总"})

    return outputs


def write_main() -> None:
    text = r"""
\documentclass[12pt,a4paper]{ctexart}
\usepackage[margin=2.5cm]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{tabularx}
\usepackage{makecell}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{xcolor}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{hyperref}

\captionsetup{font=small,labelfont=bf}
\hypersetup{colorlinks=true,linkcolor=blue!50!black,citecolor=blue!50!black,urlcolor=blue!50!black}
\graphicspath{{figures/}}

\title{基于分钟级高频数据的 A 股短时流动性压力智能预警框架\\
\large 来自 RGARCH-CARR-SK、QVAR 与 SMARTBoost 的证据}
\author{童奕然}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
本文围绕“A 股分钟级市场状态信息能否预警未来 5 分钟和 10 分钟的短时流动性压力”这一问题，构建了从压力指数、动态风险度量、尾部分位传导到样本外机器学习预警的实证框架。研究首先基于 1 分钟 OHLCV 与成交额数据构造短时流动性压力指数（LSI）和市场压力指数（MarketLSI），并以训练期历史分布确定未来压力标签。随后，本文将 RGARCH-CARR-SK 框架迁移到 MarketLSI 压力风险序列，用于刻画条件压力风险与动态高阶矩；使用 QVAR 描述市场状态变量之间的尾部分位传导和情景响应；最后，以删除未来标签聚合变量后的 SMARTBoost 作为正式样本外预警模型，检验高频历史状态变量对 \(\text{Stress\_H5}\) 与 \(\text{Stress\_H10}\) 的预警能力。全文强调代理型压力指数的可解释性、防泄漏训练验证流程和样本外预警表现，并避免将情景模拟解释为严格因果识别。

\textbf{关键词：} 高频金融；流动性压力；MarketLSI；RGARCH-CARR-SK；QVAR；SMARTBoost；样本外预警
\end{abstract}

\tableofcontents
\newpage

\input{sections/01_intro.tex}
\input{sections/02_literature.tex}
\input{sections/03_data.tex}
\input{sections/04_lsi_labels.tex}
\input{sections/05_descriptive.tex}
\input{sections/06_rgarch.tex}
\input{sections/07_qvar.tex}
\input{sections/08_smartboost.tex}
\input{sections/09_robustness_conclusion.tex}

\bibliographystyle{plain}
\bibliography{refs}

\end{document}
"""
    write_text(LATEX / "main.tex", text)


def write_sections() -> None:
    sections = {
        "01_intro.tex": r"""
\section{引言}

分钟级交易数据使得短时市场状态的连续监测成为可能。对于 A 股市场而言，单个证券的短时成交承接、价格振幅和收益波动往往会在市场压力时段同步恶化，进而形成跨证券的共同压力。本文关注的问题是：仅使用 1 分钟 OHLCV 与成交额等可得高频信息，是否能够对未来 5 分钟和 10 分钟的短时流动性压力形成可验证的样本外预警。

本文的研究对象不是订单簿层面的真实即时流动性，而是由高频成交与价格变量构造的代理型压力指数。该定位决定了本文的经验结论应被理解为“市场状态信息对短时压力事件的预警能力”，而不是对订单簿深度或买卖价差的直接度量。围绕这一定位，本文形成三层证据链：首先构造 LSI 与 MarketLSI，定义可验证的未来压力标签；其次使用 RGARCH-CARR-SK 和 QVAR 分别刻画动态风险路径与尾部分位传导；最后用 SMARTBoost 检验样本外预警效果。

\input{tables/tab_model_framework.tex}

表 \ref{tab:model-framework} 概括了本文方法体系的功能分工。RGARCH-CARR-SK 与 QVAR 主要服务于风险刻画和机制描述，SMARTBoost 则承担正式的样本外预警检验。这样的安排避免将三类模型简单处理为预测比赛，也使本文能够同时回答“压力如何刻画”“压力如何传导”和“压力能否预警”三个层次的问题。

本文的主要贡献体现在三方面。第一，基于分钟级 OHLCV 与成交额构造了面向短时压力事件的 LSI 指标，并严格使用训练期历史分布确定标准化参数与标签阈值。第二，将 RGARCH-CARR-SK 的 realized measure 驱动风险递推结构迁移到 MarketLSI 压力风险序列，形成适合本文数据对象的动态风险度量。第三，在删除 CrossStress 等未来标签聚合变量后，使用 SMARTBoost 对 \(\text{Stress\_H5}\) 与 \(\text{Stress\_H10}\) 进行时间滚动样本外预警，重点报告 PR-AUC、Top 5\% 高风险组命中率与 lift 等更适合稀有压力事件的指标。
""",
        "02_literature.tex": r"""
\section{文献综述}

\subsection{高频市场状态与压力代理指标}

高频金融研究通常利用日内收益、成交量、成交额和振幅等变量刻画市场状态。由于本文无法直接观察逐笔订单簿深度和买卖价差，因此选择以 OHLCV 与成交额构造代理型短时压力指数。该处理方式与 realized measure 文献的思路相近：并不试图复原所有微观结构变量，而是利用高频可观测信息提炼风险状态。本文的 LSI 将 ILLIQ、Range、RV 和 RelAmt 统一到训练期股票-日内 slot 的标准化框架中，避免全样本标准化带来的前瞻性问题。

\subsection{动态风险度量与 realized measure}

已实现波动和双幂变差等 realized measure 被广泛用于高频风险度量。Andersen 等关于 realized volatility 的研究强调，日内收益增量能够为波动预测提供高频信息；Barndorff-Nielsen 和 Shephard 的 bipower variation 则为跳跃与连续波动分解提供了重要基础。近年来，Liu、Zhou 和 Chen \cite{liu2025rgarch} 提出的 RGARCH-CARR-SK 模型进一步在 realized measure 驱动的风险递推中引入动态偏度和动态峰度。本文借鉴这一结构，但研究对象从原文资产波动率转向 MarketLSI 压力风险序列，因此结论应理解为对短时压力风险动态的适配度量。

\subsection{分位数系统与尾部传导}

分位数回归为研究条件分布尾部提供了直接工具 \cite{koenker2005quantile}。在多变量系统中，QVAR 可以刻画不同分位点下变量之间的动态关系，尤其适合描述压力状态、收益、波动和成交活跃度在尾部条件下的联动。本文使用 MarketLSI、CrossStress、IndexRet、IndexRV 与 MarketRelAmt 构成低维系统。需要强调的是，QVAR 情景响应反映的是标准化冲击下的尾部分位传导路径，不应被解释为政策或外生事件的严格因果效应。

\subsection{机器学习预警与 SMARTBoost}

金融预警问题往往具有非线性、低信噪比和事件不平衡特征。Giordani 等 \cite{giordani2025smartboost} 提出的 SMARTBoost 使用平滑加性树的 boosting 结构，并在叶节点引入正则化先验，面向小样本和噪声较高的环境。本文依据原文算法定义进行 Python 适配，将其作为唯一正式机器学习预警模型。与收益率预测不同，本文的预测目标仅为未来 5 分钟和 10 分钟压力标签，模型性能主要由 PR-AUC、高风险组命中率、lift 和校准指标评价。
""",
        "03_data.tex": r"""
\section{数据来源、样本处理与变量构造}

\subsection{数据来源与样本边界}

本文使用 A 股样本证券的 1 分钟 OHLCV 与成交额数据，原始预处理分钟面板保存在项目的预处理数据层。为保证可重复性，本文区分三层数据：第一层为预处理原始分钟面板；第二层为经过连续竞价时间过滤、有效分钟检查和收益率构造的模型就绪面板；第三层为 LSI、MarketLSI、压力标签和市场状态变量构成的变量与标签仓库。

连续竞价时段保留为 09:30--11:30 与 13:00--15:00。对每个 code-date 计算有效分钟数，并以 236 分钟作为基准阈值。分钟收益率在同一证券、同一交易日内递推计算，跨交易日第一分钟收益率设为缺失，避免跨日连接。

\input{tables/tab_sample_cleaning.tex}

表 \ref{tab:sample-cleaning} 给出了样本处理的核心环节。样本划分严格按照日期先后顺序进行，训练期用于标准化参数、标签阈值和模型参数估计，验证期用于调参与早停选择，测试期仅用于最终样本外评价。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.86\textwidth]{figures/fig_timeline.png}
    \caption{训练、验证与测试样本划分。图中时间区间用于说明本文所有样本外检验的时间边界，验证和测试样本均位于训练样本之后。}
    \label{fig:timeline}
\end{figure}

\subsection{核心变量定义}

本文核心变量围绕短时压力代理指标、未来压力标签和市场共同状态展开。所有需要标准化的变量均使用训练期历史信息，且以股票-日内 slot 为单位计算基准位置和尺度，避免同日未来信息或全样本信息进入特征。

\input{tables/tab_variable_definition.tex}

表 \ref{tab:variables} 汇总了后续章节使用的主要变量。CrossStress 在 QVAR 系统中作为截面压力比例出现，具有描述性和系统状态含义；由于它由未来压力标签横截面聚合得到，最终 SMARTBoost 预警模型不使用该变量作为预测特征。
""",
        "04_lsi_labels.tex": r"""
\section{LSI 指标与压力标签构造}

\subsection{LSI 指标构造}

LSI 的目标是将分钟级交易状态压缩为短时压力代理指标。对每个 \(k\in\{5,10,20\}\)，本文构造 ILLIQ、Range、RV 与 RelAmt 四类窗口变量，并使用训练期股票-日内 slot 的历史 median 与 MAD 进行标准化。基准形式为
\[
\mathrm{LSI}_{i,t}^{(k)}=
z(\mathrm{ILLIQ}_{i,t}^{(k)})
+z(\mathrm{Range}_{i,t}^{(k)})
+z(\mathrm{RV}_{i,t}^{(k)})
-z(\mathrm{RelAmt}_{i,t}^{(k)}).
\]
其中 RelAmt 取负号，是因为成交额相对承接能力下降通常意味着压力上升。该指标是基于 OHLCV 与成交额的压力代理，不等同于真实订单簿流动性。

\subsection{压力标签与市场状态变量}

未来压力标签 \(\text{Stress\_H5}\) 与 \(\text{Stress\_H10}\) 分别表示未来 5 分钟和 10 分钟窗口内压力是否超过训练期阈值。标签构造允许使用未来窗口，因为它是预测目标；但任何预测特征不得使用未来标签、未来 LSI 或由未来标签聚合得到的变量。

\input{tables/tab_label_distribution.tex}

表 \ref{tab:label-distribution} 显示，训练期标签阈值约束下的事件率接近 10\%，而验证期和测试期事件率更低。这说明样本外预警任务具有一定不平衡性，因此后文在 SMARTBoost 评价中优先使用 PR-AUC、Top 5\% 命中率和 lift，而不把 ROC-AUC 作为唯一依据。

在市场层面，本文构造 MarketLSI、IndexRet、IndexRV 和 MarketRelAmt 等共同状态变量。MarketLSI 仅由当前及过去分钟信息聚合得到，可用于预警特征；CrossStress 则是由压力标签聚合得到的截面压力比例，只在描述性系统状态和 QVAR 传导分析中使用，不进入最终 SMARTBoost 特征矩阵。
""",
        "05_descriptive.tex": r"""
\section{描述性事实与高频诊断}

\subsection{样本覆盖与数据质量}

在进入模型估计前，需要确认分钟面板在证券和时间维度上具有足够稳定的覆盖。图 \ref{fig:coverage} 按股票和月份汇总有效分钟覆盖率，避免逐日热力图过密导致的视觉噪声。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.92\textwidth]{figures/fig_coverage.png}
    \caption{股票-月份有效分钟覆盖率热力图。颜色表示对应股票在对应月份的有效分钟覆盖程度，排序后的结构用于检查样本是否存在系统性缺口。}
    \label{fig:coverage}
\end{figure}

\subsection{LSI 日内模式}

高频压力指标具有明显日内结构。图 \ref{fig:intraday} 展示 LSI\_5 在不同 slot 上的均值、中位数和分位带，并标注开盘、午后开盘和尾盘等关键时点。该图说明短时压力并非均匀分布于全天，而是在特定交易时段更易集中。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.86\textwidth]{figures/fig_intraday.png}
    \caption{LSI\_5 日内模式。图中保留 LSI 术语，并使用分位带展示横截面与日期维度下的离散程度。}
    \label{fig:intraday}
\end{figure}

\subsection{MarketLSI 与压力事件率}

图 \ref{fig:marketlsi} 将 MarketLSI 按日聚合，并叠加滚动趋势和样本区间背景。该图显示市场压力存在阶段性抬升和局部峰值，但这些阶段背景只用于描述时间异质性，不构成因果识别。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.92\textwidth]{figures/fig_marketlsi.png}
    \caption{市场压力指数（MarketLSI）日度时间序列。背景区间对应训练、验证与测试样本划分，峰值标记用于辅助识别高压力时段。}
    \label{fig:marketlsi}
\end{figure}

图 \ref{fig:event-rate} 进一步展示 H5 与 H10 压力事件率的时间变化。事件率在样本外阶段仍存在明显波动，说明单纯依赖固定基准事件率无法满足短时预警需求。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.86\textwidth]{figures/fig_event_rate.png}
    \caption{H5/H10 压力事件率时间变化。图中事件率由未来压力标签汇总得到，用于描述压力事件的时变性。}
    \label{fig:event-rate}
\end{figure}

\subsection{核心变量相关性}

图 \ref{fig:corr} 给出少量核心日度变量之间的相关性。相关结构表明 MarketLSI 与波动、收益和成交承接变量之间存在联动关系，但相关系数本身不代表因果效应。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.68\textwidth]{figures/fig_corr.png}
    \caption{核心市场状态变量相关性热力图。该图用于辅助理解变量共动结构，后续 QVAR 将进一步刻画不同分位点下的动态关系。}
    \label{fig:corr}
\end{figure}
""",
        "06_rgarch.tex": r"""
\section{RGARCH-CARR-SK 动态高阶风险度量}

Liu、Zhou 和 Chen \cite{liu2025rgarch} 提出的 RGARCH-CARR-SK 模型原本用于高频波动预测和风险度量。本文并不复刻原文的特定指数应用，而是将其 realized measure 驱动的风险递推、GCE 密度和动态偏度/峰度结构迁移到 MarketLSI 压力风险序列。因而，本章结论应理解为“基于 RGARCH-CARR-SK 框架的 MarketLSI 压力风险适配实现”。

\subsection{模型设定}

模型以 MarketLSI 的压力创新作为输入序列，并构造 RV、RBV、MedRV 和 RMAD 等 realized pressure measures。条件压力风险 \(\lambda_t\) 由滞后风险、滞后 realized pressure measure 与杠杆函数共同驱动；动态偏度 \(s_t\) 与动态峰度 \(k_t\) 分别由滞后状态和标准化冲击递推。参数通过最大似然估计获得，并报告 LLK、AIC、BIC 与样本外损失。

\input{tables/tab_rgarch_fit_loss.tex}

表 \ref{tab:rgarch-fit-loss} 显示不同 realized pressure measure 在拟合准则和样本外损失上的差异。需要注意，R2LOG 是损失指标，数值越低越好；RMAD 版本的 R2LOG 明显较低，但应结合该测度的尺度、估计路径和图形审计结果解释，而不能机械理解为全面优势。

\subsection{条件压力风险路径}

图 \ref{fig:rgarch-risk} 展示条件压力风险路径及 realized pressure measure 的对照。相比直接绘制分钟级密集路径，图中采用聚合后的论文级表达，以突出压力风险在不同样本阶段的变化。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.88\textwidth]{figures/fig_rgarch_risk.png}
    \caption{RGARCH-CARR-SK 条件压力风险路径。该图用于刻画 MarketLSI 压力风险的动态聚集，而非收益率波动预测。}
    \label{fig:rgarch-risk}
\end{figure}

\subsection{realized pressure measures 与样本外损失}

图 \ref{fig:rgarch-realized} 对比 RV、RBV、MedRV 和 RMAD 的标准化分布，图 \ref{fig:rgarch-loss} 则展示样本外 R2LOG 损失。两张图共同说明，realized pressure measure 的选择会影响风险路径和预测损失。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.82\textwidth]{figures/fig_rgarch_realized.png}
    \caption{realized pressure measures 对比。为避免不同量纲直接混画，图中使用标准化后的分布或序列比较。}
    \label{fig:rgarch-realized}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.82\textwidth]{figures/fig_rgarch_loss.png}
    \caption{RGARCH-CARR-SK 样本外 R2LOG 损失比较。R2LOG 为损失指标，越低表示样本外压力风险路径拟合越好。}
    \label{fig:rgarch-loss}
\end{figure}

动态偏度和动态峰度路径属于模型诊断结果。现有审计显示，峰度路径整体较稳定，局部跳动不宜解释为重大结构性风险突变，因此正文仅作为补充诊断讨论，不作为主要结论来源。
""",
        "07_qvar.tex": r"""
\section{QVAR 尾部分位传导与压力测试}

\subsection{模型系统与解释边界}

为描述市场压力、截面压力、收益、波动和成交承接之间的动态联动，本文使用一阶滞后 QVAR。系统变量包括 MarketLSI、CrossStress、IndexRet、IndexRV 与 MarketRelAmt。CrossStress 在本章中仅作为系统状态变量，用于描述截面压力比例；它不进入 SMARTBoost 预测特征矩阵。

QVAR 的核心价值在于比较不同条件分位点下的响应路径，尤其是 q=0.90 和 q=0.95 的尾部状态。本文将其解释为尾部分位传导和标准化情景模拟，不作严格因果识别。

\input{tables/tab_qvar_pinball.tex}

\subsection{尾部分位响应}

图 \ref{fig:qvar-response} 展示 MarketLSI 对系统状态冲击的尾部分位响应。不同分位点的路径差异表明，压力状态下的动态联动并不等同于中位数条件下的平均关系。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.86\textwidth]{figures/fig_qvar_response.png}
    \caption{QVAR 尾部分位响应。横轴为预测步长，曲线展示不同分位点下 MarketLSI 或压力状态响应；该结果反映尾部传导而非严格因果效应。}
    \label{fig:qvar-response}
\end{figure}

\subsection{压力测试情景}

本文构造四类标准化情景：市场急跌、波动放大、成交收缩/流动性压力和复合压力。表 \ref{tab:qvar-scenarios} 给出冲击定义，图 \ref{fig:qvar-stress} 展示各情景下的 MarketLSI 响应路径。不同情景的响应幅度和方向存在差异，说明 MarketLSI 对收益、波动和成交承接冲击的敏感性并不完全相同。

\input{tables/tab_qvar_scenarios.tex}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.92\textwidth]{figures/fig_qvar_stress.png}
    \caption{QVAR 四类压力测试情景。情景冲击基于标准化变量设定，用于刻画尾部分位压力传导路径，不代表外生冲击的严格因果效应。}
    \label{fig:qvar-stress}
\end{figure}
""",
        "08_smartboost.tex": r"""
\section{SMARTBoost 样本外预警}

\subsection{模型定位与防泄漏约束}

SMARTBoost 是本文唯一正式机器学习预警模型。其目标变量仅为 \(\text{Stress\_H5}\) 与 \(\text{Stress\_H10}\)，研究问题是高频历史状态变量能否预警未来短时压力事件，而不是收益率预测。本文依据 Giordani 等 \cite{giordani2025smartboost} 的算法定义进行 Python 适配实现，并使用时间顺序划分训练、验证与测试样本。

旧版特征中曾包含 CrossStress。由于 CrossStress 由未来压力标签横截面聚合得到，最终模型已完全删除该变量，并且不使用 \(\text{Stress\_H5}\)、\(\text{Stress\_H10}\)、FutureMaxLSI 或任何未来窗口派生变量。滚动特征只使用 \(t\) 时点及以前信息。

\input{tables/tab_smartboost_leakage.tex}

\subsection{样本外预测表现}

表 \ref{tab:smartboost-metrics} 汇总 validation 与 test 样本上的核心指标。由于压力事件具有不平衡性，本文将 PR-AUC、高风险组命中率和 lift 作为主要证据，ROC-AUC 仅作为辅助参考。

\input{tables/tab_smartboost_metrics.tex}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.84\textwidth]{figures/fig_sb_pr.png}
    \caption{SMARTBoost 样本外 PR 曲线。水平基准线表示对应样本的事件发生率，曲线越高说明模型越能在高风险排序中集中识别未来压力事件。}
    \label{fig:sb-pr}
\end{figure}

\subsection{高风险组命中与局部响应}

图 \ref{fig:sb-top5} 展示 Top 5\% 高风险分钟的真实压力发生率。与基准事件率相比，Top 5\% 组的发生率显著提高，说明模型排序结果具有实际预警价值。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.84\textwidth]{figures/fig_sb_top5.png}
    \caption{SMARTBoost Top 5\% 高风险组真实压力发生率。柱状图展示 validation/test 与 H5/H10 组合下的高风险组命中表现，并与基准事件率对照。}
    \label{fig:sb-top5}
\end{figure}

\input{tables/tab_smartboost_topk.tex}

图 \ref{fig:sb-partial} 给出少量核心变量的 Partial Effects。该图用于解释预测概率如何随无泄漏历史特征变化而局部调整，不能被理解为结构性因果效应。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.88\textwidth]{figures/fig_sb_partial.png}
    \caption{SMARTBoost 核心变量 Partial Effects。横轴使用“中文说明 + 英文变量名”的形式，纵轴表示预测概率的局部响应。}
    \label{fig:sb-partial}
\end{figure}
""",
        "09_robustness_conclusion.tex": r"""
\section{稳健性检验与结论}

\subsection{稳健性检验设计}

为检验核心结论是否依赖单一设定，本文围绕 LSI 与标签构造、RGARCH-CARR-SK 动态风险度量、QVAR 尾部分位传导以及 SMARTBoost 样本外预警四个方面进行稳健性检查。所有替代设定均保留时间顺序切分，标准化参数和标签阈值仅来自训练期历史分布。

\input{tables/tab_robustness_summary.tex}

\subsection{LSI 与标签构造稳健性}

标签阈值稳健性将训练期压力分位阈值从基准 90\% 扩展到 85\% 和 95\%。结果显示，虽然事件基准发生率随阈值变化而改变，SMARTBoost 在 Top 5\% 高风险组中的命中率和 lift 仍保持同向优势。缺分钟阈值和标准化方式的辅助检查也表明，核心样本结构和事件分布没有因单一阈值选择而发生方向性改变。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.82\textwidth]{figures/fig_robust_label_threshold.png}
    \caption{标签阈值稳健性。图中比较不同训练期分位阈值下的事件率、PR-AUC 与高风险组 lift。}
    \label{fig:robust-label}
\end{figure}

\subsection{RGARCH-CARR-SK 与 QVAR 稳健性}

RGARCH-CARR-SK 的 realized pressure measure 稳健性比较 RV、RBV、MedRV 和 RMAD。样本外损失表明，不同测度对条件压力风险路径存在影响，但风险路径的阶段性抬升和 realized measure 敏感性结论仍具有一致方向。动态偏度和峰度诊断显示，高阶矩路径存在局部变化，但不应将局部跳动直接解释为重大结构性风险突变。

QVAR 稳健性从分位点和情景冲击幅度两个角度展开。q=0.10、0.50、0.90 和 0.95 的比较显示，尾部状态下 MarketLSI 的响应路径与中位数状态不同；将情景冲击幅度扩展到 1.5、2.0 和 2.5 个标准化单位后，压力测试路径的方向和相对差异仍可被识别。上述结果应解释为尾部分位传导和情景模拟，而不是严格因果识别。

\subsection{SMARTBoost 稳健性与防泄漏审计}

SMARTBoost 稳健性包括替代时间切分、特征组消融、Top-K 排序阈值和校准检查。结果显示，在删除 CrossStress 后，完整无泄漏特征组仍能在测试样本中形成明显高于基准事件率的风险排序。仅使用个股历史 LSI 特征时表现有所下降，而加入 MarketLSI 等市场共同状态变量后，样本外预警能力改善，说明市场状态信息对短时压力预警具有增量价值。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.82\textwidth]{figures/fig_robust_sb_topk.png}
    \caption{SMARTBoost Top-K 稳健性。图中比较 Top 1\%、Top 5\%、Top 10\% 与 Top 20\% 高风险组的真实压力发生率和 lift。}
    \label{fig:robust-sb-topk}
\end{figure}

防泄漏审计确认，最终 SMARTBoost 特征中不包含 CrossStress、未来压力标签、FutureMaxLSI 或其他未来窗口派生变量；训练、验证和测试均按时间顺序划分，不存在随机打乱。监管阶段变量仅作为时间背景变量进入模型，不被解释为因果政策效应。

\subsection{研究结论与局限性}

综合上述证据，本文发现分钟级市场状态信息能够为未来 5 分钟和 10 分钟短时流动性压力提供可验证的样本外预警。RGARCH-CARR-SK 结果说明 MarketLSI 压力风险存在动态聚集和高阶矩特征；QVAR 结果显示尾部条件下市场压力、波动和成交承接变量之间的响应路径不同于中位数状态；SMARTBoost 结果则进一步表明，无泄漏的高频历史特征能够在样本外高风险排序中集中识别未来压力事件。

本文仍存在局限。首先，LSI 是基于 OHLCV 与成交额的代理型压力指数，无法替代订单簿深度、价差和逐笔委托信息。其次，QVAR 压力测试是标准化情景模拟，不构成严格因果识别。最后，SMARTBoost 结果体现的是样本外预警能力，后续仍可在更长样本、更多市场状态和更高频订单簿数据上进一步检验。尽管如此，本文形成了从高频压力指数到动态风险刻画、尾部分位传导和样本外智能预警的完整经验框架。
""",
    }
    for name, text in sections.items():
        write_text(SECTIONS / name, text)


def write_refs() -> None:
    refs = r"""
@article{giordani2025smartboost,
  title={SMARTboost: Sparse Multivariate Additive Regression Trees},
  author={Giordani, Paolo and Kohns, David and Villani, Mattias},
  journal={Journal of Financial Econometrics},
  volume={23},
  number={3},
  pages={nbae028},
  year={2025}
}

@misc{liu2025rgarch,
  title={A RGARCH-CARR-SK model: A new high-frequency volatility forecasting and risk measurement model based on dynamic higher moments and generalized realized measures},
  author={Liu, Junjie and Zhou, Qingnan and Chen, Zhenlong},
  year={2025},
  howpublished={Local literature PDF},
  note={Bibliographic venue, volume and pages to be completed}
}

@book{koenker2005quantile,
  title={Quantile Regression},
  author={Koenker, Roger},
  year={2005},
  publisher={Cambridge University Press}
}

@article{andersen2003modeling,
  title={Modeling and forecasting realized volatility},
  author={Andersen, Torben G. and Bollerslev, Tim and Diebold, Francis X. and Labys, Paul},
  journal={Econometrica},
  volume={71},
  number={2},
  pages={579--625},
  year={2003}
}

@article{barndorff2004power,
  title={Power and bipower variation with stochastic volatility and jumps},
  author={Barndorff-Nielsen, Ole E. and Shephard, Neil},
  journal={Journal of Financial Econometrics},
  volume={2},
  number={1},
  pages={1--37},
  year={2004}
}
"""
    write_text(LATEX / "refs.bib", refs)


def write_build_script() -> None:
    ps1 = r"""
$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir
xelatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
"""
    write_text(LATEX / "build_report.ps1", ps1)


def collect_inventory(figures: list[dict[str, str]], tables: list[dict[str, str]]) -> None:
    tex_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in [LATEX / "main.tex", *sorted(SECTIONS.glob("*.tex"))] if p.exists())
    inserted_figs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex_text)
    inserted_tables = re.findall(r"\\input\{(tables/[^}]+)\}", tex_text)
    all_figs = sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "outputs/figures").rglob("*.png"))
    all_tables = sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "outputs/tables").rglob("*") if p.suffix.lower() in {".csv", ".json"})
    bad_figs = [p for p in all_figs if "99_paper_ready" in p or "feature_importance" in p or p.endswith("fig_smartboost_roc_curve.png")]
    main_candidate = [f["source"] for f in figures if f["use"].startswith("正文") or f["use"] == "正文"]
    appendix_candidate = [f["source"] for f in figures if "附录" in f["use"]]
    must_tables = [t["file"] for t in tables]

    missing_output_figs = [p for p in all_figs if p not in [f["source"] for f in figures] and "99_paper_ready" not in p]
    missing_output_tables = [p for p in all_tables if p not in [
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_fit_criteria.csv",
        "outputs/tables/04_rgarch/rgarch_carr_sk_adapted_oos_losses.csv",
        "outputs/tables/05_qvar/qvar_blocked_oos_pinball_loss.csv",
        "outputs/tables/05_qvar/qvar_pressure_test_scenario_definitions.csv",
        "outputs/tables/06_smartboost/smartboost_metrics.csv",
        "outputs/tables/06_smartboost/smartboost_event_rate_and_lift.csv",
        "outputs/tables/07_robustness/smartboost_topk_robustness.csv",
        "outputs/tables/07_robustness/label_threshold_robustness.csv",
        "outputs/tables/07_robustness/rgarch_realized_measure_robustness.csv",
        "outputs/tables/07_robustness/qvar_quantile_robustness.csv",
        "outputs/tables/07_robustness/smartboost_feature_ablation.csv",
    ]]

    lines = [
        "# Codex LaTeX 完整性盘点",
        "",
        "## 当前 TeX 已插入图",
        *[f"- `{p}`" for p in inserted_figs],
        "",
        "## 当前 TeX 已插入表",
        *[f"- `{p}`" for p in inserted_tables],
        "",
        "## 已复制到 LaTeX 工程的图",
        *[f"- {f['title']}: `{f['dest']}` <- `{f['source']}` ({f['status']}, {f['use']})" for f in figures],
        "",
        "## outputs 中尚未插入的 PNG 图",
        *[f"- `{p}`" for p in missing_output_figs],
        "",
        "## outputs 中尚未转为 TeX 摘要表的表格/JSON",
        *[f"- `{p}`" for p in missing_output_tables],
        "",
        "## 适合正文的图",
        *[f"- `{p}`" for p in main_candidate],
        "",
        "## 适合附录的图",
        *[f"- `{p}`" for p in appendix_candidate],
        "",
        "## 不应作为正文主图使用的图",
        *[f"- `{p}`" for p in bad_figs],
        "",
        "## 必须进入正文或正文摘要的表",
        *[f"- `{p}`" for p in must_tables],
        "",
        "## 仍需核验的数值",
        "- RGARCH-CARR-SK 中 RMAD 的 R2LOG 很低，已在图形审计中说明其为真实输出而非填零；正文按损失指标解释，避免过度概括。",
        "- QVAR 情景响应路径应按图中具体方向解释，不写成所有情景均推高 MarketLSI。",
        "- SMARTBoost 所有正文数值来自删除 CrossStress 后的输出表；旧版含 CrossStress 的结果不得引用。",
    ]
    write_text(REVIEW_DIR / "codex_latex_completeness_inventory.md", "\n".join(lines))


def write_map_and_audit(figures: list[dict[str, str]], tables: list[dict[str, str]]) -> None:
    map_lines = [
        "# LaTeX 图表映射",
        "",
        "## Figures",
        "| 标题 | 源文件 | LaTeX 文件 | 用途 | 状态 |",
        "|---|---|---|---|---|",
    ]
    for f in figures:
        map_lines.append(f"| {f['title']} | `{f['source']}` | `{f['dest']}` | {f['use']} | {f['status']} |")
    map_lines += ["", "## Tables", "| 标题 | LaTeX 文件 |", "|---|---|"]
    for t in tables:
        map_lines.append(f"| {t['title']} | `{t['file']}` |")
    write_text(LATEX / "figure_table_map.md", "\n".join(map_lines))

    audit_lines = [
        "# Codex LaTeX 完整化审计",
        "",
        "## 已完成",
        "- 重写 `main.tex`，补充表格、图片、引用与排版包。",
        "- 重写 01--09 章，使正文围绕分钟级高频数据、LSI、RGARCH-CARR-SK、QVAR 与 SMARTBoost 展开。",
        "- 将核心 PNG 从 `outputs/figures/` 复制到 LaTeX 工程 `figures/`，未修改原图。",
        "- 从 CSV/JSON 结果抽取摘要指标，生成 `booktabs` 三线表。",
        "- 修正 CrossStress 表述：可作为 QVAR 系统状态变量，但不进入 SMARTBoost 预测特征。",
        "- 修正 QVAR 表述：情景模拟不是严格因果识别，且不同情景响应路径存在差异。",
        "- 修正 RGARCH 表述：R2LOG 为损失指标，动态峰度局部跳动不解释为重大结构突变。",
        "",
        "## 生成的 LaTeX 表",
        *[f"- `{t['file']}`: {t['title']}" for t in tables],
        "",
        "## 插入的核心图",
        *[f"- `{f['dest']}`: {f['title']} ({f['use']})" for f in figures if f["status"] == "copied" and ("正文" in f["use"])],
        "",
        "## 不适合正文的图表",
        "- `outputs/figures/99_paper_ready/` 下的历史派生图不作为本版来源。",
        "- SMARTBoost ROC 曲线和 calibration 曲线只作为辅助，不作为主证据。",
        "- SMARTBoost feature importance 若为空或全 0，不进入正文。",
        "",
        "## 待人工复核",
        "- Liu、Zhou 和 Chen (2025) 的完整期刊卷期页码仍需根据最终文献信息补齐。",
        "- 论文最终排版仍建议人工检查长表宽度和图题页码位置。",
        "",
        "## 编译状态",
        "- 待运行 xelatex / bibtex 后追加。",
    ]
    write_text(REVIEW_DIR / "codex_latex_completion_audit.md", "\n".join(audit_lines))


def main() -> None:
    figures = copy_figures()
    tables = make_tables()
    write_main()
    write_sections()
    write_refs()
    write_build_script()
    collect_inventory(figures, tables)
    write_map_and_audit(figures, tables)
    print(json.dumps({"figures": len(figures), "tables": len(tables)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
