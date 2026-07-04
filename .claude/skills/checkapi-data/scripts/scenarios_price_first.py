# -*- coding: utf-8 -*-
"""scenarios_price_first — 시세에서 시작하는(price-first) 시황 스크리닝 → 공시 확인 러너.

"시세상 변동폭이 크거나 / 거래대금 변동이 크거나 / 일정기간 주목할 시황이 난" 기업을
먼저 골라내고(스크리닝), 그 종목의 공시목록을 붙여 '왜 움직였나'를 본다.
빌딩블록은 news_gongsi_lab.py. 반드시 등록 IP·샌드박스 밖에서 실행.

사용:
  python scenarios_price_first.py                 # 기본 날짜/기간(파일 상단)로 전체
  python scenarios_price_first.py --date 20260703 --sdate 20260601 --edate 20260703
  python scenarios_price_first.py --only PS7      # 특정 시나리오만 (PS1~PS7)

주의:
- rank(오늘 스냅샷)는 날짜 파라미터가 없어 PS1/PS2는 '최신 거래일'만 본다.
- 기간 시나리오(PS3~PS7)는 '현재 거래대금 상위 universe_top'을 유동성 유니버스로 삼아
  과거 기간지표를 계산한다(과거 상장폐지·신규종목은 근사적으로 빠질 수 있음).
"""
from __future__ import annotations
import argparse, json
import news_gongsi_lab as lab

# ----- 기본 설정(원하면 수정하거나 CLI로 덮어쓰기) -----
DATE = "20260703"                    # 오늘형 스크리너 기준일(표시용; rank는 최신일 사용)
SDATE, EDATE = "20260601", "20260703"  # 기간형 스크리너 구간
UNIVERSE_TOP = 150                   # 기간 스크리너 유동성 유니버스 크기
TOPN = 12                            # 시나리오별 상위 표시 종목수

def _line(): print("=" * 78)
def _disc_brief(discs, k=6):
    if not discs: return "    (기간 내 공시 없음)"
    lines = [f"      · {d['일자']} [{d['유형']}] {d['제목']}" for d in discs[:k]]
    more = "" if len(discs) <= k else f"      … 외 {len(discs)-k}건"
    return "\n".join(lines + ([more] if more else []))

# ===================== PS1 오늘 등락률 상위/하위 → 공시 =====================
def ps1(snap):
    _line(); print(f"PS1  당일 등락률 상위/하위 → 최근 공시  (기준 {DATE})"); _line()
    ws = lab.drange(DATE, pre=7, post=0)[0]
    for direction, label in [("top", "상승 상위"), ("bottom", "하락 상위")]:
        print(f"\n[{label}]")
        for x in lab.screen_today(by="등락률", top=TOPN, direction=direction, snap=snap):
            d = lab.disclosures_of(x["code"], ws, DATE)
            print(f"  {x['name']}({x['code']}/{x['fam']})  {x['ret']:+.2f}%  거래대금 {x['amt']/1e8:,.0f}억  공시 {len(d)}건")
            if d: print(_disc_brief(d, 3))

# ===================== PS2 오늘 거래대금 상위 → 공시 =====================
def ps2(snap):
    _line(); print(f"PS2  당일 거래대금 상위 → 최근 공시  (기준 {DATE})"); _line()
    ws = lab.drange(DATE, pre=7, post=0)[0]
    for x in lab.screen_today(by="거래대금", top=TOPN, direction="top", snap=snap):
        d = lab.disclosures_of(x["code"], ws, DATE)
        print(f"  {x['name']}({x['code']})  거래대금 {x['amt']/1e8:,.0f}억  {x['ret']:+.2f}%  공시 {len(d)}건")
        if d: print(_disc_brief(d, 3))

# ===================== PS3 기간 모멘텀(수익률) 상·하위 → 기간 공시 =====================
def ps3(universe):
    _line(); print(f"PS3  기간 수익률 상·하위(유니버스 {len(universe)}) → 기간 공시  ({SDATE}~{EDATE})"); _line()
    rows = []
    for u in universe:
        m = lab.period_metrics(u["code"], SDATE, EDATE, u["fam"])
        if "err" not in m: rows.append((m["기간수익률%"], u, m))
    rows.sort(key=lambda t: t[0], reverse=True)
    for tag, seq in [("수익률 상위", rows[:TOPN]), ("수익률 하위", rows[-TOPN:][::-1])]:
        print(f"\n[{tag}]")
        for r, u, m in seq:
            d = lab.disclosures_of(u["code"], SDATE, EDATE)
            print(f"  {u['name']}({u['code']})  기간 {r:+.1f}%  최대일변 {m['최대일간변동%']}%  공시 {len(d)}건")
            if d: print(_disc_brief(d, 4))

