"""endpoint 하나에 대해 '바로 실행 가능한 파이썬 조회 스니펫'을 생성해 출력한다.

사용법:
    python gen_python.py /stock/m001/hist_info
    python gen_python.py /stock/m001/invest_hist > fetch_invest.py

- 해당 endpoint의 스펙(필수/선택 파라미터, 응답 F-code 정의)을 읽어
  POST 호출 + F-code→한글 컬럼 디코딩이 박힌 self-contained 코드를 찍는다.
- 손으로 스니펫을 쓰지 않으므로 endpoint마다 파라미터/디코딩이 어긋나지 않는다.
- 네트워크 호출 없음(코드 문자열만 생성).
"""

from __future__ import annotations

import argparse

from _common import domain_family, find_spec, normalize_apiurl, _force_utf8_stdout

# 파라미터명 -> 예시값 (스니펫 자리표시)
EXAMPLES = {
    "jcode": '"005930"',
    # _port 버그 우회: codelist는 각 코드를 작은따옴표로 감싸야 영숫자 종목코드(0001A0 등)가
    # 배치를 깨지 않는다. 따옴표 없이 넣으면 'Error while performing Query'로 전체 실패.
    "codelist": '''"'005930','000660'"''',
    "sdate": '"20250101"',
    "edate": '"20250131"',
    "term": '"daily"',
    "up_code": '"1"',
    "dcnt": '"100"',
    "criteria_code": '"F06508_11"',
    "data_list": '""',
}


def is_investor_endpoint(spec: dict) -> bool:
    return any((f.get("name") or "").startswith(("F0650", "F0651")) for f in spec.get("res", []))


def gen(spec: dict) -> str:
    apiurl = spec["apiurl"]
    title = spec.get("title", "")
    dom, _ = domain_family(apiurl)

    req = [p for p in spec.get("param", []) if p.get("req") == "O" and p["name"] not in ("cust_id", "auth_key")]
    opt = [p for p in spec.get("param", []) if p.get("req") != "O" and p["name"] not in ("cust_id", "auth_key")]

    # F-code -> 한글 컬럼명
    field_lines = []
    for f in spec.get("res", []):
        name, desc = (f.get("name") or "").strip(), (f.get("desc") or "").strip()
        if name:
            field_lines.append(f'    "{name}": "{desc or name}",')
    fields_block = "\n".join(field_lines) if field_lines else "    # (응답 필드 정의 없음)"

    req_lines = []
    for p in req:
        val = EXAMPLES.get(p["name"], '""  # TODO: 값 입력')
        req_lines.append(f'        "{p["name"]}": {val},  # {p.get("desc","")}')
    req_block = "\n".join(req_lines) if req_lines else "        # (cust_id/auth_key 외 필수 파라미터 없음)"

    opt_note = ""
    if opt:
        names = ", ".join(p["name"] for p in opt)
        opt_note = f'\n        # 선택 파라미터(필요 시 추가): {names}'

    investor_note = ""
    if is_investor_endpoint(spec):
        investor_note = (
            '\n# 투자자 구분은 번호(_01~_20)다. references/investor-codes.md 참조.\n'
            '# 외국인 순매수(거래량)=F06508_11, 기관=_08, 개인=_10, 전체=_12.'
        )

    return f'''"""CHECK API {apiurl} 조회 예시 — {title}
전제: 등록 IP 호스트에서 실행 / pip install requests pandas
환경변수: CHECK_CUST_ID, CHECK_AUTH_KEY (POST 요청 본문으로 전송)
"""
import os

import pandas as pd
import requests

BASE_URL = "https://checkapi.koscom.co.kr"
APIURL = "{apiurl}"  # 도메인: {dom}
{investor_note}
# 응답 각 행의 키는 F-code. 이 endpoint의 정의로 한글 컬럼명 매핑.
FIELD_NAMES = {{
{fields_block}
}}


def fetch() -> pd.DataFrame:
    payload = {{
        "cust_id": os.environ["CHECK_CUST_ID"],
        "auth_key": os.environ["CHECK_AUTH_KEY"],
{req_block}{opt_note}
    }}
    # 반드시 POST + 요청 본문. GET/쿼리스트링은 자격증명이 맞아도 인증 거부됨.
    resp = requests.post(f"{{BASE_URL}}{{APIURL}}", data=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if data.get("success") is False:
        # 값이 맞다면 '등록 IP가 아닐' 가능성(프록시/샌드박스).
        raise RuntimeError(data.get("message") or data.get("errmsg") or data)
    df = pd.DataFrame(data.get("results", []))
    return df.rename(columns=FIELD_NAMES)


if __name__ == "__main__":
    df = fetch()
    print(df.head(10).to_string())
'''


def main() -> None:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="endpoint별 파이썬 조회 스니펫 생성")
    ap.add_argument("apiurl")
    args = ap.parse_args()

    spec = find_spec(normalize_apiurl(args.apiurl))
    if not spec:
        raise SystemExit(f"'{args.apiurl}' endpoint를 찾지 못했습니다. get_endpoint_spec.py로 정확한 apiurl을 확인하세요.")
    print(gen(spec))


if __name__ == "__main__":
    main()
