# -*- coding: utf-8 -*-
"""flash_lab — 히스토리컬 장중(1분봉) 데이터로 flash crash / flash 급등을 잡고 이유를 분석.

CHECK API의 과거 1분봉(`/stock/m00X/intra_date`, edate로 과거일 지정)에서 **직전 봉 대비
급격히 튄 뒤 되돌리는** 구간(flash crash=급락후반등, flash spike=급등후되돌림)을 탐지하고,
거래량 급증·지수 동반 여부·당일 공시로 원인을 분석한다.

■ 실측으로 확인한 데이터 구조 (2026-07)
- `intra_date` (1분봉): jcode + **edate(과거일 가능)**. 하루 ≈ 382봉(09:00 개장동시호가 ~ 15:30 종가).
  시간 F20004_02 = HHMMSSss (9010000=09:01, 15300000=15:30). OHLC=F20005~08_02, 분거래량 F20010_02.
- `tick_info`(체결)·`intra_info`(10초봉)은 **당일(실시간)만** → 과거 조회 불가. 히스토리컬은 intra_date.
- **거래소별 패밀리(실측)**: m001/m003=KRX(코스피/코스닥) · **m222/m223=NXT(넥스트레이드)** ·
  **m224/m225=통합(KRX+NXT)**. NXT/통합도 hoga_info·intra_date 등 동일 endpoint 세트 보유.
  단 spec 메뉴에 state=off·"NXT 활성화되면 반영" 표기가 있어 **live 데이터 반환은 장중 실측 필요**.
  flash 탐지 기본은 KRX(m001/m003)이나, NXT/통합 급변 비교로도 확장 가능(같은 종목의 거래소별 괴리).
- 지수 1분봉: `/stock/m002/intra_date`(코스피, jcode="1") · `/stock/m004/intra_date`(코스닥) → 시장 동반 판단.
- 시장 라우팅: KOSPI=m001, KOSDAQ=m003. **m001에 코스닥 코드를 넣으면 에러**(빈 결과 아님) → fam 힌트/폴백.
- 반드시 등록 IP·샌드박스 밖에서 실행.

■ flash 정의 (직전 봉 대비 튐 + 되돌림)
- flash crash = 어떤 분봉의 저가가 직전 봉 종가 대비 -thresh% 이상 급락 → 이후 rev_win분 내 rev_frac 이상 반등.
- flash spike = 고가가 직전 봉 종가 대비 +thresh% 이상 급등 → 이후 되돌림.
- 개장(첫 skip_open봉)·종가동시호가(마지막 skip_close봉)는 구조적 변동이라 제외.
- 되돌림(recover%)이 크면 '일시적(유동성/단발 대량주문)', 작으면 '지속(재료성)'으로 해석.

■ 빠른 사용
    import flash_lab as fl
    fl.flash_moves("247540", "20260703")            # 한 종목·하루 flash 이벤트
    fl.flash_scan_day("20260703", universe_top=40)  # 특정일 시장 스캔 → flash 종목
    fl.explain_flash("247540", "20260703")          # 최대 이벤트 원인분석(거래량·지수·공시)
    fl.flash_hunt("20260601","20260703", codes=[...])  # 기간 스캔(일봉 wick 사전필터→장중 확인)

CLI:  python flash_lab.py scan 20260703          (특정일 flash 종목 스캔)
      python flash_lab.py one 247540 20260703    (한 종목 분석)
"""
from __future__ import annotations
import sys, statistics as st
from news_gongsi_lab import (call, to_i, to_f, market_snapshot, TODAY_MAX)

# ---------------- 1분봉 로딩 ----------------
def _hhmm(t): return f"{t//1000000:02d}:{(t//10000)%100:02d}"

