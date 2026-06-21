from __future__ import annotations

import importlib
import os
import platform
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ["numpy", "pandas", "pyarrow", "sklearn", "matplotlib", "yaml", "joblib", "lightgbm"]


def version_of(package: str) -> str:
    try:
        module = importlib.import_module(package)
    except Exception as exc:
        return f"MISSING ({exc.__class__.__name__}: {exc})"
    return str(getattr(module, "__version__", "installed"))


def memory_hint() -> str:
    try:
        import psutil

        vm = psutil.virtual_memory()
        return f"available={vm.available / (1024 ** 3):.2f} GB, total={vm.total / (1024 ** 3):.2f} GB"
    except Exception:
        return "unavailable"


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def count_candidate_data() -> int:
    dirs = ["data", "processed", "data_inbox", "data_intermediate", "outputs", "experiments"]
    suffixes = (".parquet", ".csv", ".csv.gz", ".pkl", ".pickle", ".feather")
    count = 0
    for name in dirs:
        base = ROOT / name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            parts = set(path.parts)
            if parts.intersection({".git", "__pycache__", ".venv", "venv", "node_modules", "build", "dist"}):
                continue
            if path.is_file() and path.name.endswith(suffixes):
                count += 1
    return count


def main() -> int:
    experiment_entry = ROOT / "experiments" / "onset_baseline_check" / "run_onset_baseline.py"
    print("Environment check")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {ROOT}")
    print(f"Git commit: {git_commit()}")
    print(f"Runtime: GitHub Actions={os.getenv('GITHUB_ACTIONS') == 'true'}, Codespaces={bool(os.getenv('CODESPACES'))}")
    print(f"Memory: {memory_hint()}")
    print("Packages:")
    for package in PACKAGES:
        print(f"  - {package}: {version_of(package)}")
    print(f"Experiment entry found: {experiment_entry.exists()} ({experiment_entry.relative_to(ROOT)})")
    print(f"Candidate data files found: {count_candidate_data()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
