from __future__ import annotations

import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[2]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from config import paths
from src.models.model_data import write_markdown


def run() -> None:
    paths.ensure_runtime_dirs()
    (paths.REVIEWS_DIR / "model_audit").mkdir(parents=True, exist_ok=True)

    note = "\n".join(
        [
            "# SMARTboost Verification",
            "",
            "## 鏍搁獙缁撹",
            "",
            "SMARTboost 鐨勫師鏂囥€丏OI銆佺畻娉曞畾涔夊拰浣滆€呬唬鐮佹簮鍙互鏍搁獙锛涙湰杞笉鐢熸垚姝ｅ紡 SMARTboost 瀹炶瘉缁撹銆?,
            "",
            "## 鍙牳楠屾潵婧?,
            "",
            "- 鍘熸枃锛歅aolo Giordani, `SMARTboost Learning for Tabular Data`, Journal of Financial Econometrics, Volume 23, Issue 3, 2025, nbae028銆?,
            "- DOI锛歨ttps://doi.org/10.1093/jjfinec/nbae028",
            "- 鏈熷垔椤甸潰锛歨ttps://academic.oup.com/jfec/article/23/3/nbae028/7901240",
            "- 浣滆€呬唬鐮侊細https://github.com/PaoloGiordani/SMARTboost.jl",
            "",
            "## 绠楁硶瑕佺偣",
            "",
            "- 鍏ㄧО锛歜oosting of symmetric smooth additive regression trees銆?,
            "- 鍩哄涔犲櫒锛歴ymmetric smooth trees銆?,
            "- 璁粌妗嗘灦锛歜oosting锛涙爲鏁伴噺鐢?CV 鎴栭獙璇侀泦鏃╁仠閫夋嫨銆?,
            "- 鎹熷け鍑芥暟锛氬師鏂囪仛鐒?Gaussian likelihood / squared loss锛涗綔鑰?Julia 浠撳簱 README 褰撳墠鍐欐槑 `loss [:L2]`銆?,
            "- 姝ｅ垯鍖?鍏堥獙锛氬 smoothness 涓?leaf values 浣跨敤 thoughtfully designed priors / penalizations锛屼互鎻愬崌灏忔牱鏈拰浣庝俊鍣瘮鍦烘櫙琛ㄧ幇銆?,
            "- 璋冨弬鏂瑰紡锛氶粯璁ゆ繁搴︺€佸涔犵巼銆乸urged CV 鎴栧崟楠岃瘉闆嗭紱鏃堕棿搴忓垪/闈㈡澘鏁版嵁寮鸿皟涓嶈兘闅忔満 CV銆?,
            "- 浠ｇ爜鐘舵€侊細浣滆€?Julia 鐗堟湰鍏紑锛汻EADME 鍚屾椂璇存槑璇ュ寘宸茬敱 HTBoost superseded銆?,
            "",
            "## 鏈」鐩墽琛岃竟鐣?,
            "",
            "- 鏈疆鍙畬鎴愭牳楠岋紝涓嶆妸 SMARTboost 缁撹鍐欏叆姝ｅ紡瀹炶瘉缁撴灉銆?,
            "- 褰撳墠宸ョ▼鏄?Python stage0-stage3 鏁版嵁娴佹按绾匡紱鏈厤缃?Julia/R bridge锛屼篃鏈獙璇佷綔鑰呭寘鍦ㄦ湰鏈哄彲澶嶇幇銆?,
            "- 鏈」鐩洰鏍囨爣绛炬槸 `Stress_H5` / `Stress_H10` 浜嬩欢棰勮锛屼綔鑰呬粨搴撳綋鍓嶅叕寮€ README 閲嶇偣璇存槑 L2 loss锛涘垎绫绘垨姒傜巼棰勮鍙ｅ緞闇€瑕侀澶栨牳楠屽疄鐜般€?,
            "- 鑻ュ悗缁杩涘叆 SMARTboost 瀹炶瘉锛屽缓璁厛鏂板缓鐙珛澶嶇幇闂ㄦ锛欽ulia 鐜銆佷綔鑰?examples銆乸urged chronological validation銆佷笌鏈」鐩爣绛炬崯澶辩殑涓€鑷存€с€?,
            "",
            "## 鏄惁鐢熸垚 blocker",
            "",
            "鏈敓鎴?`SMARTBOOST_VERIFICATION_BLOCKER.md`锛屽洜涓哄師鏂囥€丏OI銆佺畻娉曞畾涔夊拰浠ｇ爜鏉ユ簮宸茬粡鍙牳楠屻€傛寮忓疄璇佸疄鐜颁粛闇€鍚庣画鍗曠嫭浠诲姟纭杩愯鐜涓庢崯澶卞嚱鏁板彛寰勩€?,
            "",
        ]
    )
    write_markdown(paths.REVIEWS_DIR / "model_audit" / "smartboost_verification.md", note)
    print("SMARTboost verification note completed")


def main() -> int:
    try:
        run()
        return 0
    except Exception as exc:
        print(f"smartboost verification failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