# ===================== PS4 거래대금 급증(이상거래) → 공시 =====================
def ps4(universe):
    _line(); print(f"PS4  거래대금 급증(최근5일/직전평균) → 공시  ({SDATE}~{EDATE})"); _line()
    rows = []
    for u in universe:
        r = lab.abnormal_turnover(u["code"], SDATE, EDATE, u["fam"])
        if r: rows.append((r, u))
    rows.sort(key=lambda t: t[0], reverse=True)
    for r, u in rows[:TOPN]:
        d = lab.disclosures_of(u["code"], SDATE, EDATE)
        print(f"  {u['name']}({u['code']})  거래대금배수 x{r}  공시 {len(d)}건")
        if d: print(_disc_brief(d, 4))

# ===================== PS5 변동성 급증(최대 일간 변동) → 공시 =====================
def ps5(universe):
    _line(); print(f"PS5  일간 변동성 상위(기간 최대 |등락|) → 공시  ({SDATE}~{EDATE})"); _line()
    rows = []
    for u in universe:
        m = lab.period_metrics(u["code"], SDATE, EDATE, u["fam"])
        if "err" not in m: rows.append((m["최대일간변동%"], u, m))
    rows.sort(key=lambda t: t[0], reverse=True)
    for v, u, m in rows[:TOPN]:
        d = lab.disclosures_of(u["code"], SDATE, EDATE)
        print(f"  {u['name']}({u['code']})  최대일간변동 {v}%  기간 {m['기간수익률%']:+.1f}%  공시 {len(d)}건")
        if d: print(_disc_brief(d, 4))

# ===================== PS6 신고가 돌파 종목 → 공시 =====================
def ps6(universe):
    _line(); print(f"PS6  기간 내 신고가 돌파 종목 → 공시  ({SDATE}~{EDATE})"); _line()
    hits = []
    for u in universe:
        m = lab.period_metrics(u["code"], SDATE, EDATE, u["fam"])
        if "err" not in m and m["신고가돌파"]:
            hits.append((m["기간수익률%"], u, m))
    hits.sort(key=lambda t: t[0], reverse=True)
    print(f"  신고가 돌파 {len(hits)}종목:")
    for r, u, m in hits[:TOPN]:
        d = lab.disclosures_of(u["code"], SDATE, EDATE)
        print(f"  {u['name']}({u['code']})  기간 {r:+.1f}%  공시 {len(d)}건")
        if d: print(_disc_brief(d, 3))

# ===================== PS7 기간 주목주 종합 스코어 → 공시+뉴스 =====================
def ps7():
    _line(); print(f"PS7  기간 '주목 시황' 종합 스코어 → 공시+뉴스  ({SDATE}~{EDATE})"); _line()
    for m in lab.notable_movers(SDATE, EDATE, universe_top=UNIVERSE_TOP, top=TOPN):
        print(f"\n  ★ {m['name']}({m['code']}) 주목도 {m['주목도']} | "
              f"기간 {m['기간수익률%']:+.1f}% · 최대일변 {m['최대일간변동%']}% · 거래대금 x{m['거래대금증가율']}"
              f"{' · 신고가' if m['신고가'] else ''}")
        print(_disc_brief(m["공시"], 6))

def main():
    global DATE, SDATE, EDATE, UNIVERSE_TOP, TOPN
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=DATE)
    ap.add_argument("--sdate", default=SDATE); ap.add_argument("--edate", default=EDATE)
    ap.add_argument("--universe", type=int, default=UNIVERSE_TOP)
    ap.add_argument("--topn", type=int, default=TOPN)
    ap.add_argument("--only", default=None, help="PS1~PS7 중 하나만")
    a = ap.parse_args()
    DATE, SDATE, EDATE, UNIVERSE_TOP, TOPN = a.date, a.sdate, a.edate, a.universe, a.topn
    try: import sys; sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass

    only = a.only.upper() if a.only else None
    need_today = only in (None, "PS1", "PS2")
    need_univ = only in (None, "PS3", "PS4", "PS5", "PS6")
    snap = lab.market_snapshot() if (need_today or need_univ or only in (None, "PS7")) else None
    universe = sorted(snap, key=lambda x: x["amt"], reverse=True)[:UNIVERSE_TOP] if need_univ else []

    if only in (None, "PS1"): ps1(snap)
    if only in (None, "PS2"): ps2(snap)
    if only in (None, "PS3"): ps3(universe)
    if only in (None, "PS4"): ps4(universe)
    if only in (None, "PS5"): ps5(universe)
    if only in (None, "PS6"): ps6(universe)
    if only in (None, "PS7"): ps7()

if __name__ == "__main__":
    main()
