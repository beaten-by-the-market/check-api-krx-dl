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
  # 매일 이것 하나만 돌리면 된다
  # (신규 거래일 편입 -> 호가보강 -> 틱 -> KRX 1분봉 -> NXT 1분봉)
  python nxt_krx_ingest.py --daily

  python nxt_krx_ingest.py --plan                          # 남은 작업량·예상 용량/일수
  python nxt_krx_ingest.py --refresh-universe              # 신규 거래일만 편입
  python nxt_krx_ingest.py --job tick_ob                   # 개별 작업만(호가 보강)
  python nxt_krx_ingest.py --job nxt_tick
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
# F15019(체결시간)는 초 해상도뿐이다(전체 필드로 받아도 센티초 자리는 항상 00 -- API 원천 한계,
# 실호출 확인). 같은 초에 몰린 체결의 순서는 F16604(종목별저장일련번호)로 구분한다: KOSCOM 이
# 원본에서 매기는 단조증가 번호로, 응답 배열 순서(우리 n)와 정확히 일치한다(중복 없음, 실측).
#
# 호가 4개(F14501/F14531/F14511/F14541)는 체결 시점의 최우선 매도/매수 호가와 잔량이다.
# 이게 있으면 체결이 매도호가를 쳤는지 매수호가를 쳤는지, 유효 스프레드가 얼마였는지 계산된다.
# 비용: 5필드 대비 x1.77 (실측). 만료 레이스 순증이 +0.84 -> +0.16 거래일/일로 줄지만 여전히 양수.
# F15028(시가총액)은 뺐다 -- 13자리 숫자가 매 틱 반복돼 혼자 x0.30을 먹는데,
# 체결가 x 상장주식수라 틱 하나만 있으면 나머지는 역산된다.
TICK_FIELDS = ["F16604", "F15019", "F15001", "F15020", "F15022",   # 일련번호·체결시간·체결가·체결량·체결성향
               "F14501", "F14531", "F14511", "F14541"]             # 매도호가1·매수호가1·매도잔량1·매수잔량1
BAR_FIELDS = ["F20004_02", "F20005_02", "F20006_02", "F20007_02",
              "F20008_02", "F20010_02", "F20011_02"]            # 시각·시고저종·거래량·거래대금

# 호가 보강(tick_ob)용. 이미 받아둔 틱에 호가 4개만 채울 때는 전체를 다시 받을 필요가 없다.
# 키(F16604)로 행 정렬을 검증하며 UPDATE 한다 -> 9필드 전체 재수집 대비 약 44% 절약.
OB_FIELDS = ["F16604", "F14501", "F14531", "F14511", "F14541"]

FAM_NXT = {"KOSPI": "m222", "KOSDAQ": "m223"}
FAM_KRX = {"KOSPI": "m001", "KOSDAQ": "m003"}

# tick_date 보관 한계(달력 일수). 실측 101일.
# 105 로 잡았더니 이미 만료된 날(2026-07-29 기준 4/15, 105일 전)을 대상에 넣어 602콜을
# 통째로 날렸다. 경계 밖을 넉넉히 잡는 건 손해다 -- 못 받을 날을 두드리는 비용만 든다.
# 100 이면 실측 경계(101) 안쪽이라 헛시도가 없고, 하루 이틀 손해는 어차피 못 받는 날이다.
TICK_RETENTION_DAYS = 100

# 콜당 평균 응답 바이트(표본 실측) -- --plan 추정에만 쓴다.
AVG_BYTES = {"nxt_tick": 150_000, "krx_min": 50_300, "nxt_min": 53_300, "tick_ob": 900_000}

# 평시 일 한도. KOSCOM 이 일시적으로 늘려 주기도 한다(2026-08-05~09: 5GB).
# --daily-limit 로 덮어쓸 수 있다. 안내 문구용이며 실제 상한은 --budget 이다.
DAILY_LIMIT = 1_000_000_000
DEFAULT_BUDGET = 900_000_000     # 일 한도의 90%에서 스스로 멈춘다

# 미등록 IP 접속 이력이 있으면 키가 일시 차단된다(약 20분). 차단 메시지는 키 오류와 똑같이
# 'cust_id 또는 auth_key가 정확하지 않습니다.' 로 와서 구분이 안 된다.
# -> 즉시 포기하지 말고 기다렸다 재시도한다. 무인 야간 실행에서 하룻밤을 통째로 날리지 않기 위함.
AUTH_RETRY_WAIT = 300            # 5분 간격으로 재시도
AUTH_MAX_WAIT = 3600             # 최대 1시간까지 기다린 뒤 포기(차단 20분 + 여유)


class Quota(Exception):
    """일 사용량 한도 또는 자체 예산 도달. 중단하고 다음 날 재개한다."""


class ApiError(Exception):
    """success=false 또는 네트워크 오류. 절대 빈 결과로 흘리지 않는다."""


class Unavailable(Exception):
    """보관창 밖·상폐 등으로 그 (종목,일자)는 원천적으로 조회 불가."""


class Blocked(Exception):
    """인증 거부가 AUTH_MAX_WAIT 동안 안 풀렸다. 키/IP 설정 문제이거나 장기 차단."""


