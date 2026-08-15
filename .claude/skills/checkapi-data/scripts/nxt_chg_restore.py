"""chg_type(F30614) 을 API 없이 복원한다. CHECK 한도를 전혀 쓰지 않는다.

왜 필요한가
  체결장에는 chg_type=69(예상체결. 실체결 아님)가 섞여 SUM(qty) 가 과대계상된다.
  ※ '기세'가 아니다. 명세 확정과 경로별 차이는 nxt_krx_ingest.py 의 F30614 주석 참조.
    이 스크립트가 다루는 API 수집분에서 69 는 '그 시점의 직전 실체결'을 그대로 복사한
    행이다 -- 그래서 언제나 같은 (일,종목)에 값이 같은 실체결 행이 따로 존재한다.
  tick_date 보관창(100일)을 지난 날짜는 F30614 를 이제 받을 수 없다
  (2026-08-13 기준 2026-04-03~05-04 의 21거래일, 12,756 (일,종목)이 이미 그렇다).
  보관창 안이라도 소급에 쓸 한도가 없다 -- 같은 용량이면 틱 자체를 받는 게 낫다.

원리
  nxt_daily(넥스트레이드 공식 거래량·거래대금)가 정답지다. 69 를 뺀 값과 원 단위까지
  일치한다(2026-08-13 전수 검증 4,497/4,497). 그래서 어느 행인지 몰라도 총량은 안다:
      69 수량 = 틱 SUM(qty)       - nxt_daily.qty
      69 금액 = 틱 SUM(price*qty) - nxt_daily.val
  69 는 CHECK API 수집분에서 예외 없이 side=3 이다(411,952행 전수). 반대로 side=3 중
  69 가 아닌 행은 2.40%(종목·하루당 평균 0.60행)뿐이다. 그래서 '69 가 아닌 쪽'을 찾는
  작은 부분합 문제가 되고, 수량·금액 두 제약이 동시에 걸린다.

  주의: 1313 화면 캡처 이관분(src=1)은 같은 '체결 아님'을 side=0 으로 표현한다.
  그쪽은 side=3 에 69 가 한 건도 없어서 이 알고리즘의 전제가 성립하지 않는다.
  다만 캡처 이관분은 chg_type 이 이미 채워져 있어 애초에 복원 대상이 아니다.
  전제가 조용히 어긋나지 않도록, src IS NOT NULL 행이 섞인 날은 명시적으로 거부한다.

  API-69 는 대부분 중복행이다. 메인마켓 마지막 체결을 15:20 마감 뒤에도 반복 재송신한
  것이라 (ts, price, qty) 가 전부 같다 -- 2026-06-08 전 종목 중복률 95.6%(16,297행 ->
  고유 713개), 005380 은 858행이 전부 15:19:59·634,000·157 하나다. 그래서 부분합을
  '행' 단위로 세면 같은 답이 수천 가지로 갈려 죄다 모호로 떨어진다. 값이 같은 행끼리
  묶어 '어느 묶음에서 몇 개를 고르나'로 세면 진짜 갈리는 경우만 모호로 남는다.

무엇을 하지 않는가
  해가 유일할 때만 확정한다. 여러 개면 아무것도 쓰지 않고 '모름'으로 남긴다.
  틀린 값을 채우는 것이 비는 것보다 훨씬 나쁘다 -- 나중에 구분이 안 된다.
  단, 값이 같아 서로 바꿔도 모든 집계가 동일한 행들 사이의 선택은 '갈린다'로 치지 않는다.
  그런 (일,종목)은 method='subsetdup' 으로 따로 남겨 언제든 되돌릴 수 있게 한다.

  검증(2026-08-13, 정답이 있는 7거래일 4,347 표본): 행 확정 97.65%, 오답 0건.
    05-04 615 / 05-06 602 / 05-07 608 / 05-08 612 / 05-11 569 / 06-05 619 / 06-08 620
    묶음 세기 도입 전에는 89.69% 였다(모호 446 -> 100). 늘어난 346 건이 전부 중복행 때문에
    갈리던 것이고, 그중 42 건은 정답과 다른 행을 골랐지만 (수량,금액)이 같아 집계는 동일하다.

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

MAXK = 6          # 이 크기까지 부분집합을 찾는다. 종목당 실제 평균은 0.7행.
CAP = 2           # 해가 2개 이상인 걸 확인하면 바로 모호 판정 -- 전부 셀 필요가 없다

# 69 가 나올 수 있는 시각 창. 이 밖의 side=3 행은 '69 아님'이 확정이라 후보에서 뺀다.
#
# 창이 없으면 확정률은 비슷한데(87% -> 90%) '조용한 오답'이 생긴다. 창 없이 돌린 첫 판에서
# 15:40 이후 행 10건이 69 로 찍혔다(006110 15:40:52 등). 일별 합계는 맞으니 검산에 안 걸리고,
# 유일해라서 모호로도 안 빠진다. 후보가 넓으면 진짜 69 가 아닌 조합이 유일해처럼 보인다.
# 창의 값어치는 커버리지가 아니라 이런 오배정을 막는 데 있다.
#
# 상한 15:40 은 구조적이다 -- 애프터마켓은 15:30~15:40 이 주문접수뿐이고 체결은 15:40 부터다.
# 그래서 15:30~15:39 에는 69 가 생기고(전체의 12.2%) 15:40 부터는 실제 체결이 된다.
# API 로 F30614 을 받은 411,952 행 중 15:40 이후 69 는 0 건이다.
#
# 하한 09:00 은 여유를 둔 값이다. 실측 최소는 14:36:15 이고 프리장(08:00~08:50)에는 69 가
# 한 건도 없지만, 하한은 날마다 크게 흔들려서(14:36~15:30) 좁게 잡을 근거가 없다.
# (5월 4거래일 69 총 75,831행 중 15:00 이전은 6행뿐이라 창을 14:30 까지 좁힐 여지는 있다.
#  다만 복원 대상기(4월)에는 정답이 없어 분포가 같다는 보장이 없으므로 넓게 둔다.)
# 접속매매 중(15:18 이전)에도 69 가 0.86% 있는데, 거래가 거의 없는 종목에서 직전 체결의
# 시각·가격·수량을 그대로 물려받은 것이다(퍼시스 2026-06-09: 하루 157주, 14:43 체결 후
# 애프터까지 체결 없음 -> 그 사이 호가 변동이 14:43 시각으로 기록).
# 이 '직전 체결 물려받기'가 API-69 중복행의 정체이고, solve 의 묶음 세기가 겨냥하는 것이다.
WIN_LO, WIN_HI = 9_000_000, 15_400_000

DDL = """
CREATE TABLE IF NOT EXISTS restore_log (
  trade_date DATE    NOT NULL,
  code       CHAR(6) NOT NULL,
  method     VARCHAR(16) NOT NULL,   -- allside3 / subset / subsetdup / qtyonly / ambiguous
  n_rows     INT     NULL,           -- 69 로 확정한 행 수
  qty69      BIGINT  NULL,           -- 그 (일,종목)의 69 거래량 (항상 정확)
  val69      BIGINT  NULL,
  done_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (trade_date, code)
) ENGINE=InnoDB
"""


class Unsearchable(Exception):
    """해를 끝까지 세지 못했다. 유일하다고 말할 수 없으므로 '모름'으로 남긴다."""


NODE_BUDGET = 300_000   # 이만큼 뒤져도 안 끝나면 포기한다(모호와 같게 취급)


def solve(rows, target_q, target_v, maxk=MAXK, cap=CAP):
    """합이 (target_q, target_v) 인 부분집합을 찾는다. 최대 cap 개까지.

    rows: [(n, qty, val), ...]  -- qty·val 이 모두 양수인 행만 넘길 것
    반환: [(frozenset(n), swappable), ...]
          swappable = 고른 행 중에 '값이 같아 서로 바꿔도 되는' 행이 있었다는 표시.

    행을 하나씩 세지 않고 (qty, val) 이 같은 행끼리 묶어 '어느 묶음에서 몇 개'로 센다.
    API-69 는 95.6%가 중복행이라(005380 2026-06-08: 858행이 전부 같은 값) 행 단위로 세면
    같은 답이 C(858,k) 가지로 갈려 전부 모호가 된다. 묶음 단위로 세면 그건 해 하나다 --
    어느 쪽을 고르든 뺄 수량·금액이 같아 모든 집계가 동일하기 때문이다.

    묶음 수는 행 수보다 훨씬 작다(16,297행 -> 713묶음). 수량 내림차순 DFS 에 접미 최대합
    가지치기를 걸면 전수 탐색이면서도 예전 쌍합 사전보다 빠르다.
    """
    if any(q <= 0 or v <= 0 for _, q, v in rows):
        raise Unsearchable      # 가지치기가 양수 전제 위에 서 있다. 깨지면 세지 않는다.

    # 목표보다 큰 행은 어떤 조합에도 못 들어간다(전부 양수라서). 미리 빼면 묶음 수가 줄어
    # 재귀 깊이도 같이 줄어든다 -- DFS 가 묶음마다 한 단계씩 내려가기 때문이다.
    rows = [r for r in rows if r[1] <= target_q and r[2] <= target_v]

    groups = {}
    for n, q, v in rows:
        groups.setdefault((q, v), []).append(n)
    for ns in groups.values():
        ns.sort()               # SQL 결과 순서는 보장이 없다. 재실행해도 같은 행이 찍히도록.
    items = sorted(groups.items(), key=lambda kv: -kv[0][0])
    keys = [k for k, _ in items]
    mem = [ns for _, ns in items]
    G = len(keys)
    if G > 700:
        raise Unsearchable      # 재귀가 묶음당 한 단계다. 파이썬 기본 한계(1000) 전에 손 뗀다.

    suf = [0] * (G + 1)         # 묶음 i 이후로 만들 수 있는 수량 상한
    for i in range(G - 1, -1, -1):
        suf[i] = suf[i + 1] + keys[i][0] * min(len(mem[i]), maxk)

    found, budget = [], [NODE_BUDGET]

    def dfs(i, k_left, tq, tv, counts):
        if tq == 0 and tv == 0:
            found.append(tuple(counts))     # 뒤 묶음은 전부 0개 -- 해 하나로 확정
            return len(found) >= cap
        if i >= G or k_left == 0 or tq < 0 or tv < 0 or tq > suf[i]:
            return False
        budget[0] -= 1
        if budget[0] <= 0:
            raise Unsearchable
        q, v = keys[i]
        for c in range(min(len(mem[i]), k_left, tq // q), -1, -1):
            counts.append(c)
            hit = dfs(i + 1, k_left - c, tq - q * c, tv - v * c, counts)
            counts.pop()
            if hit:
                return True
        return False

    dfs(0, maxk, target_q, target_v, [])

    out = []
    for counts in found:
        picked, swap = set(), False
        for i, c in enumerate(counts):
            if c:
                picked.update(mem[i][:c])   # 값이 같으니 앞에서부터 집는다(결정적)
                if c < len(mem[i]):
                    swap = True
        out.append((frozenset(picked), swap))
    return out


class CaptureDay(Exception):
    """1313 캡처 이관분(src=1)이 섞인 날. 이 알고리즘의 전제가 성립하지 않는다."""


def _sig(ns, rows):
    """행 집합을 '값의 다중집합'으로 환원한다. 중복행 사이의 선택 차이를 무시하려고 쓴다."""
    qv = {r[0]: (r[1], r[2]) for r in rows}
    return sorted(qv[n] for n in ns)


def restore_day(conn, day, write=True, check=False):
    """하루치를 복원한다. check=True 면 쓰지 않고 정답(chg_type)과 대조만 한다."""
    with conn.cursor() as cur:
        # (0) 캡처 이관분이 섞인 날은 거부한다. 그쪽 69 는 side=0 이라 아래 후보군(side=3)이
        #     통째로 헛돈다. 애초에 chg_type 이 100% 차 있어 복원할 것도 없다.
        #     write 경로는 (3)의 filled 로도 막히지만 --verify 는 안 막혀서 여기서 잡는다.
        cur.execute("SELECT EXISTS(SELECT 1 FROM nxt_tick "
                    "WHERE trade_date=%s AND src IS NOT NULL)", (day,))
        if cur.fetchone()[0]:
            raise CaptureDay(day)

        # (1) 종목별 69 총량. 틱이 완전한 (일,종목)만 대상이 된다.
        cur.execute("""
            SELECT t.code, SUM(t.qty)-d.qty, SUM(t.price*t.qty)-d.val
            FROM nxt_tick t JOIN nxt_daily d
              ON d.trade_date=t.trade_date AND d.code=t.code
            WHERE t.trade_date=%s
            GROUP BY t.code, d.qty, d.val""", (day,))
        target = {code: (int(q), int(v)) for code, q, v in cur.fetchall()}

        # (2) 후보군: 시각 창 안의 side=3. 69 는 실측상 전부 이 조건을 만족한다.
        #     창 밖 side=3 은 '69 아님'이 확정이므로 후보에서 빠진다(모호 감소).
        #     qty>0 조건은 solve 의 가지치기가 양수 전제 위에 서 있어서 필요하다. API 수집분은
        #     파서가 qty<=0 을 이미 버리므로(fetch_tick) 실제로 걸러지는 행은 없다.
        cur.execute("""SELECT code, n, qty, price*qty, chg_type FROM nxt_tick
                       WHERE trade_date=%s AND side=3 AND qty > 0
                         AND ts >= %s AND ts < %s""",
                    (day, WIN_LO, WIN_HI))
        cand = {}
        for code, n, q, v, ct in cur.fetchall():
            cand.setdefault(code, []).append((n, int(q), int(v), ct))

        # (3) 이미 chg_type 이 채워진 (일,종목). 후보군(side=3)만 봐서는 판별할 수 없다.
        #     1313 캡처 이관분(src=1)은 같은 '체결 아님'을 side=0 으로 표현해서, side=3 에는
        #     69 가 한 건도 없다. 그래서 2026-08-10 366종목이 이미 값이 있는데도 '행 미상'으로
        #     기록됐다. 행 전체를 기준으로 판단해야 한다.
        cur.execute("""SELECT code FROM nxt_tick WHERE trade_date=%s
                       GROUP BY code HAVING SUM(chg_type IS NULL)=0""", (day,))
        filled = {code for (code,) in cur.fetchall()}

    stat = {"allside3": 0, "subset": 0, "subsetdup": 0, "qtyonly": 0, "ambiguous": 0,
            "nodata": 0, "ok": 0, "okdup": 0, "bad": 0, "superseded": 0}
    updates, logs, obsolete = [], [], []
    for code, (tq, tv) in target.items():
        rows = cand.get(code, [])
        if not check and code in filled:
            # F30614 을 이미 확보한 (일,종목)은 손대지 않는다. 추정이 실측을 덮으면 안 되고,
            # restore_log 에 '행 미상'으로 남겨도 안 된다(사실과 다르다).
            #
            # 남아 있던 기록은 지운다. 복원이 '모호'로 남긴 뒤 나중에 tick_tt 로 실측이
            # 들어오는 순서가 실제로 생기는데(2026-08-14 에 290건), 그대로 두면 restore_log
            # 가 '복원기가 못 풀었다'고 계속 주장한다. 사실은 API 로 받은 값이다.
            # --reset 은 tick_tt='ok' 행을 일부러 보존하므로 거기서는 정리되지 않는다.
            obsolete.append((day, code))
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
                try:
                    sols = solve([(r[0], r[1], r[2]) for r in rows], sq - tq, sv - tv)
                except Unsearchable:
                    # 끝까지 못 셌다 = 유일하다고 말할 수 없다. 모호와 같게 취급한다.
                    method, picked = "ambiguous", None
                else:
                    if len(sols) == 1:
                        keep, swap = sols[0]
                        method = "subsetdup" if swap else "subset"
                        picked = frozenset(r[0] for r in rows) - keep
                    else:
                        method = "ambiguous" if sols else "qtyonly"
                        picked = None

        if check and picked is not None:
            if picked == truth:
                stat["ok"] += 1
            elif _sig(picked, rows) == _sig(truth, rows):
                # 행은 다르지만 값의 다중집합이 같다 -- 어느 쪽을 골라도 모든 집계가 동일하다.
                stat["okdup"] += 1
            else:
                stat["bad"] += 1
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
            if obsolete:
                cur.executemany("DELETE FROM restore_log WHERE trade_date=%s AND code=%s",
                                obsolete)
                stat["superseded"] = cur.rowcount
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
    ap.add_argument("--reset", action="store_true",
                    help="이전 복원분을 되돌린다(알고리즘을 고쳐 다시 돌릴 때). "
                         "API 로 F30614 을 받은 (일,종목)은 건드리지 않는다.")
    args = ap.parse_args()

    conn = I.connect()
    try:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()

        if args.reset:
            # 복원은 69 표시를 '추가'만 한다. 알고리즘을 바꿔 다시 돌리려면 먼저 지워야
            # 이전 판정이 남아 섞이지 않는다.
            # ingest_log 에 tick_tt='ok' 가 있는 (일,종목)은 API 실측이므로 제외한다.
            # (2026-05-04 은 가드를 넣기 전에 복원이 돌았던 날이라 이 제외가 실제로 필요하다.)
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE nxt_tick t
                      JOIN restore_log r ON r.trade_date=t.trade_date AND r.code=t.code
                       LEFT JOIN ingest_log g ON g.job='tick_tt' AND g.status='ok'
                            AND g.trade_date=t.trade_date AND g.code=t.code
                       SET t.chg_type=NULL
                     WHERE t.chg_type=69 AND g.code IS NULL""")
                n = cur.rowcount
                cur.execute("""DELETE r FROM restore_log r
                               LEFT JOIN ingest_log g ON g.job='tick_tt' AND g.status='ok'
                                    AND g.trade_date=r.trade_date AND g.code=r.code
                               WHERE g.code IS NULL""")
                m = cur.rowcount
            conn.commit()
            print(f"복원분 되돌림: nxt_tick {n:,}행 chg_type=NULL, restore_log {m:,}건 삭제")
            print("API 실측(tick_tt='ok')분은 건드리지 않았습니다.")
            return

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
            try:
                stat, _ = restore_day(conn, args.verify, write=False, check=True)
            except CaptureDay:
                print(f"[verify] {args.verify} 는 1313 캡처 이관분(src=1)입니다. 69 가 side=0 에 "
                      "실려 이 알고리즘의 전제가 성립하지 않고, chg_type 도 이미 채워져 있습니다.")
                return
            n = stat["ok"] + stat["okdup"] + stat["bad"]
            print(f"[verify] {args.verify}  확정 {n:,}  정답 {stat['ok']:,}  "
                  f"정답(중복행 치환) {stat['okdup']:,}  오답 {stat['bad']:,}")
            print(f"  방법별: 전부69 {stat['allside3']:,}  부분합 {stat['subset']:,}  "
                  f"부분합(중복) {stat['subsetdup']:,}  모호 {stat['ambiguous']:,}  "
                  f"수량만 {stat['qtyonly']:,}")
            print("  '중복행 치환'은 고른 행이 정답과 다르지만 (수량,금액)이 같아 모든 집계가 "
                  "동일한 경우입니다 -- 오답이 아닙니다.")
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

        tot = {"allside3": 0, "subset": 0, "subsetdup": 0, "ambiguous": 0,
               "qtyonly": 0, "nodata": 0}
        n_sup = 0
        n_upd, n_skip = 0, 0
        for day in days:
            try:
                stat, k = restore_day(conn, day)
            except CaptureDay:
                n_skip += 1
                print(f"{day}  건너뜀 — 1313 캡처 이관분(src=1). chg_type 이 이미 채워져 있고 "
                      "69 가 side=0 이라 복원 대상이 아닙니다.", flush=True)
                continue
            n_upd += k
            n_sup += stat.get("superseded", 0)
            for key in tot:
                tot[key] += stat.get(key, 0)
            print(f"{day}  전부69 {stat.get('allside3',0):>4}  부분합 {stat.get('subset',0):>4}  "
                  f"부분합(중복) {stat.get('subsetdup',0):>4}  "
                  f"모호 {stat.get('ambiguous',0):>4}  수량만 {stat.get('qtyonly',0):>4}  "
                  f"({k:,}행 표시)", flush=True)
        done = tot["allside3"] + tot["subset"] + tot["subsetdup"]
        n = sum(tot.values())
        print(f"\n=== {len(days) - n_skip}거래일 {n:,}개 (일,종목)"
              + (f", 캡처분 {n_skip}일 건너뜀" if n_skip else "") + " ===")
        if not n:
            print("  대상이 없습니다.")
            return
        print(f"  행 단위 확정 : {done:,} ({done/n*100:.2f}%)  -> nxt_tick 69행 {n_upd:,}건 표시")
        print(f"    그중 중복행 치환분(subsetdup): {tot['subsetdup']:,} "
              "-- 어느 행을 골라도 집계가 같은 경우")
        print(f"  수량만 확정  : {n-done:,} ({(n-done)/n*100:.2f}%)  "
              f"-> restore_log 에 qty69/val69 만 기록(행은 미상)")
        if n_sup:
            print(f"  실측으로 대체 : {n_sup:,}  -> tick_tt 로 F30614 을 받은 (일,종목). "
                  "복원 기록을 지웠다(복원 결과가 아니다)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
