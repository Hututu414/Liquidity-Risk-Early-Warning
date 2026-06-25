# 第 4 章 流动性压力指数与标签构造

## 4.1 流动性压力指数 (LSI)
本文借鉴多因子组合思想，构造了高频流动性压力指数（Liquidity Stress Index, LSI）。
首先，针对各核心组件 $X \in \{ILLIQ, Range, RV, RelAmt\}$，在“证券-槽位”维度上进行稳健标准化：
$$ z(X_{i,t}) = \frac{X_{i,t} - \text{Median}(X_{i, \text{slot}(t)})}{\text{MAD}(X_{i, \text{slot}(t)})} $$
其中 $\text{Median}$ 和 $\text{MAD}$ 分别是该证券在对应日内槽位的历史中位数和绝对偏差中位数。

随后，将各标准化组件加总：
$$ LSI_{i,t} = z(ILLIQ_{i,t}) + z(Range_{i,t}) + z(RV_{i,t}) - z(RelAmt_{i,t}) $$
LSI 越高，代表流动性压力越大。

## 4.2 压力标签 (Stress Labels)
为了衡量未来的短时压力，我们构造了前瞻性标签 $Stress\_Hn$。
定义 $LSI\_window=5$ 为基础指数。对于时刻 $t$，其未来 $n$ 分钟内的最大压力定义为：
$$ \text{FutureMaxLSI}_{i,t}^n = \max \{LSI_{i, t+1}, \dots, LSI_{i, t+n}\} $$
我们选取训练期内所有证券 $\text{FutureMaxLSI}$ 的第 90 百分位数作为全局固定阈值 $\tau_n$。
当 $\text{FutureMaxLSI}_{i,t}^n > \tau_n$ 时，定义 $Stress\_Hn_{i,t} = 1$，否则为 0。
本文主要关注 $n=5$ (Stress_H5) 和 $n=10$ (Stress_H10) 两个预测期限。

## 4.3 市场共同压力特征
考虑到 A 股市场具有较强的同步性，我们额外构造了两个全市场维度特征：
1. **MarketLSI**：截面上所有证券 $LSI_5$ 的均值。
2. **CrossStress**：截面上处于 $Stress\_H5$ 状态的证券比例。
这些特征将作为后续预测模型的重要输入，用于捕捉系统性流动性冲击。