# ------------------------------------------------------------------ API

_env = C.load_env()
CID, KEY = _env["CHECK_CUST_ID"], _env["CHECK_AUTH_KEY"]
_bytes = 0
_last_ts_call = 0.0


def _is_auth_reject(msg: str) -> bool:
    """미등록 IP 접속으로 인한 일시 차단(약 20분)과 진짜 키 오류는 메시지가 같다."""
    return "auth_key" in msg or "cust_id" in msg or "access_denied" in msg


def call(apiurl: str, params: dict, timeseries: bool = False, tries: int = 4):
    """POST 호출. 반환: (results, 응답바이트).

    인증 거부(미등록 IP 차단 포함)는 즉시 포기하지 않고 AUTH_RETRY_WAIT 간격으로
    AUTH_MAX_WAIT 까지 기다렸다 재시도한다. 야간 무인 실행 중 20분 차단에 걸렸다고
    그날 한도를 통째로 날리면 안 되기 때문이다. 끝내 안 풀리면 Blocked 로 올린다.
    """
    global _bytes, _last_ts_call
    if timeseries:                       # 시계열(hist_info 등)만 초당 1회 제한이 있다
        gap = time.time() - _last_ts_call
        if gap < 1.15:
            time.sleep(1.15 - gap)
    body = urllib.parse.urlencode({"cust_id": CID, "auth_key": KEY, **params}).encode()

    net_fail, auth_waited = 0, 0
    while True:
        req = urllib.request.Request(BASE + apiurl, data=body)   # 재시도마다 새로 만든다
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read()
        except Exception as exc:                                 # 네트워크·타임아웃만 재시도
            # HTTP 502(Proxy Error)는 응답이 너무 커서 프록시가 못 넘긴 경우다. 서버는 응답을
            # 만들어 놓고 실패하므로 **우리가 못 받아도 KOSCOM 은 사용량으로 계산한다**.
            # (2026-08-03 실측: 삼성전자 5/06 을 6회 재시도했다가 우리 집계 461MB 인데 API 는
            #  1GB 초과 -- 90MB짜리 응답 x 6회 = 540MB 를 받지도 못하고 태웠다.)
            # 재시도해도 크기는 그대로라 성공 가능성이 없다 -> 한 번만 더 해보고 포기한다.
            if "502" in str(exc):
                if net_fail >= 1:
                    raise Unavailable(f"HTTP 502(응답 과대) — 재시도해도 크기는 같아 포기: {exc}")
                net_fail += 1
                print(f"    [502 Proxy Error] 응답이 커서 프록시가 실패 — 1회만 재시도 "
                      f"(재시도도 한도를 소모하므로 더는 반복하지 않습니다)", flush=True)
                time.sleep(3)
                continue
            net_fail += 1
            if net_fail >= NET_TRIES:
                raise ApiError(f"{apiurl} {params} -> {exc}")
            # 'Remote end closed connection' 은 대량 연속 호출 뒤 서버가 잠시 끊는 것이라
            # 몇 초 기다리면 대개 풀린다. 9초 만에 포기하면 그날 남은 예산을 통째로 버린다
            # (2026-08-02 실측: 838콜 시점에 끊겨 171MB 를 못 썼다). 지수 백오프로 버틴다.
            wait = min(60, 2 ** net_fail)                        # 2,4,8,16,32,60...
            print(f"    [네트워크 오류 {net_fail}/{NET_TRIES}] {str(exc)[:60]} — {wait}초 후 재시도",
                  flush=True)
            time.sleep(wait)
            continue

        _bytes += len(raw)
        if timeseries:
            _last_ts_call = time.time()
        payload = json.loads(raw)
        if payload.get("success"):
            return payload["results"], len(raw)

        msg = json.dumps(payload.get("message") or payload, ensure_ascii=False)
        if "사용량" in msg or "초과" in msg:
            raise Quota(msg)
        # "1초에 1회로 제한" -- 평소 tick_date 엔 안 걸리지만, 만료된 날짜를 연속으로 두드리면
        # 유발된다(실측 2026-07-29). 치명적 오류가 아니라 기다렸다 재개할 신호다.
        if "1초에 1회" in msg or "제한됩니다" in msg:
            net_fail += 1
            if net_fail >= tries:
                raise ApiError(f"{apiurl} {params} -> {msg}")
            time.sleep(2.0 * net_fail)
            continue
        # jcode_denied = 상폐/없는 종목 -> 확실히 영구 불가
        if "jcode_denied" in msg:
            raise Unavailable(msg)
        # 'File too large size(>= 500MB)' -- 응답 크기 상한이 500MB 임이 이 메시지로 확인됐다
        # (2026-08-07 실측, 005930/20260602). 그동안 502 로만 보이던 현상의 정체다.
        # 그 (종목,일자)는 필드를 줄이지 않는 한 영원히 못 받으므로 재시도가 무의미하다.
        # ApiError 로 올리면 job 전체가 멈춰 남은 예산이 다른 작업으로 새므로 Unavailable 로 처리한다.
        # 'File not exists' -- 그날 자료가 아직/아예 없는 경우(예: 당일 장중 조회).
        if "File too large" in msg or "File not exists" in msg:
            raise Unavailable(msg)
        # "performing Query" 는 두 상황에서 온다: (a)보관창 밖=영구불가, (b)대형주 일시 서버오류.
        # 재시도는 (b)를 흡수하려는 것인데, (a)일 때는 종목마다 9초씩 헛되이 쓰고 rate limit 까지
        # 유발한다(실측: 만료된 4/15 하루에 602콜 x 9초 = 90분 낭비). 2회로 줄이고, 호출부가
        # '날짜 단위 만료'를 판정해 나머지 종목을 아예 건너뛰게 한다.
        if "performing Query" in msg:
            net_fail += 1
            if net_fail >= 2:
                raise Unavailable(msg)
            time.sleep(1.0)
            continue
        if _is_auth_reject(msg):
            if auth_waited >= AUTH_MAX_WAIT:
                raise Blocked(f"인증 거부가 {AUTH_MAX_WAIT//60}분간 안 풀렸습니다: {msg}")
            auth_waited += AUTH_RETRY_WAIT
            print(f"  [인증 거부] {msg}\n"
                  f"    미등록 IP 접속에 의한 일시 차단(약 20분)일 수 있습니다. "
                  f"{AUTH_RETRY_WAIT//60}분 후 재시도 "
                  f"(누적 대기 {auth_waited//60}/{AUTH_MAX_WAIT//60}분)", flush=True)
            time.sleep(AUTH_RETRY_WAIT)
            continue
        raise ApiError(f"{apiurl} {params} -> {msg}")


