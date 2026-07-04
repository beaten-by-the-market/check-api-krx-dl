"""code_info/checkcode 카탈로그를 로컬 캐시로 1회 덤프 (search_codes.py 용).

왜 필요한가:
- `search_endpoints.py`/`search_fields.py`는 정적 명세(checkapi-specs.json)만 본다.
- 그런데 지수·지표물·FX·해외금리·경제지표(30,316개) 등 상당수 능력은 **명세에 없고
  code_info/checkcode의 '코드'로만** 존재한다 → 정적 검색으로는 통째로 안 보인다
  (실전에서 지수·원달러·해외금리·WTI를 이 때문에 "없음"으로 오판).
- 이 스크립트가 그 코드 카탈로그를 캐시로 떠서, `search_codes.py`가 오프라인 검색하게 한다.

실행: **등록 IP·샌드박스 밖**에서 1회. 코드목록은 자주 안 변하므로 가끔만 갱신하면 된다.
    python cache_codes.py
결과: ../cache/code_catalog.json (search_codes.py가 읽음)
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from _common import load_env, _force_utf8_stdout

BASE_URL = "https://checkapi.koscom.co.kr"
CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

# (라벨, apiurl, 코드필드, 이름필드, 호출법)
CATALOGS = [
    ("지수/업종(코스피)", "/stock/m002/code_info", "F16013", "F16002", "stock/m002/hist_info jcode=<코드> (지수값 F15001)"),
    ("지수/업종(코스닥)", "/stock/m004/code_info", "F16013", "F16002", "stock/m004/hist_info jcode=<코드>"),
    ("지수(KRX 통합: KRX100/300)", "/stock/m167/code_info", "F16013", "F16002", "stock/m167/hist_info jcode=<코드>"),
    ("지수(코넥스)", "/stock/m121/code_info", "F16013", "F16002", "stock/m121/hist_info jcode=<코드>"),
    ("외국환중개(원달러/FX)", "/bond/m023/code_info", "F16013", "F16002", "bond/m023/basic_info jcode=<코드> (F15001 현재가·F15183 매매기준율)"),
    ("해외금리(각국 국채)", "/bond/m025/code_info", "F16013", "F16002", "bond/m025/hist_info jcode=<코드> (F32450 중간호가)"),
    ("외환스왑", "/bond/m026/code_info", "F16013", "F16002", "bond/m026/basic_info jcode=<코드>"),
    ("선물(KOSPI200)", "/future/m005/code_info", "F16013", "F16002", "future/m005/hist_info jcode=<코드> (최근월물 F16169='Y')"),
    ("선물(KOSDAQ150)", "/future/m067/code_info", "F16013", "F16002", "future/m067/hist_info jcode=<코드>"),
    ("선물(KRX300)", "/future/m181/code_info", "F16013", "F16002", "future/m181/hist_info jcode=<코드>"),
    ("경제지표(글로벌 매크로 30k)", "/etc/economic/checkcode", "CHECK_CODE", "INDCTR_NAME", "etc/economic/indicator check_code=<코드> (DATA_VALUE/TIME)"),
    ("종목(코스피)", "/stock/m001/code_info", "F16013", "F16002", "stock/m001/hist_info jcode=<코드>"),
    ("종목(코스닥)", "/stock/m003/code_info", "F16013", "F16002", "stock/m003/hist_info jcode=<코드>"),
]


def post_raw(apiurl: str) -> list[dict]:
    env = load_env()
    payload = {"cust_id": env.get("CHECK_CUST_ID", ""), "auth_key": env.get("CHECK_AUTH_KEY", "")}
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(f"{BASE_URL}{apiurl}", data=data)
    with urllib.request.urlopen(req, timeout=90) as resp:
        d = json.loads(resp.read().decode("utf-8"))
    if d.get("success") is False:
        raise RuntimeError(d.get("message") or d.get("errmsg"))
    return d.get("results", []) or []


def main() -> None:
    _force_utf8_stdout()
    CACHE_DIR.mkdir(exist_ok=True)
    entries: list[dict] = []
    for label, apiurl, cf, nf, howto in CATALOGS:
        try:
            rows = post_raw(apiurl)
        except Exception as e:  # noqa: BLE001
            print(f"  [건너뜀] {label} ({apiurl}): {e}", file=sys.stderr)
            continue
        n = 0
        for r in rows:
            code = str(r.get(cf) or "").strip()
            if not code:
                continue
            entries.append({"catalog": label, "code": code,
                            "name": str(r.get(nf) or "").strip(), "howto": howto})
            n += 1
        print(f"  {label}: {n} 코드", flush=True)
    out = CACHE_DIR / "code_catalog.json"
    out.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    print(f"\n총 {len(entries):,} 코드 → {out}")


if __name__ == "__main__":
    main()
