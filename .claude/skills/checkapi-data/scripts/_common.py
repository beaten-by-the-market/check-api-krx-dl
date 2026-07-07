"""checkapi-data 스킬 스크립트 공용 모듈.

- 리포 루트(checkapi-specs.json 이 있는 곳)를 상위 경로에서 자동 탐색.
- 명세(checkapi-specs.json) 로드/캐시.
- .env 에서 CHECK 자격증명 로드.
표준 라이브러리만 사용한다 (requests/pandas 불필요).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _force_utf8_stdout() -> None:
    # Windows 콘솔에서 한글이 깨지지 않게 UTF-8 강제.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "checkapi-specs.json").exists():
            return parent
    raise FileNotFoundError(
        "checkapi-specs.json 을 상위 경로에서 찾지 못했습니다. "
        "이 스킬은 check-api-krx-dl 리포 안에서 실행해야 합니다."
    )


_SPECS = None


def load_specs() -> dict:
    global _SPECS
    if _SPECS is None:
        with open(find_repo_root() / "checkapi-specs.json", encoding="utf-8") as fh:
            _SPECS = json.load(fh)
    return _SPECS


def all_specs() -> list[dict]:
    return load_specs()["specs"]


def find_spec(apiurl: str) -> dict | None:
    for s in all_specs():
        if s["apiurl"] == apiurl:
            return s
    return None


def search_specs_by_substring(needle: str) -> list[dict]:
    n = needle.lower()
    return [s for s in all_specs() if n in s["apiurl"].lower()]


def normalize_apiurl(arg: str) -> str:
    """apiurl 인자를 실제 값으로 정규화한다.

    - 선행 슬래시 유무를 흡수한다.
    - Git Bash(MSYS)가 '/stock/...' 를 'C:/Program Files/Git/stock/...' 로
      바꿔버린 경우, 실제 apiurl로 끝나는 것을 되찾는다.
    """
    a = arg.replace("\\", "/")
    if find_spec(a):
        return a
    cand = "/" + a.lstrip("/")
    if find_spec(cand):
        return cand
    matches = [s["apiurl"] for s in all_specs() if a.endswith(s["apiurl"])]
    if matches:
        return max(matches, key=len)
    return cand


def domain_family(apiurl: str) -> tuple[str, str]:
    parts = apiurl.strip("/").split("/")
    dom = parts[0] if parts else ""
    fam = parts[1] if len(parts) > 1 else ""
    return dom, fam


# ── 시장명 ↔ 패밀리(domain/family) 매핑 (ground truth: specs menus[], 지수/KONEX/경계는 code_info 실측) ──
# endpoint 제목은 전부 일반명(기본정보/일별정보)이라, "국채30년 선물"·"가상자산"·"컨센서스" 같은
# 시장명으로는 검색이 안 잡힌다. 이 표로 search_endpoints가 시장명→패밀리를 해석한다.
# 상세 룩업/도메인경계 주석은 docs/checkapi/market-index.md (사람용 문서).
# ⚙ 이 dict가 단일 런타임 소스다. 여기에 항목을 추가하면 docs/checkapi/market-index.md에도
#   반드시 반영해야 한다 — 안 하면 check_market_index.py(pre-commit 훅)가 커밋을 막는다.
MARKET_NAMES: dict[str, str] = {
    # stock (KRX/NXT/통합)
    "stock/m001": "거래소 코스피 종목", "stock/m002": "거래소 코스피 업종 지수",
    "stock/m003": "코스닥 종목", "stock/m004": "코스닥 업종 지수",
    "stock/m222": "NXT 코스피 종목", "stock/m226": "NXT 코스피 업종",
    "stock/m223": "NXT 코스닥 종목", "stock/m227": "NXT 코스닥 업종",
    "stock/m224": "통합 코스피 종목", "stock/m228": "통합 코스피 업종 지수",
    "stock/m225": "통합 코스닥 종목", "stock/m229": "통합 코스닥 업종 지수",
    "stock/m008": "수익증권", "stock/m009": "신주인수권", "stock/m010": "OTCBB",
    "stock/m118": "KONEX 코넥스 종목", "stock/m121": "KONEX 코넥스 업종 지수",
    "stock/m167": "섹터지수 KRX100 KRX300 KTOP30 코리아밸류업 KRX섹터 테마지수",
    "stock/m168": "국내기타지수 코스피200 TR 레버리지 인버스 커버드콜 리츠 전략지수",
    # future (파생)
    "future/m005": "KOSPI200 선물", "future/m236": "KOSPI200 선물 야간",
    "future/m006": "KOSPI200 옵션", "future/m234": "KOSPI200 옵션 야간",
    "future/m103": "KOSPI200 미니선물", "future/m232": "KOSPI200 미니선물 야간",
    "future/m104": "KOSPI200 미니옵션", "future/m235": "KOSPI200 미니옵션 야간",
    "future/m182": "KOSPI200 위클리옵션", "future/m012": "주식옵션",
    "future/m017": "국채3년 선물", "future/m237": "국채3년 선물 야간",
    "future/m062": "국채5년 선물",
    "future/m016": "국채10년 선물", "future/m239": "국채10년 선물 야간",
    "future/m221": "국채30년 선물",
    "future/m013": "USD 달러 선물", "future/m238": "USD 달러 선물 야간",
    "future/m018": "YEN 엔 선물", "future/m019": "EURO 유로 선물", "future/m105": "CNH 위안 선물",
    "future/m067": "KOSDAQ150 선물", "future/m233": "KOSDAQ150 선물 야간",
    "future/m180": "KOSDAQ150 옵션", "future/m091": "주식선물",
    "future/m100": "섹터지수선물", "future/m181": "KRX300 선물",
    # bond (채권)
    "bond/m058": "채권발행정보", "bond/m161": "장내국채",
    "bond/m038": "통합채권 체결정보", "bond/m020": "장외 K-BOND",
    "bond/m050": "통합채권 호가", "bond/m060": "시가그룹",
    "bond/m097": "장외채권 최종호가수익률", "bond/m056": "콜",
    "bond/m043": "RP", "bond/m037": "RFR 무위험지표금리",
    "bond/m074": "발행기관별 시가평가", "bond/m023": "외국환중개 원달러 환율",
    "bond/m026": "외국환중개 외환스왑", "bond/m025": "해외금리",
    "bond/m048": "금리스왑", "bond/etc": "채권선물바스켓 CD CP",
    # ext (해외 라이센스 + 도메인경계)
    "ext/m184": "미국 지수", "ext/m194": "미국 종목", "ext/m185": "일본 지수", "ext/m195": "일본 종목",
    "ext/m186": "홍콩 지수", "ext/m196": "홍콩 종목", "ext/m187": "중국 지수", "ext/m197": "중국 종목",
    "ext/m188": "대만 지수", "ext/m198": "대만 종목", "ext/m193": "세계 지수",
    "ext/m174": "해외환율 위안달러",   # ⚠ 웹분류=채권-API
    "ext/m215": "가상자산 암호화폐 코인",  # ⚠ 웹분류=기타-API
    # news / etc
    "news/news": "뉴스", "news/gongsi": "공시",
    "etc/economic": "경제지표 달러지수 WTI", "etc/comp": "기업정보",
    "etc/ifrs": "IFRS 재무", "etc/gaap": "GAAP 재무", "etc/cons": "컨센서스 추정치",
    "etc/trend": "금융기관 수신고",
}


def market_name(apiurl: str) -> str:
    """apiurl → 시장명(있으면). 없으면 빈 문자열."""
    dom, fam = domain_family(apiurl)
    return MARKET_NAMES.get(f"{dom}/{fam}", "")


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    path = find_repo_root() / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("CHECK_CUST_ID", "CHECK_AUTH_KEY"):
        if not env.get(k) and os.environ.get(k):
            env[k] = os.environ[k]
    return env


def quote_codelist(codes) -> str:
    """복수종목(codelist) 파라미터용: 각 종목코드를 작은따옴표로 감싼 콤마열로 만든다.

    [CHECK API _port 버그 우회 — 실측 검증됨]
    codelist(_port) 경로는 종목코드를 숫자 리터럴로 취급해, '영숫자 6자리' 종목코드
    (신형 코드: 0001A0 덕양에너젠 등 스팩+최근상장 보통주 다수)가 하나라도 무따옴표로
    들어가면 배치 전체가 {"success":false,"message":"Error while performing Query."}로
    실패한다. 각 코드를 문자열 리터럴('...')로 감싸면 영숫자 코드도 정상 조회된다.
    숫자코드를 함께 감싸도 무해하며, basic_info_all_port·hist_info_port·hoga_info_port
    등 codelist를 쓰는 모든 *_port endpoint에서 동일하게 통한다(전부 실호출 확인).
    상세: 리포 루트 checkapi_bugreport_basic_info_all_port.txt.

    codes: 코드 리스트(list) 또는 콤마구분 문자열. 기존 따옴표는 벗겨 멱등 처리한다.
    """
    if isinstance(codes, str):
        parts = codes.split(",")
    else:
        parts = list(codes)
    out: list[str] = []
    for c in parts:
        c = str(c).strip().strip("'\"").strip()
        if c:
            out.append(f"'{c}'")
    return ",".join(out)


def fcode_decoder(spec: dict) -> dict[str, str]:
    """endpoint 의 res 정의로 F-code -> 한글 설명 매핑을 만든다."""
    out: dict[str, str] = {}
    for r in spec.get("res", []):
        name = (r.get("name") or "").strip()
        desc = (r.get("desc") or "").strip()
        if name:
            out[name] = desc or name
    return out