def check_fields(rows, requested, apiurl):
    """data_list 는 없는 F-code 를 조용히 버린다 -> 요청/반환 개수를 대조한다."""
    if not rows:
        return
    missing = set(requested) - set(rows[0])
    if missing:
        raise ApiError(f"{apiurl}: data_list 요청 {len(requested)}개 중 {sorted(missing)} 미반환 "
                       "(F-code 오타 의심)")


# ------------------------------------------------------------------ MySQL

def acquire_lock(conn, name="nxt_krx_ingest"):
    """수집기 중복 실행을 막는다.

    두 프로세스가 동시에 돌면 같은 (날짜,종목) 행을 서로 잠그다 'Lock wait timeout' 으로
    죽는다(2026-08-02 실측: 수동 실행이 겹쳐 25콜 만에 중단). 21:00 스케줄러와 수동 실행이
    겹치는 상황이 실제로 생기므로 구조적으로 막는다.

    MySQL GET_LOCK 은 연결이 끊기면 자동 해제되므로 프로세스가 죽어도 잠금이 남지 않는다.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT GET_LOCK(%s, 0)", (name,))
        if not cur.fetchone()[0]:
            raise SystemExit(
                "이미 다른 수집 프로세스가 실행 중입니다. 동시에 돌리면 서로의 행을 잠가 "
                "둘 다 실패합니다(Lock wait timeout). 그 프로세스가 끝난 뒤 다시 실행하세요.")


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


RETRY_MAX = 3       # 보관창 안 일시오류를 몇 번까지 재시도할지(서버측 결손이면 영원히 성공 못 함)
DEAD_DATE_STREAK = 5  # 한 날짜에서 이만큼 연속 '조회 불가'면 그 날 전체가 만료된 것으로 본다
VERIFY_RESERVE = 15_000_000  # tick_ob 예산에서 남겨둘 검증용 몫(9필드 1콜, 대형주 여유 포함)
NET_TRIES = 7       # 네트워크 오류 재시도 횟수(지수 백오프 2~60초, 총 2분 이상 버틴다)


def _retry_count(cur, job, code, day):
    """이 (job,code,day)가 지금까지 'retry'로 기록된 횟수. n_rows 칸을 카운터로 쓴다."""
    cur.execute("SELECT status, n_rows FROM ingest_log "
                "WHERE job=%s AND code=%s AND trade_date=%s", (job, code, day))
    r = cur.fetchone()
    return int(r[1]) if r and r[0] == "retry" else 0


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


def mark_backfill(conn, sdate, edate=None):
    """[sdate, edate] 구간의 기수집(ok) 틱을 전체 재수집 대상으로 되돌린다.

    ingest_log 행만 지운다. 데이터(nxt_tick)는 그대로 두고, 재수집 시 fetch_tick 이
    (날짜,종목) 단위로 DELETE 후 재삽입하므로 중복·부분저장이 생기지 않는다.
    보관창 밖 날짜는 어차피 못 받으므로 대상에서 뺀다.

    edate 를 주면 구간을 닫는다. seq 가 있는 구간은 tick_ob(호가만 UPDATE, 절반 비용)로
    처리하는 게 낫고, seq 가 없어 검증이 불가능한 구간만 이 전체 재수집이 필요하다.
    """
    def _d(s):
        return dt.date(int(s[:4]), int(s[4:6]), int(s[6:]))

    day = _d(sdate)
    floor = tick_floor()
    if day < floor:
        print(f"[backfill] {day} 는 보관 하한({floor})보다 이전이라 재수집 불가 → {floor} 로 올립니다.")
        day = floor
    where = "job='nxt_tick' AND status='ok' AND trade_date >= %s"
    args = [day]
    if edate:
        where += " AND trade_date <= %s"
        args.append(_d(edate))
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT trade_date), MIN(trade_date), MAX(trade_date) "
                    f"FROM ingest_log WHERE {where}", args)
        n, nd, mn, mx = cur.fetchone()
        if not n:
            print(f"[backfill] {day}{'~' + str(_d(edate)) if edate else ' 이후'} 재수집 대상 없음")
            return
        cur.execute(f"DELETE FROM ingest_log WHERE {where}", args)
    conn.commit()
    print(f"[backfill] {mn}~{mx} {nd}거래일 · {n:,}콜을 전체 재수집 대상으로 되돌렸습니다.")
    print(f"           예상 {n * 1.56 / 1000:.1f}GB(9필드). 틱은 오래된 날부터 처리하므로 "
          f"이 구간이 먼저 채워집니다.")


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
    except Blocked as exc:
        # 21:00 시작 시점에 IP 차단이 걸려 있으면 여기서 먼저 걸린다. call() 이 이미
        # 최대 1시간 기다려 봤으므로, 여기까지 왔으면 단순 20분 차단이 아니다.
        print(f"[STOP] 인증 차단이 안 풀렸습니다: {exc}\n"
              f"       수집을 시작하지 않습니다. 다음 실행에서 재시도합니다.")
        return
    except ApiError as exc:
        print(f"[STOP] 유니버스 갱신 실패: {exc}\n       수집을 진행하지 않습니다(불완전 유니버스 방지).")
        return

    # 과거 검증 실패 기록이 남아 있으면 이번 실행에서도 tick_ob 를 하지 않는다.
    # (실패는 '이 한 건'이 아니라 정렬 전제 자체가 깨졌다는 신호이므로 사람이 확인해야 한다.)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM ingest_log WHERE job='ob_verify' AND status='fail'")
        n_fail = cur.fetchone()[0]
    ob_ok = n_fail == 0
    if not ob_ok:
        print(f"[daily] 이전 호가 검증 실패 {n_fail}건이 남아 있어 tick_ob 를 건너뜁니다.\n"
              f"        원인 확인 후 해소하려면: "
              f"DELETE FROM ingest_log WHERE job='ob_verify' AND status='fail';")

    # 틱 계열 두 작업(tick_ob·nxt_tick)의 순서는 '가장 먼저 만료되는 쪽'이 앞선다.
    # 둘 다 보관창 안 데이터를 다루므로 고정 순서를 두면 한쪽이 만료될 때까지 굶는다.
    # 각 작업의 가장 오래된 대상 날짜를 비교해 매 실행마다 스스로 정한다.
    tick_jobs = ["tick_ob", "nxt_tick"] if ob_ok else ["nxt_tick"]
    oldest = {}
    for j in tick_jobs:
        t = targets(conn, j)
        oldest[j] = min((row[1] for row in t), default=None)
    tick_jobs = [j for j in tick_jobs if oldest[j] is not None]
    tick_jobs.sort(key=lambda j: oldest[j])
    if len(tick_jobs) == 2:
        print(f"[daily] 만료 임박 순서: "
              + " -> ".join(f"{j}(가장 오래된 대상 {oldest[j]})" for j in tick_jobs))

    for job in tick_jobs + ["krx_min", "nxt_min"]:
        if _bytes >= budget:
            print(f"\n[예산 소진] {job} 이후 작업은 다음 실행에서 이어서 진행합니다.")
            break
        # 틱은 보관 101일이 지나면 영구 소실되고, 1분봉은 소급 제한이 없다.
        # 틱 작업이 오류로 멈췄을 때 남은 예산이 1분봉으로 새면 소멸성 자원을 그만큼 잃는다
        # (2026-08-07 실측: 틱이 1,106MB 에서 멈추자 1분봉이 나머지 3,894MB 를 가져갔다).
        # -> 틱 대상이 남아 있는 한 1분봉은 시작하지 않는다.
        if job in ("krx_min", "nxt_min"):
            tick_left = sum(len(targets(conn, j)) for j in ("tick_ob", "nxt_tick"))
            if tick_left:
                print(f"\n[보류] {job} 은 건너뜁니다 — 소멸성인 틱 작업이 {tick_left:,}콜 남아 "
                      f"있어 1분봉(소급 제한 없음)보다 우선합니다.")
                continue
        if job == "tick_ob" and not ob_ok:
            continue
        print()
        # tick_ob 은 예산에서 VERIFY_RESERVE 를 남겨두고 돌린다. 안 그러면 예산을 다 쓰고
        # break 로 빠져나가 검증이 영원히 실행되지 않는다(2026-07-30 실측: 1,080콜 보강 후
        # verify 미실행). 보강해 놓고 검증을 안 하면 안전장치가 있으나 마나다.
        job_budget = budget - VERIFY_RESERVE if job == "tick_ob" else budget
        stopped_by = run(conn, job, max(0, job_budget))
        if job == "tick_ob":
            # 보강 직후 1종목을 9필드로 되받아 전수 대조한다(약 2MB, 유보분에서 지출).
            # 호가가 엉뚱한 n 에 붙는 사고는 값이 그럴듯해 나중에 발견하기가 가장 어렵다.
            print()
            try:
                ob_ok = verify_ob(conn)
            except (Quota, Blocked, ApiError, Unavailable) as exc:
                # 검증을 '못 한 것'과 검증이 '실패한 것'은 다르다. 네트워크 끊김·한도·차단으로
                # 검증을 못 돌린 건 수집 결과와 무관하므로 실행을 죽이지 않는다.
                # (2026-08-02 실측: verify 중 RemoteDisconnected 가 프로세스를 종료시켰다.)
                print(f"[verify] 검증을 수행하지 못했습니다(수집 결과와 무관): {exc}")
                ob_ok = True
            if not ob_ok:
                print("[daily] 검증 실패가 ingest_log(job='ob_verify', status='fail')에 남았습니다.\n"
                      "        다음 실행부터 tick_ob 는 자동으로 중단됩니다. 원인 확인 전까지 재개하지 마세요.")
        # 한도(quota)·인증차단(blocked)이면 다음 job 으로 넘어가 봐야 헛호출이다.
        if stopped_by in ("quota", "blocked"):
            print(f"\n[중단] {job} 이후 작업은 다음 실행에서 이어서 진행합니다.")
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
                "WHERE u.trade_date >= %s AND (l.status IS NULL OR l.status='retry') "
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
        elif job == "tick_ob":
            # 이미 틱을 받아둔 (날짜,종목) 중 보관창 안이면서 아직 호가 보강 안 한 것.
            # 최신 날짜부터 처리한다(DESC): 전진 수집이 5/19+ 를 채우므로, 보강도 5/18 에서
            # 거꾸로 내려와야 두 구간이 이어붙어 끊김 없는 호가 포함 블록이 된다.
            # 오래된 날부터 하면 하한선과 경주하다 중간에 구멍이 남는다.
            cur.execute(
                "SELECT l.code, l.trade_date, u.market FROM ingest_log l "
                "JOIN nxt_universe u ON u.code=l.code AND u.trade_date=l.trade_date "
                "LEFT JOIN ingest_log b ON b.job='tick_ob' AND b.code=l.code "
                "                      AND b.trade_date=l.trade_date "
                "WHERE l.job='nxt_tick' AND l.status='ok' AND l.trade_date >= %s "
                "  AND b.status IS NULL "
                "ORDER BY l.trade_date DESC, l.code ASC", (tick_floor(),))
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
        seq = r.get("F16604")               # KOSCOM 원순번(같은 초 안 체결 순서). 응답 배열 순서와 일치.

        def num(k):                          # 호가·잔량은 값이 없을 수 있다(장 시작 전 등)
            v = r.get(k)
            return int(v) if v not in (None, "") else None

        recs.append((day, code, n, int(seq) if seq not in (None, "") else None,
                     ts, int(r["F15001"] or 0), qty,
                     int(side) if side not in (None, "") else None,
                     num("F14501"), num("F14531"), num("F14511"), num("F14541")))
    if recs:
        cur.execute("DELETE FROM nxt_tick WHERE trade_date=%s AND code=%s", (day, code))
        for i in range(0, len(recs), 5000):
            cur.executemany(
                "INSERT INTO nxt_tick (trade_date, code, n, seq, ts, price, qty, side, "
                "ask1, bid1, ask_qty1, bid_qty1) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", recs[i:i + 5000])
    return len(recs), nb


def fetch_ob(cur, code, day, market):
    """이미 받아둔 틱에 호가 4개만 채운다(전체 재수집 대신 UPDATE).

    행 정렬 근거: 응답 배열 순서 == 저장된 n (fetch_tick 이 enumerate 인덱스를 n 으로 쓴다).
    안전장치: 저장된 seq(F16604)와 응답의 seq 를 대조해 어긋나면 ApiError 로 중단한다.
    """
    # --- API 를 부르기 전에 거를 것들 (헛호출 방지) ---
    cur.execute("SELECT COUNT(*), SUM(ask1 IS NOT NULL), SUM(seq IS NOT NULL) "
                "FROM nxt_tick WHERE trade_date=%s AND code=%s", (day, code))
    n_rows, n_ask, n_seq = cur.fetchone()
    if not n_rows:
        raise Unavailable("nxt_tick 에 해당 (날짜,종목) 데이터가 없음")
    if n_ask:
        return 0, 0                       # 이미 호가 있음 -> 호출 없이 완료 처리
    if n_seq != n_rows:
        # seq 가 없으면 행 정렬을 검증할 방법이 없다(seq 는 2026-07-19 수집분부터 있다).
        # 검증 못 하는 UPDATE 는 하지 않는다 -- 호가가 엉뚱한 체결에 붙어도 값이 그럴듯해서
        # 나중에 발견하기가 가장 어렵다. 이 구간은 5필드로 둔다(또는 전체 재수집).
        raise Unavailable(f"seq 없는 행 {n_rows - int(n_seq or 0):,}/{n_rows:,} "
                          "— 정렬 검증 불가로 호가 보강 건너뜀(2026-07-19 이전 수집분)")

    fam = FAM_NXT[market]
    url = f"/stock/{fam}/tick_date"
    rows, nb = call(url, {"jcode": code, "edate": day.strftime("%Y%m%d"),
                          "data_list": ",".join(OB_FIELDS)})
    check_fields(rows, OB_FIELDS, url)

    cur.execute("SELECT n, seq FROM nxt_tick WHERE trade_date=%s AND code=%s", (day, code))
    stored = dict(cur.fetchall())

    def num(r, k):
        v = r.get(k)
        return int(v) if v not in (None, "") else None

    ups, unverified = [], 0
    for n, r in enumerate(rows):
        if n not in stored:               # 저장 시 걸러낸 행(예상체결·수량0)
            continue
        seq = num(r, "F16604")
        if stored[n] is None or seq is None:
            unverified += 1               # 검증 불가 -- 아래에서 전체를 거부한다
        elif stored[n] != seq:
            raise ApiError(f"{day} {code} n={n}: 일련번호 불일치(저장 {stored[n]} != 응답 {seq}). "
                           "행 정렬이 어긋났습니다 — 이 건은 전체 재수집이 필요합니다.")
        ups.append((num(r, "F14501"), num(r, "F14531"), num(r, "F14511"), num(r, "F14541"),
                    day, code, n))
    # 한 행이라도 seq 로 대조하지 못했으면 UPDATE 하지 않는다.
    # 전종목·전행 seq 대조가 이 백필의 유일한 정렬 보증이므로 예외를 두지 않는다.
    if unverified:
        raise Unavailable(f"{unverified:,}행이 seq 로 검증되지 않음(저장 또는 응답에 seq 없음) "
                          "— 호가 보강 건너뜀")
    for i in range(0, len(ups), 5000):
        cur.executemany("UPDATE nxt_tick SET ask1=%s, bid1=%s, ask_qty1=%s, bid_qty1=%s "
                        "WHERE trade_date=%s AND code=%s AND n=%s", ups[i:i + 5000])
    return len(ups), nb


def verify_ob(conn, samples=1):
    """호가 보강(tick_ob)이 올바른 n 에 붙었는지 표본 검증. 하루 1종목이면 충분하다.

    tick_ob 는 '응답 배열 순서 == 저장된 n' 을 전제로 UPDATE 한다. 이 전제가 깨지면
    호가가 엉뚱한 체결에 붙는데, 값이 그럴듯해서 나중에 발견하기가 가장 어렵다.
    그래서 9필드 전체를 다시 받아 n 으로 조인하고, 기존 5필드까지 전부 대조한다.
    (기존 5필드가 어긋나면 그건 정렬이 통째로 밀렸다는 뜻이다.)

    반환: True(합격) / False(불일치 발견 -- 호출부가 tick_ob 를 멈춘다)
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT b.code, b.trade_date, u.market FROM ingest_log b "
            "JOIN nxt_universe u ON u.code=b.code AND u.trade_date=b.trade_date "
            "LEFT JOIN ingest_log v ON v.job='ob_verify' AND v.code=b.code "
            "                      AND v.trade_date=b.trade_date "
            "WHERE b.job='tick_ob' AND b.status='ok' AND b.n_rows > 0 "   # 실제 UPDATE 한 것만
            "  AND b.trade_date >= %s AND v.status IS NULL "
            "ORDER BY b.trade_date DESC, RAND() LIMIT %s", (tick_floor(), samples))
        cands = cur.fetchall()
    if not cands:
        print("[verify] 검증 대상 없음(아직 tick_ob 로 보강한 건이 없거나 모두 검증됨)")
        return True

    all_ok = True
    for code, day, market in cands:
        url = f"/stock/{FAM_NXT[market]}/tick_date"
        try:
            rows, nb = call(url, {"jcode": code, "edate": day.strftime("%Y%m%d"),
                                  "data_list": ",".join(TICK_FIELDS)})     # 9필드 전체
        except Unavailable as exc:
            print(f"[verify] {day} {code}: 조회 불가({exc}) — 건너뜁니다")
            continue
        check_fields(rows, TICK_FIELDS, url)

        with conn.cursor() as cur:
            cur.execute("SELECT n, seq, ts, price, qty, side, ask1, bid1, ask_qty1, bid_qty1 "
                        "FROM nxt_tick WHERE trade_date=%s AND code=%s", (day, code))
            stored = {r[0]: r[1:] for r in cur.fetchall()}

        def num(r, k):
            v = r.get(k)
            return int(v) if v not in (None, "") else None

        checked = mismatch = 0
        first_bad = None
        for n, r in enumerate(rows):
            ts = int(r["F15019"] or 0)
            if ts <= 0 or ts > 23_59_59_99:      # fetch_tick 과 동일한 필터
                continue
            qty = int(r["F15020"] or 0)
            if qty <= 0:
                continue
            if n not in stored:
                continue
            want = (num(r, "F16604"), ts, int(r["F15001"] or 0), qty, num(r, "F15022"),
                    num(r, "F14501"), num(r, "F14531"), num(r, "F14511"), num(r, "F14541"))
            checked += 1
            if tuple(stored[n]) != want:
                mismatch += 1
                if first_bad is None:
                    first_bad = (n, tuple(stored[n]), want)

        status = "ok" if mismatch == 0 else "fail"
        with conn.cursor() as cur:
            log_done(cur, "ob_verify", code, day, status, checked, nb,
                     "" if not mismatch else f"불일치 {mismatch}/{checked}")
        conn.commit()

        if mismatch:
            all_ok = False
            n, got, want = first_bad
            print(f"\n{'!'*70}")
            print(f"[verify 실패] {day} {code}: {mismatch:,}/{checked:,} 행 불일치")
            print(f"  n={n}  저장값 {got}")
            print(f"           재조회 {want}")
            print(f"  (순서: seq, ts, price, qty, side, ask1, bid1, ask_qty1, bid_qty1)")
            print("  tick_ob 의 행 정렬 전제가 깨졌을 수 있습니다. 호가 보강을 중단합니다.")
            print(f"{'!'*70}\n")
        else:
            print(f"[verify] {day} {code}: {checked:,}행 전부 일치 (9필드 전수 대조) — 합격")
    return all_ok


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

    # 수집 세션에서만 fsync 부담을 낮춘다(=2: 커밋 시 로그기록, fsync 는 초당 1회).
    # 크래시 시 최대 1초치를 잃을 수 있으나, 데이터+체크포인트가 같은 트랜잭션이라 함께 롤백돼
    # 정합성은 유지되고, 재개가 그 지점부터 다시 받는다. 세션 한정이라 서버 전역 설정은 안 건드린다.
    with conn.cursor() as cur:
        try:
            cur.execute("SET SESSION innodb_flush_log_at_trx_commit=2")
        except Exception:
            pass

    COMMIT_EVERY = 25                   # 종목마다 커밋(600회 fsync)하지 않고 묶어서 커밋
    dead_dates, dead_streak = set(), {}  # 날짜 단위 만료 판정용
    t0, ok, empty, exp = time.time(), 0, 0, 0
    stopped = None                      # 'quota' | 'error' | None(완주)
    try:
        for i, (code, day, market) in enumerate(todo, 1):
            if _bytes >= budget:
                raise Quota(f"자체 예산 {budget:,}B 도달")
            # 그 날짜가 이미 만료로 판정났으면 호출하지 않고 바로 기록한다.
            # (만료된 날은 전 종목이 똑같이 실패한다. 실측: 4/15 하루에 602콜 x 9초 = 90분 낭비)
            if day in dead_dates:
                with conn.cursor() as cur:
                    log_done(cur, job, code, day, "expired", msg="날짜 단위 만료 판정(호출 생략)")
                exp += 1
                continue
            with conn.cursor() as cur:
                try:
                    if job == "nxt_tick":
                        n, nb = fetch_tick(cur, code, day, market)
                    elif job == "tick_ob":
                        n, nb = fetch_ob(cur, code, day, market)
                    elif job == "nxt_min":
                        n, nb = fetch_bar(cur, code, day, market, "NXT")
                    else:
                        n, nb = fetch_bar(cur, code, day, market, "KRX")
                except Unavailable as exc:
                    # "performing Query" 는 보관창 밖(영구불가)일 수도, 대형주 일시 서버오류일 수도 있다.
                    # 날짜가 보관창 한복판(보수적으로 95일 이내)이면 일시오류로 보고 expired 로 굳히지
                    # 않는다 -> 로그를 안 남기면 다음 실행 대상에 그대로 남아 재시도된다.
                    # 경계 근처(오래된 날)면 진짜 만료이므로 expired 로 기록해 재시도를 멈춘다.
                    # 단 서버측 데이터 결손이면 영원히 성공하지 않으므로(005930/2026-05-07 실측),
                    # 실행 단위로 RETRY_MAX 회까지만 재시도하고 그 뒤엔 expired 로 굳힌다.
                    transient = (job == "nxt_tick"
                                 and "jcode_denied" not in str(exc)
                                 and day > dt.date.today() - dt.timedelta(days=95))
                    tries_so_far = _retry_count(cur, job, code, day)
                    if transient and tries_so_far < RETRY_MAX:
                        log_done(cur, job, code, day, "retry", msg=str(exc),
                                 n_rows=tries_so_far + 1)
                        print(f"    [일시오류 재시도예정] {day} {code}: {exc} "
                              f"(보관창 안, {tries_so_far + 1}/{RETRY_MAX}회 -> 다음 실행에 재시도)",
                              flush=True)
                    else:
                        why = "" if not transient else f" (재시도 {RETRY_MAX}회 소진)"
                        log_done(cur, job, code, day, "expired", msg=str(exc) + why)
                        exp += 1
                        # 같은 날짜에서 '조회 불가'가 연달아 쌓이면 그 날은 통째로 만료된 것이다.
                        # 종목별 사정이면 이렇게 연속으로 나오지 않는다.
                        if "performing Query" in str(exc):
                            dead_streak[day] = dead_streak.get(day, 0) + 1
                            if dead_streak[day] >= DEAD_DATE_STREAK:
                                dead_dates.add(day)
                                print(f"    [날짜 만료 판정] {day}: 연속 {DEAD_DATE_STREAK}종목 "
                                      f"조회 불가 -> 이 날짜의 나머지 종목은 호출 없이 건너뜁니다.",
                                      flush=True)
                else:
                    dead_streak.pop(day, None)      # 하나라도 성공하면 연속 카운터 초기화
                    log_done(cur, job, code, day, "ok" if n else "empty", n, nb)
                    ok += 1 if n else 0
                    empty += 0 if n else 1
            if i % COMMIT_EVERY == 0:
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
    except Blocked as exc:
        stopped = "blocked"
        print(f"\n[STOP] {exc}")
        print("       확인할 것: (1) 등록 IP 밖(사내 프록시·VPN·클라우드)에서 같은 키를 쓰지 않았는지")
        print("                  (2) .env 의 CHECK_CUST_ID / CHECK_AUTH_KEY 가 맞는지")
        print("       받은 데이터는 모두 저장됐고, 다음 실행에서 이어서 진행합니다.")
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
                    "WHERE job=%s AND status='ok' AND n_bytes > 0", (job,))
        n, avg = cur.fetchone()
    return (float(avg), n) if n and n >= 300 else (None, n or 0)


