from pathlib import Path
import sys

CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from config import paths


def test_project_root_detection():
    assert (paths.PROJECT_ROOT / "AGENTS.md").exists()
    assert paths.CODE_ROOT.name == "code"


def test_fixed_python_path_is_project_standard():
    assert str(paths.PYTHON_EXE).endswith(r".venv-codex-data\Scripts\python.exe")
