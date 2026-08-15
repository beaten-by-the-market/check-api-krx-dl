"""zip 덤프에서 예상체결 시계열만 뽑아 nxt_expected 에 넣는다. API 를 쓰지 않는다.

왜 별도 스크립트인가
  load_koscom_dump.py 는 nxt_tick 을 통째로 DELETE+INSERT 한다(파일당 1~2분). 여기서 필요한
  건 chg_type=69 행의 세 칸뿐이라 nxt_tick 을 건드릴 이유가 없다. 파일당 몇 초면 끝난다.

무엇을 넣나 -- API 응답에 있는데 TICK_FIELDS 에 없어 버려지던 칸들이다.
  F30531 체결/예상체결시간, F15176 예상체결가, F15308 예상체결량(증분)
  nxt_tick 에 저장된 ts/price/qty 는 69 행에서 '직전 실체결'의 값이라 예상체결이 아니다.

검산
  같은 (일,종목)에서 exp_qty 를 다 더하면 15:40:00 개장 단일가 체결량과 원 단위로 맞는다.
  --verify 가 그걸 대조한다.

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

    print(f"{'파일':30} {'69행':>7} {'exp_qty 합':>11} {'개장체결':>10} {'검산':>5}")
    tot_rows = ok = bad = 0
    try:
        for p in files:
            day, code, recs, open_qty = read_zip(p)
            s = sum(r[5] for r in recs if r[5] is not None)
            hit = (open_qty is not None and s == open_qty)
            ok += hit
            bad += (not hit)
            print(f"{os.path.basename(p)[:30]:30} {len(recs):>7,} {s:>11,} "
                  f"{('-' if open_qty is None else format(open_qty, ',')):>10} "
                  f"{'O' if hit else 'X':>5}")
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

    print(f"\n검산 일치 {ok}/{ok+bad}"
          + ("" if args.verify else f"  ·  적재 {tot_rows:,}행"))
    if bad:
        print("  불일치가 있습니다 -- exp_qty 누적합이 개장 체결량과 달라진 (일,종목)입니다.")


if __name__ == "__main__":
    main()
