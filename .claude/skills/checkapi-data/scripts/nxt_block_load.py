"""NXT 대량·바스켓매매를 nxt_daily 의 blk_qty 에 적재한다. CHECK 한도를 쓰지 않는다.

출처: nxt-data-api block_trade (nextrade.co.kr 거래현황 > 대량·바스켓매매).

왜 필요한가 -- nxt_daily 가 '그날 NXT 전체'가 아니었다
  regular_market + closing_price 로만 채워 왔는데, 여기에 대량·바스켓이 빠져 있다.
  세 층으로 나뉜다(2026-08-29 확인):
      정규시장 + 종가매매        = nxt_daily.qty   <- 틱과 일치. 복원기의 정답지
        + 대량·바스켓            = blk_qty
      ────────────────────────────
      = 종목 총거래량            = 투자자 slot12 = block_trade.isuAccTdQty

  2026-02-06 실측:
      005930  18,788,510 + 85,350  = 18,873,860   투자자 slot12 와 원 단위 일치
      034020   4,784,224 + 128,915 =  4,913,139

  이 등식이 CHECK 투자자 데이터(nxt_invest)와 넥스트레이드 화면 두 곳을 교차검증한다.
  이전에는 투자자 합계가 nxt_daily 보다 큰 8거래일을 설명하지 못했는데, 그 차이가
  정확히 대량·바스켓이었다.

복원기에는 영향이 없다. 틱에도 대량이 없고(side 9/10/11/27 이 0행) nxt_daily.qty 에도
없어 두 축이 일관된다. blk_qty 는 따로 두고 qty 는 건드리지 않는다.

하루 0~수 건뿐이라 전 기간 355거래일이 금방 끝난다.

사용
  python nxt_block_load.py --all
  python nxt_block_load.py --sdate 20260201 --edate 20260228
  python nxt_block_load.py --verify        # 투자자 slot12 == qty + blk_qty 대조
"""
from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I

I.C._force_utf8_stdout()

NXT_API = r"c:\Users\Peter\github\nxt-data-api"
if NXT_API not in sys.path:
    sys.path.insert(0, NXT_API)

DDL = [
    "ALTER TABLE nxt_daily ADD COLUMN blk_qty BIGINT NULL",
    "ALTER TABLE nxt_daily ADD COLUMN blk_val BIGINT NULL",
]


def ensure_columns(conn):
    with conn.cursor() as cur:
        cur.execute("""SELECT column_name FROM information_schema.columns
                       WHERE table_schema=DATABASE() AND table_name='nxt_daily'""")
        have = {r[0].lower() for r in cur.fetchall()}
        for sql in DDL:
            col = sql.split("ADD COLUMN ")[1].split()[0]
            if col.lower() not in have:
                cur.execute(sql)
                print(f"  컬럼 추가: {col}")
    conn.commit()


def main():
    ap = argparse.ArgumentParser(description="NXT 대량·바스켓 -> nxt_daily.blk_qty")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--sdate")
    ap.add_argument("--edate")
    ap.add_argument("--verify", action="store_true",
                    help="투자자 slot12 == qty + blk_qty 를 전 구간 대조")
    args = ap.parse_args()

    conn = I.connect()
    try:
        ensure_columns(conn)

        if args.verify:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*), SUM(inv = base) FROM (
                      SELECT i.trade_date,
                             SUM(i.buy_qty) inv,
                             SUM(d.qty) + COALESCE(SUM(d.blk_qty),0) base
                      FROM nxt_invest i
                      JOIN nxt_daily d ON d.trade_date=i.trade_date
                      WHERE i.slot=12 AND i.code=d.code
                      GROUP BY i.trade_date) t""")
                tot, ok = cur.fetchone()
                print(f"투자자 slot12 == qty + blk_qty : {int(ok or 0):,}/{tot:,} 거래일")
            return

        from nxt_data_api import fetch

        with conn.cursor() as cur:
            if args.all:
                cur.execute("SELECT trade_date FROM trading_day ORDER BY trade_date")
            elif args.sdate and args.edate:
                cur.execute("SELECT trade_date FROM trading_day "
                            "WHERE trade_date BETWEEN %s AND %s ORDER BY trade_date",
                            (args.sdate, args.edate))
            else:
                ap.error("--all / --sdate+--edate / --verify 중 하나를 주세요")
            days = [d for (d,) in cur.fetchall()]

        print(f"거래일 {len(days):,}")
        t0 = time.time()
        n_day = n_row = 0
        for i, day in enumerate(days, 1):
            try:
                df = fetch("block_trade", date=day.strftime("%Y%m%d"))
            except Exception as exc:
                print(f"  {day} 실패: {str(exc)[:80]}")
                continue
            if df is None or len(df) == 0:
                continue
            recs = []
            for r in df.itertuples(index=False):
                code = str(getattr(r, "isuSrdCd", "") or "").lstrip("A")[:6]
                if len(code) != 6:
                    continue
                q = getattr(r, "bltdAccTdQty", None)
                if q in (None, ""):
                    continue
                recs.append((int(q), day, code))
            if not recs:
                continue
            with conn.cursor() as cur:
                cur.executemany("UPDATE nxt_daily SET blk_qty=%s "
                                "WHERE trade_date=%s AND code=%s", recs)
            conn.commit()
            n_day += 1
            n_row += len(recs)
            if i % 50 == 0:
                print(f"  {i:,}/{len(days):,}일  대량보유 {n_day}일 {n_row}건  "
                      f"{time.time()-t0:.0f}초", flush=True)
        print(f"\n대량거래가 있던 날 {n_day:,}일 · {n_row:,}건 · {time.time()-t0:.0f}초")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
