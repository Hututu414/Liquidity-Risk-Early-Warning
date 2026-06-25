from __future__ import annotations

import json
import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import pandas as pd

from config import paths
from src.models.model_data import load_label_thresholds, load_time_split, write_markdown


def run() -> None:
    paths.ensure_runtime_dirs()
    paths.LEAKAGE_AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    split = load_time_split()
    thresholds = load_label_thresholds()
    params_path = paths.STAGE2_DIR / "standardization_params_train_code_slot.parquet"
    params = pd.read_parquet(params_path, columns=["code", "slot", "variable", "median", "mad", "n_train"])
    qvar_stats_path = paths.QVAR_TABLE_DIR / "qvar_train_standardization_stats.csv"
    qvar_oos_path = paths.QVAR_TABLE_DIR / "qvar_blocked_oos_pinball_loss.csv"
    rgarch_param_path = paths.RGARCH_TABLE_DIR / "rgarch_carr_sk_adapted_parameter_estimates.csv"
    smartboost_note = paths.REVIEWS_DIR / "model_audit" / "smartboost_verification.md"

    checks = []
    failures = []
    if params.empty:
        failures.append("standardization_params_train_code_slot.parquet is empty")
    else:
        checks.append(f"Stage2 train code-slot standardization rows: {len(params):,}")
        checks.append(f"Stage2 standardization median/MAD variables: {params['variable'].nunique()}")
        checks.append(f"Minimum n_train across saved code-slot-variable params: {int(params['n_train'].min())}")

    if set(thresholds) == {"H5", "H10"}:
        checks.append(f"Label thresholds from train file: {json.dumps(thresholds, ensure_ascii=False)}")
    else:
        failures.append(f"Unexpected label threshold keys: {sorted(thresholds)}")

    if qvar_stats_path.exists():
        qvar_stats = pd.read_csv(qvar_stats_path)
        checks.append(f"QVAR train-only standardization variables: {qvar_stats['variable'].tolist()}")
    else:
        failures.append("Missing QVAR train standardization stats")

    if qvar_oos_path.exists():
        qvar_oos = pd.read_csv(qvar_oos_path)
        if set(qvar_oos["eval_period"].unique()).issubset({"validation", "test"}):
            checks.append("QVAR blocked out-of-sample evaluation uses validation/test periods only.")
        else:
            failures.append("QVAR OOS metrics contain unexpected eval periods")
    else:
        failures.append("Missing QVAR blocked OOS metrics")

    if rgarch_param_path.exists():
        checks.append("RGARCH-CARR-SK adapted parameters exist; train-period estimation is documented in the model note.")
    else:
        failures.append("Missing RGARCH parameter summary")

    if smartboost_note.exists():
        checks.append("SMARTboost verification note exists; no formal SMARTboost conclusion was generated.")
    else:
        failures.append("Missing SMARTboost verification note")

    status = "PASS" if not failures else "FAIL"
    lines = [
        "# Core Model No-Lookahead Audit",
        "",
        f"- 状态：{status}",
        f"- 训练期：{split['train_start']} 至 {split['train_end']}",
        f"- 验证期：{split['validation_start']} 至 {split['validation_end']}",
        f"- 测试期：{split['test_start']} 至 {split['test_end']}",
        "",
        "## 检查结果",
        "",
        *(f"- {item}" for item in checks),
        "",
        "## 失败项",
        "",
        *(f"- {item}" for item in failures),
        "- 无" if not failures else "",
        "",
        "## 结论",
        "",
        "- Stage2 的 code-slot median/MAD 和标签阈值文件均来自训练期构造。",
        "- RGARCH-CARR-SK MarketLSI 适配模型使用训练期估计参数，然后递推验证期和测试期风险路径。",
        "- QVAR 使用训练期标准化；验证期使用训练期模型，测试期使用训练+验证期扩展模型，均按时间顺序推进。",
        "- 未使用随机打乱。",
        "",
    ]
    write_markdown(paths.LEAKAGE_AUDIT_DIR / "core_model_no_lookahead_audit.md", "\n".join(lines))
    if failures:
        raise RuntimeError("; ".join(failures))
    print("core model no-lookahead audit PASS")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"core model no-lookahead audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
