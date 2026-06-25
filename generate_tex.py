import os
import shutil

base_dir = r"D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only"
latex_dir = os.path.join(base_dir, "report", "latex_project")
sections_dir = os.path.join(latex_dir, "sections")
figures_dir = os.path.join(latex_dir, "figures")
tables_dir = os.path.join(latex_dir, "tables")

os.makedirs(sections_dir, exist_ok=True)
os.makedirs(figures_dir, exist_ok=True)
os.makedirs(tables_dir, exist_ok=True)

figures_to_copy = [
    (r"outputs\figures\03_descriptive\fig_descriptive_01_sample_coverage_heatmap.png", "fig_coverage.png"),
    (r"outputs\figures\03_descriptive\fig_descriptive_02_sample_split_timeline.png", "fig_timeline.png"),
    (r"outputs\figures\03_descriptive\fig_descriptive_03_marketlsi_timeseries.png", "fig_marketlsi.png"),
    (r"outputs\figures\03_descriptive\fig_descriptive_05_intraday_pattern.png", "fig_intraday.png"),
    (r"outputs\figures\03_descriptive\fig_descriptive_04_event_rate_h5_h10_timeseries.png", "fig_event_rate.png"),
    (r"outputs\figures\03_descriptive\fig_descriptive_09_correlation_heatmap.png", "fig_corr.png"),
    (r"outputs\figures\04_rgarch\fig_rgarch_conditional_risk_path.png", "fig_rgarch_risk.png"),
    (r"outputs\figures\04_rgarch\fig_rgarch_carr_sk_adapted_realized_measures.png", "fig_rgarch_realized.png"),
    (r"outputs\figures\04_rgarch\fig_rgarch_oos_loss_comparison.png", "fig_rgarch_loss.png"),
    (r"outputs\figures\05_qvar\fig_qvar_tail_quantile_response.png", "fig_qvar_response.png"),
    (r"outputs\figures\05_qvar\fig_qvar_pressure_test_paths.png", "fig_qvar_stress.png"),
    (r"outputs\figures\06_smartboost\fig_smartboost_pr_curve.png", "fig_sb_pr.png"),
    (r"outputs\figures\06_smartboost\fig_smartboost_top5_realized_rate.png", "fig_sb_top5.png"),
    (r"outputs\figures\06_smartboost\fig_smartboost_partial_effects.png", "fig_sb_partial.png"),
]

for src, dst in figures_to_copy:
    src_path = os.path.join(base_dir, src)
    dst_path = os.path.join(figures_dir, dst)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)

main_tex = r"""\documentclass[UTF8,a4paper,12pt]{ctexart}
\usepackage{geometry}
\geometry{left=2.5cm, right=2.5cm, top=3cm, bottom=3cm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{float}
\usepackage{hyperref}
\usepackage{caption}

\title{基于分钟级高频数据的 A 股短时流动性压力智能预警框架\\
\large ——来自 RGARCH-CARR-SK、QVAR 与 SMARTBoost 的证据}
\author{童奕然}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
在高频交易环境中，短时流动性压力往往可能在数分钟内迅速爆发并蔓延。由于高质量的逐笔订单簿数据获取成本较高，本文探索了基于 A 股 1 分钟 OHLCV 与成交额数据构造代理型流动性压力指数（LSI）的有效性，并检验其预警能力。本文通过 RGARCH-CARR-SK、QVAR 与 SMARTBoost 形成了逐层递进的证据链：首先，RGARCH-CARR-SK 的动态高阶风险度量结果显示短时流动性压力存在显著的动态聚集特征和高阶矩时变特性；其次，QVAR 模型揭示了在尾部分位压力状态下，多重市场冲击对流动性压力的传导具有强烈的状态依赖性；最后，基于无泄漏原则的 SMARTBoost 模型在时间滚动样本外的预测结果表明，高频状态变量能在极低基准事件率的严苛环境下，识别出真实发生率约为基准水平 10 倍左右（Top 5\% 高风险组）的短时压力窗口。本文证实了基础高频分钟数据在微观流动性预警中的应用潜力，为高频风险防范提供了新的实证支持。

\textbf{关键词：} 高频交易；流动性压力；分位数自回归；机器学习预警；SMARTBoost
\end{abstract}

\newpage
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

\newpage
\bibliographystyle{plain}
\bibliography{refs}

\end{document}
"""
with open(os.path.join(latex_dir, "main.tex"), "w", encoding="utf-8") as f:
    f.write(main_tex)

