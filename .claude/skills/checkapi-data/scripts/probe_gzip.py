"""REST 응답에 전송 압축이 먹는지, 그리고 한도가 압축 전/후 어느 쪽으로 세는지 잰다.

왜 재나
  nxt_krx_ingest.call() 은 Accept-Encoding 을 안 붙인다. urllib 은 requests 와 달리
  기본으로 넣어주지 않는다 -- 즉 지금까지 모든 REST 응답을 무압축 JSON 으로 받아왔다.
  틱 JSON 은 필드명이 매 줄 반복돼 압축이 극단적으로 잘 듣는다(다운로드 라우트에서
  216MB -> 12.8MB, 17배). 헤더 한 줄로 같은 이득이 난다면 nxt_tick 뿐 아니라
  tick_ob·nxt_min·krx_min 전 작업, 남은 백로그 52GB 전체의 비용이 바뀐다.

무엇이 갈리나
  (1) 서버가 gzip 을 주는가        -> Content-Encoding 헤더와 실제 수신 바이트로 즉시 판별
  (2) 한도를 압축 후로 세는가       -> 이건 헤더만으로는 모른다. 아래 --measure 참조

  다운로드 라우트에서 '전송 바이트로 센다'는 증거를 얻었지만 그건 서버가 zip 파일 자체를
  만들어 보낸 경우다(응답 본문이 곧 12.8MB). HTTP 전송 압축과는 다른 얘기라 그대로
  적용할 수 없다.

사용
  python probe_gzip.py                 # (1) 지원 여부. 같은 호출을 헤더 있이/없이 한 번씩
  python probe_gzip.py --measure N     # (2) 회계 기준. gzip 으로 N 콜 돌려 압축률을 쌓는다
                                       #     이후 하루 수집을 gzip 으로 돌려 한도가 언제
                                       #     차는지 보면 압축 전/후가 드러난다
"""
from __future__ import annotations

import argparse
import gzip
import io
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I

I.C._force_utf8_stdout()


def raw_call(apiurl, params, gz):
    """(수신바이트, 해제후바이트, Content-Encoding). call() 과 같은 방식으로 POST 한다."""
    env = I.C.load_env()
    body = urllib.parse.urlencode(
        {"cust_id": env["CHECK_CUST_ID"], "auth_key": env["CHECK_AUTH_KEY"], **params}).encode()
    headers = {"Accept-Encoding": "gzip, deflate"} if gz else {}
    req = urllib.request.Request(I.BASE + apiurl, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as r:
        wire = r.read()
        enc = (r.headers.get("Content-Encoding") or "").lower()
    plain = wire
    if "gzip" in enc:
        plain = gzip.GzipFile(fileobj=io.BytesIO(wire)).read()
    return len(wire), len(plain), enc or "(없음)"


def main():
    ap = argparse.ArgumentParser(description="REST 전송 압축 확인")
    ap.add_argument("--code", default="005930")
    ap.add_argument("--date", default=None, help="YYYYMMDD. 기본은 보관창 안 최근 거래일")
    ap.add_argument("--measure", type=int, metavar="N",
                    help="gzip 으로 N 콜 돌려 압축률 분포를 본다")
    args = ap.parse_args()

    conn = I.connect()
    with conn.cursor() as cur:
        if args.date:
            d8 = args.date
        else:
            cur.execute("""SELECT MAX(trade_date) FROM ingest_log
                           WHERE job='nxt_tick' AND status='ok'""")
            d8 = cur.fetchone()[0].strftime("%Y%m%d")
    conn.close()

    url = "/stock/m222/tick_date"
    params = {"jcode": args.code, "edate": d8, "data_list": ",".join(I.TICK_FIELDS)}
    print(f"대상 {url}  jcode={args.code} edate={d8}  필드 {len(I.TICK_FIELDS)}개\n")

    print("=== (1) 서버가 gzip 을 주는가 ===")
    for gz in (False, True):
        wire, plain, enc = raw_call(url, params, gz)
        tag = "Accept-Encoding 보냄" if gz else "안 보냄"
        print(f"  {tag:22} 수신 {wire:>12,}  해제후 {plain:>12,}  "
              f"Content-Encoding={enc}")
        if gz:
            if "gzip" in enc:
                print(f"  -> 압축 지원. {plain/max(1,wire):.1f}배")
                print("     남은 건 한도 회계 기준이다. 하루 수집을 gzip 으로 돌려")
                print("     한도가 '수신 합계' 로 차는지 '해제후 합계' 로 차는지 보면 된다.")
            else:
                print("  -> 압축 미지원. 이 경로로는 이득이 없다.")

    if args.measure:
        print(f"\n=== (2) 압축률 분포 ({args.measure}콜) ===")
        conn = I.connect()
        with conn.cursor() as cur:
            cur.execute("""SELECT code, trade_date FROM ingest_log
                           WHERE job='nxt_tick' AND status='ok' AND n_bytes > 0
                           ORDER BY RAND() LIMIT %s""", (args.measure,))
            rows = cur.fetchall()
        conn.close()
        tw = tp = 0
        for code, day in rows:
            w, p, _ = raw_call(url, {"jcode": code, "edate": day.strftime("%Y%m%d"),
                                     "data_list": ",".join(I.TICK_FIELDS)}, True)
            tw += w
            tp += p
            print(f"  {day} {code}  수신 {w:>10,}  해제후 {p:>11,}  {p/max(1,w):>5.1f}배")
        print(f"  합계 수신 {tw:,} / 해제후 {tp:,} = {tp/max(1,tw):.1f}배")


if __name__ == "__main__":
    main()
