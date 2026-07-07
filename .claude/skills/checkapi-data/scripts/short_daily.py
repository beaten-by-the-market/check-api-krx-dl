"""공매도 데일리 브리프 재현 (EOD 배치).

사용법:
    python short_daily.py 20260703

재현(실측 검증):
- 시장별 공매도 거래대금 + 거래대금대비비중(비중1)  [m002/m004 F33095·F15023]
- 전체 공매도 거래대금 + 전일 대비                    [KOSPI+KOSDAQ 합]
- 공매도 거래대금 상위 종목                            [rank_short_date criteria=F33095]
- 공매도 거래비중 상위 종목                            [rank_short_date + F33095/F15023]
- 공매도 과열종목 지정                                 [basic_info_all F34989='Y'] (검증: 코스닥 12종목 PDF 일치)

한계:
- **투자주체별 공매도 비중: 재현 불가** — CHECK에 공매도의 투자자(외국인/기관/개인) 차원이
  아예 없다(전수 검색 확인). 외부(KRX 공매도 종합포털) 필요.
- 공매도 잔고금액 상위/총계(T-2): short_hist_info F19297를 종목별로 모아야 함(느림) → 별도.
- CHECK 공매도거래대금은 KRX 확정치 대비 ~2% 낮을 수 있음(잠정/시장조성 집계 차이).
등록 IP·샌드박스 밖에서 실행.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from _common import load_env, quote_codelist, _force_utf8_stdout

BASE_URL = "https://checkapi.koscom.co.kr"
# (라벨, 지수패밀리, 지수코드, 종목패밀리)
MARKETS = [
    {"label": "KOSPI", "idx_fam": "m002", "idx_code": "1", "stk_fam": "m001"},
    {"label": "KOSDAQ", "idx_fam": "m004", "idx_code": "1", "stk_fam": "m003"},
]


def post(apiurl: str, **params: str) -> list[dict]:
    env = load_env()
    cust_id, auth_key = env.get("CHECK_CUST_ID"), env.get("CHECK_AUTH_KEY")
    if not cust_id or not auth_key:
        raise SystemExit("CHECK_CUST_ID / CHECK_AUTH_KEY 를 .env/환경변수에서 찾지 못했습니다.")
    payload = {"cust_id": cust_id, "auth_key": auth_key, **params}
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(f"{BASE_URL}{apiurl}", data=data)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            d = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {apiurl}")
    if d.get("success") is False:
        raise RuntimeError(f"{d.get('message') or d.get('errmsg')} (등록 IP·샌드박스 밖 실행?)")
    return d.get("results", []) or []


def _n(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def resilient_port(stk_fam: str, codes: list[str]) -> list[dict]:
    """basic_info_all_port 벌크. 영숫자 코드가 무따옴표로 섞이면 코스콤 _port 버그로
    전체 실패 → 각 코드를 작은따옴표로 감싸(quote_codelist) 영숫자 종목까지 한 콜에
    정상 조회한다(실측 검증). 상세는 리포 루트 checkapi_bugreport_*.txt."""
    if not codes:
        return []
    return post(f"/stock/{stk_fam}/basic_info_all_port", codelist=quote_codelist(codes))


def name_map(stk_fam: str) -> dict:
    return {str(c.get("F16013")): (c.get("F16002") or str(c.get("F16013")))
            for c in post(f"/stock/{stk_fam}/code_info") if c.get("F16013")}


def market_short(m: dict, date: str) -> dict:
    """지수레벨 공매도 거래대금·총거래대금·비중1·전일 공매도대금."""
    start = (datetime.strptime(date, "%Y%m%d") - timedelta(days=10)).strftime("%Y%m%d")
    rows = post(f"/stock/{m['idx_fam']}/hist_info", jcode=m["idx_code"], sdate=start, edate=date)
    rows.sort(key=lambda r: str(r.get("F12506", "")), reverse=True)
    if not rows or str(rows[0].get("F12506")) != date:
        return {"label": m["label"], "missing": True}
    cur = rows[0]
    short_amt = _n(cur.get("F33095"))              # 공매도거래대금(원)
    trade_amt = _n(cur.get("F15023")) * 1_000_000  # 거래대금(백만원)->원
    prev_short = _n(rows[1].get("F33095")) if len(rows) > 1 else None
    return {
        "label": m["label"],
        "short_eok": short_amt / 1e8,
        "ratio": (short_amt / trade_amt * 100) if trade_amt else 0.0,
        "prev_short_eok": (prev_short / 1e8) if prev_short is not None else None,
    }


def top_short(m: dict, date: str, names: dict, n: int = 5) -> dict:
    """공매도 거래대금 상위 / 거래비중 상위."""
    r = post(f"/stock/{m['stk_fam']}/rank_short_date", up_code="1",
             criteria_code="F33095", sdate=date, edate=date)
    rows = [{"code": str(x.get("F16013")), "name": names.get(str(x.get("F16013")), str(x.get("F16013"))),
             "short": _n(x.get("F33095")), "trade": _n(x.get("F15023")),
             "ratio": (_n(x.get("F33095")) / _n(x.get("F15023")) * 100) if _n(x.get("F15023")) else 0.0}
            for x in r]
    by_amt = sorted(rows, key=lambda x: -x["short"])[:n]
    by_ratio = sorted([x for x in rows if x["short"] > 0], key=lambda x: -x["ratio"])[:n]
    return {"by_amt": by_amt, "by_ratio": by_ratio}


def overheated(m: dict) -> list[str]:
    """공매도 과열종목 지정(F34989='Y') 스캔. basic_info는 당일 스냅샷."""
    codes = list(name_map(m["stk_fam"]).keys())
    rows = resilient_port(m["stk_fam"], codes)
    return [r.get("F16002") or str(r.get("F16013")) for r in rows if r.get("F34989") == "Y"]


def _balance_date(stk_fam: str, date: str, ref_codes: list[str]) -> str | None:
    """공매도 잔고의 최근 보고일(≈T-2)을 참조종목 몇 개로 한 번만 확정한다."""
    start = (datetime.strptime(date, "%Y%m%d") - timedelta(days=10)).strftime("%Y%m%d")
    for c in ref_codes:
        try:
            r = post(f"/stock/{stk_fam}/short_hist_info", jcode=c, sdate=start, edate=date)
        except Exception:  # noqa: BLE001
            continue
        rows = [x for x in r if _n(x.get("F19297")) > 0]
        if rows:
            return str(max(rows, key=lambda x: str(x.get("F12506"))).get("F12506"))
    return None


def balance_section(m: dict, date: str, names: dict, retries: int = 1) -> dict:
    """[--balance] 공매도 잔고금액 총계·상위 — short_hist_info F19297 종목별 순차 합산.

    잔고는 T+2 보고라 최근 며칠은 미보고(0). 최근 보고일을 참조종목으로 한 번 확정한 뒤
    그 '단일일자'로 전 종목을 조회(창 조회보다 가벼움). 순차만(멀티스레드 금지).
    """
    codes = list(names.keys())
    bal_date = _balance_date(m["stk_fam"], date, codes[:20]) or date
    total = 0.0
    per_stock: list[tuple[str, float]] = []
    pending = codes
    for _ in range(retries + 1):
        still: list[str] = []
        for i, c in enumerate(pending, 1):
            try:
                r = post(f"/stock/{m['stk_fam']}/short_hist_info", jcode=c, sdate=bal_date, edate=bal_date)
            except Exception:  # noqa: BLE001  간헐 SSL/네트워크 오류 재시도
                still.append(c)
                continue
            if r:
                amt = _n(r[0].get("F19297"))
                if amt > 0:
                    total += amt
                    per_stock.append((c, amt))
            if i % 400 == 0:
                print(f"    [{m['label']} 잔고 {bal_date}] {i}/{len(pending)}...", file=sys.stderr, flush=True)
        pending = still
        if not pending:
            break
    top = sorted(per_stock, key=lambda x: -x[1])[:5]
    return {"bal_date": bal_date, "total_eok": total / 1e8, "covered": len(per_stock),
            "failed": len(pending), "top": [{"name": names.get(c, c), "eok": a / 1e8} for c, a in top]}


def main() -> None:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="공매도 데일리 브리프 재현")
    ap.add_argument("date")
    ap.add_argument("--balance", action="store_true",
                    help="공매도 잔고금액 총계·상위 추가(종목별 순차, ~시장당 2분)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    names = {m["label"]: name_map(m["stk_fam"]) for m in MARKETS}
    mkt = {m["label"]: market_short(m, args.date) for m in MARKETS}
    tops = {m["label"]: top_short(m, args.date, names[m["label"]]) for m in MARKETS}
    heat = {m["label"]: overheated(m) for m in MARKETS}
    bal = {m["label"]: balance_section(m, args.date, names[m["label"]]) for m in MARKETS} if args.balance else {}

    if args.json:
        print(json.dumps({"date": args.date, "market": mkt, "top": tops, "overheated": heat, "balance": bal},
                         ensure_ascii=False, indent=2))
        return

    dt = datetime.strptime(args.date, "%Y%m%d")
    total = sum(v["short_eok"] for v in mkt.values() if not v.get("missing"))
    prev_total = sum(v["prev_short_eok"] for v in mkt.values()
                     if not v.get("missing") and v.get("prev_short_eok") is not None)
    L = [f"[공매도 데일리 브리프 {dt.strftime('%Y-%m-%d')}] — CHECK API 재현", ""]
    L.append(f"▣ 핵심  전체 공매도 거래대금 {total:,.0f}억  (전일 {total - prev_total:+,.0f}억)")
    L.append(f"        공매도 과열종목: " + " / ".join(f"{k} {len(v)}건" for k, v in heat.items()))

    L.append("\n▣ 시장별 공매도 (거래대금 기준)")
    for k, v in mkt.items():
        if v.get("missing"):
            L.append(f"  {k}: 데이터 없음")
        else:
            L.append(f"  {k:<7} 공매도 {v['short_eok']:,.0f}억  (거래대금대비 {v['ratio']:.2f}%)")

    for k in names:
        t = tops[k]
        L.append(f"\n▣ {k} 공매도 거래대금 상위")
        for x in t["by_amt"]:
            L.append(f"  {x['name']:<16} {x['short']/1e6:,.0f}백만  (비중 {x['ratio']:.2f}%)")
        L.append(f"▣ {k} 공매도 거래비중 상위")
        for x in t["by_ratio"]:
            L.append(f"  {x['name']:<16} 비중 {x['ratio']:.2f}%  ({x['short']/1e6:,.0f}백만)")

    if bal:
        L.append("\n▣ 공매도 잔고금액 (T-2 최근 보고분)")
        for k, v in bal.items():
            note = f", 실패 {v['failed']}" if v.get("failed") else ""
            L.append(f"  {k} 총계 {v['total_eok']:,.0f}억  [{v['covered']}종목{note}]  상위: "
                     + ", ".join(f"{x['name']}({x['eok']:,.0f}억)" for x in v["top"]))

    L.append("\n▣ 공매도 과열종목 지정 (F34989, 당일 기준)")
    for k, v in heat.items():
        L.append(f"  {k}({len(v)}): {', '.join(v) if v else '-'}")

    L.append("")
    L.append("※ 투자주체별 공매도 비중: CHECK에 공매도의 투자자 차원 자체가 없어 재현 불가 → 외부(KRX 공매도포털).")
    L.append("※ 거래비중: CHECK 공식비중(F33097)=39.48류로 산출하나, KRX(~37%)와 총거래대금 정의차로 근사.")
    L.append("※ 공매도대금은 KRX 확정치 대비 ~2% 낮을 수 있음(잠정/시장조성 집계 차이).")
    if not bal:
        L.append("※ 공매도 잔고(총계/상위)는 --balance 로 추가(종목별 순차, ~시장당 2분).")
    print("\n".join(L))


if __name__ == "__main__":
    main()
