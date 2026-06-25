# -*- coding: utf-8 -*-
from pathlib import Path
import re, csv, shutil, subprocess
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path('/workspaces/Liquidity-Risk-Early-Warning')
PACK=ROOT/'experiments/paper_material_pack'
D={k:PACK/k for k in ['outputs','figures_main','figures_appendix','figure_qc','scripts','source_index']}
ON=ROOT/'experiments/onset_baseline_check/outputs'; PR=ROOT/'experiments/onset_baseline_check/checkpoints/predictions'; FU=ROOT/'experiments/econometric_ml_fusion/outputs'; CK=ROOT/'experiments/econometric_ml_fusion/checkpoints'
plt.rcParams.update({'font.family':'DejaVu Sans','axes.titlesize':9,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'savefig.dpi':300,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':0.25})
idx=[]
def rel(p):
    try: return str(Path(p).relative_to(ROOT))
    except Exception: return str(p)
def add(a,t,s,on=False,qv=False,fu=False,main=False,app=False,rev=False):
    idx.append({'artifact_path':rel(a),'artifact_type':t,'source_files':';'.join(map(str,s)),'from_onset':on,'from_qvar':qv,'from_fusion_negative_result':fu,'can_enter_main_text':main,'suggest_appendix':app,'needs_manual_review':rev})
def save(fig,name,folder):
    png=folder/(name+'.png'); pdf=folder/(name+'.pdf'); fig.tight_layout(pad=.8); fig.savefig(png,dpi=300,bbox_inches='tight'); fig.savefig(pdf,bbox_inches='tight'); plt.close(fig); return png,pdf
def pred(h,m,g): return pq.read_table(PR/f'predictions_onset_{h}_{m}_{g}.parquet',columns=['y','score','date']).to_pandas()
def pr_points(y,s,n=500):
    y=np.asarray(y).astype(int); s=np.asarray(s); o=np.argsort(-s,kind='mergesort'); yy=y[o]; tot=yy.sum(); tp=np.cumsum(yy); rank=np.arange(1,len(yy)+1); prec=tp/rank; rec=tp/tot; ix=np.unique(np.linspace(0,len(yy)-1,min(n,len(yy))).astype(int)); return np.r_[0,rec[ix],1],np.r_[prec[0],prec[ix],tot/len(yy)]
full=pd.read_csv(D['outputs']/'derived_full80_daily_marketlsi_event_rate.csv',parse_dates=['date'])
qday=pd.read_csv(D['outputs']/'derived_qvar_daily_tail_states.csv',parse_dates=['date'])
mc=pd.read_csv(ON/'model_comparison_summary.csv'); de=pd.read_csv(ON/'delta_vs_persistence.csv'); ev=pd.read_csv(ON/'event_level_metrics_revised.csv'); bu=pd.read_csv(ON/'budgeted_event_metrics.csv'); tk=pd.read_csv(ON/'topk_lift_table.csv'); li=pd.read_csv(FU/'lockbox_incremental_metrics.csv')
qv=pq.read_table(CK/'qvar_market_states.parquet').to_pandas()
preds={(h,m,g):pred(h,m,g) for h in ['H5','H10'] for m,g in [('LightGBM','ALL'),('Naive','P')]}
periods=[('base_train',pd.Timestamp('2023-05-15'),pd.Timestamp('2025-02-28')),('base_validation',pd.Timestamp('2025-03-01'),pd.Timestamp('2025-09-26')),('development/test',pd.Timestamp('2025-09-27'),pd.Timestamp('2026-02-28')),('lockbox',pd.Timestamp('2026-03-01'),pd.Timestamp('2026-05-13'))]
# main figures
fig,ax=plt.subplots(figsize=(7.2,2.8)); ax.plot(full.date,full.MarketLSI_daily_mean,color='black',lw=.8,label='MarketLSI daily mean')
for lab,s,e in periods: ax.axvspan(s,e,color='0.9',alpha=.55 if lab=='lockbox' else .3,lw=0)
for _,r in full.nlargest(5,'MarketLSI_daily_mean').iterrows(): ax.axvline(r.date,color='0.35',lw=.5,ls='--'); ax.text(r.date,ax.get_ylim()[1],r.date.strftime('%Y-%m-%d'),rotation=90,va='top',ha='right',fontsize=5)
ax.set_ylabel('MarketLSI'); ax.set_xlabel('Date'); ax.legend(frameon=False,loc='upper left'); p=save(fig,'fig_main_01_marketlsi_events',D['figures_main']); add(p[0],'main_figure_png',[rel(D['outputs']/'derived_full80_daily_marketlsi_event_rate.csv')],on=True,main=True); add(p[1],'main_figure_pdf',[rel(D['outputs']/'derived_full80_daily_marketlsi_event_rate.csv')],on=True,main=True)
fig,ax=plt.subplots(figsize=(6.4,2.8))
for c,ls,col in [('qvar_mlsi_q50','-','black'),('qvar_mlsi_q90','--','0.35'),('qvar_mlsi_q95',':','0.15')]: ax.plot(qday.date,qday[c],lw=1,ls=ls,color=col,label=c)
ax.set_ylabel('Conditional quantile'); ax.set_xlabel('Date'); ax.legend(frameon=False,ncol=3,loc='upper left'); p=save(fig,'fig_main_02_qvar_tail_response',D['figures_main']); add(p[0],'main_figure_png',[rel(D['outputs']/'derived_qvar_daily_tail_states.csv')],qv=True,main=True); add(p[1],'main_figure_pdf',[rel(D['outputs']/'derived_qvar_daily_tail_states.csv')],qv=True,main=True)
fig,ax=plt.subplots(2,1,figsize=(6.4,3.6),sharex=True); ax[0].plot(qday.date,qday.xsec_lsi_mean,color='black',lw=.9); ax[0].set_ylabel('xsec LSI mean'); ax[1].plot(qday.date,qday.qvar_tail_spread_95_50,color='black',lw=.9,label='tail spread 95-50'); hi=qday.qvar_composite_tail_state>.5; ax[1].fill_between(qday.date,qday.qvar_tail_spread_95_50.min(),qday.qvar_tail_spread_95_50.max(),where=hi,color='0.85',alpha=.7,label='high-tail state'); ax[1].set_ylabel('QVAR spread'); ax[1].set_xlabel('Date'); ax[1].legend(frameon=False,loc='upper left'); p=save(fig,'fig_main_03_qvar_tail_state_series',D['figures_main']); add(p[0],'main_figure_png',[rel(D['outputs']/'derived_qvar_daily_tail_states.csv')],qv=True,main=True); add(p[1],'main_figure_pdf',[rel(D['outputs']/'derived_qvar_daily_tail_states.csv')],qv=True,main=True)
fig,axes=plt.subplots(1,2,figsize=(7,3),sharey=True)
for ax,h in zip(axes,['H5','H10']):
    for m,g,lab,c,ls in [('Naive','P','Naive persistence','0.55','--'),('LightGBM','ALL','LightGBM ALL','black','-')]:
        r,pc=pr_points(preds[(h,m,g)].y,preds[(h,m,g)].score); ax.plot(r,pc,color=c,ls=ls,lw=1,label=lab)
    ax.set_title(h); ax.set_xlabel('Recall')
axes[0].set_ylabel('Precision'); axes[0].legend(frameon=False); p=save(fig,'fig_main_04_onset_pr_curve',D['figures_main']); add(p[0],'main_figure_png',[rel(PR)],on=True,main=True,rev=True); add(p[1],'main_figure_pdf',[rel(PR)],on=True,main=True,rev=True)
cr=[]
for h in ['H5','H10']:
    d=de[(de.comparison==f'{h} best_vs_naive')&(de.metric=='PR_AUC')].iloc[0]; cr.append((h,d.observed_delta,d.ci_low,d.ci_high))
fig,ax=plt.subplots(figsize=(4.8,2.4)); y=np.arange(len(cr)); vals=[r[1] for r in cr]; ax.errorbar(vals,y,xerr=[[r[1]-r[2] for r in cr],[r[3]-r[1] for r in cr]],fmt='o',color='black',ecolor='0.35',capsize=3); ax.axvline(0,color='0.5',lw=.8); ax.set_yticks(y,[r[0] for r in cr]); ax.set_xlabel('Delta PR-AUC vs naive'); p=save(fig,'fig_main_05_delta_pr_auc',D['figures_main']); add(p[0],'main_figure_png',[rel(ON/'delta_vs_persistence.csv')],on=True,main=True); add(p[1],'main_figure_pdf',[rel(ON/'delta_vs_persistence.csv')],on=True,main=True)
fig,ax=plt.subplots(figsize=(5.4,3)); fgs=['P','M','C','ALL']; x=np.arange(len(fgs)); w=.35
for i,h in enumerate(['H5','H10']):
    vals=[mc[(mc.horizon==h)&(mc.model=='LightGBM')&(mc.feature_group==fg)].PR_AUC.iloc[0] for fg in fgs]; ax.bar(x+(i-.5)*w,vals,width=w,label=h,color='black' if i==0 else '0.65',edgecolor='black',linewidth=.4)
ax.set_xticks(x,fgs); ax.set_ylabel('PR-AUC'); ax.legend(frameon=False); p=save(fig,'fig_main_06_feature_group_increment',D['figures_main']); add(p[0],'main_figure_png',[rel(ON/'model_comparison_summary.csv')],on=True,main=True); add(p[1],'main_figure_pdf',[rel(ON/'model_comparison_summary.csv')],on=True,main=True)
fig,ax=plt.subplots(1,2,figsize=(6.8,3)); x=np.arange(len(ev)); ax[0].bar(x-.18,ev.label_aligned_event_recall,width=.36,color='black',label='label-aligned'); ax[0].bar(x+.18,ev.practical_window_event_recall,width=.36,color='0.65',edgecolor='black',linewidth=.4,label='practical'); ax[0].set_xticks(x,list(ev.horizon)); ax[0].set_ylabel('Event recall'); ax[0].legend(frameon=False); ax[1].bar(x-.18,ev.daily_false_alarms,width=.36,color='black'); ax[1].bar(x+.18,ev.practical_daily_false_alarms,width=.36,color='0.65',edgecolor='black',linewidth=.4); ax[1].set_xticks(x,list(ev.horizon)); ax[1].set_ylabel('Daily false alarms'); p=save(fig,'fig_main_07_event_level_monitoring',D['figures_main']); add(p[0],'main_figure_png',[rel(ON/'event_level_metrics_revised.csv')],on=True,main=True); add(p[1],'main_figure_pdf',[rel(ON/'event_level_metrics_revised.csv')],on=True,main=True)
fig,ax=plt.subplots(1,2,figsize=(7,3))
for h,c,mk in [('H5','black','o'),('H10','0.45','s')]:
    b=bu[(bu.horizon==h)&(bu.budget_type=='daily_top_n')].sort_values('budget_value'); ax[0].plot(b.budget_value,b.event_recall_practical,color=c,marker=mk,lw=1,label=h); ax[1].plot(b.budget_value,b.false_alarms_per_detected_event_practical,color=c,marker=mk,lw=1,label=h)
ax[0].set_xlabel('Daily signal budget'); ax[0].set_ylabel('Practical event recall'); ax[1].set_xlabel('Daily signal budget'); ax[1].set_ylabel('False alarms per detected event'); ax[0].legend(frameon=False); ax[1].legend(frameon=False); p=save(fig,'fig_main_08_budgeted_event_tradeoff',D['figures_main']); add(p[0],'main_figure_png',[rel(ON/'budgeted_event_metrics.csv')],on=True,main=True); add(p[1],'main_figure_pdf',[rel(ON/'budgeted_event_metrics.csv')],on=True,main=True)
# appendix figures
fig,ax=plt.subplots(figsize=(6.4,2.8)); ax.plot(full.date,full.Stress_H5_daily_rate,color='black',lw=.8,label='H5'); ax.plot(full.date,full.Stress_H10_daily_rate,color='0.5',lw=.8,ls='--',label='H10'); ax.set_ylabel('Daily onset event rate'); ax.set_xlabel('Date'); ax.legend(frameon=False); p=save(fig,'fig_appendix_a1_label_event_rate',D['figures_appendix']); add(p[0],'appendix_figure_png',[rel(D['outputs']/'derived_full80_daily_marketlsi_event_rate.csv')],on=True,app=True); add(p[1],'appendix_figure_pdf',[rel(D['outputs']/'derived_full80_daily_marketlsi_event_rate.csv')],on=True,app=True)
fig,axes=plt.subplots(1,2,figsize=(7,3),sharey=True)
for ax,h in zip(axes,['H5','H10']):
    for m,g,lab,c,ls in [('Naive','P','Naive','0.55','--'),('LightGBM','ALL','LightGBM ALL','black','-')]:
        d=tk[(tk.period=='test')&(tk.horizon==h)&(tk.model==m)&(tk.feature_group==g)].sort_values('top_frac'); ax.plot(d.top_frac*100,d.lift,color=c,ls=ls,marker='o',lw=1,label=lab)
    ax.set_title(h); ax.set_xlabel('Top percentile')
axes[0].set_ylabel('Lift'); axes[0].legend(frameon=False); p=save(fig,'fig_appendix_a2_topk_lift_curve',D['figures_appendix']); add(p[0],'appendix_figure_png',[rel(ON/'topk_lift_table.csv')],on=True,app=True); add(p[1],'appendix_figure_pdf',[rel(ON/'topk_lift_table.csv')],on=True,app=True)
calrows=[]; fig,axes=plt.subplots(1,2,figsize=(7,3),sharex=True,sharey=True)
for ax,h in zip(axes,['H5','H10']):
    d=preds[(h,'LightGBM','ALL')].copy(); d['bin']=pd.qcut(d.score,q=10,duplicates='drop'); cal=d.groupby('bin',observed=True).agg(mean_score=('score','mean'),obs_rate=('y','mean'),rows=('y','size')).reset_index(drop=True); cal['horizon']=h; calrows.extend(cal.to_dict('records')); ax.plot([0,1],[0,1],color='0.7',lw=.8,ls='--'); ax.plot(cal.mean_score,cal.obs_rate,color='black',marker='o',lw=1); ax.set_title(h); ax.set_xlabel('Mean predicted score')
axes[0].set_ylabel('Observed event rate'); calp=D['outputs']/'derived_calibration_bins.csv'; pd.DataFrame(calrows).to_csv(calp,index=False,encoding='utf-8-sig'); add(calp,'derived_csv',[rel(PR)],on=True,app=True,rev=True); p=save(fig,'fig_appendix_a3_calibration_curve',D['figures_appendix']); add(p[0],'appendix_figure_png',[rel(calp)],on=True,app=True); add(p[1],'appendix_figure_pdf',[rel(calp)],on=True,app=True)
fig,ax=plt.subplots(1,2,figsize=(7,3)); ax[0].hist(qv.qvar_tail_spread_95_50.dropna(),bins=40,color='0.3',edgecolor='white'); ax[0].set_xlabel('qvar_tail_spread_95_50'); ax[0].set_ylabel('Count'); sh=pd.Series({'high_tail_state':qv.qvar_high_tail_state.mean(),'composite_tail_state':qv.qvar_composite_tail_state.mean()}); ax[1].bar(np.arange(len(sh)),sh.values,color=['black','0.6'],edgecolor='black',linewidth=.4); ax[1].set_xticks(np.arange(len(sh)),sh.index,rotation=20,ha='right'); ax[1].set_ylabel('State share'); p=save(fig,'fig_appendix_a4_qvar_diagnostics',D['figures_appendix']); add(p[0],'appendix_figure_png',[rel(CK/'qvar_market_states.parquet')],qv=True,app=True); add(p[1],'appendix_figure_pdf',[rel(CK/'qvar_market_states.parquet')],qv=True,app=True)
rg=pd.read_csv(FU/'rgarch_state_diagnostics.csv'); fig,ax=plt.subplots(figsize=(5.6,2.6)); vals=[0 if v!='valid_for_primary' else 1 for v in rg.validity]; ax.bar(np.arange(len(vals)),vals,color='0.7',edgecolor='black',linewidth=.5); ax.set_xticks(np.arange(len(vals)),rg.spec,rotation=25,ha='right'); ax.set_ylim(0,1.05); ax.set_ylabel('Valid for primary'); p=save(fig,'fig_appendix_a5_rgarch_invalidity_summary',D['figures_appendix']); add(p[0],'appendix_figure_png',[rel(FU/'rgarch_state_diagnostics.csv')],fu=True,app=True); add(p[1],'appendix_figure_pdf',[rel(FU/'rgarch_state_diagnostics.csv')],fu=True,app=True)
fig,ax=plt.subplots(figsize=(7.2,3)); sel=li[li.scheme.isin(['F1_ALL_QVAR','F4_ALL_ECON_INTERACTIONS','F9_STACKED','B2_EconometricHazard'])]; schemes=list(sel.scheme.drop_duplicates()); x=np.arange(len(schemes)); w=.35
for i,h in enumerate(['H5','H10']):
    vals=[]
    for s in schemes:
        d=sel[(sel.scheme==s)&(sel.horizon==h)]; vals.append(d.Delta_PR_AUC_vs_ML_ALL.iloc[0] if len(d) else np.nan)
    ax.bar(x+(i-.5)*w,vals,width=w,label=h,color='black' if i==0 else '0.65',edgecolor='black',linewidth=.4)
ax.axhline(0,color='0.4',lw=.8); ax.set_xticks(x,schemes,rotation=25,ha='right'); ax.set_ylabel('Delta PR-AUC vs ML_ALL'); ax.legend(frameon=False); p=save(fig,'fig_appendix_a6_fusion_negative_result',D['figures_appendix']); add(p[0],'appendix_figure_png',[rel(FU/'lockbox_incremental_metrics.csv')],fu=True,app=True); add(p[1],'appendix_figure_pdf',[rel(FU/'lockbox_incremental_metrics.csv')],fu=True,app=True)
# captions
(D['figures_main']/'captions.md').write_text('# 正文图 caption 草稿\n\nfig_main_01_marketlsi_events：展示 MarketLSI 日度均值和样本区间边界，说明成交后压力代理与市场状态变化的对应性。\n\nfig_main_02_qvar_tail_response：展示 QVAR q=0.50/0.90/0.95 的 MarketLSI 条件分位路径，用于尾部联动描述，不用于预测增量主张。\n\nfig_main_03_qvar_tail_state_series：展示 QVAR tail spread 与高尾部状态，说明 QVAR 是市场尾部状态描述器。\n\nfig_main_04_onset_pr_curve：比较 H5/H10 naive persistence 与 LightGBM ALL 的样本外 PR 曲线。\n\nfig_main_05_delta_pr_auc：展示 best-vs-naive Delta PR-AUC 和 block-bootstrap CI。\n\nfig_main_06_feature_group_increment：展示 P/M/C/ALL PR-AUC，强调 ALL 有增量、C 单独不构成核心贡献。\n\nfig_main_07_event_level_monitoring：展示事件级 recall 和 daily false alarms，说明提前识别与误报成本并存。\n\nfig_main_08_budgeted_event_tradeoff：展示 daily_top_n 预算下 practical recall 与误报权衡。\n',encoding='utf-8')
(D['figures_appendix']/'captions.md').write_text('# 附录图 caption 草稿\n\nfig_appendix_a1_label_event_rate：H5/H10 onset 事件率随时间变化。\n\nfig_appendix_a2_topk_lift_curve：Top 1/5/10/20% lift 曲线。\n\nfig_appendix_a3_calibration_curve：LightGBM ALL 分箱校准曲线，仅作诊断。\n\nfig_appendix_a4_qvar_diagnostics：QVAR tail spread 分布与尾部状态占比。\n\nfig_appendix_a5_rgarch_invalidity_summary：RGARCH 候选规格 invalid 诊断，不进正文主线。\n\nfig_appendix_a6_fusion_negative_result：融合方案相对 ML_ALL 的 Delta PR-AUC，展示未稳定增量。\n',encoding='utf-8')
add(D['figures_main']/'captions.md','main_caption_md',[rel(D['figures_main'])],on=True,qv=True,main=True); add(D['figures_appendix']/'captions.md','appendix_caption_md',[rel(D['figures_appendix'])],on=True,qv=True,fu=True,app=True)
# append source index
old=pd.read_csv(D['source_index']/'source_file_index.csv') if (D['source_index']/'source_file_index.csv').exists() else pd.DataFrame()
pd.concat([old,pd.DataFrame(idx)],ignore_index=True).to_csv(D['source_index']/'source_file_index.csv',index=False,encoding='utf-8-sig')
shutil.copyfile(__file__,D['scripts']/'build_pack_figures.py')
print('FIGURES_DONE', len(list(D['figures_main'].glob('*.png'))), len(list(D['figures_appendix'].glob('*.png'))))
