"""NXT 애프터/프리 -> KRX 시초가 연구용 수집기 (CHECK API -> MySQL).

연구 설계
  NXT에서 (거래일 D, 종목 S)가 거래됐다면
    - NXT 체결(틱)    : D의 프리(08:00~08:50)·메인·애프터(15:40~20:00) 전 세션
    - KRX 1분봉       : D 와 익일 D+1  (D+1 09:00 시초가 형성이 관심 대상)
  을 모은다.

핵심 제약 (2026-07-13 실측)
  - tick_date 는 **최근 약 101일(달력)** 만 보관한다. 그 이전 날짜는
    'Error while performing Query.' 로 실패한다 -> NXT 출범(2025-03-24)부터의 틱은 존재하지 않는다.
    **틱은 매일 하루치씩 영구 소실되는 소멸성 자원이다. 오래된 날부터 먼저 받는다.**
  - intra_date(1분봉)는 2025-03-24까지 소급된다. 급하지 않다.
  - 상폐 종목은 장중 데이터(틱·1분봉) 조회가 안 된다(일봉만 남음) -> status='expired' 로 기록.
  - 일 사용량 한도 1,000,000,000 bytes. 아껴야 할 자원은 호출 수가 아니라 **응답 바이트**다.
    data_list 로 필드를 좁히지 않으면 tick_date 1콜(삼성전자)이 312MB다.
  - intra_date / tick_date 는 초당 1회 제한이 **없다**(무간격 연속 호출 확인). 반면
    hist_info 등 시계열은 제한이 있어 달력 조회에만 간격을 둔다.

사용
  # 매일 이것 하나만 돌리면 된다 (신규 거래일 자동 편입 -> 틱 -> KRX 1분봉 -> NXT 1분봉)
  python nxt_krx_ingest.py --daily

  python nxt_krx_ingest.py --plan                          # 남은 작업량·예상 용량/일수
  python nxt_krx_ingest.py --refresh-universe              # 신규 거래일만 편입
  python nxt_krx_ingest.py --job nxt_tick                  # 개별 작업만
  python nxt_krx_ingest.py --daily --budget 300000000      # 오늘 남은 한도만큼만

최초 1회 (이미 완료)
  python nxt_universe.py --sdate 20250301 --edate <오늘>   # 과거 유니버스 CSV
  python nxt_krx_ingest.py --init-calendar --load-universe ../../../data/nxt_universe_daily.csv

등록 IP·샌드박스 밖에서 실행. .env 에 CHECK_CUST_ID/CHECK_AUTH_KEY 와
MYSQL_HOST/MYSQL_PORT/MYSQL_USER/MYSQL_PASSWORD/MYSQL_DB 가 있어야 한다.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C

C._force_utf8_stdout()

BASE = "https://checkapi.koscom.co.kr"

# 응답 필드(F-code). data_list 로 이것만 받는다 -- 전체 필드로 받으면 수십 배가 된다.
TICK_FIELDS = ["F15019", "F15001", "F15020", "F15022"]          # 체결시간·체결가·체결량·체결성향
BAR_FIELDS = ["F20004_02", "F20005_02", "F20006_02", "F20007_02",
              "F20008_02", "F20010_02", "F20011_02"]            # 시각·시고저종·거래량·거래대금

FAM_NXT = {"KOSPI": "m222", "KOSDAQ": "m223"}
FAM_KRX = {"KOSPI": "m001", "KOSDAQ": "m003"}

# tick_date 보관 한계(달력 일수). 실측 101일 -> 여유를 두고 105일까지만 시도한다.
TICK_RETENTION_DAYS = 105

# 콜당 평균 응답 바이트(표본 실측) -- --plan 추정에만 쓴다.
AVG_BYTES = {"nxt_tick": 150_000, "krx_min": 50_300, "nxt_min": 53_300}

DAILY_LIMIT = 1_000_000_000
DEFAULT_BUDGET = 900_000_000     # 일 한도의 90%에서 스스로 멈춘다


class Quota(Exception):
    """일 사용량 한도 또는 자체 예산 도달. 중단하고 다음 날 재개한다."""


class ApiError(Exception):
    """success=false 또는 네트워크 오류. 절대 빈 결과로 흘리지 않는다."""


class Unavailable(Exception):
    """보관창 밖·상폐 등으로 그 (종목,일자)는 원천적으로 조회 불가."""


# ------------------------------------------------------------------ API

_env = C.load_env()
CID, KEY = _env["CHECK_CUST_ID"], _env["CHECK_AUTH_KEY"]
_bytes = 0
_last_ts_call = 0.0


def call(apiurl: str, params: dict, timeseries: bool = False, tries: int = 4):
    """POST 호출. 반환: (results, 응답바이트)."""
    global _bytes, _last_ts_call
    if timeseries:                       # 시계열(hist_info 등)만 초당 1회 제한이 있다
        gap = time.time() - _last_ts_call
        if gap < 1.15:
            time.sleep(1.15 - gap)
    body = urllib.parse.urlencode({"cust_id": CID, "auth_key": KEY, **params}).encode()
    req = urllib.request.Request(BASE + apiurl, data=body)
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read()
            _bytes += len(raw)
            if timeseries:
                _last_ts_call = time.time()
            payload = json.loads(raw)
            if payload.get("success"):
                return payload["results"], len(raw)
            msg = json.dumps(payload.get("message") or payload, ensure_ascii=False)
            if "사용량" in msg or "초과" in msg:
                raise Quota(msg)
            # 보관창 밖 / 상폐 / 해당일 데이터 없음 -> 재시도해도 소용없다
            if "performing Query" in msg or "jcode_denied" in msg:
                raise Unavailable(msg)
            raise ApiError(f"{apiurl} {params} -> {msg}")
        except (Quota, ApiError, Unavailable):
            raise
        except Exception as exc:                       # 네트워크·타임아웃만 재시도
            if attempt == tries - 1:
                raise ApiError(f"{apiurl} {params} -> {exc}")
            time.sleep(1.5 * (attempt + 1))


def check_fields(rows, requested, apiurl):
    """data_list 는 없는 F-code 를 조용히 버린다 -> 요청/반환 개수를 대조한다."""
    if not rows:
        return
    missing = set(requested) - set(rows[0])
    if missing:
        raise ApiError(f"{apiurl}: data_list 요청 {len(requested)}개 중 {sorted(missing)} 미반환 "
                       "(F-code 오타 의심)")


# ------------------------------------------------------------------ MySQL

def connect():
    try:
        import pymysql
    except ImportError:
        raise SystemExit("pymysql 이 필요합니다:  pip install pymysql")
    missing = [k for k in ("MYSQL_USER", "MYSQL_PASSWORD") if not _env.get(k)]
    if missing:
        raise SystemExit(f".env 에 {', '.join(missing)} 를 추가하세요 "
                         "(MYSQL_HOST/MYSQL_PORT/MYSQL_DB 는 기본값 localhost/3306/nxt_krx).")
    return pymysql.connect(
        host=_env.get("MYSQL_HOST", "127.0.0.1"),
        port=int(_env.get("MYSQL_PORT", 3306)),
        user=_env["MYSQL_USER"],
        password=_env["MYSQL_PASSWORD"],
        database=_env.get("MYSQL_DB", "nxt_krx"),
        charset="utf8mb4",
        autocommit=False,
    )


def log_done(cur, job, code, day, status, n_rows=0, n_bytes=0, msg=None):
    cur.execute(
        "INSERT INTO ingest_log (job, code, trade_date, status, n_rows, n_bytes, msg) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE status=VALUES(status), n_rows=VALUES(n_rows), "
        "n_bytes=VALUES(n_bytes), msg=VALUES(msg), done_at=CURRENT_TIMESTAMP",
        (job, code, day, status, n_rows, n_bytes, (msg or "")[:200]))


# ------------------------------------------------------------------ 셋업

def init_calendar(conn, sdate, edate):
    """코스피 지수(m002) 일별정보로 거래일 달력을 만든다. 익일(D+1) 계산의 기준."""
    rows, _ = call("/stock/m002/hist_info",
                   {"jcode": "1", "sdate": sdate, "edate": edate, "data_list": "F12506"},
                   timeseries=True)
    days = sorted({str(r["F12506"]) for r in rows})
    with conn.cursor() as cur:
        cur.execute("DELETE FROM trading_day")
        cur.executemany(
            "INSERT INTO trading_day (trade_date, seq) VALUES (%s,%s)",
            [(f"{d[:4]}-{d[4:6]}-{d[6:]}", i) for i, d in enumerate(days)])
    conn.commit()
    print(f"[calendar] 거래일 {len(days)}일 적재: {days[0]} ~ {days[-1]}")


def load_universe(conn, path):
    """nxt_universe.py 산출 CSV -> nxt_universe 테이블."""
    with open(path, encoding="utf-8-sig") as fh:
        rows = []
        for r in csv.DictReader(fh):
            d = r["일자"]
            rows.append((f"{d[:4]}-{d[4:6]}-{d[6:]}", r["단축코드"],
                         "KOSPI" if "KOSPI" in r["시장"] else "KOSDAQ",
                         r.get("종목명") or None,
                         0 if r.get("현재상장여부") == "상폐" else 1))
    with conn.cursor() as cur:
        cur.execute("DELETE FROM nxt_universe")
        for i in range(0, len(rows), 5000):
            cur.executemany(
                "INSERT INTO nxt_universe (trade_date, code, market, name, listed_now) "
                "VALUES (%s,%s,%s,%s,%s)", rows[i:i + 5000])
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT code), MIN(trade_date), MAX(trade_date), "
                    "SUM(listed_now=0) FROM nxt_universe")
        n, ncode, d0, d1, ndel = cur.fetchone()
    print(f"[universe] {n:,}쌍 · 고유종목 {ncode:,} · {d0}~{d1} · 현재상폐 {ndel:,}쌍")


def refresh_universe(conn, sdate="20250301"):
    """신규 거래일을 감지해 달력·유니버스를 증분 갱신한다.

    - 달력(trading_day)은 통째로 다시 만든다(수백 행이라 싸다. seq 연속성도 보장된다).
    - nxt_universe 는 아직 없는 거래일만 rank_invest_date 로 채운다(시장당 1콜, ~70KB).
    - 당일(오늘)은 넣지 않는다. NXT 는 20:00까지 거래하므로 장 마감 전 조회는 불완전하다.
    """
    today = dt.date.today()
    rows, _ = call("/stock/m002/hist_info",
                   {"jcode": "1", "sdate": sdate, "edate": today.strftime("%Y%m%d"),
                    "data_list": "F12506"}, timeseries=True)
    days = sorted({str(r["F12506"]) for r in rows})
    with conn.cursor() as cur:
        cur.execute("DELETE FROM trading_day")
        cur.executemany("INSERT INTO trading_day (trade_date, seq) VALUES (%s,%s)",
                        [(f"{d[:4]}-{d[4:6]}-{d[6:]}", i) for i, d in enumerate(days)])
        cur.execute("SELECT DISTINCT trade_date FROM nxt_universe")
        have = {r[0] for r in cur.fetchall()}
    conn.commit()

    want = [d for d in days
            if dt.date(int(d[:4]), int(d[4:6]), int(d[6:])) < today
            and dt.date(int(d[:4]), int(d[4:6]), int(d[6:])) not in have]
    if not want:
        print(f"[universe] 신규 거래일 없음 (최신 {max(have) if have else '-'})")
        return 0

    print(f"[universe] 신규 거래일 {len(want)}일: {', '.join(want)}")
    names = {}
    for fam in FAM_NXT.values():
        try:
            for r in call(f"/stock/{fam}/code_info", {})[0]:
                names[r["F16013"]] = r.get("F16002")
        except (ApiError, Unavailable) as exc:
            print(f"[warn] {fam} code_info 실패({exc}) — 종목명 공란으로 진행")

    added = 0
    for d in want:
        day = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        recs = []
        for market, fam in FAM_NXT.items():
            res, _ = call(f"/stock/{fam}/rank_invest_date", {
                "criteria_code": "F06508_12", "sort_code": "0", "sdate": d, "edate": d,
                "data_list": "F16013,F06505_12,F06507_12"})
            check_fields(res, ["F16013", "F06505_12", "F06507_12"], f"/stock/{fam}/rank_invest_date")
            for r in res:
                # 상장 != 거래. 실제 체결은 매도(F06505) 또는 매수(F06507) 거래량 > 0.
                if int(r.get("F06505_12") or 0) > 0 or int(r.get("F06507_12") or 0) > 0:
                    code = r["F16013"]
                    recs.append((day, code, market, names.get(code),
                                 1 if code in names else 0))
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO nxt_universe (trade_date, code, market, name, listed_now) "
                "VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name)", recs)
        conn.commit()
        added += len(recs)
        print(f"  {day}: 거래종목 {len(recs)}개")
    print(f"[universe] {added:,}쌍 추가 · 수신 {_bytes/1e6:.0f}MB")
    return added


def daily(conn, budget):
    """일일 러너: 유니버스 갱신 -> 우선순위대로 예산 소진까지 수집.

    예산(응답 바이트)은 한 프로세스 안에서 세 작업이 공유한다. 틱이 소멸성이므로 항상 먼저.
    """
    already = spent_today(conn)
    budget = max(0, budget - already)          # 오늘 이미 쓴 만큼 차감 (중복 실행 방지)
    print(f"===== 일일 수집 {dt.date.today()} — 오늘 이미 {already/1e6:.0f}MB 수신, "
          f"이번 실행 예산 {budget/1e6:.0f}MB (일 한도 {DAILY_LIMIT/1e6:.0f}MB) =====\n")
    if budget <= 0:
        print("오늘 예산을 이미 소진했습니다. 내일 다시 실행하세요.")
        return
    try:
        refresh_universe(conn)
    except Quota as exc:
        print(f"[STOP] 유니버스 갱신 중 한도 도달: {exc}")
        return
    except ApiError as exc:
        print(f"[STOP] 유니버스 갱신 실패: {exc}\n       수집을 진행하지 않습니다(불완전 유니버스 방지).")
        return

    for job in ("nxt_tick", "krx_min", "nxt_min"):
        if _bytes >= budget:
            print(f"\n[예산 소진] {job} 이후 작업은 다음 실행에서 이어서 진행합니다.")
            break
        print()
        # KOSCOM 이 자체 예산보다 먼저 한도를 걸 수 있다(다른 작업이 같은 cust_id 를 썼을 때).
        # 그때 다음 job 으로 넘어가면 헛호출만 하므로 여기서 끊는다.
        if run(conn, job, budget) == "quota":
            print(f"\n[한도 도달] {job} 이후 작업은 다음 실행에서 이어서 진행합니다.")
            break
    print(f"\n===== 오늘 총 수신 {_bytes/1e6:.0f}MB =====")


# ------------------------------------------------------------------ 작업 목록

def tick_floor():
    """오늘 기준 tick_date 로 시도해볼 가치가 있는 가장 오래된 날짜."""
    return dt.date.today() - dt.timedelta(days=TICK_RETENTION_DAYS)


def targets(conn, job):
    """미완료 (code, trade_date, market) 목록. 틱은 오래된 날부터(소멸성)."""
    with conn.cursor() as cur:
        if job == "nxt_tick":
            cur.execute(
                "SELECT u.code, u.trade_date, u.market FROM nxt_universe u "
                "LEFT JOIN ingest_log l ON l.job=%s AND l.code=u.code AND l.trade_date=u.trade_date "
                "WHERE u.trade_date >= %s AND l.status IS NULL "
                "ORDER BY u.trade_date ASC, u.code ASC",        # 오래된 날 = 먼저 만료 = 먼저 수집
                ("nxt_tick", tick_floor()))
        elif job == "nxt_min":
            # 틱을 확보하지 못한 쌍에만 필요하다(틱이 있으면 1분봉은 거기서 재구성 가능).
            # 보관창 날짜(< tick_floor)로 거르면 안 된다 — 창이 앞으로 밀리면서 이미 틱을 받아둔
            # 날이 창 밖으로 나가고, 그때 1분봉을 중복 수집하게 된다.
            cur.execute(
                "SELECT u.code, u.trade_date, u.market FROM nxt_universe u "
                "LEFT JOIN ingest_log l ON l.job=%s AND l.code=u.code AND l.trade_date=u.trade_date "
                "LEFT JOIN ingest_log t ON t.job='nxt_tick' AND t.code=u.code "
                "                      AND t.trade_date=u.trade_date AND t.status='ok' "
                "WHERE l.status IS NULL AND t.status IS NULL "
                "ORDER BY u.trade_date DESC, u.code ASC",
                ("nxt_min",))
        elif job == "krx_min":
            # (D) 와 (D+1) 의 합집합. NXT 거래종목 집합이 날마다 거의 같아 합집합은 약 1.05배뿐이다.
            cur.execute(
                "SELECT DISTINCT t.code, t.trade_date, t.market FROM ("
                "  SELECT u.code, u.trade_date, u.market FROM nxt_universe u"
                "  UNION"
                "  SELECT u.code, n.trade_date, u.market FROM nxt_universe u"
                "    JOIN trading_day d  ON d.trade_date = u.trade_date"
                "    JOIN trading_day n  ON n.seq = d.seq + 1"      # 익일
                ") t "
                "LEFT JOIN ingest_log l ON l.job=%s AND l.code=t.code AND l.trade_date=t.trade_date "
                "WHERE l.status IS NULL "
                "ORDER BY t.trade_date DESC, t.code ASC",
                ("krx_min",))
        else:
            raise SystemExit(f"알 수 없는 job: {job}")
        return cur.fetchall()


# ------------------------------------------------------------------ 수집

def fetch_tick(cur, code, day, market):
    fam = FAM_NXT[market]
    url = f"/stock/{fam}/tick_date"
    rows, nb = call(url, {"jcode": code, "edate": day.strftime("%Y%m%d"),
                          "data_list": ",".join(TICK_FIELDS)})
    check_fields(rows, TICK_FIELDS, url)
    recs = []
    for n, r in enumerate(rows):
        ts = int(r["F15019"] or 0)
        # 예상체결(ts=0) 과 세션 마커(31000000 장마감 / 41000000 시간외마감 / 51000000 장전 등) 제외
        if ts <= 0 or ts > 23_59_59_99:
            continue
        qty = int(r["F15020"] or 0)
        if qty <= 0:
            continue
        side = r.get("F15022")
        recs.append((day, code, n, ts, int(r["F15001"] or 0), qty,
                     int(side) if side not in (None, "") else None))
    if recs:
        cur.execute("DELETE FROM nxt_tick WHERE trade_date=%s AND code=%s", (day, code))
        for i in range(0, len(recs), 5000):
            cur.executemany(
                "INSERT INTO nxt_tick (trade_date, code, n, ts, price, qty, side) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)", recs[i:i + 5000])
    return len(recs), nb


def fetch_bar(cur, code, day, market, venue):
    fam = (FAM_NXT if venue == "NXT" else FAM_KRX)[market]
    url = f"/stock/{fam}/intra_date"
    rows, nb = call(url, {"jcode": code, "edate": day.strftime("%Y%m%d"),
                          "data_list": ",".join(BAR_FIELDS)})
    check_fields(rows, BAR_FIELDS, url)

    def num(v):
        return None if v in (None, "") else int(float(v))

    recs = [(venue, day, code, int(r["F20004_02"]),
             num(r.get("F20005_02")), num(r.get("F20006_02")),
             num(r.get("F20007_02")), num(r.get("F20008_02")),
             num(r.get("F20010_02")), num(r.get("F20011_02"))) for r in rows]
    if recs:
        cur.execute("DELETE FROM bar_1m WHERE trade_date=%s AND code=%s AND venue=%s",
                    (day, code, venue))
        for i in range(0, len(recs), 5000):
            cur.executemany(
                "INSERT INTO bar_1m (venue, trade_date, code, ts, px_open, px_high, px_low, "
                "px_close, volume, value) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                recs[i:i + 5000])
    return len(recs), nb


def run(conn, job, budget):
    todo = targets(conn, job)
    if not todo:
        print(f"[{job}] 남은 작업 없음 — 완료 상태입니다.")
        return
    est = len(todo) * AVG_BYTES[job]
    print(f"[{job}] 남은 {len(todo):,}콜 · 예상 {est/1e9:.1f}GB "
          f"(오늘 예산 {budget/1e6:.0f}MB -> 약 {min(budget, est)/AVG_BYTES[job]:,.0f}콜 처리 예정)")
    if job == "nxt_tick":
        print(f"       틱 보관 하한 {tick_floor()} — 오래된 날부터 처리합니다(만료 레이스).")

    t0, ok, empty, exp = time.time(), 0, 0, 0
    stopped = None                      # 'quota' | 'error' | None(완주)
    try:
        for i, (code, day, market) in enumerate(todo, 1):
            if _bytes >= budget:
                raise Quota(f"자체 예산 {budget:,}B 도달")
            with conn.cursor() as cur:
                try:
                    if job == "nxt_tick":
                        n, nb = fetch_tick(cur, code, day, market)
                    elif job == "nxt_min":
                        n, nb = fetch_bar(cur, code, day, market, "NXT")
                    else:
                        n, nb = fetch_bar(cur, code, day, market, "KRX")
                except Unavailable as exc:
                    log_done(cur, job, code, day, "expired", msg=str(exc))
                    exp += 1
                else:
                    log_done(cur, job, code, day, "ok" if n else "empty", n, nb)
                    ok += 1 if n else 0
                    empty += 0 if n else 1
            conn.commit()
            if i % 200 == 0:
                rate = i / max(time.time() - t0, 1)
                print(f"  {i:,}/{len(todo):,}  ok {ok:,} / 빈 {empty:,} / 불가 {exp:,}  "
                      f"{_bytes/1e6:.0f}MB  {rate:.1f}콜/s  "
                      f"ETA(예산소진) {(budget-_bytes)/max(_bytes/max(i,1),1)/max(rate,0.01)/60:.0f}분", flush=True)
    except Quota as exc:
        stopped = "quota"
        print(f"\n[STOP] {exc}")
        print("       한도/예산 도달은 정상 종료입니다(오류 아님). 자정에 한도가 리셋되며,")
        print("       다음 실행에서 ingest_log 기준으로 이어서 진행합니다.")
    except ApiError as exc:
        stopped = "error"
        print(f"\n[STOP] API 오류: {exc}")
        print("       빈 결과로 흘리지 않고 중단했습니다. 원인 확인 후 재실행하세요.")
    finally:
        conn.commit()
        print(f"\n[{job}] 이번 실행: ok {ok:,} · 빈응답 {empty:,} · 조회불가 {exp:,} · "
              f"수신 {_bytes/1e6:.0f}MB · {time.time()-t0:.0f}초")
        coverage(conn, job)
    return stopped


def coverage(conn, job):
    """완전성 검사: 남은 작업과 커버 범위를 출력한다(조용한 누락 방지)."""
    with conn.cursor() as cur:
        cur.execute("SELECT status, COUNT(*), SUM(n_rows) FROM ingest_log WHERE job=%s "
                    "GROUP BY status", (job,))
        stat = cur.fetchall()
    left = len(targets(conn, job))
    done = {s: (c, r or 0) for s, c, r in stat}
    parts = " · ".join(f"{s} {c:,}콜/{r:,}행" for s, (c, r) in sorted(done.items()))
    print(f"[{job}] 누적: {parts or '없음'}  |  남은 작업 {left:,}콜")


def spent_today(conn):
    """오늘 이미 수신한 바이트(ingest_log 기준). 같은 날 두 번 돌려도 일 한도를 넘지 않게 한다.

    프로브·유니버스 수집 등 ingest_log 를 안 거친 호출은 안 잡히므로 완벽하진 않다.
    그래도 스케줄러 실행 + 수동 실행이 겹쳐 한도를 두 배로 쓰는 사고는 막는다.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(n_bytes),0) FROM ingest_log WHERE done_at >= CURDATE()")
        return int(cur.fetchone()[0])


