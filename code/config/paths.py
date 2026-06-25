"""Central path definitions for the liquidity pressure project."""

from __future__ import annotations

from pathlib import Path


PYTHON_EXE = Path(r"D:\Users\TtT20\source\repos\.venv-codex-data\Scripts\python.exe")

CODE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_ROOT.parent

CONFIG_DIR = CODE_ROOT / "config"
SRC_DIR = CODE_ROOT / "src"
TESTS_DIR = CODE_ROOT / "tests"

DATA_INBOX = PROJECT_ROOT / "data_inbox"
PREPROCESSED_ROOT = DATA_INBOX / "preprocessed"
RAW_PANEL_PATH = PREPROCESSED_ROOT / "panel" / "minute_panel_preprocessed_raw.parquet"
PREPROCESSED_QUALITY_DIR = PREPROCESSED_ROOT / "quality"
PREPROCESSED_SAMPLE_DIR = PREPROCESSED_ROOT / "sample"
PREPROCESSED_SCRIPTS_DIR = PREPROCESSED_ROOT / "scripts"

INTERMEDIATE_DIR = PROJECT_ROOT / "data_intermediate"
STAGE0_PROFILE_DIR = INTERMEDIATE_DIR / "stage0_input_profile"
STAGE1_DIR = INTERMEDIATE_DIR / "stage1_model_ready"
MODEL_READY_BY_CODE_DIR = STAGE1_DIR / "model_ready_panel_by_code"
STAGE2_DIR = INTERMEDIATE_DIR / "stage2_lsi_labels"
STRESS_COMPONENTS_RAW_BY_CODE_DIR = STAGE2_DIR / "stress_components_raw_by_code"
LSI_UNLABELED_BY_CODE_DIR = STAGE2_DIR / "lsi_unlabeled_by_code"
LSI_LABELED_NO_MARKET_BY_CODE_DIR = STAGE2_DIR / "lsi_labeled_no_market_by_code"
LSI_LABELS_BY_CODE_DIR = STAGE2_DIR / "lsi_labels_by_code"

OUTPUT_DIR = PROJECT_ROOT / "outputs"
DIAGNOSTICS_OUTPUT_DIR = OUTPUT_DIR / "descriptive_diagnostics"
FIGURE_OUTPUT_DIR = DIAGNOSTICS_OUTPUT_DIR / "figures"
TABLE_OUTPUT_DIR = DIAGNOSTICS_OUTPUT_DIR / "tables"
TABLES_ROOT = OUTPUT_DIR / "tables"
FIGURES_ROOT = OUTPUT_DIR / "figures"
RGARCH_TABLE_DIR = TABLES_ROOT / "04_rgarch"
RGARCH_FIGURE_DIR = FIGURES_ROOT / "04_rgarch"
QVAR_TABLE_DIR = TABLES_ROOT / "05_qvar"
QVAR_FIGURE_DIR = FIGURES_ROOT / "05_qvar"
SMARTBOOST_TABLE_DIR = TABLES_ROOT / "06_smartboost"
SMARTBOOST_FIGURE_DIR = FIGURES_ROOT / "06_smartboost"

AGENT_WORKSPACE_DIR = PROJECT_ROOT / "agent_workspaces" / "codex_workspace"
REVIEWS_DIR = PROJECT_ROOT / "reviews"
DATA_AUDIT_DIR = REVIEWS_DIR / "data_audit"
LEAKAGE_AUDIT_DIR = REVIEWS_DIR / "leakage_audit"
FINAL_PACKAGE_AUDIT_DIR = REVIEWS_DIR / "final_package_audit"
ENVIRONMENT_MISSING_PACKAGES_PATH = REVIEWS_DIR / "environment_missing_packages.md"

LOG_DIR = PROJECT_ROOT / "pipeline_logs"
FINAL_OUTPUT_DIR = PROJECT_ROOT / "final_output"


def project_path(*parts: str) -> Path:
    """Return a path under the project root."""

    return PROJECT_ROOT.joinpath(*parts)


def require_project_root() -> Path:
    """Validate and return the project root."""

    if not (PROJECT_ROOT / "AGENTS.md").exists():
        raise RuntimeError(f"Project root was not detected correctly: {PROJECT_ROOT}")
    return PROJECT_ROOT


def ensure_runtime_dirs() -> None:
    """Create generated-output directories used by stages 0-3."""

    for path in [
        STAGE0_PROFILE_DIR,
        STAGE1_DIR,
        MODEL_READY_BY_CODE_DIR,
        STAGE2_DIR,
        STRESS_COMPONENTS_RAW_BY_CODE_DIR,
        LSI_UNLABELED_BY_CODE_DIR,
        LSI_LABELED_NO_MARKET_BY_CODE_DIR,
        LSI_LABELS_BY_CODE_DIR,
        DIAGNOSTICS_OUTPUT_DIR,
        FIGURE_OUTPUT_DIR,
        TABLE_OUTPUT_DIR,
        TABLES_ROOT,
        FIGURES_ROOT,
        RGARCH_TABLE_DIR,
        RGARCH_FIGURE_DIR,
        QVAR_TABLE_DIR,
        QVAR_FIGURE_DIR,
        SMARTBOOST_TABLE_DIR,
        SMARTBOOST_FIGURE_DIR,
        AGENT_WORKSPACE_DIR,
        DATA_AUDIT_DIR,
        LEAKAGE_AUDIT_DIR,
        FINAL_PACKAGE_AUDIT_DIR,
        LOG_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
