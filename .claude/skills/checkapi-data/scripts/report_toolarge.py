"""500MB 파일 한계로 받지 못한 (종목, 거래일) 목록을 뽑는다 — KOSCOM 별도 제공 요청용.

'File too large size(>= 500MB)' 는 KOSCOM 원본 파일 크기 제한이라 data_list 로 필드를
줄여도 우회되지 않는다(2026-08-07 확인). 거래가 활발한 날의 대형주는 이 API 로는
받을 방법이 없으므로, 목록을 남겨 별도 제공을 요청한다.

만료(expired)와 반드시 구분한다:
  expired  = 보관 101일이 지나 사라진 것. 우리가 늦어서 놓친 것.
  toolarge = 보관창 안인데 KOSCOM 측 제한으로 못 받는 것. 요청 대상.

사용
  python report_toolarge.py              # 화면 출력
  python report_toolarge.py --csv out.csv
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I

I.C._force_utf8_stdout()


def main():
    ap = argparse.ArgumentParser(description="500MB 초과로 못 받은 목록")
    ap.add_argument("--csv", metavar="PATH", help="CSV 로 저장")
    args = ap.parse_args()

    conn = I.connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.trade_date, l.code, u.name, u.market, l.done_at, l.msg
        FROM ingest_log l
        LEFT JOIN nxt_universe u ON u.code = l.code AND u.trade_date = l.trade_date
        WHERE l.status = 'toolarge'
        ORDER BY l.trade_date, l.code""")
    rows = cur.fetchall()

    if not rows:
        print("500MB 초과로 못 받은 건이 없습니다.")
        conn.close()
        return

    print(f"500MB 파일 한계로 받지 못한 건: {len(rows)}개\n")
    print(f"{'거래일':12} {'종목':8} {'종목명':16} {'시장':7} {'확인시각':19}")
    print("-" * 70)
    for d, code, name, market, at, msg in rows:
        print(f"{str(d):12} {code:8} {(name or ''):16} {(market or ''):7} {str(at)[:19]}")

    # 같은 종목이 반복되는지 = 구조적 문제인지 확인
    cur.execute("""SELECT code, COUNT(*) n, MIN(trade_date), MAX(trade_date)
                   FROM ingest_log WHERE status='toolarge' GROUP BY code ORDER BY n DESC""")
    rep = cur.fetchall()
    print(f"\n종목별 집계 ({len(rep)}종목):")
    for code, n, mn, mx in rep:
        print(f"  {code}: {n}건  ({mn} ~ {mx})")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["거래일", "종목코드", "종목명", "시장", "확인시각", "메시지"])
            for d, code, name, market, at, msg in rows:
                w.writerow([d, code, name or "", market or "", at, msg or ""])
        print(f"\nCSV 저장: {args.csv}")
    conn.close()


if __name__ == "__main__":
    main()