def observed_avg(conn, job):
    """이미 받은 콜의 실측 평균 바이트. 표본이 적으면 None(사전 추정치로 대체)."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), AVG(n_bytes) FROM ingest_log "
                    "WHERE job=%s AND status='ok'", (job,))
        n, avg = cur.fetchone()
    return (float(avg), n) if n and n >= 300 else (None, n or 0)


def plan(conn):
    print(f"틱 보관 하한(오늘 기준) : {tick_floor()}  — 이보다 오래된 날의 체결은 API에 없습니다.\n")
    total = 0
    for job in ("nxt_tick", "krx_min", "nxt_min"):
        n = len(targets(conn, job))
        avg, nsample = observed_avg(conn, job)
        src = f"실측 {nsample:,}콜" if avg else "사전추정"
        avg = avg or AVG_BYTES[job]
        gb = n * avg / 1e9
        total += gb
        print(f"  {job:9} 남은 {n:>8,}콜 x {avg/1000:>6.0f}KB({src:>12}) = {gb:>5.1f}GB "
              f"({gb:>4.1f}일치 한도)")
    print(f"  {'합계':9} {'':>44} {total:>5.1f}GB  ({total:.0f}일)")
    print("\n권장 순서: nxt_tick(소멸성) -> krx_min -> nxt_min")
    print("주의: 표본 300콜 미만이면 사전추정치입니다. 코드 오름차순 처리라 초반 표본은 "
          "대형주에 쏠려 과대추정되는 경향이 있습니다.")


class _Tee:
    """stdout 을 파일에도 쓴다. 배치파일 리다이렉션(> 파일)을 안 쓰기 위한 것 —
    cmd 는 % 를 변수로 먹고 한글 주석을 CP949 로 오독해 배치가 조용히 깨진다."""

    def __init__(self, path):
        self.f = open(path, "a", encoding="utf-8")
        self.out = sys.stdout

    def write(self, s):
        self.out.write(s)
        self.f.write(s)
        self.f.flush()

    def flush(self):
        self.out.flush()
        self.f.flush()


def main():
    ap = argparse.ArgumentParser(description="NXT 틱 + KRX/NXT 1분봉 -> MySQL 수집기")
    ap.add_argument("--log", metavar="DIR",
                    help="이 디렉터리에 ingest_YYYYMMDD.log 로 진행 로그를 남긴다(스케줄러용)")
    ap.add_argument("--job", choices=["nxt_tick", "krx_min", "nxt_min"])
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                    help=f"이번 실행에서 받을 최대 응답 바이트 (기본 {DEFAULT_BUDGET:,}, 일 한도 {DAILY_LIMIT:,})")
    ap.add_argument("--daily", action="store_true",
                    help="일일 러너: 유니버스 증분 갱신 + 우선순위대로 예산 소진까지 수집")
    ap.add_argument("--refresh-universe", action="store_true",
                    help="신규 거래일만 유니버스에 추가(수집은 안 함)")
    ap.add_argument("--init-calendar", action="store_true")
    ap.add_argument("--load-universe", metavar="CSV")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--sdate", default="20250301")
    ap.add_argument("--edate", default=dt.date.today().strftime("%Y%m%d"))
    args = ap.parse_args()

    if args.log:
        os.makedirs(args.log, exist_ok=True)
        sys.stdout = _Tee(os.path.join(args.log, f"ingest_{dt.date.today():%Y%m%d}.log"))
        print(f"\n===== {dt.datetime.now():%Y-%m-%d %H:%M:%S} 시작 =====")

    conn = connect()
    try:
        if args.init_calendar:
            init_calendar(conn, args.sdate, args.edate)
        if args.load_universe:
            load_universe(conn, args.load_universe)
        if args.refresh_universe:
            refresh_universe(conn, args.sdate)
        if args.daily:
            daily(conn, args.budget)
        if args.plan:
            plan(conn)
        if args.job:
            run(conn, args.job, args.budget)
        if not any([args.init_calendar, args.load_universe, args.refresh_universe,
                    args.daily, args.plan, args.job]):
            ap.print_help()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
