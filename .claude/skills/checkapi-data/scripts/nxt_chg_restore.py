"""chg_type(F30614) 을 API 없이 복원한다. CHECK 한도를 전혀 쓰지 않는다.

왜 필요한가
  체결장에는 chg_type=69(기세, 실체결 아님)가 섞여 SUM(qty) 가 과대계상된다.
  tick_date 보관창(100일)을 지난 날짜는 F30614 를 이제 받을 수 없다
  (2026-08-13 기준 2026-04-03~05-04 의 21거래일, 12,756 (일,종목)이 이미 그렇다).
  보관창 안이라도 소급에 쓸 한도가 없다 -- 같은 용량이면 틱 자체를 받는 게 낫다.

원리
  nxt_daily(넥스트레이드 공식 거래량·거래대금)가 정답지다. 69 를 뺀 값과 원 단위까지
  일치한다(2026-08-13 전수 검증 4,497/4,497). 그래서 어느 행인지 몰라도 총량은 안다:
      69 수량 = 틱 SUM(qty)       - nxt_daily.qty
      69 금액 = 틱 SUM(price*qty) - nxt_daily.val
  69 는 실측상 100% side=3 이고, side=3 중 69 아닌 행은 2.6% 뿐이다(종목당 평균 0.7행).
  그래서 '69 가 아닌 쪽'을 찾는 작은 부분합 문제가 된다. 수량·금액 두 제약이 동시에 걸린다.

무엇을 하지 않는가
  해가 유일할 때만 확정한다. 여러 개면 아무것도 쓰지 않고 '모름'으로 남긴다.
  틀린 값을 채우는 것이 비는 것보다 훨씬 나쁘다 -- 나중에 구분이 안 된다.
  검증(2026-08-13, 8거래일 4,066 표본): 유일해 87.31%, 오답 0건.

  1분봉은 쓰지 않는다. 봉 거래량도 69 를 제외한 값이지만, 애프터 세션 경계(15:40~)에서
  봉과 틱의 분 배정이 어긋난다(2026-06-08 에 103종목 123분). 이걸 참으로 가정했더니
  정답률이 86.62% 로 떨어지고 오답이 13.21% 생겼다. 제약을 늘려도 전제가 틀리면 손해다.

복원한 값의 표시
  chg_type 에 69 를 쓰고, src 는 건드리지 않는다. 대신 restore_log 에 (거래일, 종목)
  단위로 방법과 근거를 남겨, 복원분과 API 수신분을 언제든 구분할 수 있게 한다.

사용
  python nxt_chg_restore.py --plan                     # 복원 가능 범위만 계산
  python nxt_chg_restore.py --date 2026-04-03          # 하루
  python nxt_chg_restore.py --sdate 2026-04-03 --edate 2026-05-04
  python nxt_chg_restore.py --verify 2026-06-08        # 정답이 있는 날로 대조(쓰기 없음)
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I

I.C._force_utf8_stdout()

MAXK = 4          # 이 크기까지 부분집합을 찾는다. 종목당 실제 평균은 0.7행.
CAP = 2           # 해가 2개 이상인 걸 확인하면 바로 모호 판정 -- 전부 셀 필요가 없다

DDL = """
CREATE TABLE IF NOT EXISTS restore_log (
  trade_date DATE    NOT NULL,
  code       CHAR(6) NOT NULL,
  method     VARCHAR(16) NOT NULL,   -- allside3 / subset / qtyonly / ambiguous
  n_rows     INT     NULL,           -- 69 로 확정한 행 수
  qty69      BIGINT  NULL,           -- 그 (일,종목)의 69 거래량 (항상 정확)
  val69      BIGINT  NULL,
  done_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (trade_date, code)
) ENGINE=InnoDB
"""


def solve(rows, target_q, target_v, maxk=MAXK, cap=CAP):
    """합이 (target_q, target_v) 인 부분집합을 최소 크기부터 찾는다. 최대 cap 개까지.

    rows: [(n, qty, val), ...]   반환: [frozenset(n), ...]
    조합을 그대로 돌리면 후보가 858개까지 나와 폭발한다(C(858,4)=2.2e10).
    쌍합 사전으로 k=3,4 를 각각 O(n)/O(n^2) 조회에 푼다.
    """
    n = len(rows)
    sols = [frozenset([r[0]]) for r in rows if r[1] == target_q and r[2] == target_v]
    if sols or maxk < 2 or n < 2:
        return sols[:cap]

    pair = {}
    for i in range(n):
        ni, qi, vi = rows[i]
        for j in range(i + 1, n):
            nj, qj, vj = rows[j]
            b = pair.setdefault((qi + qj, vi + vj), [])
            if len(b) < 8:
                b.append((ni, nj))

    if (target_q, target_v) in pair:
        return [frozenset(p) for p in pair[(target_q, target_v)][:cap]]
    if maxk < 3:
        return []

    out = []
    for ni, qi, vi in rows:
        for p in pair.get((target_q - qi, target_v - vi), ()):
            if ni not in p:
                s = frozenset((ni,) + p)
                if s not in out:
                    out.append(s)
                    if len(out) >= cap:
                        return out
    if out or maxk < 4:
        return out

    for (q1, v1), ps1 in pair.items():
        for p2 in pair.get((target_q - q1, target_v - v1), ()):
            for p1 in ps1:
                if not set(p1) & set(p2):
                    s = frozenset(p1 + p2)
                    if s not in out:
                        out.append(s)
                        if len(out) >= cap:
                            return out
    return out


def restore_day(conn, day, write=True, check=False):
    """하루치를 복원한다. check=True 면 쓰지 않고 정답(chg_type)과 대조만 한다."""
    with conn.cursor() as cur:
        # (1) 종목별 69 총량. 틱이 완전한 (일,종목)만 대상이 된다.
        cur.execute("""
            SELECT t.code, SUM(t.qty)-d.qty, SUM(t.price*t.qty)-d.val
            FROM nxt_tick t JOIN nxt_daily d
              ON d.trade_date=t.trade_date AND d.code=t.code
            WHERE t.trade_date=%s
            GROUP BY t.code, d.qty, d.val""", (day,))
        target = {code: (int(q), int(v)) for code, q, v in cur.fetchall()}

        # (2) 후보군: side=3. 69 는 실측상 전부 여기 들어있다.
        cur.execute("""SELECT code, n, qty, price*qty, chg_type FROM nxt_tick
                       WHERE trade_date=%s AND side=3""", (day,))
        cand = {}
        for code, n, q, v, ct in cur.fetchall():
            cand.setdefault(code, []).append((n, int(q), int(v), ct))

    stat = {"allside3": 0, "subset": 0, "qtyonly": 0, "ambiguous": 0, "nodata": 0,
            "ok": 0, "bad": 0}
    updates, logs = [], []
    for code, (tq, tv) in target.items():
        rows = cand.get(code, [])
        if not check and rows and all(r[3] is not None for r in rows):
            # API 로 F30614 을 이미 받은 (일,종목)은 손대지 않는다. 추정이 실측을 덮으면 안 된다.
            continue
        if check and any(r[3] is None for r in rows):
            # 정답이 없는 종목을 대조에 넣으면 truth 가 빈 집합이 되어 전부 오답으로 보인다
            continue
        truth = frozenset(r[0] for r in rows if r[3] == 69) if check else None
        if tq == 0 and tv == 0:                       # 69 자체가 없는 날·종목
            method, picked = "allside3", frozenset()
        elif not rows:
            stat["nodata"] += 1
            logs.append((day, code, "qtyonly", None, tq, tv))
            continue
        else:
            sq = sum(r[1] for r in rows); sv = sum(r[2] for r in rows)
            if (sq, sv) == (tq, tv):                  # side=3 전부가 69
                method, picked = "allside3", frozenset(r[0] for r in rows)
            elif tq > sq or tq < 0:                   # 전제 위반 -> 손대지 않는다
                method, picked = "qtyonly", None
            else:
                sols = solve([(r[0], r[1], r[2]) for r in rows], sq - tq, sv - tv)
                if len(sols) == 1:
                    method = "subset"
                    picked = frozenset(r[0] for r in rows) - sols[0]
                else:
                    method = "ambiguous" if sols else "qtyonly"
                    picked = None

        if check and picked is not None:
            stat["ok" if picked == truth else "bad"] += 1
        stat[method] = stat.get(method, 0) + 1
        logs.append((day, code, method, len(picked) if picked is not None else None, tq, tv))
        if picked and write and not check:
            updates.extend((day, code, n) for n in picked)

    if write and not check:
        with conn.cursor() as cur:
            for i in range(0, len(updates), 5000):
                chunk = updates[i:i + 5000]
                cur.executemany("UPDATE nxt_tick SET chg_type=69 "
                                "WHERE trade_date=%s AND code=%s AND n=%s", chunk)
            cur.executemany(
                "INSERT INTO restore_log (trade_date, code, method, n_rows, qty69, val69) "
                "VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE method=VALUES(method), "
                "n_rows=VALUES(n_rows), qty69=VALUES(qty69), val69=VALUES(val69), "
                "done_at=CURRENT_TIMESTAMP", logs)
        conn.commit()
    return stat, len(updates)


def main():
    ap = argparse.ArgumentParser(description="chg_type(F30614) 무한도 복원")
    ap.add_argument("--date")
    ap.add_argument("--sdate")
    ap.add_argument("--edate")
    ap.add_argument("--verify", metavar="YYYY-MM-DD",
                    help="정답이 있는 날로 대조만 한다(DB 를 바꾸지 않음)")
    ap.add_argument("--plan", action="store_true")
    args = ap.parse_args()

    conn = I.connect()
    try:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()

        if args.plan:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT t.trade_date, COUNT(*) 종목,
                           SUM(t.has_daily) 기준선있음, SUM(t.done) 복원완료
                    FROM (SELECT n.trade_date, n.code,
                                 MAX(d.code IS NOT NULL) has_daily,
                                 MAX(r.code IS NOT NULL) done
                          FROM (SELECT DISTINCT trade_date, code FROM nxt_tick) n
                          LEFT JOIN nxt_daily  d ON d.trade_date=n.trade_date AND d.code=n.code
                          LEFT JOIN restore_log r ON r.trade_date=n.trade_date AND r.code=n.code
                          GROUP BY n.trade_date, n.code) t
                    GROUP BY t.trade_date ORDER BY t.trade_date""")
                print(f"{'거래일':11} {'종목':>6} {'기준선':>7} {'복원완료':>8}")
                for d, n, hd, dn in cur.fetchall():
                    print(f"{str(d):11} {n:>6,} {int(hd):>7,} {int(dn):>8,}")
            return

        if args.verify:
            stat, _ = restore_day(conn, args.verify, write=False, check=True)
            n = stat["ok"] + stat["bad"]
            print(f"[verify] {args.verify}  확정 {n:,}  정답 {stat['ok']:,}  오답 {stat['bad']:,}")
            print(f"  방법별: 전부69 {stat['allside3']:,}  부분합 {stat['subset']:,}  "
                  f"모호 {stat['ambiguous']:,}  수량만 {stat['qtyonly']:,}")
            if stat["bad"]:
                print("  오답이 있습니다 -- 복원을 진행하지 마세요.")
            return

        with conn.cursor() as cur:
            if args.date:
                days = [args.date]
            elif args.sdate and args.edate:
                cur.execute("SELECT DISTINCT trade_date FROM nxt_tick "
                            "WHERE trade_date BETWEEN %s AND %s ORDER BY trade_date",
                            (args.sdate, args.edate))
                days = [str(d) for (d,) in cur.fetchall()]
            else:
                ap.error("--date / --sdate+--edate / --plan / --verify 중 하나를 주세요")

        tot = {"allside3": 0, "subset": 0, "ambiguous": 0, "qtyonly": 0, "nodata": 0}
        n_upd = 0
        for day in days:
            stat, k = restore_day(conn, day)
            n_upd += k
            for key in tot:
                tot[key] += stat.get(key, 0)
            print(f"{day}  전부69 {stat.get('allside3',0):>4}  부분합 {stat.get('subset',0):>4}  "
                  f"모호 {stat.get('ambiguous',0):>4}  수량만 {stat.get('qtyonly',0):>4}  "
                  f"({k:,}행 표시)", flush=True)
        done = tot["allside3"] + tot["subset"]
        n = sum(tot.values())
        print(f"\n=== {len(days)}거래일 {n:,}개 (일,종목) ===")
        print(f"  행 단위 확정 : {done:,} ({done/n*100:.2f}%)  -> nxt_tick 69행 {n_upd:,}건 표시")
        print(f"  수량만 확정  : {n-done:,} ({(n-done)/n*100:.2f}%)  "
              f"-> restore_log 에 qty69/val69 만 기록(행은 미상)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
