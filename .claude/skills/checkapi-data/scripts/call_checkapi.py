"""CHECK API endpoint를 실제 호출하고 F-code를 한글 컬럼으로 디코딩해 출력한다.

사용법:
    python call_checkapi.py /stock/m001/hist_info jcode=005930 sdate=20250602 edate=20250605
    python call_checkapi.py /stock/m001/hist_info jcode=005930 sdate=20250602 edate=20250605 --csv out.csv
    python call_checkapi.py /stock/m001/hist_info jcode=005930 ... --raw     # F-code 원본 키 유지

중요:
- POST(요청 본문)로만 호출된다. cust_id/auth_key는 .env에서 자동 주입.
- CHECK API는 등록 IP에서의 호출만 허용한다. 자격증명이 맞아도 등록 외 IP(프록시/샌드박스)면
  'cust_id 또는 auth_key가 정확하지 않습니다'로 거부된다. => 반드시 등록 IP 호스트에서,
  (에이전트가 실행 시) 샌드박스 밖에서 실행할 것.
- 응답 results의 키는 F-code이며, 해당 endpoint의 res 정의로 한글 컬럼명으로 바꿔 출력한다.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

from _common import fcode_decoder, find_spec, load_env, normalize_apiurl, quote_codelist, _force_utf8_stdout

BASE_URL = "https://checkapi.koscom.co.kr"


def parse_kv(pairs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            raise SystemExit(f"파라미터는 key=value 형식이어야 합니다: {p!r}")
        k, v = p.split("=", 1)
        out[k.strip()] = v
    return out


def as_table(rows: list[dict], limit: int) -> str:
    if not rows:
        return "(빈 결과)"
    cols = list(rows[0].keys())
    shown = rows[:limit]
    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in shown)) for c in cols}
    line = " | ".join(str(c).ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    body = [" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols) for r in shown]
    tail = "" if len(rows) <= limit else f"\n... 총 {len(rows)}행 중 {limit}행 표시 (--limit 로 조정)"
    return "\n".join([line, sep, *body]) + tail


def main() -> None:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="CHECK API 실제 호출")
    ap.add_argument("apiurl")
    ap.add_argument("params", nargs="*", help="key=value 파라미터 (jcode=005930 등)")
    ap.add_argument("--raw", action="store_true", help="F-code 키를 한글로 바꾸지 않음")
    ap.add_argument("--limit", type=int, default=20, help="표로 보여줄 행 수")
    ap.add_argument("--csv", help="전체 결과를 CSV로 저장할 경로")
    ap.add_argument("--json", action="store_true", help="원본 JSON 그대로 출력")
    args = ap.parse_args()

    args.apiurl = normalize_apiurl(args.apiurl)
    env = load_env()
    cust_id, auth_key = env.get("CHECK_CUST_ID"), env.get("CHECK_AUTH_KEY")
    if not cust_id or not auth_key:
        raise SystemExit("CHECK_CUST_ID / CHECK_AUTH_KEY 를 .env 또는 환경변수에서 찾지 못했습니다.")

    params = parse_kv(args.params)
    # _port 버그 우회: codelist는 각 코드를 작은따옴표로 감싸야 영숫자 종목코드가 실패하지 않는다.
    if params.get("codelist"):
        params["codelist"] = quote_codelist(params["codelist"])
    payload = {"cust_id": cust_id, "auth_key": auth_key, **params}
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(f"{BASE_URL}{args.apiurl}", data=data)  # POST
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read()
        print(f"[HTTP {e.code}] {body[:300]!r}")
        sys.exit(1)

    d = json.loads(body.decode("utf-8"))
    if d.get("success") is False:
        msg = d.get("message") or d.get("errmsg") or d
        print(f"[실패] {msg}")
        print("힌트: 값이 맞다면 '등록 IP가 아닐' 가능성. 등록 IP 호스트에서(샌드박스 밖) 실행하세요.")
        sys.exit(1)

    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return

    results = d.get("results", d)
    if not isinstance(results, list):
        results = [results]

    spec = find_spec(args.apiurl)
    decoder = fcode_decoder(spec) if (spec and not args.raw) else {}

    def rename(row: dict) -> dict:
        if not decoder:
            return row
        out = {}
        for k, v in row.items():
            out[decoder.get(k, k)] = v
        return out

    decoded = [rename(r) for r in results]

    print(f"{args.apiurl}  |  {len(decoded)}행")
    print(as_table(decoded, args.limit))

    if args.csv:
        import csv
        with open(args.csv, "w", encoding="utf-8-sig", newline="") as fh:
            if decoded:
                w = csv.DictWriter(fh, fieldnames=list(decoded[0].keys()))
                w.writeheader()
                w.writerows(decoded)
        print(f"\nCSV 저장: {args.csv} ({len(decoded)}행)")


if __name__ == "__main__":
    main()
