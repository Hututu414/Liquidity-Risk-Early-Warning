import os

base_dir = r"D:\Users\TtT20\source\repos\金融科技大作业\fintech_hft_liquidity_agent_workspace_v1_agent_only\report\report_fragments"
output_file = os.path.join(base_dir, "full_paper_gemini_draft.md")

title_and_abstract = """# 题目：A 股高频市场状态信息能否预警短时流动性压力

## 摘要
在高频交易环境中，短时流动性压力往往可能在数分钟内迅速爆发并蔓延。由于高质量的逐笔订单簿数据获取成本较高，本文探索了基于 A 股 1 分钟 OHLCV 与成交额数据构造代理型流动性压力指数（LSI）的有效性，并检验其预警能力。本文通过 RGARCH-CARR-SK、QVAR 与 SMARTBoost 形成了逐层递进的证据链：首先，RGARCH-CARR-SK 的动态高阶风险度量结果显示短时流动性压力存在显著的动态聚集特征和高阶矩时变特性；其次，QVAR 模型揭示了在尾部分位压力状态下，多重市场冲击对流动性压力的传导具有强烈的状态依赖性；最后，基于无泄漏原则的 SMARTBoost 模型在时间滚动样本外的预测结果表明，高频状态变量能在极低基准事件率的严苛环境下，识别出真实发生率约为基准水平 10 倍左右（Top 5% 高风险组）的短时压力窗口。本文证实了基础高频分钟数据在微观流动性预警中的应用潜力，为高频风险防范提供了新的实证支持。

## 关键词
高频交易；流动性压力；分位数自回归；机器学习预警；SMARTBoost

---

"""

references = """

---

# 参考文献

[待补充引用] Liu, Zhou, and Chen (2025). 
[待补充引用] Paolo Giordani (2025). SMARTboost Learning for Tabular Data, Journal of Financial Econometrics, Volume 23, Issue 3, nbae028.
[待补充引用] 其他相关高频流动性、广义已实现测度、分位数自回归相关文献。
"""

chapters = [
    "chapter_01_intro.md",
    "chapter_02_literature.md",
    "chapter_03_data.md",
    "chapter_04_lsi_labels.md",
    "chapter_05_descriptive.md",
    "chapter_06_rgarch.md",
    "chapter_07_qvar.md",
    "chapter_08_smartboost.md",
    "chapter_09_robustness_conclusion.md"
]

with open(output_file, "w", encoding="utf-8") as f_out:
    f_out.write(title_and_abstract)
    for ch in chapters:
        ch_path = os.path.join(base_dir, ch)
        if os.path.exists(ch_path):
            with open(ch_path, "r", encoding="utf-8") as f_in:
                f_out.write(f_in.read() + "\n\n")
    f_out.write(references)

print("Full paper drafted successfully.")