def plan(conn):
    print(f"틱 보관 하한(오늘 기준) : {tick_floor()}  — 이보다 오래된 날의 체결은 API에 없습니다.\n")
    total = 0
    for job in ("tick_ob", "nxt_tick", "krx_min", "nxt_min"):
        n = len(targets(conn, job))
        avg, nsample = observed_avg(conn, job)
        src = f"실측 {nsample:,}콜" if avg else "사전추정"
        avg = avg or AVG_BYTES[job]
        gb = n * avg / 1e9
        total += gb
        print(f"  {job:9} 남은 {n:>8,}콜 x {avg/1000:>6.0f}KB({src:>12}) = {gb:>5.1f}GB "
              f"({gb:>4.1f}일치 한도)")
    print(f"  {'합계':9} {'':>44} {total:>5.1f}GB  ({total:.0f}일)")
    print("\n권장 순서: tick_ob(호가보강·만료임박) -> nxt_tick(소멸성) -> krx_min -> nxt_min")
    print("  tick_ob 는 이미 받아둔 틱에 호가 4개만 UPDATE 한다(전체 재수집 대비 약 44% 절약).")
    print("  대상은 보관창 안으로 한정돼 스스로 소진되고, 최신 날짜부터 처리해 전진 구간과 이어붙는다.")
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
    global DAILY_LIMIT
    ap = argparse.ArgumentParser(description="NXT 틱 + KRX/NXT 1분봉 -> MySQL 수집기")
    ap.add_argument("--log", metavar="DIR",
                    help="이 디렉터리에 ingest_YYYYMMDD.log 로 진행 로그를 남긴다(스케줄러용)")
    ap.add_argument("--job", choices=["tick_ob", "nxt_tick", "krx_min", "nxt_min"])
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                    help=f"이번 실행에서 받을 최대 응답 바이트 (기본 {DEFAULT_BUDGET:,}, 일 한도 {DAILY_LIMIT:,})")
    ap.add_argument("--daily-limit", type=int, default=DAILY_LIMIT,
                    help="일 한도(안내 표시용). KOSCOM 한시 상향 기간에 맞춘다.")
    ap.add_argument("--daily", action="store_true",
                    help="일일 러너: 유니버스 증분 갱신 + 우선순위대로 예산 소진까지 수집")
    ap.add_argument("--refresh-universe", action="store_true",
                    help="신규 거래일만 유니버스에 추가(수집은 안 함)")
    ap.add_argument("--backfill-to", metavar="YYYYMMDD",
                    help="--backfill-from 과 함께 구간을 닫는다(생략하면 이후 전부)")
    ap.add_argument("--backfill-from", metavar="YYYYMMDD",
                    help="이 날짜 이후 기수집(ok) 틱의 ingest_log 를 지워 재수집 대상으로 되돌린다. "
                         "필드를 추가한 뒤 과거분을 새 필드로 다시 받을 때 사용. "
                         "데이터는 재수집 시 (날짜,종목) 단위로 DELETE 후 재삽입되므로 안전하다.")
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

    DAILY_LIMIT = args.daily_limit

    conn = connect()
    # 수집·백필처럼 nxt_tick 을 쓰는 작업만 잠근다. --plan 같은 읽기 전용은 언제든 되게 둔다.
    if args.job or args.daily or args.backfill_from:
        acquire_lock(conn)
    try:
        if args.init_calendar:
            init_calendar(conn, args.sdate, args.edate)
        if args.load_universe:
            load_universe(conn, args.load_universe)
        if args.refresh_universe:
            refresh_universe(conn, args.sdate)
        if args.backfill_from:
            mark_backfill(conn, args.backfill_from, args.backfill_to)
        if args.daily:
            daily(conn, args.budget)
        if args.plan:
            plan(conn)
        if args.job:
            run(conn, args.job, args.budget)
        if not any([args.init_calendar, args.load_universe, args.refresh_universe,
                    args.backfill_from, args.daily, args.plan, args.job]):
            ap.print_help()
    except Blocked as exc:               # --daily 밖의 경로(--refresh-universe 등)에서 올라온 것
        print(f"\n[STOP] {exc}")
        print("       등록 IP 밖에서 같은 키를 쓰지 않았는지, .env 자격증명이 맞는지 확인하세요.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