def minute_bars(jcode, date, fam=None):
    """(fam, [bar]) — bar=dict(t,hhmm,o,h,l,c,vol,amt,chg). fam 미지정 시 m001→m003 폴백."""
    fams = [fam] if fam else ["m001", "m003"]
    for fm in fams:
        try:
            rows = call(f"/stock/{fm}/intra_date", jcode=jcode, edate=date)
        except Exception:
            rows = None
        if rows:
            bars = []
            for r in rows:
                t = to_i(r.get("F20004_02")); c = to_i(r.get("F20008_02"))
                if c <= 0: continue
                bars.append(dict(t=t, hhmm=_hhmm(t), o=to_i(r.get("F20005_02")),
                    h=to_i(r.get("F20006_02")), l=to_i(r.get("F20007_02")), c=c,
                    vol=to_i(r.get("F20010_02")), amt=to_i(r.get("F20011_02")),
                    chg=to_f(r.get("F20041_02"))))
            bars.sort(key=lambda b: b["t"])
            return fm, bars
    return (fam or "m001"), []

# ---------------- flash 탐지 ----------------
def _mkev(kind, bars, i, prev, exc, recov, medvol):
    b = bars[i]
    return dict(kind=kind, time=b["hhmm"], excursion=round(exc, 2), recover=round(recov, 0),
                low=b["l"], high=b["h"], close=b["c"], prev_close=prev, vol=b["vol"],
                vol_ratio=round(b["vol"]/medvol, 1) if medvol else None, amt=b["amt"], idx=i,
                shape=("V자(일시적)" if recov >= 70 else "부분되돌림" if recov >= 30 else "지속(재료성)"))

def flash_moves(jcode, date, fam=None, thresh=4.0, rev_frac=0.5, rev_win=5,
                skip_open=3, skip_close=10, min_gap=3):
    """한 종목·하루의 flash crash/spike 이벤트 목록. 직전 봉 종가 대비 저가/고가 튐 기준."""
    fam, bars = minute_bars(jcode, date, fam)
    n = len(bars)
    if n < 20: return fam, bars, []
    c = [b["c"] for b in bars]
    vv = [b["vol"] for b in bars if b["vol"] > 0]
    medvol = st.median(vv) if vv else 0
    lo, hi = max(1, skip_open), n - skip_close
    ev = []; last = -999
    for i in range(lo, hi):
        p = c[i-1]
        if not p: continue
        exc_dn = (bars[i]["l"]-p)/p*100
        exc_up = (bars[i]["h"]-p)/p*100
        if exc_dn <= -thresh and (i-last) >= min_gap:
            trough = bars[i]["l"]; rev = max(c[i:i+rev_win+1])
            recov = (rev-trough)/(p-trough)*100 if p > trough else 0
            ev.append(_mkev("crash", bars, i, p, exc_dn, recov, medvol)); last = i
        elif exc_up >= thresh and (i-last) >= min_gap:
            peak = bars[i]["h"]; rev = min(c[i:i+rev_win+1])
            revert = (peak-rev)/(peak-p)*100 if peak > p else 0
            ev.append(_mkev("spike", bars, i, p, exc_up, revert, medvol)); last = i
    return fam, bars, ev

# ---------------- 지수(시장) 동반 여부 ----------------
_IDX_CACHE = {}
def index_series(fam, date):
    """(time_hhmm -> 지수종가) 맵. fam m001→코스피(m002 jcode=1), m003→코스닥(m004 jcode=1).
    ※ 코스닥 종합 = m004 jcode="1"(실측 868.41). jcode="2"는 다른 지수(2209)이므로 쓰지 말 것."""
    key = (fam, date)
    if key in _IDX_CACHE: return _IDX_CACHE[key]
    ifam, jcode = ("m002", "1") if fam == "m001" else ("m004", "1")  # 종합지수=1 (코스닥도 "1")
    m = {}
    try:
        for r in call(f"/stock/{ifam}/intra_date", jcode=jcode, edate=date):
            t = to_i(r.get("F20004_02")); v = to_f(r.get("F20008_02"))
            if v: m[_hhmm(t)] = v
    except Exception:
        pass
    _IDX_CACHE[key] = m
    return m

def _index_move_at(idxmap, hhmm, pre=2):
    """해당 분 기준 직전 pre분 대비 지수 등락률(%). 시장 동반 급락이면 마찬가지로 음수."""
    times = sorted(idxmap)
    if hhmm not in idxmap:
        cand = [t for t in times if t <= hhmm]
        if not cand: return None
        hhmm = cand[-1]
    j = times.index(hhmm)
    if j < pre: return None
    a, b = idxmap[times[j-pre]], idxmap[hhmm]
    return round((b-a)/a*100, 2) if a else None