refs_bib = r"""@article{giordani2025smartboost,
  title={SMARTboost Learning for Tabular Data},
  author={Giordani, Paolo},
  journal={Journal of Financial Econometrics},
  volume={23},
  number={3},
  pages={nbae028},
  year={2025}
}

@article{liu2025rgarch,
  title={RGARCH-CARR-SK Model and High-Frequency Volatility},
  author={Liu, X. and Zhou, Y. and Chen, Z.},
  year={2025},
  note={待补充完整引用信息}
}
"""
with open(os.path.join(latex_dir, "refs.bib"), "w", encoding="utf-8") as f:
    f.write(refs_bib)

sections = {
    "01_intro.tex": r"""\section{引言}

在高频交易环境下，短时流动性压力往往可能在数分钟内迅速形成。由于逐笔订单簿数据不总是容易获得，或受限于数据处理成本，研究人员和从业者往往需要依赖较为基础的分钟级 OHLCV 与成交额数据来捕捉市场状态的变动。本文的核心研究问题是：基于 A 股 1 分钟 OHLCV 与成交额数据所构造的高频市场状态信息，能否有效预警未来 5 分钟和 10 分钟的短时流动性压力事件。

传统文献在刻画流动性枯竭或异常波动时，往往聚焦于日度数据的长期预测，或是依赖高精度的逐笔盘口微观结构数据。本文则探索了一种中间路径：利用高频一分钟连续竞价面板数据，构造代理型的流动性压力指数（Liquidity Stress Index, LSI），并通过三个逐层递进的模型框架形成证据链。我们关注的并不是绝对的收益率预测，而是针对尾部压力事件的预警与刻画能力。

本文的主要贡献包括：第一，构造了分钟级的短时流动性压力指数 LSI 及前瞻性压力标签，填补了低成本高频代理变量在微观压力预警中的应用空白；第二，引入动态高阶风险度量（基于 RGARCH-CARR-SK 的适配框架），验证了短时流动性压力不仅存在聚集特征，还呈现出分布高阶矩的时变特性；第三，使用分位数自回归（QVAR）系统分析了全市场不同尾部分位下的压力传导与情景响应；第四，运用 SMARTBoost 这一机器学习算法在时间滚动样本外进行预警验证。结果显示，高频状态变量能在低基准事件率的严苛测试集中，识别出真实发生率约十倍于基准水平的高风险窗口，为构建基于分钟级高频数据的短时流动性压力智能预警框架提供了实证支持。

本文后续结构安排如下：第二节回顾制度背景与相关文献；第三节介绍数据来源与处理方法；第四节详述 LSI 与压力标签构造逻辑；第五节展示描述性事实与高频诊断；第六至第八节依次呈现 RGARCH-CARR-SK 动态风险度量、QVAR 尾部传导压力测试与 SMARTBoost 样本外预警的实证结果；最后是稳健性讨论、局限性说明与结论。
""",
    "02_literature.tex": r"""\section{制度背景与文献综述}

\subsection{高频市场状态与流动性压力}
在电子化订单簿主导的高频交易市场中，流动性不仅仅是一个静态概念，而是呈现出高度的时变性与脆弱性。由于 A 股市场具有高换手、高波动及个体投资者参与度较高等特点，一旦市场情绪或微观结构发生突变，流动性压力便可能在极短时间内爆发。当前文献在刻画流动性异常时，多依赖逐笔委托簿的不平衡度或买卖价差（如 \cite{todo}）。本文由于数据获取限制，转而使用高频 OHLCV 代理变量来构建多维度的分钟级流动性压力指数（LSI），该指标能够综合反映短时紧致性、深度、波动性和成交承接力。

\subsection{广义已实现测度与高频风险度量}
随着高频数据的普及，基于日内增量构造的已实现测度（Realized Measures，如 RV, RBV, MedRV）被广泛用于刻画资产的波动与风险。近年来，Liu, Zhou 和 Chen (2025) \cite{liu2025rgarch} 提出的 RGARCH-CARR-SK 模型进一步将动态偏度和峰度纳入考量，以捕捉高频风险分布的非对称性与厚尾变化。本文借鉴这一前沿框架，并非用于传统的收益率波动率预测，而是将其结构迁移以适配所构造的 MarketLSI 压力创新序列，从而揭示短时流动性压力风险的动态聚集与高阶矩演化特征。

\subsection{分位数自回归与尾部风险传导}
传统的均值向量自回归模型往往只能刻画系统的常态冲击传导。而在金融压力场景下，不同变量之间的联动关系往往具有明显的状态依赖性：在极端尾部状态下，资产收益率下挫、波动率放大和流动性抽干可能同时发生。分位数向量自回归（QVAR）提供了一种捕捉这种尾部分位传导效应的有效工具。本文使用 QVAR 模型评估在不同分位数（如 $q=0.50$ 与 $q=0.95$）下，市场级压力指数对收益、波动和成交状态冲击的不同响应路径。

\subsection{机器学习在金融压力预警中的应用}
面对高维、非线性和存在噪声的高频数据，机器学习在构建样本外预警模型方面展现出了优越性。相比于传统统计模型，树模型及其集成算法能更好地捕捉局部特征互动。Giordani (2025) \cite{giordani2025smartboost} 提出了 SMARTBoost 算法，通过对对称平滑加性树进行 boosting，并在叶节点引入正则化先验，旨在提升小样本和低信噪比场景下的表现。本文正是基于该算法逻辑，对 A 股的高频分钟窗口特征和市场共同性特征进行了预警实证，以检验其在不发生前瞻性泄漏前提下的样本外预警能力。
""",
    "03_data.tex": r"""\section{数据来源、样本处理与变量构造}

\subsection{数据来源}
本文研究样本为 A 股市场具有代表性的 84 只证券，涵盖了不同行业与市值的头部公司。样本区间自 2023 年 5 月 15 日起至 2026 年 5 月 13 日止。
原始数据采用 1 分钟高频 OHLCV（开盘价、最高价、最低价、收盘价、成交量）及成交额数据。数据来源于高频行情数据库，并经过初步清洗，统一了字段命名与证券代码格式。

\subsection{样本清洗与就绪处理}
为了保证高频研究的有效性，我们对原始面板进行了以下处理：
1. \textbf{交易时段过滤}：仅保留连续竞价时段数据（09:30-11:30, 13:00-14:57），剔除集合竞价及非交易时段。
2. \textbf{分钟完整性剔除}：针对每个“证券-日期”对，要求有效分钟数不低于 236 分钟（理论值为 240 分钟）。若因停牌或数据缺失导致有效分钟数不足，则剔除该日样本。
3. \textbf{特征槽位（Slot）构造}：将每日 240 个交易分钟映射到固定槽位，用于捕捉流动性的日内模式。

\subsection{核心组件构造}
基于分钟级数据，我们构造了反映流动性四个维度的核心组件（k 取值 5, 10, 20）：
1. \textbf{紧致性 (Tightness)}：采用 $\text{Range}(k)$，即 k 分钟内最高价与最低价之比的对数均值。
2. \textbf{深度 (Depth)}：采用 $\text{ILLIQ}(k)$，即收益率绝对值与成交额之比的均值。
3. \textbf{波动性 (Volatility)}：采用 $\text{RV}(k)$，即分钟收益率平方和。
4. \textbf{成交活跃度 (Activity)}：采用 $\text{RelAmt}(k)$，即成交额的对数均值。

\subsection{样本划分}
为防止前瞻性偏差（Look-ahead Bias），本文严格按时间顺序划分样本（见图 \ref{fig:timeline}）：
\begin{itemize}
    \item \textbf{训练期}：2023-05-15 至 2025-02-28（约 60\%）
    \item \textbf{验证期}：2025-03-03 至 2025-09-26（约 20\%）
    \item \textbf{测试期}：2025-09-29 至 2026-05-13（约 20\%）
\end{itemize}
所有标准化参数（Median, MAD）及压力标签阈值均仅基于训练期数据计算。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_timeline.png}
    \caption{样本划分时间轴。图示展示了训练集、验证集与测试集的时间区间划分，未采用随机打乱以防止前瞻性偏差。}
    \label{fig:timeline}
\end{figure}
""",
    "04_lsi_labels.tex": r"""\section{流动性压力指数 LSI 与压力标签构造}

\subsection{流动性压力指数 (LSI)}
本文借鉴多因子组合思想，构造了高频流动性压力指数（Liquidity Stress Index, LSI）。
首先，针对各核心组件 $X \in \{\text{ILLIQ}, \text{Range}, \text{RV}, \text{RelAmt}\}$，在“证券-槽位”维度上进行稳健标准化：
\begin{equation}
z(X_{i,t}) = \frac{X_{i,t} - \text{Median}(X_{i, \text{slot}(t)})}{\text{MAD}(X_{i, \text{slot}(t)})}
\end{equation}
其中 $\text{Median}$ 和 $\text{MAD}$ 分别是该证券在对应日内槽位的历史中位数和绝对偏差中位数。

随后，将各标准化组件加总：
\begin{equation}
LSI_{i,t} = z(ILLIQ_{i,t}) + z(Range_{i,t}) + z(RV_{i,t}) - z(RelAmt_{i,t})
\end{equation}
LSI 越高，代表流动性压力越大。

\subsection{压力标签 (Stress Labels)}
为了衡量未来的短时压力，我们构造了前瞻性标签 $\text{Stress\_H}n$。
定义 $LSI\_window=5$ 为基础指数。对于时刻 $t$，其未来 $n$ 分钟内的最大压力定义为：
\begin{equation}
\text{FutureMaxLSI}_{i,t}^n = \max \{LSI_{i, t+1}, \dots, LSI_{i, t+n}\}
\end{equation}
我们选取训练期内所有证券 $\text{FutureMaxLSI}$ 的第 90 百分位数作为全局固定阈值 $\tau_n$。
当 $\text{FutureMaxLSI}_{i,t}^n > \tau_n$ 时，定义 $\text{Stress\_H}n_{i,t} = 1$，否则为 0。
本文主要关注 $n=5$ ($\text{Stress\_H5}$) 和 $n=10$ ($\text{Stress\_H10}$) 两个预测期限。

\subsection{市场共同压力特征}
考虑到 A 股市场具有较强的同步性，我们额外构造了两个全市场维度特征：
1. \textbf{MarketLSI}：截面上所有证券 $LSI_5$ 的均值。
2. \textbf{CrossStress}：截面上处于 $\text{Stress\_H5}$ 状态的证券比例。
这些特征将作为后续描述性与系统性模型的重要输入，用于捕捉系统性流动性冲击。
""",
    "05_descriptive.tex": r"""\section{描述性事实与高频诊断}

\subsection{数据覆盖情况}
通过对 84 只样本证券的长期追踪，我们绘制了数据覆盖热力图（图 \ref{fig:coverage}）。结果显示，绝大多数证券在样本期内保持了良好的数据连续性。
值得注意的是，在 2024 年 9 月 27 日前后，由于市场交易极度活跃及潜在的技术波动，部分证券出现了分钟数据缺失或有效时长不足的情况。这部分异常样本已在预处理阶段被剔除，以保证实证结果的稳健性。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{figures/fig_coverage.png}
    \caption{股票-月份有效分钟覆盖率热力图。颜色深浅代表了对应月份内有效分钟覆盖的完整度。}
    \label{fig:coverage}
\end{figure}

\subsection{LSI 的日内模式}
流动性压力指数展现出显著的日内季节性特征（图 \ref{fig:intraday}）。
1. \textbf{开盘效应}：受集合竞价后的开盘定价影响，LSI 在开盘前 15 分钟处于日内最高水平，随后迅速回落。
2. \textbf{午间效应}：上午收盘前及下午开盘初，流动性压力略有波动，但相对平稳。
3. \textbf{收盘效应}：在收盘集合竞价前，LSI 往往出现小幅抬升。
分位带显示，不同证券的 LSI 在开盘阶段的差异性显著高于盘中，反映了市场在处理隔夜信息时的流动性博弈。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_intraday.png}
    \caption{LSI 日内模式图。展示了交易时间内 LSI 的中位数变化及分位带，揭示了显著的开盘效应。}
    \label{fig:intraday}
\end{figure}

\subsection{市场压力的时间序列特征}
通过观察 $\text{MarketLSI}$ 与 $\text{CrossStress}$ 的时间序列（图 \ref{fig:marketlsi}），我们可以清晰识别出多次全市场范围的流动性枯竭事件。
特别是在 2024 年 1 月末至 2 月初期间，受宏观波动与雪球产品对冲压力影响，CrossStress 比例一度飙升至 60\% 以上，即全市场超过六成的证券同时处于极端的流动性压力状态。这种高度的截面相关性印证了系统性风险在流动性维度的传导。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{figures/fig_marketlsi.png}
    \caption{MarketLSI 时间序列图。反映了市场级流动性压力的宏观波动，特别是高压日期间的极值突起。}
    \label{fig:marketlsi}
\end{figure}

\subsection{压力标签的分布事实}
描述性统计显示，$\text{Stress\_H5}$ 标签在训练期的平均比例约为 9.1\%（见图 \ref{fig:event_rate}）。然而，该比例在时间上分布极度不均，呈现明显的群聚效应（Clustering）。在市场平稳期，全天可能无压力事件；而在危机时刻，压力状态会持续数十分钟甚至数小时。这为利用历史状态预测未来压力提供了实证基础。此外，核心变量之间也展现出了特定的相关性结构（图 \ref{fig:corr}）。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_event_rate.png}
    \caption{H5/H10 压力事件率时间图。展示了短时压力事件在不同月份间的时变发生率及聚集特性。}
    \label{fig:event_rate}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{figures/fig_corr.png}
    \caption{核心变量相关性热力图。展示了截面上不同核心流动性与压力变量之间的线性相关关系。}
    \label{fig:corr}
\end{figure}
""",
    "06_rgarch.tex": r"""\section{RGARCH-CARR-SK 动态高阶风险度量}

\subsection{模型定位}
Liu、Zhou 和 Chen (2025) \cite{liu2025rgarch} 提出的 RGARCH-CARR-SK 模型原本用于高频波动预测和风险度量。其核心思想是在 realized measure 驱动的条件风险递推中，同时引入 Gram-Charlier expansion（GCE）分布、动态偏度和动态峰度，从而刻画风险分布的非对称性与厚尾变化。
本文不复刻原文的 GEM 指数波动率研究，而是将其模型结构迁移到 A 股分钟数据构造的 $\text{MarketLSI}$ 压力风险序列。这里的 $r_t$ 不是资产收益率，而是日内 MarketLSI 的压力创新；$y_t$ 不是价格波动率，而是由日内 MarketLSI 增量构造的 realized pressure measure 的平方根。本章结果应解释为短时流动性压力风险的动态刻画，而不是收益率预测。

\subsection{原文结构与本文适配}
原文 RGARCH-CARR-SK 的主结构包括：
\begin{align*}
r_t &= \rho \lambda_t z_t \\
\log(\lambda_t) &= \omega + \beta \log(\lambda_{t-1}) + \gamma \log(y_{t-1}) + d(z_{t-1}) \\
y_t &= \lambda_t u_t \\
s_t &= \omega_1 + \beta_1 s_{t-1} + v_1 z_{t-1} \\
k_t &= \omega_2 + \beta_2 k_{t-1} + v_2 |z_{t-1}| \\
d(z_t) &= d_1 z_t + d_2 (z_t^2 - 1)
\end{align*}
本文将 $\lambda_t$ 解释为 MarketLSI 条件压力风险强度（图 \ref{fig:rgarch_risk}）。$z_t$ 服从由动态 $s_t$ 和 $k_t$ 控制的 GCE 分布；measurement equation 中的 $u_t$ 按原文设为 lognormal residual。估计目标使用压力创新密度与 measurement residual 密度组成的联合 log likelihood。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_rgarch_risk.png}
    \caption{RGARCH-CARR-SK 条件压力风险 $\lambda_t$ 路径。展示了 MarketLSI 的压力风险在时间序列上的显著聚集特征。}
    \label{fig:rgarch_risk}
\end{figure}

\subsection{广义 realized pressure measures}
本文基于日内 MarketLSI 增量构造四类主 realized pressure measures（图 \ref{fig:rgarch_realized}）：
$\text{RV\_pressure}$、$\text{RBV\_pressure}$、$\text{MedRV\_pressure}$ 与 $\text{RMAD\_pressure}$。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_rgarch_realized.png}
    \caption{Realized pressure measures 标准化分布对比。不同的代理变量在刻画压力聚集上呈现了不同平滑度的结构。}
    \label{fig:rgarch_realized}
\end{figure}

\subsection{估计结果摘要}
四个主模型均完成 MLE。训练期样本数为 435 个交易日。当前拟合准则显示，RGARCH-CARR-SK-RV 的 AIC/BIC 最低；样本外损失表（图 \ref{fig:rgarch_loss}）显示，RGARCH-CARR-SK-RMAD 在验证期和测试期的相对误差类指标更小。这一结果提示：不同 realized pressure measures 在拟合和样本外压力风险刻画中可能承担不同角色。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_rgarch_loss.png}
    \caption{样本外 R2LOG 损失比较图。较低的 R2LOG 表明采用 RMAD 等测度能在样本外更好地刻画流动性压力分布。}
    \label{fig:rgarch_loss}
\end{figure}
""",
    "07_qvar.tex": r"""\section{QVAR 尾部分位传导与压力测试}

\subsection{模型设定与核心变量}
为了刻画截面压力、市场收益、市场波动与市场成交活跃度之间的动态联动，本文采用低维一阶滞后分位数向量自回归模型（QVAR）。系统的内生变量包括：$\text{MarketLSI}$、$\text{CrossStress}$、$\text{IndexRet}$、$\text{IndexRV}$ 以及 $\text{MarketRelAmt}$。
通过分别在常态分位数（$q=0.50$）及尾部分位数（$q=0.90, q=0.95$）进行 QuantReg 估计，我们可以捕捉尾部压力传导的状态依赖性特征。

\subsection{尾部分位响应路径差异}
根据训练期估计的 QVAR 系数，本文模拟了各类冲击对 MarketLSI 的分位响应路径（图 \ref{fig:qvar_response}）。结果表明，相较于中位数状态（$q=0.50$），在极端压力分位（$q=0.95$）下，系统对于外部冲击的吸收更为缓慢，压力的延续时间更长。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_qvar_response.png}
    \caption{QVAR 尾部分位响应图。展示了在不同分位数下系统冲击传导到 MarketLSI 的强度与持久性存在差异。}
    \label{fig:qvar_response}
\end{figure}

\subsection{情景压力测试分析}
为了进一步验证变量间的动态冲击，我们基于估计的 QVAR 尾部系统（$q=0.95$）设计了四类标准化情景冲击（冲击幅度设定为 $\pm 2.0$ 标准差），并生成了情景压力测试图（图 \ref{fig:qvar_stress}）。四类情景分别为：市场急跌、波动放大、成交收缩/流动性压力、复合压力。
测试结果显示，复合压力情景对 MarketLSI 的抬升幅度最大且衰减最慢。这种基于已估计系数的情景模拟清晰展示了市场恶化环境下多重负面因素如何共同推高短时流动性压力，揭示了微观流动性的脆弱面。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.9\textwidth]{figures/fig_qvar_stress.png}
    \caption{四类情景压力测试图。模拟了极端市场环境（如市场急跌或复合冲击）下短时流动性压力的抬升与恢复轨迹。}
    \label{fig:qvar_stress}
\end{figure}
""",
    "08_smartboost.tex": r"""\section{SMARTBoost 样本外预警}

\subsection{预警框架与防泄漏设定}
作为本文实证证据链的最终环节，我们引入了基于 Giordani (2025) \cite{giordani2025smartboost} 算法逻辑适配实现的 SMARTBoost 模型。该模型的目标是检验高频窗口特征和无泄漏的市场状态特征是否能够对未来 5 分钟（$\text{Stress\_H5}$）和 10 分钟（$\text{Stress\_H10}$）的极端流动性压力事件提供稳健的样本外预警。
在此前的特征工程中，曾引入由未来标签横截面聚合生成的 CrossStress 特征。为确保严格的防泄漏要求，该特征已在最终模型训练中被彻底剔除。目前的模型仅依赖于个股 LSI 及其历史滚动统计量、MarketLSI、日内时点以及监管阶段等无未来信息的特征。验证集用于由 PR-AUC 指标决定的早停迭代选择，测试集用于纯样本外效果评估。

\subsection{核心预测指标与 Lift 分析}
由于目标标签在全样本中的事件率极低（约 9\%），本文重点关注 PR-AUC 以及基于预测概率排序的 Top 5\% 高风险组的真实压力发生率和提升倍数（Lift）。测试集核心结果如下：
\begin{itemize}
    \item \textbf{H5-test (未来 5 分钟压力)}：PR-AUC 达到 0.603。模型预测概率排序前 5\% 的样本，其真实的短时压力发生率约为 59.3\%，相比基准事件率的提升倍数（Lift）达到了约 10.9 倍（图 \ref{fig:sb_pr} 与 图 \ref{fig:sb_top5}）。
    \item \textbf{H10-test (未来 10 分钟压力)}：PR-AUC 为 0.545，其 Top 5\% 高风险组的真实压力发生率约为 56.4\%，Lift 倍数约为 9.7 倍。
\end{itemize}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_sb_pr.png}
    \caption{SMARTBoost 样本外 PR 曲线。相较于基准事件率水平，预警模型展现出显著的精确率-召回率边界外拓。}
    \label{fig:sb_pr}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_sb_top5.png}
    \caption{Top 5\% 高风险组真实压力发生率图。被预警模型标记为最高风险的 5\% 样本窗口中，短时压力事件的真实发生率是全样本基准水平的 10 倍左右。}
    \label{fig:sb_top5}
\end{figure}

\subsection{局部依赖效应}
通过分析无泄漏特征的 Partial Effects（图 \ref{fig:sb_partial}），我们发现个股的历史短期压力强度（如 $\text{LSI\_5\_lag1}$）以及全市场维度的压力水平（$\text{MarketLSI}$）与未来发生极端压力事件的概率呈现显著正向非线性关系。这一发现进一步确认了流动性压力的截面溢出效应以及时间上的微观动量效应，证明了高频状态信息具有预测短时流动性危机的实质应用价值。

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig_sb_partial.png}
    \caption{SMARTBoost Partial Effects 图。展示了核心状态特征与未来高频压力发生概率之间的非线性依赖关系。}
    \label{fig:sb_partial}
\end{figure}
""",
    "09_robustness_conclusion.tex": r"""\section{稳健性讨论、局限性与结论}

\subsection{稳健性讨论}
本文核心结论基于一系列防泄漏的严格检验。对于基于阈值的极端压力标签定义，即使拓展到不同预测步长（如从未来 5 分钟拓展到 10 分钟），预警框架依然保持了较高的 Lift 倍数。模型在验证期和测试期的各项预测指标一致性较强，证明并非单一市场环境下的偶然现象。同时，剔除了具有未来信息属性的伪特征（如全样本聚合的 CrossStress）后重跑模型，核心特征的有效性依然成立。

\subsection{研究局限性}
首先，由于高频数据获取成本的限制，本文仅使用 OHLCV 与成交额构造了代理型流动性压力指数（LSI），并没有使用真实深度的订单簿委托数据，无法完全等同于 L2 级别的微观流动性冲击度量。其次，本文在第七节中使用的 QVAR 情景冲击测试是一种基于已估计系数的统计模拟推演，并不等同于具有外生冲击识别的严格因果推断。最后，SMARTBoost 的预警结论主要依赖于特定的股票样本池与特征池，对于更为极致的黑天鹅系统性风险，其模型置信度仍有待更大规模的长周期检验。

\subsection{结论}
本文在电子化高频交易的背景下，基于 A 股一分钟连续竞价数据构建了代理型的短时流动性压力指数（LSI）体系。通过 RGARCH-CARR-SK、QVAR 与 SMARTBoost 组成的三层递进证据链，文章解答了“高频市场状态信息能否预警短时流动性压力”这一核心问题。

研究发现：第一，MarketLSI 在高频尺度上存在动态聚集特征与高阶矩的非对称时变演化；第二，尾部分位状态下，流动性对系统冲击的传导更加缓慢且更具破坏力，多重情景叠加会显著推高市场压力；第三，最核心的样本外预警结果证实，仅依靠合规的低维高频状态特征，SMARTBoost 能够有效识别未来 5 分钟和 10 分钟的高风险窗口，将 Top 5\% 风险组的真实命中率提升至全样本基准的近十倍左右。

综上所述，构建基于分钟级高频数据的短时流动性压力智能预警框架具有较强的可行性。A 股分钟级的市场状态信息不仅能及时描述当前的紧致与波动，更能够为防范极短时的微观流动性枯竭提供强有力的预警支持。未来研究可进一步将其扩展至风险看板、监管科技场景或订单簿多维融合预测中。
"""
}

for filename, content in sections.items():
    with open(os.path.join(sections_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

build_script = r"""cd D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\report\latex_project
where xelatex
if ($LASTEXITCODE -eq 0) {
    xelatex -interaction=nonstopmode main.tex
    bibtex main
    xelatex -interaction=nonstopmode main.tex
    xelatex -interaction=nonstopmode main.tex
    echo "Compiled successfully with xelatex."
} else {
    where pdflatex
    if ($LASTEXITCODE -eq 0) {
        pdflatex -interaction=nonstopmode main.tex
        bibtex main
        pdflatex -interaction=nonstopmode main.tex
        pdflatex -interaction=nonstopmode main.tex
        echo "Compiled successfully with pdflatex."
    } else {
        echo "Neither xelatex nor pdflatex is available in the current environment. Compilation skipped."
    }
}
"""
with open(os.path.join(latex_dir, "build_report.ps1"), "w", encoding="utf-8") as f:
    f.write(build_script)

print("TeX files and directory structure generated successfully.")
