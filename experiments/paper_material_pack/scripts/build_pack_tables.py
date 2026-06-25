# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json, re, shutil
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

ROOT=Path('/workspaces/Liquidity-Risk-Early-Warning')
PACK=ROOT/'experiments/paper_material_pack'
ON=ROOT/'experiments/onset_baseline_check/outputs'
FU=ROOT/'experiments/econometric_ml_fusion/outputs'
CK=ROOT/'experiments/econometric_ml_fusion/checkpoints'
PR=ROOT/'experiments/onset_baseline_check/checkpoints/predictions'
FULL=ROOT/'data/processed/onset_model_panel_full80.parquet'
D={k:PACK/k for k in ['outputs','tables_main','tables_appendix','figures_main','figures_appendix','figure_qc','writing_notes','source_index','scripts','archive']}
for p in [PACK,*D.values()]: p.mkdir(parents=True,exist_ok=True)
idx=[]; missing=[]
def rel(p):
    p=Path(p)
    try: return str(p.relative_to(ROOT))
    except Exception: return str(p)
def src(a,t,s,on=False,qv=False,fu=False,main=False,app=False,rev=False):
    idx.append({'artifact_path':rel(a),'artifact_type':t,'source_files':';'.join(map(str,s)),'from_onset':on,'from_qvar':qv,'from_fusion_negative_result':fu,'can_enter_main_text':main,'suggest_appendix':app,'needs_manual_review':rev})
def read(p):
    if not p.exists(): missing.append(rel(p)); return pd.DataFrame()
    return pd.read_csv(p)
def cell(x):
    if pd.isna(x): return ''
    if isinstance(x,float):
        if abs(x)>=1000: return f'{x:,.0f}'
        if abs(x)>=10: return f'{x:.3f}'
        return f'{x:.6f}'.rstrip('0').rstrip('.')
    return str(x).replace('|','\\|')
