"""KOSCOM 이 별도 전달한 체결 덤프를 nxt_tick 에 적재한다.

API 로 못 받은 (날짜, 종목)을 문의해 받아낸 파일용. 보관창이 지났거나 서버측 결손으로
tick_date 가 실패한 건이 여기 해당한다(실측: 005930 / 2026-05-07).

형식: JSONL — 한 줄에 API 응답 행 하나(38필드 전부). 압축(.zip) 또는 평문 모두 지원.
파일명 규칙 `{fam}_{YYYYMMDD}_{code}` 에서 날짜·종목을 읽는다(인자로 덮어쓸 수 있다).

적재 규칙은 fetch_tick 과 **정확히 동일**해야 한다. 그래야 API 로 받은 데이터와 n 체계가
일치하고, 나중에 호가 보강(tick_ob)이나 검증(verify_ob)이 같은 전제로 동작한다:
  - n = 원본 파일의 행 인덱스(0-based). 걸러낸 행의 번호는 건너뛴다.
  - 예상체결(ts<=0)·세션마커(ts>23595999)·수량0 행은 저장하지 않는다.

사용
  python load_koscom_dump.py "C:/.../m222_20260507_005930.zip"
  python load_koscom_dump.py <파일> --code 005930 --date 20260507 --dry-run
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nxt_krx_ingest as I

I.C._force_utf8_stdout()

# 파일엔 36~38필드가 다 있지만 우리는 이것만 저장한다.
# ※ TICK_FIELDS 가 늘면 아래 recs.append 와 INSERT 도 같이 늘려야 한다. 안 그러면 조용히
#   빠진다 -- F30614(등락구분)가 실제로 그랬다(2026-08-14 발견). 검증은 필드 '존재'만 보고
#   저장 여부는 안 보기 때문에 오류 없이 NULL 로 들어간다.
TICK_FIELDS = I.TICK_FIELDS


def open_rows(path):
    """JSONL 을 한 줄씩 흘려보낸다(543MB 를 메모리에 올리지 않는다)."""
    if path.lower().endswith(".zip"):
        z = zipfile.ZipFile(path)
        names = z.namelist()
        if len(names) != 1:
            raise SystemExit(f"zip 안에 파일이 {len(names)}개 — 하나만 있어야 합니다: {names}")
        fh = z.open(names[0])
    else:
        fh = open(path, "rb")
    with fh:
        for line in fh:
            line = line.strip()
            if line:
                yield line


def parse_name(path):
    # 종목코드에 영문이 섞인다(0008Z0 에스엔시스 등). \d{6} 으로 잡으면 그런 파일이
    # 조용히 '종목/날짜를 알 수 없음'으로 떨어진다. 2026-08-17 에 실제로 그랬다.
    m = re.search(r"(m\d+)_(\d{8})_([0-9A-Z]{6})", os.path.basename(path))
    if not m:
        return None, None, None
    return m.group(1), m.group(2), m.group(3)


def num(r, k):
    v = r.get(k)
    return int(v) if v not in (None, "") else None


def load_one(conn, path, day, code, fam, dry_run=False, quiet=False):
    """파일 하나를 적재한다. conn 을 재사용한다 -- 파일마다 접속하면 그게 병목이다."""
    def say(*a):
        if not quiet:
            print(*a)

    say(f"파일 {os.path.basename(path)}")
    say(f"  대상: {day} {code}" + (f"  (패밀리 {fam})" if fam else ""))

    recs, total, skipped = [], 0, 0
    t0 = time.time()
    for n, line in enumerate(open_rows(path)):
        total += 1
        r = json.loads(line)
        if n == 0:
            missing_field = set(TICK_FIELDS) - set(r)
            if missing_field:
                raise SystemExit(f"필요 필드 누락: {sorted(missing_field)}")
        ts = int(r["F15019"] or 0)
        if ts <= 0 or ts > 23_59_59_99:      # 예상체결·세션마커 — fetch_tick 과 동일
            skipped += 1
            continue
        qty = int(r["F15020"] or 0)
        if qty <= 0:
            skipped += 1
            continue
        recs.append((day, code, n, num(r, "F16604"), ts, int(r["F15001"] or 0), qty,
                     num(r, "F15022"),
                     num(r, "F14501"), num(r, "F14531"), num(r, "F14511"), num(r, "F14541"),
                     num(r, "F30614")))

    say(f"  읽음 {total:,}행 → 저장대상 {len(recs):,}행 (제외 {skipped:,}: 예상체결·마커·수량0)")
    if recs:
        seqs = [x[3] for x in recs]
        say(f"  시각 {recs[0][4]} ~ {recs[-1][4]} · seq {seqs[0]:,} ~ {seqs[-1]:,} "
            f"· 단조증가 {all(seqs[i] <= seqs[i+1] for i in range(len(seqs)-1))}")
    if dry_run:
        say("  [dry-run] 적재하지 않고 종료")
        return len(recs)

    with conn.cursor() as cur:
        cur.execute("DELETE FROM nxt_tick WHERE trade_date=%s AND code=%s", (day, code))
        for i in range(0, len(recs), 5000):
            cur.executemany(
                "INSERT INTO nxt_tick (trade_date, code, n, seq, ts, price, qty, side, "
                "ask1, bid1, ask_qty1, bid_qty1, chg_type) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", recs[i:i + 5000])
        # API 로 못 받아 retry/expired 로 남아 있던 기록을 ok 로 정정한다.
        I.log_done(cur, "nxt_tick", code, day, "ok", len(recs), 0,
                   "KOSCOM 별도 전달 덤프로 적재")
    conn.commit()
    say(f"  적재 완료: {len(recs):,}행 ({time.time()-t0:.1f}초)")
    return len(recs)


def main():
    ap = argparse.ArgumentParser(description="KOSCOM 전달 체결 덤프 -> nxt_tick 적재")
    ap.add_argument("paths", nargs="+", help="zip 파일, 폴더, 또는 목록 텍스트파일")
    ap.add_argument("--code", help="종목코드 6자리(파일명에서 못 읽을 때)")
    ap.add_argument("--date", help="거래일 YYYYMMDD(파일명에서 못 읽을 때)")
    ap.add_argument("--dry-run", action="store_true", help="적재하지 않고 검증만")
    ap.add_argument("--move-done", action="store_true",
                    help="적재에 성공한 파일을 <폴더>/done/ 으로 옮긴다. 폴더를 통째로 넘겨도 "
                         "다음 실행이 새 파일만 보게 되어, 배치가 쌓일수록 커지는 재적재를 없앤다")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            files.extend(sorted(glob.glob(os.path.join(p, "*.zip"))))
        elif p.lower().endswith(".txt"):
            with open(p, encoding="utf-8") as f:
                files.extend(x.strip() for x in f if x.strip())
        else:
            files.append(p)
    if not files:
        raise SystemExit("대상 파일이 없습니다.")

    # 접속을 한 번만 연다. 파일마다 프로세스를 띄우면 파일당 3~4초가 드는데
    # 실제 DB 작업은 0~2초다 -- 나머지가 인터프리터 기동과 접속 비용이었다.
    conn = I.connect()
    ok = fail = rows = 0
    t0 = time.time()
    try:
        for i, path in enumerate(files, 1):
            fam, d8, code = parse_name(path)
            code = args.code or code
            d8 = args.date or d8
            if not (code and d8):
                print(f"[{i}] {os.path.basename(path)} — 종목/날짜를 못 읽음. 건너뜀")
                fail += 1
                continue
            day = f"{d8[:4]}-{d8[4:6]}-{d8[6:]}"
            try:
                rows += load_one(conn, path, day, code, fam, args.dry_run,
                                 quiet=len(files) > 1)
                ok += 1
                if args.move_done and not args.dry_run:
                    dst = os.path.join(os.path.dirname(path), "done")
                    os.makedirs(dst, exist_ok=True)
                    os.replace(path, os.path.join(dst, os.path.basename(path)))
            except Exception as exc:
                print(f"[{i}] {os.path.basename(path)} 실패: {exc}")
                fail += 1
                conn.rollback()
            if len(files) > 1 and i % 200 == 0:
                el = time.time() - t0
                print(f"  {i:,}/{len(files):,}  {rows:,}행  {el:.0f}초  "
                      f"({el/i:.2f}초/파일)", flush=True)
    finally:
        conn.close()
    print(f"\n적재 {ok:,}건 · {rows:,}행 · 실패 {fail:,} · {time.time()-t0:.0f}초")


if __name__ == "__main__":
    main()