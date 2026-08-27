"""NXT 투자자별 일별 매매를 nxt_invest 에 적재한다.

출처: /stock/m222|m223/rank_invest_date 를 하루씩(sdate=edate=D) 부른다.
한 콜이 그날 그 시장의 전 종목을 준다 -- 거래일당 2콜(KOSPI·KOSDAQ)이면 끝이다.

체결장과 성격이 다르다
  tick_date 는 101일이 지나면 영구 소실이라 만료와 경주해야 했다. 이건 소멸성이 아니다.
  2025-03-24(NXT 출범)까지 그대로 조회된다(실측: 2025-03-24 850종목 정상).
  그래서 급할 것이 없고, 한 번 받아두면 다시 받을 이유도 없다.

용량 (2026-08-07 실측)
  수량 3계열 43필드   KOSPI 594KB + KOSDAQ 1,272KB = 1.87MB/일
  수량+금액 57필드    약 2.5MB/일
  355거래일 전 기간을 금액까지 받아도 0.9GB -- 하루 한도 안이다.

slot 구조 (명세에 대응표가 없어 실측으로 확정. 2026-08-27)
  slot 12 = 합계(전체). 매수=매도이고 nxt_daily 그날 시장 거래량과 원 단위로 일치한다.
            투자자 유형이 아니다.
  slot 12 = 1+2+3+4+5+6+9+10+11+13   (성분 10개의 합)
  slot  8 = 1+2+3+4+5+6+13           (기관계)
  slot 14 = 별도 집계. 성분에 안 들어간다(외국인 관련 추정)
  slot  7 = 관측된 값 없음
  비중 추정: 10=개인(34.9%) 11=외국인(8.6%) 1=금융투자 9=기타법인 13=연기금

무엇을 저장하지 않나
  순매수(F06508/F06511)는 정의상 매수-매도라 파생 가능하다. 받으면 응답만 커진다.
  값이 전부 0인 (종목,슬롯)은 행을 만들지 않는다. 없으면 0으로 읽으면 된다.

사용
  python nxt_invest_load.py --plan                       # 남은 거래일만 계산
  python nxt_invest_load.py --sdate 20250324 --edate 20260825
  python nxt_invest_load.py --all                        # 거래일 달력 전체
  python nxt_invest_load.py --all --no-value             # 수량만(응답 26% 절감)
"""
from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I

I.C._force_utf8_stdout()

SLOTS = range(1, 15)
QTY = ([f"F06507_{i:02d}" for i in SLOTS]      # 매수거래량
       + [f"F06505_{i:02d}" for i in SLOTS])   # 매도거래량
VAL = ([f"F06510_{i:02d}" for i in SLOTS]      # 매수거래대금
       + [f"F06509_{i:02d}" for i in SLOTS])   # 매도거래대금

DDL = """
CREATE TABLE IF NOT EXISTS nxt_invest (
  trade_date DATE             NOT NULL,
  code       CHAR(6)          NOT NULL,
  slot       TINYINT UNSIGNED NOT NULL,
  buy_qty    BIGINT           NULL,
  sell_qty   BIGINT           NULL,
  buy_val    BIGINT           NULL,
  sell_val   BIGINT           NULL,
  PRIMARY KEY (trade_date, code, slot),
  KEY ix_code (code, trade_date)
) ENGINE=InnoDB
"""


def num(r, k):
    v = r.get(k)
    return int(v) if v not in (None, "") else 0


