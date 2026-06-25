# Inclusion decision note

Final decision: B. Use as robustness or limitation

Reason: The onset task has predictive content, but the full set of main-text gates is not satisfied.

Evidence:
- H5: validation selected LightGBM / ALL; test PR-AUC=0.1578; Delta PR-AUC vs naive=0.1035; Top5 lift=5.5465; Delta Top5 lift vs naive=4.9381.
- H10: validation selected SMARTBoost / ALL; test PR-AUC=0.1928; Delta PR-AUC vs naive=0.1162; Top5 lift=5.4515; Delta Top5 lift vs naive=4.5873.

Bootstrap summary:
- H5 best_vs_naive / PR_AUC: delta=0.1035, 95% CI=[0.0948, 0.1162], rows=80000
- H5 best_vs_naive / Top5_lift: delta=4.9381, 95% CI=[4.5916, 5.3461], rows=80000
- H5 M_vs_P_same_model / PR_AUC: delta=-0.0103, 95% CI=[-0.0161, -0.0033], rows=80000
- H5 M_vs_P_same_model / Top5_lift: delta=-0.0990, 95% CI=[-0.5230, 0.2187], rows=80000
- H5 C_vs_P_same_model / PR_AUC: delta=-0.0126, 95% CI=[-0.0201, -0.0050], rows=80000
- H5 C_vs_P_same_model / Top5_lift: delta=-0.4033, 95% CI=[-0.7026, -0.0270], rows=80000
- H5 ALL_vs_P_same_model / PR_AUC: delta=0.0259, 95% CI=[0.0165, 0.0352], rows=80000
- H5 ALL_vs_P_same_model / Top5_lift: delta=0.6367, 95% CI=[0.2744, 1.0219], rows=80000
- H10 best_vs_naive / PR_AUC: delta=0.1162, 95% CI=[0.1067, 0.1278], rows=80000
- H10 best_vs_naive / Top5_lift: delta=4.5873, 95% CI=[4.1932, 4.8610], rows=80000
- H10 M_vs_P_same_model / PR_AUC: delta=-0.0295, 95% CI=[-0.0358, -0.0224], rows=80000
- H10 M_vs_P_same_model / Top5_lift: delta=-0.4211, 95% CI=[-0.6096, -0.2376], rows=80000
- H10 C_vs_P_same_model / PR_AUC: delta=-0.0302, 95% CI=[-0.0375, -0.0227], rows=80000
- H10 C_vs_P_same_model / Top5_lift: delta=-0.4820, 95% CI=[-0.6852, -0.2969], rows=80000
- H10 ALL_vs_P_same_model / PR_AUC: delta=0.0105, 95% CI=[0.0015, 0.0223], rows=80000
- H10 ALL_vs_P_same_model / Top5_lift: delta=0.1219, 95% CI=[-0.1836, 0.4272], rows=80000

Event-level summary:
- H10: events=2209, recall=20.01%, mean lead=21.9344 minutes, daily false alarms=24.2429
- H5: events=2462, recall=19.54%, mean lead=10.3763 minutes, daily false alarms=24.8406

Paper-body safety: this run did not modify LaTeX paper text.
