"""크기 제한(toolarge)으로 REST 로 못 받은 (일,종목)을 다운로드 라우트로 회수한다.

왜 필요한가
  tick_date 는 응답이 일정 크기를 넘으면 거부한다.
      {"success": false, "message": "ERROR READ FILE. : File too large size(>= 500MB)."}
  임계값은 2026-08-07 에 500MB, 08-12 에 200MB 로 관측됐다(같은 endpoint·같은 호출).
  거부되는 건 언제나 최대 종목이다 -- 2026-08-14 기준 46건 중 005930 이 20건, 000660 이 9건.
  이 46건은 복원기(nxt_chg_restore.py)도 못 푸는 잔여의 대부분이다.

라우트
  CHECK API 웹 테스트 폼에서만 드러나는 경로다. 문서·카탈로그 어디에도 없다.
      GET /etc/download/tick?cust_id=..&auth_key=..&jcode=..&edate=..&api_url=<REST 경로>

  ※ 명세로는 이 라우트를 판정할 수 없다. /etc 도메인에 26개(comp·cons·economic·gaap·
    ifrs 등)가 있지만 download 는 하나도 없다 -- 즉 명세는 이 경로의 존재도, api_url 에
    무엇이 들어가는지도 말해주지 않는다. 웹 테스트 폼에서 관측해 알아낸 것이 전부다.

    그래서 api_url 에 intra_date 를 넣어 1분봉을 받는 발상은 근거가 없다. 명세에 없는
    조합을 추측으로 때리는 것일 뿐이다(2026-08-15 판단).

    다만 '분봉 다운로드가 없다'는 뜻은 아니다. 1분봉 조회 화면에 별도 다운로드 버튼이
    있다면 그 경로는 이것과 다른 URL 일 것이고, 알아내는 방법은 명세가 아니라
    그 화면을 직접 여는 것이다. 확인 전까지는 REST 로 간다고 전제한다.
  api_url 은 URL 인코딩된 REST 경로다(/stock/m222/tick_date -> %2Fstock%2Fm222%2Ftick_date).
  응답은 zip 이고 안에는 JSONL(한 줄에 체결 하나, 36필드 전부)이 종목코드 이름으로 들어 있다.
  data_list 는 무시된다(2026-08-14 실측: 2필드를 보내도 36필드가 온다). 대신 압축이 세서
  원본 216MB 가 12.8MB 로 온다 -- 그리고 일 한도는 전송 바이트로 계산된다(실측 확인).
  즉 REST 로 2필드만 받는 것보다 오히려 싸다.
  저장 이름은 load_koscom_dump.py 가 파일명에서 날짜·종목을 읽는 규칙에 맞췄다
  ({fam}_{YYYYMMDD}_{code}.zip).

무엇을 우회하고 무엇을 우회하지 않는가 (2026-08-14 실측)
  크기 제한: 우회한다. REST 가 toolarge 로 거부하는 건이 그대로 받아진다.
  보관창   : 우회하지 않는다. 05-04(102일 전)는 받아졌지만 04-29(107일)·04-15(121일)는
             HTTP 500 이다. KOSPI·KOSDAQ 둘 다 같아 시장 문제가 아니라 날짜 문제다.
             -> 4월분 미확정 379건은 이 라우트로도 못 살린다. 영구 미상이다.
  건당 비용: 12~30MB(전송 기준). 005930 하루가 12.8MB, 큰 날은 29MB.

주의 -- 실패가 성공처럼 보인다
  이 라우트는 오류도 200 OK + Content-Disposition 으로 준다. 브라우저는 그걸 .zip 으로
  저장하고, 사용자는 받은 줄 안다(2026-08-13 에 실제로 92바이트짜리 가짜 zip 두 개가
  Downloads 에 남았다). 그래서 이 스크립트는 첫 바이트를 보고 '{' 면 데이터가 아니라고
  판정하고 파일로 남기지 않는다. 한도 초과 메시지면 즉시 중단한다.

사용
  python koscom_tick_download.py --plan             # 대상만 출력(호출 없음)
  python koscom_tick_download.py --probe            # 1건만 때려 라우트 성질을 확인
  python koscom_tick_download.py --budget 300000000 # 예산만큼만
  python koscom_tick_download.py --no-data-list     # 전 필드로 받는다(비쌈)

등록 IP 밖에서는 실패한다. .env 의 CHECK_CUST_ID/CHECK_AUTH_KEY 를 쓴다.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I

I.C._force_utf8_stdout()

BASE = "https://checkapi.koscom.co.kr"
ROUTE = "/etc/download/tick"
OUTDIR = os.path.join(os.path.expanduser("~"), "Downloads", "koscom_tick")

# 틱 자체가 없는 건은 전 필드가 필요하다. chg_type 만 비는 건은 키+등락구분 2필드면 된다.
FULL_FIELDS = I.TICK_FIELDS
TT_FIELDS = I.CHG_TYPE_FIELDS


def targets(conn, include_expired=False):
    """(trade_date, code, market, need, fields) 목록. 만료 임박 순.

    need='tick'  틱 자체가 없다(nxt_tick 이 toolarge). 전 필드로 받아야 한다.
    need='tt'    틱은 있고 chg_type 만 없다. 2필드면 된다.
    """
    floor = dt.date.today() - dt.timedelta(days=I.TICK_RETENTION_DAYS)
    out = []
    with conn.cursor() as cur:
        cur.execute("""
            SELECT l.trade_date, l.code, l.job,
                   COALESCE(u.market, 'KOSPI')
            FROM ingest_log l
            LEFT JOIN nxt_universe u
                   ON u.code = l.code AND u.trade_date = l.trade_date
            WHERE l.status = 'toolarge' AND l.job IN ('nxt_tick', 'tick_tt')
            ORDER BY l.trade_date ASC, l.code ASC""")
        rows = cur.fetchall()

        # tick_tt 쪽은 복원기가 이미 푼 건을 뺀다 -- 그건 받을 이유가 없다.
        cur.execute("""SELECT trade_date, code FROM restore_log
                       WHERE method IN ('ambiguous','qtyonly')""")
        unresolved = {(d, c) for d, c in cur.fetchall()}

    seen = set()
    for day, code, job, market in rows:
        need = "tick" if job == "nxt_tick" else "tt"
        if need == "tt" and (day, code) not in unresolved:
            continue                       # 복원기가 풀었다
        if (day, code) in seen:
            continue
        seen.add((day, code))
        if not include_expired and day < floor:
            continue
        out.append((day, code, market, need,
                    FULL_FIELDS if need == "tick" else TT_FIELDS))
    # 틱 자체가 없는 건이 훨씬 값지다. 같은 만료일이면 그쪽을 먼저.
    out.sort(key=lambda r: (r[0], r[3] != "tick", r[1]))
    return out


TRUNC_TRIES = 3     # 전송이 끊기면 이만큼 다시 시도한다


def backlog_targets(conn, n):
    """아직 못 받은 (일,종목) 중 거래량 구간별로 고르게 n 건 뽑는다.

    왜 거래량인가: 백로그는 아직 안 받아서 틱 수를 모른다. nxt_daily.qty 는 전 구간에
    있고 틱 수와 강하게 붙어 있어 크기의 대리로 쓸 수 있다.

    왜 구간별인가: 지금까지 이 라우트로 받은 건 전부 초대형주(005930·000660 등)라
    평균 18.8MB 다. 백로그의 평균 종목은 훨씬 작고(REST 평균 1.15MB), 그 구간에서는
    zip 오버헤드가 이득을 까먹을 수 있다. 한쪽 끝만 재면 전체를 잘못 판단한다.
    """
    floor = dt.date.today() - dt.timedelta(days=I.TICK_RETENTION_DAYS)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT u.trade_date, u.code, u.market, d.qty
            FROM nxt_universe u
            JOIN nxt_daily d ON d.trade_date=u.trade_date AND d.code=u.code
            LEFT JOIN ingest_log l ON l.job='nxt_tick' AND l.code=u.code
                                  AND l.trade_date=u.trade_date
            WHERE u.trade_date >= %s AND d.qty > 0
              AND (l.status IS NULL OR l.status='retry')
            ORDER BY u.trade_date ASC""", (floor,))
        rows = list(cur.fetchall())      # pymysql 은 튜플을 준다
    if not rows:
        return []
    rows.sort(key=lambda r: int(r[3]))
    step = max(1, len(rows) // n)
    picked = [rows[min(i * step, len(rows) - 1)] for i in range(n)]
    seen, out = set(), []
    for day, code, market, qty in picked:
        if (day, code) in seen:
            continue
        seen.add((day, code))
        out.append((day, code, market, "tick", FULL_FIELDS, int(qty)))
    return out


def fetch(env, day, code, market, fields, send_fields=True, timeout=900):
    """(body, content_type, fam). 전송이 끊기면 다시 시도한다.

    수십 MB 를 한 연결로 받다 보니 IncompleteRead 가 실제로 난다
    (2026-08-14 05-07/005930: 7.3MB 받고 22.5MB 남긴 채 끊김).
    끊겨도 서버는 이미 만들어 보냈으므로 한도는 그대로 나간다 -- 그냥 넘기면 그 바이트가
    통째로 손해다. 그래서 포기하지 않고 다시 받는다.
    """
    fam = I.FAM_NXT[market]
    q = {"cust_id": env["CHECK_CUST_ID"], "auth_key": env["CHECK_AUTH_KEY"],
         "jcode": code, "edate": day.strftime("%Y%m%d"),
         "api_url": f"/stock/{fam}/tick_date"}
    if send_fields:
        q["data_list"] = ",".join(fields)
    url = f"{BASE}{ROUTE}?{urllib.parse.urlencode(q)}"

    last = None
    for attempt in range(1, TRUNC_TRIES + 1):
        req = urllib.request.Request(url, headers={"Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                want = r.headers.get("Content-Length")
                body = r.read()
                if want and len(body) < int(want):
                    raise IOError(f"잘림 {len(body):,}/{int(want):,}")
                return body, r.headers.get("Content-Type", ""), fam
        except (IOError, OSError) as exc:
            last = exc
            if attempt < TRUNC_TRIES:
                print(f"    끊김({exc}) — 재시도 {attempt}/{TRUNC_TRIES - 1}")
                time.sleep(5 * attempt)
    raise IOError(f"{TRUNC_TRIES}회 모두 끊김: {last}")


def classify(body):
    """(kind, detail). kind: 'data' | 'error' | 'quota'

    이 라우트는 오류도 200 OK 로 준다. 본문 첫 글자가 판별의 유일한 근거다.
    """
    head = body[:1]
    if head != b"{":
        return "data", f"{len(body):,} bytes"
    try:
        txt = body.decode("utf-8", "replace")
    except Exception:
        txt = repr(body[:200])
    if "사용량" in txt or "Bytes" in txt:
        return "quota", txt.strip()
    return "error", txt.strip()


def main():
    ap = argparse.ArgumentParser(description="toolarge 건을 다운로드 라우트로 회수")
    ap.add_argument("--plan", action="store_true", help="대상만 출력(호출 없음)")
    ap.add_argument("--probe", action="store_true",
                    help="1건만 때려 data_list 반영 여부와 보관창 우회 여부를 본다")
    ap.add_argument("--budget", type=int, default=300_000_000,
                    help="이 바이트를 넘기면 멈춘다(기본 300MB)")
    ap.add_argument("--no-data-list", action="store_true",
                    help="data_list 를 보내지 않는다(전 필드. 라우트가 무시하는지 대조용)")
    ap.add_argument("--include-expired", action="store_true",
                    help="보관창 밖 날짜도 대상에 넣는다(라우트가 창을 우회하는지 시험)")
    ap.add_argument("--backlog", type=int, metavar="N",
                    help="toolarge 대신 일반 백로그(아직 못 받은 틱)에서 거래량 구간별로 "
                         "N 건을 받는다. REST 대비 바이트를 재는 용도이자 실제 수집이다")
    ap.add_argument("--only", metavar="YYYY-MM-DD:CODE",
                    help="이 (일,종목) 하나만 받는다. toolarge 목록 밖도 지정할 수 있다 "
                         "-- 복원기가 못 푼 보관창 밖 건을 시험할 때 쓴다")
    ap.add_argument("--outdir", default=OUTDIR)
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    env = I.C.load_env()
    for k in ("CHECK_CUST_ID", "CHECK_AUTH_KEY"):
        if not env.get(k):
            raise SystemExit(f".env 에 {k} 가 없습니다.")

    conn = I.connect()
    try:
        if args.backlog:
            bl = backlog_targets(conn, args.backlog)
            tg = [t[:5] for t in bl]
            vol = {(t[0], t[1]): t[5] for t in bl}
        elif args.only:
            d, code = args.only.split(":")
            day = dt.date(int(d[:4]), int(d[5:7]), int(d[8:10]))
            with conn.cursor() as cur:
                cur.execute("SELECT market FROM nxt_universe WHERE trade_date=%s AND code=%s",
                            (day, code))
                row = cur.fetchone()
            tg = [(day, code, row[0] if row else "KOSPI", "tt", TT_FIELDS)]
            vol = {}
        else:
            tg = targets(conn, include_expired=args.include_expired or args.probe)
            vol = {}
    finally:
        conn.close()

    floor = dt.date.today() - dt.timedelta(days=I.TICK_RETENTION_DAYS)
    print(f"보관 하한 {floor} (오늘 기준). 대상 {len(tg)}건"
          + ("  [만료분 포함]" if args.include_expired or args.probe else ""))
    def saved(day, code, market):
        """이미 받아둔 파일. 실패 응답(수십 바이트)은 받은 것으로 치지 않는다."""
        p = os.path.join(args.outdir, f"{I.FAM_NXT[market]}_{day:%Y%m%d}_{code}.zip")
        return p if os.path.exists(p) and os.path.getsize(p) > 1000 else None

    print(f"{'거래일':11} {'종목':8} {'시장':7} {'필요':5} {'필드':>4} {'만료':11} {'상태':>10}")
    left = 0
    for day, code, market, need, fields in tg:
        exp = day + dt.timedelta(days=I.TICK_RETENTION_DAYS)
        have = saved(day, code, market)
        if not have:
            left += 1
        state = f"{os.path.getsize(have)/1e6:.1f}MB" if have else "미수신"
        tag = "  <- 창 밖" if day < floor else ""
        print(f"{str(day):11} {code:8} {market:7} {need:5} {len(fields):>4} "
              f"{str(exp):11} {state:>10}{tag}")
    print(f"\n대상 {len(tg)}건 중 미수신 {left}건")
    if args.plan:
        return

    os.makedirs(args.outdir, exist_ok=True)
    send = not args.no_data_list

    if args.probe:
        # 창 밖 + 가장 큰 종목을 고른다. 크기·보관창 두 제약을 한 번에 건드린다.
        old = [t for t in tg if t[0] < floor] or tg
        day, code, market, need, fields = old[0]
        print(f"\n[probe] {day} {code} {market} need={need} "
              f"data_list={'보냄(' + str(len(fields)) + '필드)' if send else '안 보냄'}")
        body, ctype, fam = fetch(env, day, code, market, fields, send)
        kind, detail = classify(body)
        print(f"  -> {kind}  content-type={ctype}\n     {detail[:300]}")
        if kind == "data":
            path = os.path.join(args.outdir, f"{fam}_{day:%Y%m%d}_{code}.zip")
            with open(path, "wb") as f:
                f.write(body)
            print(f"     저장: {path}")
            print("     => 크기 제한과 보관창을 모두 우회한다. 전량 회수 가능.")
        elif "too large" in detail.lower():
            print("     => 크기 제한이 그대로 걸린다. 이 라우트로는 회수 불가.")
        elif "Query" in detail:
            print("     => 크기는 통과, 보관창이 막았다. 창 안 건은 받을 수 있다.")
        return

    spent = ok = 0
    for day, code, market, need, fields in tg:
        fam = I.FAM_NXT[market]
        path = os.path.join(args.outdir, f"{fam}_{day:%Y%m%d}_{code}.zip")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            print(f"{day} {code}  건너뜀(이미 있음)")
            continue
        if spent >= args.budget:
            print(f"\n예산 {args.budget:,} 소진 -- 중단. 남은 대상은 다음 실행에서.")
            break
        try:
            body, ctype, fam = fetch(env, day, code, market, fields, send)
        except Exception as exc:
            print(f"{day} {code}  실패: {exc}")
            continue
        spent += len(body)
        kind, detail = classify(body)
        if kind == "quota":
            print(f"{day} {code}  한도 초과 -- 중단\n  {detail}")
            break
        if kind == "error":
            print(f"{day} {code}  오류: {detail[:160]}")
            continue
        with open(path, "wb") as f:
            f.write(body)
        ok += 1
        v = vol.get((day, code))
        extra = f"  거래량 {v:,}  bytes/주 {len(body)/max(1,v):.2f}" if v else ""
        print(f"{day} {code}  받음 {len(body):,} bytes -> {os.path.basename(path)}{extra}")
        time.sleep(args.sleep)

    print(f"\n받음 {ok}건 / 누적 {spent:,} bytes / 저장 {args.outdir}")
    if ok:
        print("zip 안의 형식을 확인한 뒤 load_koscom_dump.py 로 적재하세요.")


if __name__ == "__main__":
    main()
