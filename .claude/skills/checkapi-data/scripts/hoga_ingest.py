# -*- coding: utf-8 -*-
"""hoga_ingest — CHECK API 실시간 호가(10단계)를 폴링해 PostgreSQL/TimescaleDB에 적재.

KRX·NXT·통합(KRX+NXT) 세 거래소의 호가를 종목 워치리스트 단위로 주기 폴링해
`hoga_book` 하이퍼테이블에 넣는다. 스키마는 hoga_schema.sql 참조.

■ 거래소 패밀리 (실측)
    KRX      코스피 m001 · 코스닥 m003
    NXT      코스피 m222 · 코스닥 m223
    통합     코스피 m224 · 코스닥 m225
  호가 endpoint: /stock/{fam}/hoga_info_port (codelist, 복수종목 1콜) — 46필드 10단계.
  ⚠ NXT/통합은 spec 메뉴에 state=off·"NXT 활성화되면 반영" 표기 → live 반환은 장중 실측 필요.

■ 핵심 성질
  - CHECK API는 REST POST 스냅샷(스트리밍/웹소켓 없음) → "실시간"=주기 폴링.
  - 등록 IP·샌드박스 밖에서만 실데이터. 장중(09:00~15:30, 평일)에만 의미.
  - hoga_info에는 거래소 타임스탬프가 없어 수집시각(ts)을 서버에서 찍는다.

■ 사용
  # 1) DB 준비:  psql -d marketdata -f hoga_schema.sql
  # 2) .env 에 CHECK 자격증명 + DB 접속:
  #      CHECK_CUST_ID=..., CHECK_AUTH_KEY=...
  #      PG_DSN=postgresql://user:pw@localhost:5432/marketdata
  # 3) 워치리스트(watchlist.json) 예:
  #      {"kospi": ["005930","000660"], "kosdaq": ["247540","086520"]}
  python hoga_ingest.py --watchlist watchlist.json --venues krx,nxt,unified --interval 1.0
  python hoga_ingest.py --watchlist watchlist.json --once --dry-run   # 적재 없이 파싱/SQL 확인
  python hoga_ingest.py --selftest                                    # 네트워크·DB 없이 파서 검증

  ※ 일요일/휴장 등 실데이터가 없을 때는 --dry-run/--selftest로 배선만 검증하고,
     실적재는 장중에 --venues로 돌린다.
"""
from __future__ import annotations
import sys, os, json, time, argparse, datetime as dt

# 거래소×시장 → 패밀리
VENUE_FAM = {
    "krx":     {"kospi": "m001", "kosdaq": "m003"},
    "nxt":     {"kospi": "m222", "kosdaq": "m223"},
    "unified": {"kospi": "m224", "kosdaq": "m225"},
}
LEVELS = 10

# 46필드 F-code 매핑 (10단계)
def _fkeys():
    ask_px  = [f"F145{i:02d}" for i in range(1, 11)]      # F14501..F14510 매도호가
    ask_qty = [f"F145{i:02d}" for i in range(11, 21)]     # F14511..F14520 매도잔량
    bid_px  = [f"F145{i:02d}" for i in range(31, 41)]     # F14531..F14540 매수호가
    bid_qty = [f"F145{i:02d}" for i in range(41, 51)]     # F14541..F14550 매수잔량
    return ask_px, ask_qty, bid_px, bid_qty
ASK_PX, ASK_QTY, BID_PX, BID_QTY = _fkeys()
F_ISIN, F_CODE = "F16012", "F16013"
F_ASK_TOT, F_BID_TOT, F_ASK_TOT_D, F_BID_TOT_D = "F14565", "F14567", "F14566", "F14568"

def _to_i(x):
    try: return int(float(x))
    except Exception: return 0

def parse_row(rec, venue, market, ts):
    """CHECK 응답 1건(F-code dict) → hoga_book 행 dict."""
    return dict(
        ts=ts, venue=venue, market=market,
        code=str(rec.get(F_CODE, "")).strip(), isin=str(rec.get(F_ISIN, "")).strip() or None,
        ask_px=[_to_i(rec.get(k)) for k in ASK_PX], ask_qty=[_to_i(rec.get(k)) for k in ASK_QTY],
        bid_px=[_to_i(rec.get(k)) for k in BID_PX], bid_qty=[_to_i(rec.get(k)) for k in BID_QTY],
        ask_tot=_to_i(rec.get(F_ASK_TOT)), bid_tot=_to_i(rec.get(F_BID_TOT)),
        ask_tot_d=_to_i(rec.get(F_ASK_TOT_D)), bid_tot_d=_to_i(rec.get(F_BID_TOT_D)),
    )

