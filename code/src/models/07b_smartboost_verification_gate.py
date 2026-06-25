from __future__ import annotations

import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from config import paths
from src.models.model_data import write_markdown


REQUIRED_TERMS = [
    "SMARTboost Learning for Tabular Data",
    "10.1093/jjfinec/nbae028",
    "boosting of symmetric smooth additive regression trees",
    "symmetric smooth trees",
    "loss [:L2]",
    "https://github.com/PaoloGiordani/SMARTboost.jl",
]


def run() -> None:
    paths.ensure_runtime_dirs()
    model_audit = paths.REVIEWS_DIR / "model_audit"
    model_audit.mkdir(parents=True, exist_ok=True)
    note_path = model_audit / "smartboost_verification.md"
    if not note_path.exists():
        blocker = model_audit / "SMARTBOOST_VERIFICATION_BLOCKER.md"
        write_markdown(blocker, "# SMARTBOOST Verification Blocker\n\nMissing `smartboost_verification.md`.\n")
        raise FileNotFoundError(note_path)

    text = note_path.read_text(encoding="utf-8")
    missing = [term for term in REQUIRED_TERMS if term not in text]
    try:
        from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: F401
    except Exception as exc:
        missing.append(f"Python adaptation dependency missing: {type(exc).__name__}: {exc}")

    if missing:
        blocker = "\n".join(
            [
                "# SMARTBOOST_VERIFICATION_BLOCKER",
                "",
                "SMARTBoost verification is not sufficient for formal forecasting.",
                "",
                "## Missing items",
                "",
                *(f"- {item}" for item in missing),
                "",
            ]
        )
        write_markdown(model_audit / "SMARTBOOST_VERIFICATION_BLOCKER.md", blocker)
        raise RuntimeError("; ".join(missing))

    gate = "\n".join(
        [
            "# SMARTBoost Verification Gate",
            "",
            "- 鐘舵€侊細PASS",
            "- 鍘熸枃銆丏OI銆佺畻娉曞畾涔夈€佸熀瀛︿範鍣ㄣ€佹崯澶卞嚱鏁拌鏄庡拰浣滆€呬唬鐮佹潵婧愬潎宸插湪 `smartboost_verification.md` 涓櫥璁般€?,
            "- 褰撳墠宸ョ▼涓嶇洿鎺ヨ繍琛屼綔鑰?Julia 鍖咃紱鏈疆鍏佽杩涘叆 **鍩轰簬鍘熸枃绠楁硶瀹氫箟鐨?Python 閫傞厤瀹炵幇**銆?,
            "- 鐩爣鍙橀噺闄愬畾涓?`Stress_H5` 鍜?`Stress_H10`銆?,
            "- 楠岃瘉蹇呴』浣跨敤鏃堕棿婊氬姩鏍锋湰澶栵紝涓嶅厑璁搁殢鏈哄垝鍒嗐€?,
            "",
        ]
    )
    write_markdown(model_audit / "smartboost_verification_gate.md", gate)
    print("SMARTBoost verification gate PASS")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"SMARTBoost verification gate failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
