# -*- coding: utf-8 -*-
from pathlib import Path
import csv, subprocess
import pandas as pd
ROOT=Path('/workspaces/Liquidity-Risk-Early-Warning')
PACK=ROOT/'experiments/paper_material_pack'
figs=['fig_main_01_marketlsi_events','fig_main_02_qvar_tail_response','fig_main_03_qvar_tail_state_series','fig_main_04_onset_pr_curve','fig_main_05_delta_pr_auc','fig_main_06_feature_group_increment','fig_main_07_event_level_monitoring','fig_main_08_budgeted_event_tradeoff','fig_appendix_a1_label_event_rate','fig_appendix_a2_topk_lift_curve','fig_appendix_a3_calibration_curve','fig_appendix_a4_qvar_diagnostics','fig_appendix_a5_rgarch_invalidity_summary','fig_appendix_a6_fusion_negative_result']
checks=[]
def add(k,p,e): checks.append({'check':k,'passed':bool(p),'evidence':str(e)})
bad=[]
for p in PACK.rglob('*.csv'):
    try: pd.read_csv(p)
    except Exception as e: bad.append(str(p)+':'+str(e))
add('all_csv_readable',not bad,'bad={}'.format(bad[:3]))
empty=[str(p) for p in PACK.rglob('*.md') if p.stat().st_size==0]
add('all_md_nonempty',not empty,'empty={}'.format(empty[:3]))
miss=[]
for stem in figs:
    folder=PACK/'figures_main' if stem.startswith('fig_main') else PACK/'figures_appendix'
    for ext in ['png','pdf']:
        if not (folder/(stem+'.'+ext)).exists(): miss.append(str(folder/(stem+'.'+ext)))
add('all_png_pdf_exist',not miss,'missing={}'.format(miss[:4]))
qc=PACK/'figure_qc/figure_quality_report.csv'
if qc.exists():
    q=pd.read_csv(qc); add('figure_qc_pass',(q.status=='PASS').all(),q.status.value_counts().to_dict())
else: add('figure_qc_pass',False,'missing qc csv')
idx=PACK/'source_index/source_file_index.csv'
if idx.exists():
    s=pd.read_csv(idx); add('source_index_complete',len(s)>=40,'rows={}'.format(len(s)))
else: add('source_index_complete',False,'missing')
text='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in PACK.rglob('*.md'))
bad_phrases=['QVAR 状态显著提升 ML_ALL','QVAR 状态稳定提升 ML_ALL，','横截面 C 单独显著增量成立','LSI 等同于真实盘口流动性','FutureMaxLSI']
hits=[x for x in bad_phrases if x in text]
add('no_disallowed_positive_claims',not hits,'hits={}'.format(hits))
add('crossstress_not_used_as_feature','CrossStress_used=True' not in text and 'CrossStress as feature' not in text,'negative/zero mentions only')
res=subprocess.run('git diff --name-only -- report/latex_project 08_report/latex_project',shell=True,cwd=ROOT,capture_output=True,text=True)
add('final_tex_not_modified',res.stdout.strip()=='',res.stdout.strip() or 'no diff')
lines=['# Final Material Check Report','']
for c in checks:
    lines.append('- {}: {} ({})'.format(c['check'],'PASS' if c['passed'] else 'FAIL',c['evidence']))
lines += ['', 'overall_pass: {}'.format(all(c['passed'] for c in checks))]
(PACK/'final_material_check_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
with (PACK/'final_material_check_report.csv').open('w',newline='',encoding='utf-8-sig') as f:
    wr=csv.DictWriter(f,fieldnames=['check','passed','evidence']); wr.writeheader(); wr.writerows(checks)
print('FINAL_MATERIAL_CHECK_PASS',all(c['passed'] for c in checks))
