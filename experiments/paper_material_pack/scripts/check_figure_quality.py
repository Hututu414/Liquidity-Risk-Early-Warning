# -*- coding: utf-8 -*-
from pathlib import Path
import csv, re
import numpy as np
try:
    from PIL import Image
except Exception:
    Image=None
ROOT=Path('/workspaces/Liquidity-Risk-Early-Warning')
PACK=ROOT/'experiments/paper_material_pack'
OUT=PACK/'figure_qc'
OUT.mkdir(parents=True,exist_ok=True)
expected=['fig_main_01_marketlsi_events','fig_main_02_qvar_tail_response','fig_main_03_qvar_tail_state_series','fig_main_04_onset_pr_curve','fig_main_05_delta_pr_auc','fig_main_06_feature_group_increment','fig_main_07_event_level_monitoring','fig_main_08_budgeted_event_tradeoff','fig_appendix_a1_label_event_rate','fig_appendix_a2_topk_lift_curve','fig_appendix_a3_calibration_curve','fig_appendix_a4_qvar_diagnostics','fig_appendix_a5_rgarch_invalidity_summary','fig_appendix_a6_fusion_negative_result']
def rel(p):
    try: return str(p.relative_to(ROOT))
    except Exception: return str(p)
rows=[]
for stem in expected:
    folder=PACK/'figures_main' if stem.startswith('fig_main') else PACK/'figures_appendix'
    png=folder/(stem+'.png'); pdf=folder/(stem+'.pdf')
    st='PASS'; issues=[]; w=0; h=0; dpi=''
    if not png.exists(): st='FAIL'; issues.append('missing_png')
    if not pdf.exists(): st='FAIL'; issues.append('missing_pdf')
    if png.exists():
        if png.stat().st_size<20000: st='FAIL'; issues.append('png_too_small')
        if Image:
            try:
                im=Image.open(png); w,h=im.size; dpi=str(im.info.get('dpi','')); arr=np.asarray(im.convert('L'))
                if w<1200 or h<700: st='FAIL'; issues.append('pixel_dimension_low')
                if float(arr.std())<2: st='FAIL'; issues.append('possibly_blank')
            except Exception as e:
                st='FAIL'; issues.append('png_read_error:'+str(e))
    if pdf.exists() and pdf.stat().st_size<5000: st='FAIL'; issues.append('pdf_too_small')
    if not re.match(r'fig_(main|appendix)_[0-9a-z_]+$',stem): st='FAIL'; issues.append('bad_name')
    if not issues: issues.append('static_checks_ok')
    rows.append({'figure':stem,'png':rel(png),'pdf':rel(pdf),'status':st,'issues':';'.join(issues),'width_px':w,'height_px':h,'dpi':dpi})
with (OUT/'figure_quality_report.csv').open('w',newline='',encoding='utf-8-sig') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
passed=all(r['status']=='PASS' for r in rows)
md=['# Figure Quality Report','', '- total_figures: {}'.format(len(rows)), '- passed: {}'.format(passed), '', '| figure | status | issues | width_px | height_px |','| --- | --- | --- | --- | --- |']
for r in rows:
    md.append('| {} | {} | {} | {} | {} |'.format(r['figure'],r['status'],r['issues'],r['width_px'],r['height_px']))
md.append('\nAll required PNG/PDF figure pairs passed static quality checks. No automatic repair was triggered.' if passed else '\nSome figures failed static checks. Re-run builder once, then inspect manually.')
(OUT/'figure_quality_report.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print('FIGURE_QC_PASS',passed)
