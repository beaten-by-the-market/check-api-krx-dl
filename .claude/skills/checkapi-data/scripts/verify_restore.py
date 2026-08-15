"""복원기가 실제로 배정한 값을 zip 정답과 대조한다.

왜 필요한가
  지금까지의 --verify 는 tick_tt 로 정답을 받은 날에서 복원기를 '돌려본' 것이다. 정작
  복원기가 값을 쓴 (일,종목)은 정답이 없어 검증된 적이 없다. 모집단이 다르다.
  zip 라우트로 그 날들의 정답(F30614)을 받아올 수 있게 되면서 직접 대조가 가능해졌다.

함정 -- 적재하면 검증이 불가능해진다
  load_koscom_dump.py 로 zip 을 넣으면 chg_type 이 정답으로 덮어써져 복원값이 사라진다.
  그래서 반드시 '받기 -> 대조 -> 적재' 순서다. 이 스크립트는 DB 를 건드리지 않는다.

표본 설계 (--plan 이 그대로 보여준다)
  전수  배정된 69 의 최소 시각 < 15:00        창 하한 전제가 가장 아슬아슬한 케이스.
                                              거래가 오후 일찍 끊긴 종목(016800 등)
  전수  method='subset'                       희소하고 순수 추론
  층화  method='subsetdup'  거래량 5분위       중복행 사이 선택이 실제로 갈리는 곳.
                                              평균 거래량이 allside3 의 7배다
  층화  method='allside3'   거래량 5분위       다수지만 자기검증적 -- 후보 전체 합이 목표와
                                              일치해야 발동하므로 '창 밖 69'로는 못 속인다
  각 층 안에서 (거래일, 종목) 순으로 균등 간격 추출 -> 날짜가 한쪽에 몰리지 않는다.

판정 -- 기준을 solve() 의 묶음과 맞춰야 한다
  solve() 는 (qty, price*qty) 로 묶어 세고, 같은 묶음 안에서는 어느 행을 고르든 뺄 수량·금액이
  같다고 보고 method='subsetdup' 으로 표시한다. 즉 ts 가 다른 행을 고르는 것은 설계된 동작이다.
  대조 기준에 ts 를 넣으면 그걸 전부 오답으로 세게 된다(실제로 그렇게 세서 15건이 나왔다).

  완전일치  행 집합이 같다
  값동등    행은 다르지만 (ts,price,qty) 다중집합이 같다
  집계동등  (price,qty) 다중집합이 같다 -- 시각만 다르다. 수량·금액 집계는 완전히 동일하다
  세션이동  집계동등인데 15:30 경계를 넘나들어 세션별 집계가 달라진다  <- 유일하게 실질 영향
  불일치    수량·금액이 달라진다. 진짜 오답

사용
  python verify_restore.py --plan
  python verify_restore.py --fetch --budget 200000000
  python verify_restore.py --check
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I
import koscom_tick_download as D

I.C._force_utf8_stdout()

OUTDIR = os.path.join(os.path.expanduser("~"), "Downloads", "koscom_verify")
BYTES_PER_SHARE = 0.6      # zip 실측 회귀. 거래량 15주->847B, 22.8M주->12.8MB 로 거의 선형
EARLY = 15_000_000         # 이 시각 이전에 69 가 있으면 '이른 시각' 위험군


def strata(conn, n_dup, n_all):
    floor = dt.date.today() - dt.timedelta(days=I.TICK_RETENTION_DAYS)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT r.trade_date, r.code, r.method, d.qty, u.market
            FROM restore_log r
            JOIN nxt_daily d    ON d.trade_date=r.trade_date AND d.code=r.code
            JOIN nxt_universe u ON u.trade_date=r.trade_date AND u.code=r.code
            WHERE r.method IN ('allside3','subset','subsetdup') AND r.trade_date >= %s
            ORDER BY r.trade_date, r.code""", (floor,))
        pop = [(d, c, m, int(q), mk) for d, c, m, q, mk in cur.fetchall()]

        cur.execute("""
            SELECT t.trade_date, t.code, MIN(t.ts) FROM nxt_tick t
            JOIN restore_log r ON r.trade_date=t.trade_date AND r.code=t.code
            WHERE t.chg_type=69 AND t.trade_date >= %s
              AND r.method IN ('allside3','subset','subsetdup')
            GROUP BY t.trade_date, t.code HAVING MIN(t.ts) < %s""", (floor, EARLY))
        early = {(d, c) for d, c, _ in cur.fetchall()}

    picked, why = {}, {}

    def take(rows, k, label):
        if not rows or k <= 0:
            return
        step = max(1, len(rows) // k)
        for i in range(0, len(rows), step):
            r = rows[i]
            if len(([x for x in picked if why.get(x) == label])) >= k:
                break
            picked.setdefault((r[0], r[1]), r)
            why.setdefault((r[0], r[1]), label)

    for r in pop:                                    # 전수 1: 이른 시각
        if (r[0], r[1]) in early:
            picked[(r[0], r[1])] = r
            why[(r[0], r[1])] = "이른시각"
    for r in pop:                                    # 전수 2: subset
        if r[2] == "subset":
            picked.setdefault((r[0], r[1]), r)
            why.setdefault((r[0], r[1]), "subset")

    for method, k, lab in (("subsetdup", n_dup, "dup"), ("allside3", n_all, "all")):
        rows = [r for r in pop if r[2] == method and (r[0], r[1]) not in picked]
        rows.sort(key=lambda r: r[3])                # 거래량 오름차순 -> 5분위
        per = max(1, k // 5)
        for qi in range(5):
            lo, hi = len(rows) * qi // 5, len(rows) * (qi + 1) // 5
            seg = sorted(rows[lo:hi], key=lambda r: (r[0], r[1]))   # 날짜 분산
            step = max(1, len(seg) // per)
            for r in seg[::step][:per]:
                picked.setdefault((r[0], r[1]), r)
                why.setdefault((r[0], r[1]), f"{lab}Q{qi+1}")
    return [(*v, why[k]) for k, v in picked.items()], len(pop)


def zip_path(day, code, market, outdir):
    return os.path.join(outdir, f"{I.FAM_NXT[market]}_{day:%Y%m%d}_{code}.zip")


def truth_from_zip(path):
    """(69 행의 n 집합, {n: (ts,price,qty)}). 저장 규칙(ts 범위·qty>0)을 그대로 적용한다."""
    ns, val = set(), {}
    z = zipfile.ZipFile(path)
    with z.open(z.namelist()[0]) as f:
        for n, line in enumerate(f):
            r = json.loads(line)
            ts = int(r.get("F15019") or 0)
            qty = int(r.get("F15020") or 0)
            if ts <= 0 or ts > 23_59_59_99 or qty <= 0:
                continue
            if r.get("F30614") == "69":
                ns.add(n)
                val[n] = (ts, int(r.get("F15001") or 0), qty)
    return ns, val


def main():
    ap = argparse.ArgumentParser(description="복원 배정 vs zip 정답 대조")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dup", type=int, default=150)
    ap.add_argument("--all", type=int, default=150, dest="n_all")
    ap.add_argument("--budget", type=int, default=200_000_000)
    ap.add_argument("--outdir", default=OUTDIR)
    args = ap.parse_args()

    conn = I.connect()
    try:
        sample, npop = strata(conn, args.dup, args.n_all)
        sample.sort(key=lambda r: (r[0], r[1]))
        est = sum(r[3] for r in sample) * BYTES_PER_SHARE

        if args.plan or not (args.fetch or args.check):
            cnt = Counter(r[5] for r in sample)
            print(f"모집단 {npop:,}  ·  표본 {len(sample):,}  ·  예상 {est/1e6:.0f}MB")
            print("층별:", dict(sorted(cnt.items())))
            print(f"거래일 {len(set(r[0] for r in sample))}개 · "
                  f"거래량 {min(r[3] for r in sample):,} ~ {max(r[3] for r in sample):,}")
            print("\n이른시각 층(전수):")
            for r in sample:
                if r[5] == "이른시각":
                    print(f"  {r[0]} {r[1]} {r[2]:10} 거래량 {r[3]:>12,}")
            return

        os.makedirs(args.outdir, exist_ok=True)
        if args.fetch:
            env = I.C.load_env()
            spent = ok = 0
            for day, code, method, qty, market, lab in sample:
                p = zip_path(day, code, market, args.outdir)
                if os.path.exists(p) and os.path.getsize(p) > 500:
                    continue
                if spent >= args.budget:
                    print(f"\n예산 소진 -- 중단 ({ok}건 확보)")
                    break
                try:
                    body, _, _ = D.fetch(env, day, code, market, I.TICK_FIELDS)
                except Exception as exc:
                    print(f"{day} {code} 실패: {exc}")
                    continue
                spent += len(body)
                kind, detail = D.classify(body)
                if kind == "quota":
                    print(f"{day} {code} 한도 초과 -- 중단\n  {detail}")
                    break
                if kind == "error":
                    print(f"{day} {code} 오류: {detail[:120]}")
                    continue
                with open(p, "wb") as f:
                    f.write(body)
                ok += 1
                if ok % 25 == 0:
                    print(f"  {ok}건 · {spent/1e6:.0f}MB", flush=True)
                time.sleep(0.3)
            print(f"\n받음 {ok}건 / {spent:,} bytes -> {args.outdir}")

        if args.check:
            res = Counter()
            bad = []
            with conn.cursor() as cur:
                for day, code, method, qty, market, lab in sample:
                    p = zip_path(day, code, market, args.outdir)
                    if not os.path.exists(p):
                        res["파일없음"] += 1
                        continue
                    tn, tval = truth_from_zip(p)
                    cur.execute("""SELECT n, ts, price, qty FROM nxt_tick
                                   WHERE trade_date=%s AND code=%s AND chg_type=69""",
                                (day, code))
                    db = {int(n): (int(ts), int(pr), int(q)) for n, ts, pr, q in cur.fetchall()}
                    rn = set(db)
                    sess = lambda v: sorted((x[1], x[2], x[0] >= 15_300_000) for x in v)
                    agg = lambda v: sorted((x[1], x[2]) for x in v)
                    if rn == tn:
                        res[f"완전일치:{lab}"] += 1
                    elif sorted(db.values()) == sorted(tval.values()):
                        res[f"값동등:{lab}"] += 1
                    elif agg(db.values()) == agg(tval.values()):
                        if sess(db.values()) == sess(tval.values()):
                            res[f"집계동등:{lab}"] += 1
                        else:
                            res[f"세션이동:{lab}"] += 1
                            bad.append((day, code, method, lab, len(rn), len(tn), "세션이동"))
                    else:
                        res[f"불일치:{lab}"] += 1
                        bad.append((day, code, method, lab, len(rn), len(tn), "수량·금액 다름"))
            def s(pfx):
                return sum(v for k, v in res.items() if k.startswith(pfx))
            tot = sum(v for k, v in res.items() if not k.startswith("파일없음"))
            print(f"대조 {tot:,}건 (미수신 {res.get('파일없음', 0)}건 제외)")
            print(f"  완전일치 {s('완전일치'):,}  값동등 {s('값동등'):,}  집계동등 {s('집계동등'):,}"
                  f"  세션이동 {s('세션이동'):,}  불일치 {s('불일치'):,}")
            print(f"  -> 수량·금액 집계가 정답과 동일한 비율 "
                  f"{(tot - s('불일치'))/max(1,tot)*100:.2f}%")
            print("\n층별:")
            for k in sorted(res):
                if not k.startswith("파일없음"):
                    print(f"  {k:24} {res[k]:>5,}")
            if bad:
                print("\n집계 이외 차이 상세:")
                for d, c, m, lab, a, b, kind in bad[:20]:
                    print(f"  {d} {c} {m:10} {lab:10} 복원 {a}행 / 정답 {b}행  [{kind}]")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
