"""넥스트레이드 공식 일별 거래량·거래대금을 nxt_daily 에 적재한다.

출처: nxt-data-api (nextrade.co.kr 거래현황). CHECK API 한도를 쓰지 않고 로그인도 필요 없다.

왜 필요한가
  체결 데이터에는 chg_type=69(실체결 아님) 가 섞여 있어 SUM(qty) 가 과대계상된다.
  이 표가 정답지 역할을 해서 (1) 소급 보강이 끝난 구간의 완전성을 검증하고,
  (2) chg_type 을 못 받는 구간(보관창 밖)의 총량 분석을 정확하게 해 준다.

세션이 둘로 나뉘는 것에 주의
  regular_market(정규시장) + closing_price(종가매매) = 그날 NXT 전체.
  둘을 더해야 우리 틱(69 제외)과 일치한다. 실측(2026-06-08, 3종목)에서 원 단위까지 맞았다:
    005380  공식 1,694,523주 / 1,079,911,321,000원  = 틱 69제외 (종가매매 0건)
    066570  정규 5,279,636 + 종가 315   = 틱 69제외 5,279,951
    454910  정규 6,276,652 + 종가  29   = 틱 69제외 6,276,681

사용
  python nxt_daily_load.py --sdate 20260403 --edate 20260813
  python nxt_daily_load.py --date 20260812          # 하루만
  python nxt_daily_load.py --verify 20260608        # 틱 합계와 대조
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I

I.C._force_utf8_stdout()

NXT_API = r"c:\Users\Peter\github\nxt-data-api"
if NXT_API not in sys.path:
    sys.path.insert(0, NXT_API)

MARKET = {"STK": "KOSPI", "KSQ": "KOSDAQ"}


def _rows(df, qty_col="accTdQty", val_col="accTrval"):
    """DataFrame -> {code: (market, name, qty, val)}"""
    out = {}
    for r in df.itertuples(index=False):
        code = str(getattr(r, "isuSrdCd", "") or "").lstrip("A")[:6]
        if len(code) != 6:
            continue
        out[code] = (
            MARKET.get(str(getattr(r, "mktId", "") or ""), None),
            getattr(r, "isuAbwdNm", None),
            int(getattr(r, qty_col, 0) or 0),
            int(getattr(r, val_col, 0) or 0),
        )
    return out


def load_day(conn, fetch, d8):
    reg = _rows(fetch("regular_market", date=d8))
    cls = _rows(fetch("closing_price", date=d8))
    if not reg and not cls:
        return 0
    day = f"{d8[:4]}-{d8[4:6]}-{d8[6:]}"
    recs = []
    for code in set(reg) | set(cls):
        m, nm, rq, rv = reg.get(code, (None, None, 0, 0))
        m2, nm2, cq, cv = cls.get(code, (None, None, 0, 0))
        recs.append((day, code, m or m2, nm or nm2, rq, rv, cq, cv, rq + cq, rv + cv))
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO nxt_daily (trade_date, code, market, name, reg_qty, reg_val, "
            "cls_qty, cls_val, qty, val) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE market=VALUES(market), name=VALUES(name), "
            "reg_qty=VALUES(reg_qty), reg_val=VALUES(reg_val), cls_qty=VALUES(cls_qty), "
            "cls_val=VALUES(cls_val), qty=VALUES(qty), val=VALUES(val)", recs)
    conn.commit()
    return len(recs)


def verify(conn, d8):
    """공식 거래량과 우리 틱 합계를 대조한다. chg_type 이 있는 종목만 의미가 있다."""
    day = f"{d8[:4]}-{d8[4:6]}-{d8[6:]}"
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.code, d.name, d.qty, d.val,
                   SUM(CASE WHEN t.chg_type <> 69 THEN t.qty END),
                   SUM(CASE WHEN t.chg_type <> 69 THEN t.price*t.qty END),
                   SUM(t.chg_type IS NULL)
            FROM nxt_daily d JOIN nxt_tick t
              ON t.trade_date = d.trade_date AND t.code = d.code
            WHERE d.trade_date = %s AND t.src IS NULL
            GROUP BY d.code, d.name, d.qty, d.val
            HAVING SUM(t.chg_type IS NULL) = 0        -- chg_type 이 전부 채워진 종목만
            ORDER BY d.qty DESC LIMIT 20""", (day,))
        rows = cur.fetchall()
    if not rows:
        print(f"[verify] {day}: chg_type 이 완비된 종목이 없습니다(소급 진행 중).")
        return
    ok = 0
    print(f"[verify] {day}  (chg_type 완비 종목 상위 {len(rows)}개)")
    print(f"  {'종목':7} {'종목명':12} {'거래량 차이':>12} {'거래대금 차이':>16}")
    for code, nm, oq, ov, tq, tv, _ in rows:
        dq, dv = int(tq or 0) - int(oq), int(tv or 0) - int(ov)
        ok += 1 if (dq == 0 and dv == 0) else 0
        mark = "" if (dq == 0 and dv == 0) else "  <-- 불일치"
        print(f"  {code:7} {(nm or ''):12} {dq:>+12,} {dv:>+16,}{mark}")
    print(f"  일치 {ok}/{len(rows)}")


def main():
    ap = argparse.ArgumentParser(description="NXT 공식 일별 거래량·거래대금 적재")
    ap.add_argument("--date", metavar="YYYYMMDD")
    ap.add_argument("--sdate", metavar="YYYYMMDD")
    ap.add_argument("--edate", metavar="YYYYMMDD")
    ap.add_argument("--recent", type=int, metavar="N",
                    help="최근 N 거래일. run_daily.bat 이 날짜 계산 없이 부르려고 있다")
    ap.add_argument("--verify", metavar="YYYYMMDD")
    args = ap.parse_args()

    conn = I.connect()
    try:
        if args.verify:
            verify(conn, args.verify)
            return
        from nxt_data_api import fetch                       # noqa: E402
        days = []
        if args.date:
            days = [args.date]
        elif args.recent:
            with conn.cursor() as cur:
                cur.execute("SELECT trade_date FROM trading_day WHERE trade_date <= CURDATE() "
                            "ORDER BY trade_date DESC LIMIT %s", (args.recent,))
                days = sorted(d.strftime("%Y%m%d") for (d,) in cur.fetchall())
        elif args.sdate and args.edate:
            with conn.cursor() as cur:                        # 거래일 달력에서만 뽑는다
                cur.execute("SELECT trade_date FROM trading_day WHERE trade_date BETWEEN %s AND %s "
                            "ORDER BY trade_date",
                            (f"{args.sdate[:4]}-{args.sdate[4:6]}-{args.sdate[6:]}",
                             f"{args.edate[:4]}-{args.edate[4:6]}-{args.edate[6:]}"))
                days = [d.strftime("%Y%m%d") for (d,) in cur.fetchall()]
        else:
            ap.error("--date / --recent / --sdate+--edate 중 하나를 주세요")
        if not days:
            print("대상 거래일이 없습니다."); return

        print(f"적재 대상 {len(days)}거래일: {days[0]} ~ {days[-1]}")
        tot = 0
        for i, d8 in enumerate(days, 1):
            try:
                n = load_day(conn, fetch, d8)
            except Exception as exc:                          # 하루 실패가 전체를 막지 않게
                print(f"  {d8}: 실패 {str(exc)[:60]}")
                continue
            tot += n
            if i % 10 == 0 or i == len(days):
                print(f"  {i}/{len(days)}  {d8}: {n}종목 (누적 {tot:,}행)", flush=True)
        print(f"\n적재 완료: {tot:,}행")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