# ---------------- CHECK API 호출 ----------------
def _get_caller():
    """news_gongsi_lab.call 재사용(POST+.env 자동). 없으면 최소 구현."""
    try:
        from news_gongsi_lab import call
        return call
    except Exception:
        import urllib.parse, urllib.request
        from _common import load_env
        env = load_env(); cid, ak = env.get("CHECK_CUST_ID"), env.get("CHECK_AUTH_KEY")
        BASE = "https://checkapi.koscom.co.kr"
        def call(apiurl, **params):
            data = urllib.parse.urlencode({"cust_id": cid, "auth_key": ak, **params}).encode()
            with urllib.request.urlopen(urllib.request.Request(BASE + apiurl, data=data), timeout=30) as r:
                d = json.loads(r.read().decode("utf-8"))
            res = d.get("results", d) if isinstance(d, dict) else d
            return res if isinstance(res, list) else [res]
        return call

def fetch_venue_market(call, venue, market, codes):
    """한 (거래소,시장)의 호가를 복수종목 1콜로. codelist는 각 코드를 작은따옴표로 감싼
    형식('005930','000660')이어야 _port 버그(영숫자 코드 배치 실패)를 피한다."""
    from _common import quote_codelist
    fam = VENUE_FAM[venue][market]
    return call(f"/stock/{fam}/hoga_info_port", codelist=quote_codelist(codes))

# ---------------- DB 적재 ----------------
INSERT_SQL = """
INSERT INTO hoga_book (ts,venue,market,code,isin,ask_px,ask_qty,bid_px,bid_qty,
                       ask_tot,bid_tot,ask_tot_d,bid_tot_d)
VALUES (%(ts)s,%(venue)s,%(market)s,%(code)s,%(isin)s,%(ask_px)s,%(ask_qty)s,%(bid_px)s,%(bid_qty)s,
        %(ask_tot)s,%(bid_tot)s,%(ask_tot_d)s,%(bid_tot_d)s)
ON CONFLICT (venue,code,ts) DO NOTHING
"""

class DB:
    def __init__(self, dsn):
        import psycopg2, psycopg2.extras  # psycopg2 또는 psycopg 사용
        self.conn = psycopg2.connect(dsn); self.conn.autocommit = False
        self.extras = psycopg2.extras
    def insert(self, rows):
        with self.conn.cursor() as cur:
            self.extras.execute_batch(cur, INSERT_SQL, rows, page_size=500)
        self.conn.commit()
    def close(self):
        try: self.conn.close()
        except Exception: pass

# ---------------- 장중 여부 ----------------
def in_session(now=None):
    now = now or dt.datetime.now()
    if now.weekday() >= 5: return False                 # 주말
    hm = now.hour * 100 + now.minute
    return 900 <= hm <= 1530                              # 정규장(대략)

# ---------------- 폴링 루프 ----------------
def poll_once(call, venues, watchlist, ts=None, db=None, dry=False, log=print):
    ts = ts or dt.datetime.now()
    total = 0
    for venue in venues:
        for market, codes in watchlist.items():
            if not codes: continue
            try:
                recs = fetch_venue_market(call, venue, market, codes)
            except Exception as ex:
                log(f"  [{venue}/{market}] 조회 실패: {ex}"); continue
            rows = [parse_row(r, venue, market, ts) for r in recs if str(r.get(F_CODE, "")).strip()]
            total += len(rows)
            if dry:
                for r in rows[:2]:
                    log(f"  [{venue}/{market}] {r['code']} bid1={r['bid_px'][0]}({r['bid_qty'][0]}) "
                        f"ask1={r['ask_px'][0]}({r['ask_qty'][0]}) sum(b/a)={r['bid_tot']}/{r['ask_tot']}")
                log(f"  [{venue}/{market}] {len(rows)}건 (dry-run, 미적재)")
            elif db and rows:
                db.insert(rows)
    return total