# ---------------- 원인 분석 ----------------
def explain_flash(jcode, date, fam=None, event=None, thresh=4.0):
    """최대(가장 큰) flash 이벤트의 원인 태그: 거래량급증·시장동반·당일공시·되돌림형태."""
    if event is None:
        fam, bars, evs = flash_moves(jcode, date, fam, thresh=thresh)
        if not evs:
            return dict(jcode=jcode, date=date, found=False, fam=fam)
        event = max(evs, key=lambda e: abs(e["excursion"]))
    idxmap = index_series(fam, date)
    idxmove = _index_move_at(idxmap, event["time"])
    # 당일 종목 공시
    gong = []
    try:
        for g in call("/news/gongsi/gongsi_jong", jcode=jcode, sdate=date, edate=date, dcnt="50"):
            ttl = str(g.get("TITLE") or "").strip()
            tm = str(g.get("TIME") or "").strip()
            if ttl: gong.append((tm, ttl))
    except Exception:
        pass
    tags = []
    if event["vol_ratio"] and event["vol_ratio"] >= 5: tags.append(f"거래량급증({event['vol_ratio']}x)")
    if idxmove is not None and ((event["kind"]=="crash" and idxmove <= -0.3) or
                                (event["kind"]=="spike" and idxmove >= 0.3)):
        tags.append(f"시장동반(지수 {idxmove:+.2f}%)")
    else:
        tags.append(f"개별이슈(지수 {idxmove:+.2f}%)" if idxmove is not None else "지수데이터없음")
    if gong: tags.append(f"당일공시 {len(gong)}건")
    tags.append(event["shape"])
    return dict(jcode=jcode, date=date, found=True, fam=fam, event=event,
                index_move=idxmove, disclosures=gong[:8], reason_tags=tags)

# ---------------- 특정일 시장 스캔 ----------------
# 통합/NXT fam → 감지용 KRX fam (유니버스는 통합 거래대금으로 뽑되, 감지는 검증된 KRX 1분봉으로)
_KRX_OF = {"m224": "m001", "m225": "m003", "m222": "m001", "m223": "m003"}

def flash_scan_day(date, codes=None, universe_top=40, thresh=4.0, market="both",
                   worst_only=True, detect_venue="krx"):
    """특정일, 유니버스에서 flash crash/spike가 있었던 종목 스캔.
    codes=None이면 **통합 거래대금 상위**(NXT 포함, 정확)를 유니버스로. flash 감지는 기본 KRX 1분봉
    (detect_venue='unified'면 통합 1분봉으로 감지). 반환: 이벤트 있는 종목만."""
    if codes is None:
        snap = [s for s in market_snapshot(fam=market) if s.get("amt", 0) > 0]  # 통합 기본
        snap.sort(key=lambda x: -x["amt"])
        uni = [(s["code"], s["name"], s["fam"]) for s in snap[:universe_top]]
    else:
        uni = [(c, "", None) if isinstance(c, str) else c for c in codes]
    out = []
    for code, nm, fam in uni:
        dfam = fam if detect_venue == "unified" else _KRX_OF.get(fam, fam)  # 감지용 거래소
        fam, bars, evs = flash_moves(code, date, dfam, thresh=thresh)
        if not evs: continue
        if not nm:
            nm = code
        evs2 = [max(evs, key=lambda e: abs(e["excursion"]))] if worst_only else evs
        for e in evs2:
            out.append(dict(code=code, name=nm, fam=fam, **{k: e[k] for k in
                        ("kind","time","excursion","recover","vol_ratio","shape")}))
    out.sort(key=lambda x: -abs(x["excursion"]))
    return out