def md(df):
    if df.empty: return 'No rows.\n'
    cols=list(df.columns); out=['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
    for _,r in df.iterrows(): out.append('| '+' | '.join(cell(r[c]) for c in cols)+' |')
    return '\n'.join(out)+'\n'
def wt(df,base,typ,sources,**kw):
    cp=base.with_suffix('.csv'); mp=base.with_suffix('.md')
    df.to_csv(cp,index=False,encoding='utf-8-sig'); mp.write_text(md(df),encoding='utf-8')
    src(cp,typ+'_csv',sources,**kw); src(mp,typ+'_md',[rel(cp)],**kw)
def summary():
    d={}; p=ON/'cloud_run_summary.md'
    if p.exists():
        for line in p.read_text(encoding='utf-8',errors='ignore').splitlines():
            m=re.match(r'-\s*([^:]+):\s*(.*)$',line.strip())
            if m: d[m.group(1)]=m.group(2)
    else: missing.append(rel(p))
    return d
def thresholds():
    for p in [ROOT/'data_intermediate/stage2_lsi_labels/label_thresholds_train.json',ROOT/'experiments/onset_baseline_check/checkpoints/onset_thresholds_ready.json']:
        if not p.exists(): continue
        try: obj=json.loads(p.read_text(encoding='utf-8'))
        except Exception: continue
        flat={}
        def walk(k,v):
            if isinstance(v,dict):
                for kk,vv in v.items(): walk(f'{k}.{kk}' if k else kk,vv)
            else: flat[k]=v
        walk('',obj); return flat
    return {}
def daily_full():
    out=D['outputs']/'derived_full80_daily_marketlsi_event_rate.csv'
    if out.exists(): return pd.read_csv(out,parse_dates=['date'])
    acc=defaultdict(lambda:[0.,0.,0.,0])
    pf=pq.ParquetFile(FULL)
    for b in pf.iter_batches(batch_size=500000,columns=['date','MarketLSI','Stress_H5','Stress_H10']):
        x=b.to_pandas(); x['date']=pd.to_datetime(x['date']).dt.date.astype(str)
        g=x.groupby('date').agg(ml=('MarketLSI','sum'),h5=('Stress_H5','sum'),h10=('Stress_H10','sum'),n=('MarketLSI','size'))
        for dt,r in g.iterrows():
            a=acc[dt]; a[0]+=r.ml; a[1]+=r.h5; a[2]+=r.h10; a[3]+=int(r.n)
    rows=[]
    for dt,a in sorted(acc.items()):
        n=max(a[3],1); rows.append({'date':dt,'MarketLSI_daily_mean':a[0]/n,'Stress_H5_daily_rate':a[1]/n,'Stress_H10_daily_rate':a[2]/n,'row_count':n})
    df=pd.DataFrame(rows); df['date']=pd.to_datetime(df['date']); df.to_csv(out,index=False,encoding='utf-8-sig')
    src(out,'derived_csv',[rel(FULL)],on=True); return df
def auc(y,s):
    y=np.asarray(y).astype(int); s=np.asarray(s); np_=y.sum(); nn=len(y)-np_
    if np_==0 or nn==0: return np.nan
    rk=pd.Series(s).rank(method='average').to_numpy(); return float((rk[y==1].sum()-np_*(np_+1)/2)/(np_*nn))
def ap(y,s):
    y=np.asarray(y).astype(int); o=np.argsort(-np.asarray(s),kind='mergesort'); yy=y[o]; tot=yy.sum()
    if tot==0: return np.nan
    prec=np.cumsum(yy)/np.arange(1,len(yy)+1); return float((prec*yy).sum()/tot)
def pred(h,m,g):
    p=PR/f'predictions_onset_{h}_{m}_{g}.parquet'
    if not p.exists(): missing.append(rel(p)); return pd.DataFrame(columns=['y','score','date'])
    return pq.read_table(p,columns=['y','score','date']).to_pandas()

cloud=summary(); th=thresholds(); full=daily_full()
mc=read(ON/'model_comparison_summary.csv'); de=read(ON/'delta_vs_persistence.csv'); tk=read(ON/'topk_lift_table.csv'); ev=read(ON/'event_level_metrics_revised.csv'); bu=read(ON/'budgeted_event_metrics.csv')
qd=read(FU/'qvar_state_diagnostics.csv'); qp=read(FU/'qvar_parameter_history.csv'); qm=read(FU/'qvar_feature_manifest.csv'); rg=read(FU/'rgarch_state_diagnostics.csv'); li=read(FU/'lockbox_incremental_metrics.csv'); mr=read(FU/'model_ranking.csv')
qv=pq.read_table(CK/'qvar_market_states.parquet').to_pandas(); qv['date']=pd.to_datetime(qv['date'])
qday=qv.groupby('date',as_index=False).agg(xsec_lsi_mean=('xsec_lsi_mean','mean'),xsec_lsi_q90=('xsec_lsi_q90','mean'),qvar_mlsi_q50=('qvar_mlsi_q50','mean'),qvar_mlsi_q90=('qvar_mlsi_q90','mean'),qvar_mlsi_q95=('qvar_mlsi_q95','mean'),qvar_tail_spread_95_50=('qvar_tail_spread_95_50','mean'),qvar_tail_surprise_95=('qvar_tail_surprise_95','mean'),qvar_high_tail_state=('qvar_high_tail_state','mean'),qvar_composite_tail_state=('qvar_composite_tail_state','mean'))
qday.to_csv(D['outputs']/'derived_qvar_daily_tail_states.csv',index=False,encoding='utf-8-sig'); src(D['outputs']/'derived_qvar_daily_tail_states.csv','derived_csv',[rel(CK/'qvar_market_states.parquet')],qv=True)
preds={}; prrows=[]
for h in ['H5','H10']:
    for m,g in [('LightGBM','ALL'),('Naive','P')]:
        x=pred(h,m,g); preds[(h,m,g)]=x
        if len(x): prrows.append({'horizon':h,'model':m,'feature_group':g,'rows':len(x),'event_rate':x.y.mean(),'PR_AUC_average_precision':ap(x.y,x.score),'ROC_AUC':auc(x.y,x.score)})
pd.DataFrame(prrows).to_csv(D['outputs']/'derived_prediction_score_diagnostics.csv',index=False,encoding='utf-8-sig'); src(D['outputs']/'derived_prediction_score_diagnostics.csv','derived_csv',[rel(PR)],on=True,rev=True)
# main tables
sample=pd.DataFrame([{'sample_stock_count':cloud.get('stock_count_after_cap','80'),'trading_days':full.date.nunique(),'rows':cloud.get('data_rows',''),'columns':cloud.get('data_columns',''),'date_range':cloud.get('data_range',''),'base_train':'through 2025-02-28','base_validation':'2025-03-01 to 2025-09-26','test_or_development':'onset test starts 2025-09-29; fusion_development 2025-09-27 to 2026-02-28','lockbox':'fusion_lockbox 2026-03-01 to 2026-05-13','threshold_H5':th.get('H5') or th.get('thresholds.H5') or 'see source json','threshold_H10':th.get('H10') or th.get('thresholds.H10') or 'see source json','gap':cloud.get('gap','5'),'lookback_clean':cloud.get('lookback_clean','10'),'threshold_quantile':cloud.get('threshold_quantile','0.9')}])
wt(sample,D['tables_main']/'table_main_01_sample_structure','main_table',[rel(ON/'cloud_run_summary.md'),rel(FULL)],on=True,main=True)
piv=qp.pivot_table(index='quantile',columns='regressor',values='estimate',aggfunc='mean').reset_index(); rows=[]
for _,r in piv.iterrows(): rows.append({'QVAR_variable':'MarketLSI','quantile':r.get('quantile'),'MarketLSI_lag1_coef':r.get('MarketLSI_lag1'),'IndexRet_lag1_coef':r.get('IndexRet_lag1'),'IndexRV_lag1_coef':r.get('IndexRV_lag1'),'MarketRelAmt_lag1_coef':r.get('MarketRelAmt_lag1'),'tail_spread_95_50_median':qv.qvar_tail_spread_95_50.median(),'tail_spread_95_50_p95':qv.qvar_tail_spread_95_50.quantile(.95),'CrossStress_used':bool(qm.uses_crossstress.any()) if len(qm) else False,'interpretation_boundary':'tail comovement descriptor; not a stable ML_ALL increment claim'})
wt(pd.DataFrame(rows),D['tables_main']/'table_main_02_qvar_tail_state_summary','main_table',[rel(FU/'qvar_parameter_history.csv'),rel(FU/'qvar_feature_manifest.csv')],qv=True,main=True)
best=[]; pdg=pd.read_csv(D['outputs']/'derived_prediction_score_diagnostics.csv')
for h in ['H5','H10']:
    hc=mc[mc.horizon==h]; b=hc[hc.status=='OK'].sort_values('PR_AUC',ascending=False).iloc[0]; n=hc[(hc.model=='Naive')&(hc.feature_group=='P')].iloc[0]; c=de[(de.comparison==f'{h} best_vs_naive')&(de.metric=='PR_AUC')].iloc[0]; ro=pdg[(pdg.horizon==h)&(pdg.model==b.model)&(pdg.feature_group==b.feature_group)]
    best.append({'horizon':h,'event_rate':b.event_rate,'naive_PR_AUC':n.PR_AUC,'best_model':b.model,'best_feature_group':b.feature_group,'best_PR_AUC':b.PR_AUC,'Delta_PR_AUC_vs_naive':c.observed_delta,'CI_low':c.ci_low,'CI_high':c.ci_high,'Top5_hit':b.Top5_hit_rate,'Top5_lift':b.Top5_lift,'Brier':b.Brier,'ROC_AUC':ro.ROC_AUC.iloc[0] if len(ro) else np.nan})
wt(pd.DataFrame(best),D['tables_main']/'table_main_03_onset_ml_main_result','main_table',[rel(ON/'model_comparison_summary.csv'),rel(ON/'delta_vs_persistence.csv'),rel(PR)],on=True,main=True,rev=True)
fgrows=[]
for h in ['H5','H10']:
    r={'horizon':h}
    for fg in ['P','M','C','ALL']: r[f'{fg}_PR_AUC']=mc[(mc.horizon==h)&(mc.model=='LightGBM')&(mc.feature_group==fg)].PR_AUC.iloc[0]
    for comp in ['ALL_vs_P_same_model','C_vs_P_same_model']:
        d=de[(de.comparison==f'{h} {comp}')&(de.metric=='PR_AUC')]; lab=comp.replace('_same_model',''); r[f'{lab}_Delta_PR_AUC']=d.observed_delta.iloc[0]; r[f'{lab}_CI']=f'[{d.ci_low.iloc[0]:.6f}, {d.ci_high.iloc[0]:.6f}]'
    r['interpretation']='ALL stable increment; C standalone no stable positive increment'; fgrows.append(r)
wt(pd.DataFrame(fgrows),D['tables_main']/'table_main_04_feature_group_increment','main_table',[rel(ON/'model_comparison_summary.csv'),rel(ON/'delta_vs_persistence.csv')],on=True,main=True)
em=[]
for _,r in ev.iterrows():
    b=bu[(bu.horizon==r.horizon)&(bu.budget_type=='daily_top_n')&(bu.budget_value.round(0)==50)]
    em.append({'horizon':r.horizon,'label_aligned_recall':r.label_aligned_event_recall,'practical_window_recall':r.practical_window_event_recall,'daily_false_alarms_top5pct':r.daily_false_alarms,'false_alarms_per_detected_event_top5pct':r.false_alarms_per_detected_event,'average_lead_time':r.average_lead_time,'median_lead_time':r.median_lead_time,'budget_setting':'daily_top_50','budget_practical_recall':b.event_recall_practical.iloc[0] if len(b) else np.nan,'budget_practical_false_alarms_per_detected':b.false_alarms_per_detected_event_practical.iloc[0] if len(b) else np.nan,'recommended_main_metric':'daily_top_50 practical recall with false alarms per detected event'})
wt(pd.DataFrame(em),D['tables_main']/'table_main_05_event_level_monitoring','main_table',[rel(ON/'event_level_metrics_revised.csv'),rel(ON/'budgeted_event_metrics.csv')],on=True,main=True)
bound=pd.DataFrame([['QVAR','retain','main','no stable ML_ALL increment claim','tail quantile comovement/state descriptor'],['RGARCH-CARR-SK','remove from main text','appendix or limitation only','none','all candidate specs invalid_for_primary'],['econometric-ML fusion','do not use as main storyline','appendix/negative result only','not stable beyond ML_ALL','avoid method stacking'],['cross-sectional C','not standalone core contribution','main as ablation boundary','no stable standalone positive increment','ALL improves but C alone is not core'],['ML onset','core result','main','stable vs naive persistence','primary out-of-sample warning evidence']],columns=['module','paper_role','main_or_appendix','predictive_increment_claim','conclusion'])
wt(bound,D['tables_main']/'table_main_06_qvar_ml_boundary','main_table',[rel(FU/'paper_optimization_decision.md'),rel(ON/'cloud_ml_effectiveness_result_digest.md')],on=True,qv=True,fu=True,main=True)
# appendix tables
for name,df,ss,kw in [('appendix_table_a1_full_model_comparison',mc,[rel(ON/'model_comparison_summary.csv')],{'on':True}),('appendix_table_a2_topk_lift',tk,[rel(ON/'topk_lift_table.csv')],{'on':True}),('appendix_table_a3_delta_vs_persistence',de,[rel(ON/'delta_vs_persistence.csv')],{'on':True})]: wt(df,D['tables_appendix']/name,'appendix_table',ss,app=True,**kw)
qapp=pd.concat([pd.DataFrame({'section':['diagnostics']*len(qd)}).join(qd.reset_index(drop=True)),pd.DataFrame({'section':['feature_manifest']*len(qm)}).join(qm.reset_index(drop=True))],ignore_index=True)
wt(qapp,D['tables_appendix']/'appendix_table_a4_qvar_diagnostics','appendix_table',[rel(FU/'qvar_state_diagnostics.csv'),rel(FU/'qvar_feature_manifest.csv')],qv=True,app=True)
rg2=rg.copy(); rg2['paper_decision']='remove from main text; keep only as invalidity diagnostic if needed'; rg2['primary_module']=False
wt(rg2,D['tables_appendix']/'appendix_table_a5_rgarch_removed_diagnostics','appendix_table',[rel(FU/'rgarch_state_diagnostics.csv'),rel(FU/'rgarch_validity_decision.md')],fu=True,app=True)
fn=li.merge(mr.rename(columns={'Delta_PR_AUC_vs_ML_ALL':'avg_development_rank_delta'}),on='scheme',how='left'); fn['paper_decision']='negative/boundary result; F9 ex-post cannot reselect main scheme'
wt(fn,D['tables_appendix']/'appendix_table_a6_fusion_negative_result','appendix_table',[rel(FU/'lockbox_incremental_metrics.csv'),rel(FU/'model_ranking.csv')],fu=True,app=True)
# notes
notes={
'new_paper_logic.md':'# 新论文主线说明\n\n1. 新主线：压力测度—尾部状态描述—样本外 onset 预警。LSI/MarketLSI 是基于成交后高频数据的短时流动性压力代理；QVAR 描述 MarketLSI、收益、波动和成交承接的尾部分位联动；ML onset 检验样本外预警能力。\n\n2. 删除 RGARCH：RV、RBV、MedRV、RMAD 均 invalid_for_primary。RGARCH 模块从正文删除；若必须保留，只能在附录或局限性中一句话说明其诊断不稳。\n\n3. 不再讲融合实验：融合未稳定超过 ML_ALL，F9 ex-post 不能回头选择主方案。融合实验不作为论文主线。\n\n4. QVAR 角色：尾部分位联动描述器。\n\n5. ML onset 角色：核心样本外预警结果。\n\n6. 结构从“三方法并列”改为“压力测度—尾部状态描述—样本外 onset 预警”。\n\n7. 保留 LSI、QVAR、onset 标签、P/M/C/ALL、事件级评价和预算评价。\n\n8. 降级 fusion、RGARCH 诊断和 C 单独贡献。\n\n9. 删除 RGARCH 正文模块和融合成功叙述。\n\n10. 正文进入 MarketLSI、QVAR tail state、onset 主结果、特征组增量、事件级和预算评价。\n\n11. 附录进入完整模型、Top-K、QVAR 诊断、RGARCH invalid 和 fusion negative。\n\n12. 不再提 RGARCH 主贡献、融合成功、QVAR 稳定提升 ML_ALL、C 单独显著和因果解释。\n',
'paper_structure_revision_plan.md':'# 论文结构重构方案\n\n原论文问题是方法堆叠且证据强度不一致。新主线为数据、LSI 构造与 onset 标签；QVAR 尾部分位联动与市场压力状态；样本外 onset 预警模型与基线设计；实证结果；结论与局限性。引言聚焦成交后高频数据是否可形成短时压力代理和样本外预警。文献综述围绕流动性压力度量、尾部分位联动、机器学习预警和事件级评价。RGARCH 正文删除，只在附录或局限性记录 invalid_for_primary。QVAR 保留为尾部状态描述。ML onset 成为核心。稳健性安排完整模型、Top-K、校准、QVAR 诊断、RGARCH 删除依据和融合负结果。正文图为 fig_main_01 至 fig_main_08，正文表为 table_main_01 至 table_main_06；附录图为 fig_appendix_a1 至 a6，附录表为 appendix_table_a1 至 a6。\n',
'claims_allowed_disallowed.md':'# 结果声明边界\n\n## A. 可以声称\n1. 基于成交后高频数据构造的 LSI 能刻画短时压力代理。\n2. MarketLSI 与重大市场状态变化具有事件对应性。\n3. QVAR 显示市场压力、收益、波动、成交承接存在尾部分位联动。\n4. onset 标签下，ML 相对 naive persistence 有稳定 PR-AUC 增量。\n5. ALL 特征组相对 P 有稳定增量。\n6. 修正事件级评价显示模型对部分压力 episode 有提前识别能力。\n7. 预算约束评价可说明有限监测资源下的排序价值。\n\n## B. 不应声称\n1. LSI 是真实盘口流动性。\n2. RGARCH 是核心贡献。\n3. 计量-ML 融合成功。\n4. QVAR 状态稳定提升 ML_ALL。\n5. 横截面 C 单独显著。\n6. 事件级预警可替代监管或交易决策。\n7. 模型有因果解释。\n',
'abstract_intro_material.md':'# 摘要和引言素材\n\n## 新摘要候选（不超过300字）\n本文基于 A 股 1 分钟 OHLCV 与成交额数据，构造反映短时流动性压力的 LSI 与 MarketLSI 指标，并研究历史高频状态能否预警未来 5 或 10 分钟的新一轮压力发生。研究首先使用 QVAR 描述 MarketLSI、收益、波动和成交承接之间的尾部分位联动；随后构造剥离窗口重叠和 LSI 持续性的 onset 标签，使用机器学习模型进行样本外预警检验。结果显示，LightGBM 在 ALL 特征组下相对 naive persistence 具有稳定 PR-AUC 和 Top-K lift 增量，修正事件级评价表明模型可提前识别部分压力 episode。结论限于成交后数据下的压力代理和非因果样本外预警。\n\n## 引言第一段候选\n分钟级市场数据为流动性压力监测提供了高频观测窗口，但成交后 OHLCV 与成交额并不能直接等同于盘口真实流动性。本文关注能否利用这些成交后高频信息构造短时压力代理，并在剥离机械持续性和窗口重叠后，对未来 5 或 10 分钟新一轮压力发生形成样本外预警。\n\n## 核心研究问题候选\nLSI/MarketLSI 是否可作为压力代理；QVAR 是否揭示尾部分位联动；历史高频状态是否相对持久性基准提供样本外预警增量。\n\n## 三条贡献候选\n构造 onset 压力标签；用 QVAR 描述尾部状态；用样本外 ML 与事件级评价检验有限监测资源下的排序价值。\n\n## 主要发现候选\nLightGBM / ALL 在 H5/H10 上相对 naive persistence 取得稳定 PR-AUC 增量；ALL 相对 P 有稳定增量；C 单独不构成核心贡献；QVAR 可描述尾部状态但不应声称其稳定提升 ML_ALL。\n\n## 局限性候选\nLSI 不是真实盘口 ground truth；结果不是因果解释；预警有误报成本；RGARCH 与融合实验不进入正文主结论。\n'}
for n,t in notes.items():
    p=D['writing_notes']/n; p.write_text(t,encoding='utf-8'); src(p,'writing_note_md',[rel(ON/'cloud_ml_effectiveness_result_digest.md'),rel(FU/'paper_optimization_decision.md')],on=True,qv=True,fu=True,main=True,rev=n=='abstract_intro_material.md')
# README/handoff/source
(PACK/'README.md').write_text(f'# Paper Material Pack\n\nGenerated: {datetime.utcnow().isoformat(timespec="seconds")}Z\n\n本轮目的：生成正式改写论文前的材料包，不修改论文正文或 final TeX。\n\n删除 RGARCH：所有候选规格 invalid_for_primary，正文材料删除 RGARCH 主模块，仅附录保留负结果诊断。\n\n不再强调融合实验：融合未稳定超过 ML_ALL，F9 ex-post 不能回头作为主方案。\n\n新主线：QVAR 尾部风险描述 + 机器学习 onset 样本外预警。\n\n正文表：table_main_01 至 table_main_06。附录表：appendix_table_a1 至 appendix_table_a6。正文图：fig_main_01 至 fig_main_08。附录图：fig_appendix_a1 至 fig_appendix_a6。\n\n图表 QC 报告位于 figure_qc/。下一步可基于 writing_notes/ 正式改写论文正文。\n\nSafety：未修改论文正文，未修改 final TeX，未提交 parquet/checkpoint/joblib/raw data。\n',encoding='utf-8')
(PACK/'handoff_paper_material_pack.md').write_text(f'# Handoff: paper material pack\n\nGenerated: {datetime.utcnow().isoformat(timespec="seconds")}Z\n\n输出路径：experiments/paper_material_pack/README.md；tables_main/；tables_appendix/；figures_main/；figures_appendix/；figure_qc/；writing_notes/；source_index/source_file_index.csv；final_material_check_report.md。\n\n关键结论：论文主线调整为 QVAR 尾部风险描述 + ML onset 样本外预警；RGARCH 从正文删除；融合实验不作为主线；QVAR 是状态描述器；ML onset 是核心结果。\n\n正文建议：使用 table_main_01 至 06 和 fig_main_01 至 08。附录建议：使用 appendix_table_a1 至 a6 和 fig_appendix_a1 至 a6。\n\n风险点：LSI 只能称为成交后高频数据下的短时压力代理；事件级预警有误报成本；不能做因果或决策替代声明。\n\nSafety：未修改论文正文；未修改 final TeX；未提交 parquet / checkpoint / joblib。\n',encoding='utf-8')
src(PACK/'README.md','readme_md',[rel(D['writing_notes']/'new_paper_logic.md')],main=True); src(PACK/'handoff_paper_material_pack.md','handoff_md',[rel(PACK/'README.md')],main=True)
pd.DataFrame(idx).to_csv(D['source_index']/'source_file_index.csv',index=False,encoding='utf-8-sig')
pd.DataFrame({'missing_source':sorted(set(missing))}).to_csv(D['outputs']/'missing_source_inventory.csv',index=False,encoding='utf-8-sig')
(D['outputs']/'missing_source_inventory.md').write_text(md(pd.DataFrame({'missing_source':sorted(set(missing))})),encoding='utf-8')
shutil.copyfile(__file__,D['scripts']/'build_pack_tables.py')
print('TABLES_NOTES_DONE', PACK)
print('missing', sorted(set(missing)))