def run(args):
    watchlist = json.load(open(args.watchlist, encoding="utf-8")) if args.watchlist else \
                {"kospi": ["005930", "000660"], "kosdaq": ["247540"]}
    venues = [v.strip() for v in args.venues.split(",") if v.strip()]
    for v in venues:
        if v not in VENUE_FAM: sys.exit(f"알 수 없는 거래소: {v} (krx/nxt/unified)")
    call = _get_caller()
    db = None
    if not args.dry_run:
        dsn = os.environ.get("PG_DSN") or args.dsn
        if not dsn: sys.exit("PG_DSN(.env 또는 --dsn) 필요. 적재 없이 볼 땐 --dry-run.")
        db = DB(dsn)
    print(f"[hoga_ingest] venues={venues} interval={args.interval}s "
          f"{'DRY-RUN' if args.dry_run else 'DB적재'} 워치리스트 "
          f"코스피{len(watchlist.get('kospi',[]))}·코스닥{len(watchlist.get('kosdaq',[]))}")
    try:
        while True:
            t0 = time.time()
            if not args.ignore_session and not in_session():
                print(f"  {dt.datetime.now():%H:%M} 장 시간 아님 — 대기(--ignore-session으로 무시)")
                if args.once: break
                time.sleep(min(60, args.interval * 30)); continue
            n = poll_once(call, venues, watchlist, db=db, dry=args.dry_run)
            print(f"  {dt.datetime.now():%H:%M:%S} {n}건 ({time.time()-t0:.2f}s)")
            if args.once: break
            time.sleep(max(0.0, args.interval - (time.time() - t0)))
    except KeyboardInterrupt:
        print("중단됨")
    finally:
        if db: db.close()

# ---------------- 셀프테스트 (네트워크/DB 불필요) ----------------
def selftest():
    print("[selftest] 46필드 파서 검증 (합성 데이터, 네트워크·DB 없음)")
    rec = {F_CODE: "005930", F_ISIN: "KR7005930003"}
    for i, k in enumerate(ASK_PX): rec[k] = 80000 + (i + 1) * 100
    for i, k in enumerate(ASK_QTY): rec[k] = (i + 1) * 10
    for i, k in enumerate(BID_PX): rec[k] = 79900 - i * 100
    for i, k in enumerate(BID_QTY): rec[k] = (i + 1) * 7
    rec[F_ASK_TOT], rec[F_BID_TOT] = 550, 385
    row = parse_row(rec, "krx", "kospi", dt.datetime(2026, 7, 3, 9, 5, 0))
    assert row["code"] == "005930" and len(row["ask_px"]) == 10 and len(row["bid_qty"]) == 10
    assert row["ask_px"][0] == 80100 and row["bid_px"][0] == 79900 and row["ask_tot"] == 550
    spread = row["ask_px"][0] - row["bid_px"][0]
    print(f"  bid1={row['bid_px'][0]}({row['bid_qty'][0]})  ask1={row['ask_px'][0]}({row['ask_qty'][0]})  "
          f"spread={spread}  ask_tot={row['ask_tot']}  bid_tot={row['bid_tot']}")
    print("  INSERT 대상 컬럼:", ", ".join(k for k in row))
    print("  거래소 패밀리:", VENUE_FAM)
    print("  ✅ 파서/매핑 정상. 실적재는 장중 등록IP에서 --venues 로.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="CHECK 실시간 호가 → Postgres/TimescaleDB 적재")
    ap.add_argument("--watchlist", help="종목 워치리스트 JSON ({kospi:[...],kosdaq:[...]})")
    ap.add_argument("--venues", default="krx", help="krx,nxt,unified 중 콤마구분 (기본 krx)")
    ap.add_argument("--interval", type=float, default=1.0, help="폴링 간격(초)")
    ap.add_argument("--dsn", help="PG 접속 문자열(없으면 PG_DSN 환경변수)")
    ap.add_argument("--once", action="store_true", help="1회만")
    ap.add_argument("--dry-run", action="store_true", help="적재 없이 파싱/샘플 출력")
    ap.add_argument("--ignore-session", action="store_true", help="장 시간 체크 무시(테스트)")
    ap.add_argument("--selftest", action="store_true", help="네트워크·DB 없이 파서 검증")
    a = ap.parse_args()
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    if a.selftest: selftest()
    else: run(a)