# ---------------- 기간 헌트 (일봉 wick 사전필터 → 장중 확인) ----------------
def daily_wick(jcode, date, fam=None):
    """일봉 아래꼬리/위꼬리 비율(%) — flash 후보 사전필터용. 장중 급락후회복은 큰 아래꼬리로 남는다."""
    from news_gongsi_lab import hist, fam_of
    fam = fam or fam_of(jcode)
    h = call(f"/stock/{fam}/hist_info", jcode=jcode, sdate=date, edate=date)
    if not h: return None
    r = h[0]
    o, hi, lo, c = to_i(r.get("F15009")), to_i(r.get("F15010")), to_i(r.get("F15011")), to_i(r.get("F15001"))
    if not c: return None
    lower = (min(o, c)-lo)/c*100      # 아래꼬리(flash crash 흔적)
    upper = (hi-max(o, c))/c*100       # 위꼬리(flash spike 흔적)
    return dict(jcode=jcode, date=date, fam=fam, lower_wick=round(lower, 2),
                upper_wick=round(upper, 2), o=o, h=hi, l=lo, c=c)

def flash_hunt(sdate, edate, codes, wick=6.0, thresh=5.0, confirm=True):
    """기간[sdate,edate] 동안 codes 중 flash 후보를 찾는다.
    1) 각 종목·각 거래일 일봉 wick으로 싸게 후보를 좁히고, 2) confirm이면 장중 1분봉으로 확정."""
    from news_gongsi_lab import trading_days, fam_of
    days = trading_days(sdate, min(edate, TODAY_MAX))
    hits = []
    for code in ([c if isinstance(c, str) else c[0] for c in codes]):
        fam = fam_of(code)
        for d in days:
            w = daily_wick(code, d, fam)
            if not w: continue
            if w["lower_wick"] >= wick or w["upper_wick"] >= wick:
                rec = dict(code=code, date=d, fam=fam,
                           lower_wick=w["lower_wick"], upper_wick=w["upper_wick"])
                if confirm:
                    _, _, evs = flash_moves(code, d, fam, thresh=thresh)
                    rec["intraday_events"] = len(evs)
                    rec["worst"] = (max(evs, key=lambda e: abs(e["excursion"]))
                                    if evs else None)
                hits.append(rec)
    hits.sort(key=lambda x: -max(x["lower_wick"], x["upper_wick"]))
    return hits

# ---------------- 포맷/CLI ----------------
def _try_utf8():
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass

def _print_scan(date, rows):
    print(f"\n■ {date} flash crash/급등 종목 스캔 ({len(rows)}건 탐지)\n")
    print(f"{'종목':13s}{'유형':>6}{'시각':>7}{'튐':>8}{'되돌림':>7}{'거래량배수':>9}  형태")
    for r in rows:
        k = "급락" if r["kind"]=="crash" else "급등"
        vr = f"{r['vol_ratio']}x" if r["vol_ratio"] else "-"
        print(f"  {r['name'][:11]:12s}{k:>6}{r['time']:>7}{r['excursion']:+7.1f}%{r['recover']:6.0f}%{vr:>9}  {r['shape']}")

def _print_one(jcode, date):
    ex = explain_flash(jcode, date)
    if not ex.get("found"):
        print(f"{jcode} {date}: flash 이벤트 없음 (fam {ex.get('fam')})"); return
    e = ex["event"]
    print(f"\n■ {jcode} {date} — 최대 flash 이벤트")
    k = "flash crash(급락후반등)" if e["kind"]=="crash" else "flash spike(급등후되돌림)"
    print(f"  {k}  {e['time']}  직전대비 {e['excursion']:+.1f}%  되돌림 {e['recover']:.0f}% ({e['shape']})")
    print(f"  저가 {e['low']:,} / 직전종가 {e['prev_close']:,} / 분거래량 {e['vol']:,} (평소 {e['vol_ratio']}배)")
    print(f"  원인 태그: {', '.join(ex['reason_tags'])}")
    if ex["disclosures"]:
        print("  당일 공시:")
        for tm, ttl in ex["disclosures"][:5]:
            print(f"    {tm} {ttl[:50]}")

if __name__ == "__main__":
    _try_utf8()
    a = sys.argv[1:]
    if a and a[0] == "scan":
        date = a[1] if len(a) > 1 else TODAY_MAX
        th = float(a[2]) if len(a) > 2 else 4.0
        _print_scan(date, flash_scan_day(date, thresh=th))
    elif a and a[0] == "one":
        _print_one(a[1], a[2] if len(a) > 2 else TODAY_MAX)
    else:
        print(__doc__)