def fetch_day(conn, day, fam, with_value):
    """(적재행수, 수신바이트). day 는 date."""
    d8 = day.strftime("%Y%m%d")
    fields = ["F16013"] + QTY + (VAL if with_value else [])
    res, nb = I.call(f"/stock/{fam}/rank_invest_date", {
        "criteria_code": "F06508_08", "sort_code": "0",
        "sdate": d8, "edate": d8, "data_list": ",".join(fields)})

    recs = []
    for r in res:
        code = str(r.get("F16013") or "").strip()[:6]
        if len(code) != 6:
            continue
        for i in SLOTS:
            bq = num(r, f"F06507_{i:02d}")
            sq = num(r, f"F06505_{i:02d}")
            bv = num(r, f"F06510_{i:02d}") if with_value else None
            sv = num(r, f"F06509_{i:02d}") if with_value else None
            if not (bq or sq or bv or sv):
                continue          # 전부 0 이면 행을 만들지 않는다
            recs.append((day, code, i, bq, sq, bv, sv))

    # DELETE 하지 않고 ON DUPLICATE KEY UPDATE 로 덮는다. 과거 (일,종목,슬롯)이 사라지는
    # 일이 없으므로 지울 대상이 없고, 지우려면 시장 범위를 nxt_universe 로 좁혀야 하는데
    # rank_invest_date 는 유니버스보다 넓은 전 상장종목을 준다(833 vs 630) -- 안 맞는다.
    with conn.cursor() as cur:
        for i in range(0, len(recs), 5000):
            cur.executemany(
                "INSERT INTO nxt_invest (trade_date, code, slot, buy_qty, sell_qty, "
                "buy_val, sell_val) VALUES (%s,%s,%s,%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE buy_qty=VALUES(buy_qty), sell_qty=VALUES(sell_qty), "
                "buy_val=VALUES(buy_val), sell_val=VALUES(sell_val)", recs[i:i + 5000])
        I.log_done(cur, "nxt_inv", fam, day, "ok" if recs else "empty", len(recs), nb, None)
    conn.commit()
    return len(recs), nb


def main():
    ap = argparse.ArgumentParser(description="NXT 투자자별 일별 매매 적재")
    ap.add_argument("--sdate")
    ap.add_argument("--edate")
    ap.add_argument("--all", action="store_true", help="거래일 달력 전체")
    ap.add_argument("--plan", action="store_true", help="남은 거래일만 계산")
    ap.add_argument("--no-value", action="store_true", help="거래대금 없이 수량만")
    ap.add_argument("--budget", type=int, default=900_000_000)
    args = ap.parse_args()

    conn = I.connect()
    try:
        with conn.cursor() as cur:
            cur.execute(DDL)
            conn.commit()
            if args.all:
                cur.execute("SELECT trade_date FROM trading_day ORDER BY trade_date")
            elif args.sdate and args.edate:
                cur.execute("SELECT trade_date FROM trading_day "
                            "WHERE trade_date BETWEEN %s AND %s ORDER BY trade_date",
                            (args.sdate, args.edate))
            else:
                ap.error("--all 또는 --sdate+--edate 를 주세요")
            days = [d for (d,) in cur.fetchall()]
            cur.execute("SELECT trade_date, code FROM ingest_log "
                        "WHERE job='nxt_inv' AND status IN ('ok','empty')")
            done = {(d, c) for d, c in cur.fetchall()}

        todo = [(d, f) for d in days for f in ("m222", "m223") if (d, f) not in done]
        per = 1.25 if args.no_value else 1.7      # 콜당 평균 MB(실측 기반)
        print(f"거래일 {len(days):,}  ·  남은 콜 {len(todo):,}  ·  "
              f"예상 {len(todo)*per/1000:.2f}GB"
              + ("  [수량만]" if args.no_value else "  [수량+금액]"))
        if args.plan or not todo:
            return

        spent = rows = ok = 0
        t0 = time.time()
        for i, (day, fam) in enumerate(todo, 1):
            if spent >= args.budget:
                print(f"\n예산 소진 -- 중단. 남은 {len(todo)-i+1:,}콜은 다음 실행에서.")
                break
            try:
                n, nb = fetch_day(conn, day, fam, not args.no_value)
            except Exception as exc:
                print(f"  {day} {fam} 실패: {str(exc)[:90]}")
                continue
            spent += nb
            rows += n
            ok += 1
            if ok % 40 == 0:
                el = time.time() - t0
                print(f"  {ok:,}/{len(todo):,}콜  {rows:,}행  {spent/1e6:.0f}MB  "
                      f"{el:.0f}초", flush=True)
        print(f"\n적재 {ok:,}콜 · {rows:,}행 · {spent:,} bytes · {time.time()-t0:.0f}초")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
