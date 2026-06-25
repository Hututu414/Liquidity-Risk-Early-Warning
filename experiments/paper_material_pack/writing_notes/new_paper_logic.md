# 新论文主线说明

1. 新主线：压力测度—尾部状态描述—样本外 onset 预警。LSI/MarketLSI 是基于成交后高频数据的短时流动性压力代理；QVAR 描述 MarketLSI、收益、波动和成交承接的尾部分位联动；ML onset 检验样本外预警能力。

2. 删除 RGARCH：RV、RBV、MedRV、RMAD 均 invalid_for_primary。RGARCH 模块从正文删除；若必须保留，只能在附录或局限性中一句话说明其诊断不稳。

3. 不再讲融合实验：融合未稳定超过 ML_ALL，F9 ex-post 不能回头选择主方案。融合实验不作为论文主线。

4. QVAR 角色：尾部分位联动描述器。

5. ML onset 角色：核心样本外预警结果。

6. 结构从“三方法并列”改为“压力测度—尾部状态描述—样本外 onset 预警”。

7. 保留 LSI、QVAR、onset 标签、P/M/C/ALL、事件级评价和预算评价。

8. 降级 fusion、RGARCH 诊断和 C 单独贡献。

9. 删除 RGARCH 正文模块和融合成功叙述。

10. 正文进入 MarketLSI、QVAR tail state、onset 主结果、特征组增量、事件级和预算评价。

11. 附录进入完整模型、Top-K、QVAR 诊断、RGARCH invalid 和 fusion negative。

12. 不再提 RGARCH 主贡献、融合成功、QVAR 稳定提升 ML_ALL、C 单独显著和因果解释。
