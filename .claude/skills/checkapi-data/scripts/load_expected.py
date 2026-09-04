"""zip 덤프에서 예상체결 시계열만 뽑아 nxt_expected 에 넣는다. API 를 쓰지 않는다.

왜 별도 스크립트인가
  load_koscom_dump.py 는 nxt_tick 을 통째로 DELETE+INSERT 한다(파일당 1~2분). 여기서 필요한
  건 chg_type=69 행의 세 칸뿐이라 nxt_tick 을 건드릴 이유가 없다. 파일당 몇 초면 끝난다.

무엇을 넣나 -- API 응답에 있는데 TICK_FIELDS 에 없어 버려지던 칸들이다.
  F30531 체결/예상체결시간, F15176 예상체결가, F15308 예상체결량(증분)
  nxt_tick 에 저장된 ts/price/qty 는 69 행에서 '직전 실체결'의 값이라 예상체결이 아니다.

검산
  같은 (일,종목)에서 exp_qty 를 다 더하면 15:40:00 개장 단일가 체결량과 원 단위로 맞는다.
  단 예상체결 갱신이 실제로 나온 종목에서만 성립한다. 거래가 적으면 갱신이 아예 없거나
  (69행 0) 수량이 전부 0으로만 오고, 그래도 15:40 에 체결은 일어난다 -- 이건 결손이 아니라
  얇은 종목의 성질이다. 그래서 69행이 없거나 exp_qty 합이 0이면 '해당없음'으로 센다.
  실측(2026-08-16): 대형주 44건 44/44 일치. 소형주 12건 중 5건이 해당없음이었고
  69행 수가 대형주 297~3,711 vs 소형주 0~35 로 자릿수가 다르다.
  전수(2026-09-04): --restored 8,886/8,886 · --missing 19,628/19,629 · --dates 1,599/1,599.
  합계 30,113/30,114. 불일치 1건은 미조사.

주의 -- zip 을 nxt_tick 에 넣었다고 여기까지 된 게 아니다
  load_koscom_dump.py 와 이 스크립트는 별개다. 2026-09-04 에 --missing 25,611건이 nxt_tick 에는
  들어갔는데 이 스크립트를 안 돌려 nxt_expected 가 06-08~08-07 을 통째로 비운 채였다.
  zip 을 적재하면 같은 폴더에 이것도 돌려야 한다.

사용
  python load_expected.py "C:/Users/Peter/Downloads/koscom_tick"      # 폴더 전체
  python load_expected.py <zip> [...]                                  # 개별 파일
  python load_expected.py <경로> --verify                              # 쓰기 없이 대조만
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I

I.C._force_utf8_stdout()

DDL = """
CREATE TABLE IF NOT EXISTS nxt_expected (
  trade_date DATE         NOT NULL,
  code       CHAR(6)      NOT NULL,
  n          INT UNSIGNED NOT NULL,
  exp_ts     INT UNSIGNED NULL,
  exp_price  INT          NULL,
  exp_qty    INT          NULL,
  PRIMARY KEY (trade_date, code, n)
) ENGINE=InnoDB
"""


def num(r, k):
    v = r.get(k)
    return int(v) if v not in (None, "") else None


def read_zip(path):
    """(day, code, recs, open_qty). recs=[(n, exp_ts, exp_price, exp_qty), ...]"""
    m = re.match(r"(m\d+)_(\d{8})_(\w+)\.zip$", os.path.basename(path))
    if not m:
        raise SystemExit(f"파일명에서 날짜·종목을 못 읽음: {path}")
    _, d8, code = m.groups()
    day = f"{d8[:4]}-{d8[4:6]}-{d8[6:]}"

    recs, open_qty = [], None
    z = zipfile.ZipFile(path)
    with z.open(z.namelist()[0]) as f:
        for n, line in enumerate(f):
            r = json.loads(line)
            if r.get("F30614") == "69":
                recs.append((day, code, n, num(r, "F30531"), num(r, "F15176"),
                             num(r, "F15308")))
            elif open_qty is None:
                ts = num(r, "F15019") or 0
                q = num(r, "F15020") or 0
                if ts >= 15_400_000 and q > 0:      # 애프터 개장 첫 실체결
                    open_qty = q
    return day, code, recs, open_qty


def main():
    ap = argparse.ArgumentParser(description="zip 덤프 -> nxt_expected")
    ap.add_argument("paths", nargs="+", help="zip 파일 또는 폴더")
    ap.add_argument("--verify", action="store_true", help="쓰지 않고 대조만")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        files.extend(sorted(glob.glob(os.path.join(p, "*.zip"))) if os.path.isdir(p) else [p])
    if not files:
        raise SystemExit("대상 zip 이 없습니다.")

    conn = I.connect()
    if not args.verify:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()

    print(f"{'파일':30} {'69행':>7} {'exp_qty 합':>11} {'개장체결':>10} {'검산':>7}")
    tot_rows = ok = bad = na = 0
    try:
        for p in files:
            day, code, recs, open_qty = read_zip(p)
            s = sum(r[5] for r in recs if r[5] is not None)
            if not recs or s == 0:
                mark, na = "해당없음", na + 1      # 갱신이 안 나온 얇은 종목
            elif open_qty is not None and s == open_qty:
                mark, ok = "O", ok + 1
            else:
                mark, bad = "X", bad + 1
            print(f"{os.path.basename(p)[:30]:30} {len(recs):>7,} {s:>11,} "
                  f"{('-' if open_qty is None else format(open_qty, ',')):>10} "
                  f"{mark:>7}")
            if args.verify or not recs:
                continue
            with conn.cursor() as cur:
                cur.execute("DELETE FROM nxt_expected WHERE trade_date=%s AND code=%s",
                            (day, code))
                for i in range(0, len(recs), 5000):
                    cur.executemany(
                        "INSERT INTO nxt_expected (trade_date, code, n, exp_ts, exp_price, "
                        "exp_qty) VALUES (%s,%s,%s,%s,%s,%s)", recs[i:i + 5000])
            conn.commit()
            tot_rows += len(recs)
    finally:
        conn.close()

    print(f"\n검산 일치 {ok}/{ok+bad}" + (f"  ·  해당없음 {na}" if na else "")
          + ("" if args.verify else f"  ·  적재 {tot_rows:,}행"))
    if bad:
        print("  불일치가 있습니다 -- 예상체결 갱신이 나왔는데 누적합이 개장 체결량과 다릅니다.")


if __name__ == "__main__":
    main()
