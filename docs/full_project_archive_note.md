# Full Project Archive Branch

This branch keeps the complete small-file project archive for internal recovery and reference.

It includes:

- Clean code-release files from `main`.
- Local thesis source and compiled thesis PDF assets under `report/latex_project/`.
- Legacy paper-build assets under `08_report/latex_project/`.
- Agent handoff and audit notes.
- Paper material pack files.
- Small result tables, figures, and documentation.

It still excludes large or cache-like files:

```text
*.parquet
*.joblib
*.pkl
*.pickle
*.npy
*.npz
data_inbox/
data_intermediate/
checkpoints/
logs/
pipeline_logs/
__pycache__/
.venv/
```

The default public/review branch remains `main`. This archive branch is not intended as the teacher-facing clean repository.
