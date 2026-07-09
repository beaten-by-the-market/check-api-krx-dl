"""NXT(넥스트레이드) 일별 실거래 유니버스 추출 — 상폐 종목 포함, 시세 없음.

상세 배경·함정은 references/nxt-analysis.md 참조. 등록 IP·샌드박스 밖에서 실행.

원리
  - 유니버스: rank_invest_date(sdate=edate=D) 는 그날 '상장돼 있던' 종목을 준다(상폐 종목 포함).
  - 실거래 판별: 매도 F06505_12 또는 매수 F06507_12 > 0. (hist_info 거래량>0 과 실측 일치)
  - data_list 로 3필드만 받아 응답 바이트를 1/23 로 줄인다. 안 그러면 일 한도 1GB를 초과한다.

방어 장치 (과거 사고 재발 방지)
  1. success=false 를 빈 결과로 흘리지 않고 즉시 중단한다.
  2. 누적 수신 바이트가 BYTE_CAP 을 넘으면 스스로 멈춘다.
  3. 체크포인트를 남겨 중단 지점부터 재개한다.
  4. 완료 시 시장별 커버 거래일 수를 출력해 완전성을 검사한다.

사용
  python nxt_universe.py --probe                 # data_list 지원/한도 상태만 확인
  python nxt_universe.py                         # 전체 수집
  python nxt_universe.py --sdate 20250301 --edate 20260709 --out ./nxt.csv
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C

BASE = "https://checkapi.koscom.co.kr"
FAMS = {"m222": "NXT-KOSPI", "m223": "NXT-KOSDAQ"}
SLIM = ["F16013", "F06505_12", "F06507_12"]   # 단축코드 · 매도거래량(전체) · 매수거래량(전체)
# 주의: data_list 는 없는 F-code 를 조용히 버린다. 매수는 F06507 이며 F06506 은 존재하지 않는다.
BYTE_CAP = 700_000_000        # 일 한도 1e9 의 70%
TS_INTERVAL = 1.15            # 시계열 조회는 초당 1회 제한

_env = C.load_env()
CID, KEY = _env["CHECK_CUST_ID"], _env["CHECK_AUTH_KEY"]
_bytes = 0
_last_ts = 0.0


class Quota(Exception):
    """일 사용량 한도 또는 자체 상한 도달."""


class ApiError(Exception):
    """success=false 또는 네트워크 오류. 절대 빈 결과로 흘리지 않는다."""


def call(apiurl, params=None, timeseries=False, tries=4):
    global _bytes, _last_ts
    if timeseries:
        gap = time.time() - _last_ts
        if gap < TS_INTERVAL:
            time.sleep(TS_INTERVAL - gap)
    body = urllib.parse.urlencode({"cust_id": CID, "auth_key": KEY, **(params or {})}).encode()
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE + apiurl, data=body), timeout=180) as resp:
                raw = resp.read()
            _bytes += len(raw)
            if timeseries:
                _last_ts = time.time()
            payload = json.loads(raw)
            if payload.get("success"):
                return payload["results"]
            msg = json.dumps(payload.get("message") or payload.get("results") or payload, ensure_ascii=False)
            if "사용량" in msg or "초과" in msg:
                raise Quota(msg)
            raise ApiError(f"{apiurl} {params} -> {msg}")
        except (Quota, ApiError):
            raise
        except Exception as exc:
            if attempt == tries - 1:
                raise ApiError(f"{apiurl} {params} -> {exc}")
            time.sleep(1.5 * (attempt + 1))


def probe_data_list():
    """NXT 패밀리가 data_list 를 실제로 지원하는지 1회 호출로 판별한다."""
    rows = call("/stock/m222/rank_invest_date", {
        "criteria_code": "F06508_12", "sort_code": "0",
        "sdate": "20260708", "edate": "20260708", "data_list": ",".join(SLIM)})
    if not rows:
        raise ApiError("probe: 빈 응답")
    keys = set(rows[0])
    missing = set(SLIM) - keys              # data_list 는 없는 코드를 조용히 버린다 → 반드시 대조
    if missing:
        print(f"[probe] 경고: 요청했으나 반환되지 않은 필드 {sorted(missing)} — F-code 확인 필요")
    slim_ok = keys <= set(SLIM) | {"SDATE", "EDATE"}
    print(f"[probe] 반환 필드 {len(keys)}개: {sorted(keys)}")
    print(f"[probe] data_list {'지원 O -> 날짜별 loop(경량)' if slim_ok else '무시됨 -> 종목별 hist_info loop'}")
    return slim_ok


def trading_days(sdate, edate):
    """코스피 지수(m002) 일별정보로 거래일 달력을 만든다."""
    cal = call("/stock/m002/hist_info", {"jcode": "1", "sdate": sdate, "edate": edate}, timeseries=True)
    return sorted({str(r["F12506"]) for r in cal})


def month_spans(sdate, edate):
    y, m = int(sdate[:4]), int(sdate[4:6])
    ey, em = int(edate[:4]), int(edate[4:6])
    while (y, m) <= (ey, em):
        last = [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
        yield f"{y}{m:02d}01", f"{y}{m:02d}{last}"
        m, y = (m + 1, y) if m < 12 else (1, y + 1)


def traded(row):
    return int(row.get("F06505_12") or 0) > 0 or int(row.get("F06507_12") or 0) > 0


def _guard():
    if _bytes > BYTE_CAP:
        raise Quota(f"자체 상한 {BYTE_CAP:,}B 도달 (일 한도 1e9 보호)")


def collect_by_date(sdate, edate, done, out, ckpt):
    """A안: data_list 지원 시. 거래일 × 시장 = 약 662회, 3필드."""
    days = trading_days(sdate, edate)
    print(f"[calendar] 거래일 {len(days)}일 {days[0]}~{days[-1]}", flush=True)
    for fam, label in FAMS.items():
        for i, d in enumerate(days, 1):
            key = f"{fam}:{d}"
            if key in done:
                continue
            _guard()
            res = call(f"/stock/{fam}/rank_invest_date", {
                "criteria_code": "F06508_12", "sort_code": "0",
                "sdate": d, "edate": d, "data_list": ",".join(SLIM)})
            rows = [{"일자": d, "시장": label, "단축코드": r["F16013"]} for r in res if traded(r)]
            _save(ckpt, key, rows)
            out.extend(rows)
            if i % 50 == 0:
                print(f"  {fam} {i}/{len(days)} 누적 {len(out):,}행 {_bytes/1e6:.0f}MB", flush=True)


def collect_by_code(sdate, edate, done, out, ckpt):
    """B안: data_list 미지원 시. 월별 유니버스(합집합) + 종목별 hist_info."""
    universe = {}
    for fam in FAMS:
        codes = set()
        for sd, ed in month_spans(sdate, edate):
            _guard()
            res = call(f"/stock/{fam}/rank_invest_date",
                       {"criteria_code": "F06508_12", "sort_code": "0", "sdate": sd, "edate": ed})
            codes |= {r["F16013"] for r in res}
        universe[fam] = sorted(codes)
        print(f"[universe] {fam} {len(codes)}종목 (상폐 포함) {_bytes/1e6:.0f}MB", flush=True)
    for fam, label in FAMS.items():
        for i, jcode in enumerate(universe[fam], 1):
            key = f"{fam}:{jcode}"
            if key in done:
                continue
            _guard()
            res = call(f"/stock/{fam}/hist_info",
                       {"jcode": jcode, "sdate": sdate, "edate": edate, "data_list": "F12506,F15015"},
                       timeseries=True)
            rows = [{"일자": str(r["F12506"]), "시장": label, "단축코드": jcode}
                    for r in res if int(r["F15015"] or 0) > 0]
            _save(ckpt, key, rows)
            out.extend(rows)
            if i % 200 == 0:
                print(f"  {fam} {i}/{len(universe[fam])} 누적 {len(out):,}행 {_bytes/1e6:.0f}MB", flush=True)


def _load(ckpt):
    done, rows = set(), []
    if os.path.exists(ckpt):
        with open(ckpt, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                done.add(rec["_k"])
                rows.extend(rec["rows"])
    return done, rows


def _save(ckpt, key, rows):
    with open(ckpt, "a", encoding="utf-8") as f:
        f.write(json.dumps({"_k": key, "rows": rows}, ensure_ascii=False) + "\n")


def write_out(out, path):
    if not out:
        print("수집 행 없음")
        return
    names = {}
    try:
        for fam in FAMS:
            for r in call(f"/stock/{fam}/code_info"):
                names[r["F16013"]] = (r["F16002"], r["F34501"])
    except (Quota, ApiError) as exc:
        print(f"[warn] 종목명 조회 실패({exc}) — 이름 공란으로 진행")
    for r in out:
        name, group = names.get(r["단축코드"], ("", ""))
        r["종목명"], r["증권그룹"] = name, group
        r["현재상장여부"] = "상장" if r["단축코드"] in names else "상폐"
    out.sort(key=lambda r: (r["일자"], r["시장"], r["단축코드"]))
    cols = ["일자", "시장", "단축코드", "종목명", "증권그룹", "현재상장여부"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows({c: r[c] for c in cols} for r in out)

    counts = {}
    for r in out:
        counts[(r["일자"], r["시장"])] = counts.get((r["일자"], r["시장"]), 0) + 1
    cnt_path = path.replace(".csv", "_count.csv")
    with open(cnt_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["일자", "시장", "거래종목수"])
        for (d, m), n in sorted(counts.items()):
            writer.writerow([d, m, n])

    delisted = {r["단축코드"] for r in out if r["현재상장여부"] == "상폐"}
    print(f"\n총 {len(out):,}행 | 고유종목 {len({r['단축코드'] for r in out}):,} | 현재 상폐 {len(delisted)}")
    for label in FAMS.values():                       # 완전성 검사: 시장별 커버 거래일
        ds = sorted({r["일자"] for r in out if r["시장"] == label})
        print(f"  {label}: {len(ds)}거래일  {ds[0] if ds else '-'} ~ {ds[-1] if ds else '-'}")
    print(f"CSV: {path}\n요약: {cnt_path}")


def main():
    ap = argparse.ArgumentParser(description="NXT 일별 실거래 유니버스 추출")
    ap.add_argument("--sdate", default="20250301")
    ap.add_argument("--edate", default=time.strftime("%Y%m%d"))
    ap.add_argument("--out", default="nxt_universe_daily.csv")
    ap.add_argument("--ckpt", default="nxt_universe_ckpt.jsonl")
    ap.add_argument("--probe", action="store_true", help="data_list 지원/한도 상태만 확인")
    args = ap.parse_args()

    if args.probe:
        try:
            probe_data_list()
        except Quota as exc:
            print(f"[quota] 일 사용량 한도 소진 상태: {exc}")
        return

    t0 = time.time()
    done, out = _load(args.ckpt)
    if done:
        print(f"[resume] 체크포인트 {len(done)}건, {len(out):,}행 이어서 진행")
    try:
        collect = collect_by_date if probe_data_list() else collect_by_code
        collect(args.sdate, args.edate, done, out, args.ckpt)
        print(f"\n[done] {time.time()-t0:.0f}s, 수신 {_bytes/1e6:.0f}MB")
    except Quota as exc:
        print(f"\n[STOP] 한도/상한 도달: {exc}")
        print(f"       여기까지 {len(out):,}행. 체크포인트 저장됨 → 리셋 후 재실행하면 이어서 진행합니다.")
    except ApiError as exc:
        print(f"\n[STOP] API 오류: {exc}")
        print("       빈 응답을 '거래 0건'으로 넘기지 않고 중단했습니다.")
    write_out(out, args.out)


if __name__ == "__main__":
    main()