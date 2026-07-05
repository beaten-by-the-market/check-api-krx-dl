# -*- coding: utf-8 -*-
"""comp_fundamentals_lab — 기업정보·IFRS·컨센서스(etc/comp·etc/ifrs·etc/cons)를
시세·수급·공시와 결합해 펀더멘털 분석을 돌리는 도구 모음.

CHECK API '기타-API'의 세 축을 서로/기존 하네스와 입체적으로 엮는다:
  · 기업정보 /etc/comp/*  : 기본정보·소개·주주현황·시장점유율·매출구성비
  · IFRS     /etc/ifrs/*  : 실제 재무(회계년도 전체/계정별/추이) + 실적발표일
  · 컨센서스 /etc/cons/*  : 애널리스트 추정치(생성일자별 스냅샷=리비전 히스토리 내장)

■ 실측으로 검증된 핵심 구조 (2026-07 기준)
- TERM_TYP(기간구분):  1x=별도, 3x=연결 ;  x1=누적(연간/반기/9M), x2=분기단독.
    → 애널리스트/밸류에이션 표준은 **연결 = 31(누적) / 32(분기)**. 기본값 CON='31'.
    (삼성 FY2025 영업이익: 별도 23.6조=term1, 연결 43.6조=term31 로 확인)
- YYMM = 재무년월(대상 회계기간). 12월 결산이면 202512=연간, 202503/06/09=분기말.
- 금액 단위: IFRS/컨센 금액계정은 **천원**. per-share(EPS·BPS·DPS·목표주가)는 **원**.
- 컨센서스: comp_cons(yyyymm)은 [모든 계정 × 모든 생성일자] → 수만 행(무겁다).
    한 지표의 추정 리비전만 볼 땐 **comp_cons_item(yyyymm+icode)** 가 가볍다(생성일자 시계열).
    한 지표를 여러 대상연도로 볼 땐 comp_cons_hist(icode, sdate~edate=재무년월).
- 컨센↔실제 계정코드는 체계가 다르다 → BRIDGE로 매핑(매출/영익/순익/EPS 등).
- 실적발표일(comp_perf_date)은 **미래 예정일까지** 준다 → 이벤트 캘린더로 활용.
- 반드시 등록 IP·샌드박스 밖에서 실행(_common .env 자동 로드). call/hist/invest는 news_gongsi_lab 재사용.

■ 빠른 사용
    import comp_fundamentals_lab as f
    f.earnings_surprise("005930", "202512")          # CS1 컨센 vs 실제 서프라이즈
    f.estimate_revision("005930", "202512")          # CS2 추정 리비전 + 목표주가 드리프트
    f.earnings_event_study("005930", "202512")       # CS3 발표일 전후 주가·수급 반응
    f.peer_valuation(["005930","000660"], "202512")  # CS4 피어 밸류에이션 횡단면
    f.business_profile("005930")                     # CS5 사업 프로파일(매출구성·점유율·소개)
    f.ownership("005930", "202412")                  # CS6 지분구조/유통물량
    f.fundamental_trend("005930")                    # CS7 다년 재무 트렌드
    f.revision_screen()                              # CS8 최근 추정 상향 종목 횡단면 스크리너
    f.upgraded_then_reaction()                       # CS9 최근 상향 종목 × 과거 상향시 주가반응

CLI:  python comp_fundamentals_lab.py demo            (삼성전자 전 시나리오)
      python comp_fundamentals_lab.py screen 영업이익  (추정 상향 종목 랭킹)
"""
from __future__ import annotations
import sys, datetime as dt
from news_gongsi_lab import call, to_i, to_f, hist, invest, short, pick_fam, fam_of, drange

# ---------------- TERM_TYP / 단위 상수 ----------------
SEP, CON = "1", "31"          # 별도 연간(누적) / 연결 연간(누적)
SEP_Q, CON_Q = "2", "32"      # 별도 분기단독 / 연결 분기단독

# ---------------- 컨센↔IFRS 계정 브리지 (연결 기준 핵심 지표) ----------------
# (라벨, 컨센 ITEM_CD, IFRS ITEM_CD). IFRS는 제조업(FINACC_TYP=1) 코드.
BRIDGE = [
    ("매출액",          "121000", "200000"),
    ("영업이익",        "121500", "201370"),
    ("당기순이익",      "122700", "203170"),
    ("당기순이익(지배)", "122710", "203180"),
    ("EPS(지배)",       "312000", "203380"),
]
# 밸류에이션 컨센 계정 — per-company 조회로 실제 채워지는 것만(실측 검증).
CONS_VALUATION = {
    "121500":"영업이익","121000":"매출액","122700":"당기순이익","122710":"당기순이익(지배)",
    "312000":"EPS(지배)","314000":"BPS(지배)","211550":"ROE","211500":"ROE(지배)",
    "211000":"영업이익률","211200":"순이익률","382100":"P/E","382500":"P/B","383300":"P/S",
    "331000":"EV/EBITDA","423800":"DPS(수정,보통주)","432400":"현금배당수익률","502900":"배당성향",
}
# ⚠️ 미제공(실측): 아래 계정들은 코드일람엔 있으나 comp_cons_item/hist(jcode+yyyymm+icode)로는
#   빈 결과다 — 목표주가·투자의견·참여증권사(610xxx), 추정 상/하향 브로커수(235xxx·311xxx),
#   Fwd.12M 롤링(121560·122760·312060·382160 등). 이 피드는 "회계연도 앵커 추정치"만 서빙.
#   따라서 리비전 모멘텀은 카운트가 아니라 '추정치 시계열의 변화'(생성일자)로 계산한다.
UNAVAILABLE = {"610100","610300","610500","311110","311120","235420","312060","121560","382160"}

# ---------------- 계정코드 카탈로그 (지연 캐시) ----------------
_IFRS_NAME, _CONS_NAME = {}, {}
def _load_names():
    global _IFRS_NAME, _CONS_NAME
    if not _IFRS_NAME:
        for r in call("/etc/ifrs/comp_ifrs_code"):
            ft = str(r.get("FINACC_TYP",""))
            _IFRS_NAME.setdefault((str(r.get("ITEM_CD")), ft), str(r.get("ITEM_NM_KOR","")).strip())
    if not _CONS_NAME:
        for r in call("/etc/cons/comp_cons_code"):
            _CONS_NAME[str(r.get("ITEM_CD"))] = str(r.get("ITEM_NM_KOR","")).strip()
def ifrs_name(code, finacc="1"):
    _load_names(); return _IFRS_NAME.get((str(code), str(finacc)), str(code))
def cons_name(code):
    _load_names(); return _CONS_NAME.get(str(code), str(code))

# ---------------- 기업정보 (etc/comp) ----------------
def basic(jcode):
    r = call("/etc/comp/comp_basic", jcode=jcode)
    return r[0] if r else {}
def comment(jcode):
    r = call("/etc/comp/comp_comment", jcode=jcode)
    if not r: return []
    return [str(r[0].get(f"COMMENT{i}","")).strip() for i in range(1,6) if str(r[0].get(f"COMMENT{i}","")).strip()]
def holders(jcode, yyyymm):
    return call("/etc/comp/comp_holder", jcode=jcode, yyyymm=yyyymm)
def sales_mix(jcode, yyyymm):
    return call("/etc/comp/comp_sales", jcode=jcode, yyyymm=yyyymm)
def sales_mix_hist(jcode):
    return call("/etc/comp/comp_sales_hist", jcode=jcode)
def market_share(jcode, yyyymm):
    return call("/etc/comp/comp_market", jcode=jcode, yyyymm=yyyymm)

# ---------------- IFRS (실제 재무) ----------------
def ifrs_all(jcode, yyyymm, term=CON):
    """{ITEM_CD: VAL} — 한 회계기간 전체 계정(지정 term)."""
    rows = call("/etc/ifrs/comp_ifrs", jcode=jcode, yyyymm=yyyymm)
    return {str(r["ITEM_CD"]): to_f(r["VAL"]) for r in rows if str(r.get("TERM_TYP"))==str(term)}
def ifrs_val(jcode, yyyymm, icode, term=CON):
    rows = call("/etc/ifrs/comp_ifrs_item", jcode=jcode, yyyymm=yyyymm, icode=icode)
    for r in rows:
        if str(r.get("TERM_TYP"))==str(term): return to_f(r["VAL"])
    return None
def ifrs_series(jcode, icode, sdate=None, edate=None, term=CON):
    """[(YYMM, VAL)] 오름차순 — 한 계정의 다년/다분기 실제치."""
    kw = dict(jcode=jcode, icode=icode)
    if sdate: kw["sdate"]=sdate
    if edate: kw["edate"]=edate
    rows = [r for r in call("/etc/ifrs/comp_ifrs_hist", **kw) if str(r.get("TERM_TYP"))==str(term)]
    return sorted(((str(r["YYMM"]), to_f(r["VAL"])) for r in rows), key=lambda x: x[0])
def perf_calendar(jcode, future_from=None):
    """실적발표일 이벤트. future_from(YYYYMMDD) 주면 그 이후 예정만."""
    rows = call("/etc/ifrs/comp_perf_date", jcode=jcode)
    ev = []
    for r in rows:
        ev.append(dict(yymm=str(r.get("YYMM")), term=str(r.get("TERM_TYPE")),
                       start=str(r.get("START_DT")), end=str(r.get("END_DT")),
                       actual=str(r.get("FST_PUB_DT") or ""), prelim=str(r.get("PF_DT") or "")))
    ev.sort(key=lambda e: (e["actual"] or e["prelim"] or "0", e["yymm"]))
    if future_from:
        ev = [e for e in ev if (e["actual"] or e["prelim"] or "0") >= future_from]
    return ev

# ---------------- 컨센서스 (추정치) ----------------
def cons_series(jcode, yyyymm, icode, term=CON):
    """[(CNS_DT, VAL)] 오름차순 — 한 지표의 생성일자별 추정 리비전 타임라인."""
    rows = [r for r in call("/etc/cons/comp_cons_item", jcode=jcode, yyyymm=yyyymm, icode=icode)
            if str(r.get("TERM_TYP"))==str(term)]
    return sorted(((str(r["CNS_DT"]), to_f(r["VAL"])) for r in rows), key=lambda x: x[0])
def cons_latest(jcode, yyyymm, icode, term=CON, asof=None):
    """지정 대상연도 지표의 최신 추정치 → (VAL, CNS_DT). asof(YYYYMMDD) 주면 그 이하만."""
    s = cons_series(jcode, yyyymm, icode, term)   # [(CNS_DT, VAL)]
    if asof: s = [x for x in s if x[0] <= asof]
    return (s[-1][1], s[-1][0]) if s else (None, None)
def cons_multiyear(jcode, icode, sdate, edate, term=CON):
    """[(YYMM, latest VAL)] — 한 지표를 여러 대상연도로(각 연도 최신 추정)."""
    rows = [r for r in call("/etc/cons/comp_cons_hist", jcode=jcode, icode=icode, sdate=sdate, edate=edate)
            if str(r.get("TERM_TYP"))==str(term)]
    by = {}
    for r in rows:
        ym=str(r["YYMM"]); d=str(r["CNS_DT"])
        if ym not in by or d>by[ym][0]: by[ym]=(d, to_f(r["VAL"]))
    return sorted(((ym, v[1]) for ym,v in by.items()), key=lambda x:x[0])

# ==================================================================
# CS1  어닝 서프라이즈 : 컨센서스(발표 직전) vs 실제(IFRS)
# ==================================================================
def earnings_surprise(jcode, yyyymm, term=CON):
    """발표일 직전 컨센 대비 실제 실적 서프라이즈(%). BRIDGE의 핵심 지표.
    반환: {name: dict(consensus, actual, surprise_pct, asof)}"""
    cal = perf_calendar(jcode)
    ann = min((e["actual"] for e in cal if e["yymm"]==str(yyyymm) and e["actual"]), default=None)
    asof = None
    if ann:  # 발표 전날까지의 컨센만 사용
        d = dt.datetime.strptime(ann, "%Y%m%d") - dt.timedelta(days=1)
        asof = d.strftime("%Y%m%d")
    out = {}
    for lbl, ccode, icode in BRIDGE:
        cval, cdt = cons_latest(jcode, yyyymm, ccode, term, asof=asof)
        aval = ifrs_val(jcode, yyyymm, icode, term)
        sur = ((aval - cval)/abs(cval)*100) if (cval not in (None,0) and aval is not None) else None
        out[lbl] = dict(consensus=cval, actual=aval, surprise_pct=sur, asof=cdt, announce=ann)
    return out

# ==================================================================
# CS2  추정 리비전 모멘텀 : 컨센 생성일자 시계열 + 목표주가 드리프트
# ==================================================================
def estimate_revision(jcode, yyyymm, icode="121500", term=CON, tail=8):
    """지정 지표의 추정 리비전 모멘텀 — 컨센 생성일자 시계열의 변화로 계산.
    (목표주가/투자의견/상하향 카운트는 이 피드 미제공 → 추정치 자체의 표류로 대체.)
    스냅샷은 영업일 단위 ≈ 5일=1주, 21일=1개월, 63일=3개월."""
    s = cons_series(jcode, yyyymm, icode, term)   # [(CNS_DT, VAL)]
    def chg_over(n):
        if len(s) < 2: return None
        a = s[max(0, len(s)-1-n)]; b = s[-1]
        return dict(from_=a, to=b, pct=((b[1]-a[1])/abs(a[1])*100 if a[1] else None))
    return dict(metric=cons_name(icode), n_snap=len(s), series_tail=s[-tail:],
                rev_1w=chg_over(5), rev_1m=chg_over(21), rev_3m=chg_over(63),
                overall=chg_over(len(s)))

# ==================================================================
# CS3  실적발표 이벤트 스터디 : perf_date + 시세 + 수급 (+서프라이즈 연계)
# ==================================================================
def earnings_event_study(jcode, yyyymm, term=CON, pre=10, post=10):
    """발표일(perf_date) 전후 주가/거래량/외국인·기관 순매수 반응 + 서프라이즈."""
    cal = perf_calendar(jcode)
    ann = next((e["actual"] for e in cal if e["yymm"]==str(yyyymm) and e["actual"]), None)
    if not ann: return dict(error=f"{yyyymm} 실적발표일 없음")
    s, e = drange(ann, pre=pre*2, post=post*2)   # 거래일 여유 위해 달력일 넉넉히
    fam, H = pick_fam(jcode, s, e)
    H = sorted(H, key=lambda r: str(r.get("F12506")))     # 입회일
    days = [str(r.get("F12506")) for r in H]
    # 발표일 이상 첫 거래일 = D0
    d0 = next((d for d in days if d >= ann), days[-1] if days else ann)
    i0 = days.index(d0) if d0 in days else len(days)-1
    I = {str(r.get("F12506")): r for r in invest(jcode, s, e, fam)}
    def px(r):  return to_f(r.get("F15001"))            # 현재가(종가)
    def ret(a,b): return ((px(b)-px(a))/px(a)*100) if px(a) else None
    win = H[max(0,i0-pre):i0+post+1]
    d0row = H[i0] if i0 < len(H) else None
    def fnet(code, sub):  # 순매수(주) 합
        return sum(to_i(I.get(d,{}).get(f"F06508_{code}",0)) for d in sub)
    after = [str(r.get("F12506")) for r in H[i0:i0+post+1]]
    before= [str(r.get("F12506")) for r in H[max(0,i0-pre):i0]]
    sur = earnings_surprise(jcode, yyyymm, term)
    return dict(announce=ann, d0=d0, fam=fam,
        surprise={k:v["surprise_pct"] for k,v in sur.items()},
        ret_pre = ret(win[0], H[i0]) if win and d0row else None,
        ret_post= ret(H[i0], win[-1]) if win and d0row else None,
        d0_return = to_f(d0row.get("F15004")) if d0row else None,   # 등락율
        foreign_net_after = fnet("11", after), inst_net_after = fnet("08", after),
        foreign_net_before= fnet("11", before), inst_net_before= fnet("08", before),
        window=[(str(r.get("F12506")), to_f(r.get("F15004"))) for r in win])

# ==================================================================
# CS4  피어 밸류에이션 횡단면 : comp_basic 업종 + 컨센 멀티플 + 실제 재무
# ==================================================================
def valuation(jcode, yyyymm, term=CON):
    """한 종목의 컨센 밸류에이션 스냅샷(최신 추정).
    ※ 단위: PER/PBR/PSR/EV_EBITDA=배수(unit8), 배당수익률=%(unit6),
       ROE/OPM/NPM/배당성향=소수분수(unit7)→ ×100해 %로 반환."""
    b = basic(jcode)
    def cl(code): return cons_latest(jcode, yyyymm, code, term)[0]
    def clp(code):                       # unit7 비율 → %
        v = cl(code); return v*100 if v is not None else None
    return dict(jcode=jcode, name=str(b.get("CMP_NM_KOR","")), wics=str(b.get("WICS","")),
                group=str(b.get("GRP_CD","")),
                per=cl("382100"), pbr=cl("382500"), psr=cl("383300"),
                roe=clp("211550"), opm=clp("211000"), npm=clp("211200"), payout=clp("502900"),
                ev_ebitda=cl("331000"), div_yield=cl("432400"), bps=cl("314000"),
                op=cl("121500"), ni=cl("122700"), eps=cl("312000"))
def peer_valuation(jcodes, yyyymm, term=CON):
    """여러 종목 밸류에이션 횡단면 표(딕셔너리 리스트)."""
    return [valuation(j, yyyymm, term) for j in jcodes]

# ==================================================================
# CS5  사업 프로파일 : 매출구성비 + 시장점유율 + 기업소개
# ==================================================================
def business_profile(jcode, yyyymm=None):
    b = basic(jcode)
    if not yyyymm:  # 기본: 최근 결산연월 추정(결산월 기준 직전 연말)
        fye = to_i(b.get("FYE_MN",12)) or 12
        y = dt.date.today().year - 1
        yyyymm = f"{y}{fye:02d}"
    mix = [(str(r.get("AC_MAIN_PRODUCT","")).strip(), to_f(r.get("AC_SALES_RATIO"))) for r in sales_mix(jcode, yyyymm)]
    mkt = [(str(r.get("AD_PROD_NAME","")).strip(), str(r.get("AD_COMP_NAME","")).strip(), to_f(r.get("AD_OCCU_RATIO"))) for r in market_share(jcode, yyyymm)]
    return dict(jcode=jcode, name=str(b.get("CMP_NM_KOR","")), yyyymm=yyyymm,
                ceo=str(b.get("CEO","")), listed=str(b.get("LIST_DT","")), wics=str(b.get("WICS","")),
                comment=comment(jcode),
                sales_mix=sorted(mix, key=lambda x:-x[1]),
                market_share=sorted(mkt, key=lambda x:-x[2]))

# ==================================================================
# CS6  지분구조 / 유통물량 : 주주현황 + 시세(시총·거래량)
# ==================================================================
def ownership(jcode, yyyymm):
    """주주현황 → 지배주주(대주주 1인 총계) 블록 지분 + 개별 주주 + 추정 유통비율.
    ※ 실제 키는 BB_COMM_RATE(언더스코어). 'BB_SEQ=1/대주주 1인 총계'는 소계행이라
       개별 합산하면 이중계상 → 총계행을 지배지분으로 쓰고 개별은 따로 나열."""
    hs = holders(jcode, yyyymm)
    rows = [dict(seq=to_i(r.get("BB_SEQ")), name=str(r.get("BB_NAME","")).strip(),
                 rel=str(r.get("BB_RELATION","")).strip(), gubn=str(r.get("BB_GUBN","")).strip(),
                 shares=to_i(r.get("BB_COMM")), pct=to_f(r.get("BB_COMM_RATE")),
                 pref=to_i(r.get("BB_PREF")), pref_pct=to_f(r.get("BB_PREF_RATE"))) for r in hs]
    block = next((r for r in rows if ("총계" in r["rel"]) or r["gubn"]=="10"), None)
    control = block["pct"] if block else sum(r["pct"] for r in rows)
    indiv = sorted((r for r in rows if r is not block), key=lambda x:-x["pct"])
    return dict(jcode=jcode, yyyymm=yyyymm, control_block=block,
                control_pct=round(control,2), est_float_pct=round(max(0.0,100-control),2),
                holders=indiv[:15])

# ==================================================================
# CS7  다년 재무 트렌드 : IFRS_hist 핵심 지표 + 컨센 향후추정 결합
# ==================================================================
def fundamental_trend(jcode, sdate="202012", edate="202512", term=CON, fwd_edate="202812"):
    """실제(과거)+컨센(향후) 매출/영익/순익 트렌드 + 마진 추이."""
    def ser(icode): return dict(ifrs_series(jcode, icode, sdate, edate, term))
    rev = ser("200000"); op = ser("201370"); ni = ser("203170")
    yms = sorted(set(rev)|set(op)|set(ni))
    hist_rows = []
    for ym in yms:
        r=rev.get(ym); o=op.get(ym); n=ni.get(ym)
        hist_rows.append(dict(yymm=ym, revenue=r, op=o, ni=n,
            opm=(o/r*100 if r and o is not None else None)))
    # 컨센 향후 추정(연간).  ※ 원거리 추정은 이 피드에서 신뢰도 낮음(값 팽창) →
    #   직전 실제치 대비 0.3~3.0배 sanity gate를 통과한 연도만 채택하고 나머지는 dropped로 표기.
    last_rev = next((r["revenue"] for r in reversed(hist_rows) if r["revenue"]), None)
    last_op  = next((r["op"] for r in reversed(hist_rows) if r["op"]), None)
    fwd_rev = dict(cons_multiyear(jcode, "121000", edate, fwd_edate, term))
    fwd_op  = dict(cons_multiyear(jcode, "121500", edate, fwd_edate, term))
    fwd_rows=[]; dropped=[]
    for ym in sorted(set(fwd_rev)|set(fwd_op)):
        if ym <= edate or ym > fwd_edate: continue
        r=fwd_rev.get(ym); o=fwd_op.get(ym)
        sane = ((last_rev is None or r is None or 0.3 <= r/last_rev <= 3.0) and
                (last_op  is None or o is None or 0.3 <= o/last_op  <= 3.0))
        row = dict(yymm=ym, revenue_est=r, op_est=o, opm=(o/r*100 if r and o else None))
        (fwd_rows if sane else dropped).append(row)
    return dict(jcode=jcode, actual=hist_rows, forecast=fwd_rows, forecast_dropped=dropped)

# ==================================================================
# CS8  추정 상향 스크리너 (횡단면) : 유니버스 전체의 컨센 리비전 랭킹
# ==================================================================
def revision_screen(universe=None, yyyymm=None, icode="121500", term=CON,
                    window=21, top=20, min_snap=25, universe_top=60):
    """'최근 추정치 상향된 종목' 찾기 — 유니버스 각 종목의 당해 예측연도 컨센(icode)
    최근 window(영업일) 리비전%를 계산해 상위 랭킹.
    ※ 이 피드는 원거리 컨센 '절대레벨'은 부정확하나 '1개월 상대 리비전'은 안정적(실측).
       → 상향/하향 판별에는 유효. 저베이스(추정≈0, 턴어라운드)는 %가 튀므로 turnaround 플래그.
    universe=None이면 시총 상위(KOSPI+KOSDAQ) universe_top개 자동 사용(등록 IP 필요).
    반환: [dict(code,name,rev_pct,rev_1w,base_조,last_조,n,turnaround)] 리비전 내림차순."""
    from news_gongsi_lab import market_snapshot
    if yyyymm is None:
        yyyymm = f"{dt.date.today().year}12"          # 당해 예측연도(FY current)
    if universe is None:
        snap = [s for s in market_snapshot(fam="both") if s.get("mktcap",0)>0]
        snap.sort(key=lambda x:-x["mktcap"])
        universe = [(s["code"], s["name"]) for s in snap[:universe_top]]
    else:
        universe = [(u, "") if isinstance(u,str) else u for u in universe]
    out = []
    for code, nm in universe:
        try:
            ser = cons_series(code, yyyymm, icode, term)   # [(CNS_DT,VAL)]
        except Exception:
            continue
        if len(ser) < min_snap:
            continue
        last = ser[-1]; base = ser[max(0, len(ser)-1-window)]; wk = ser[max(0, len(ser)-6)]
        rev  = ((last[1]-base[1])/abs(base[1])*100) if base[1] else None
        rev1w= ((last[1]-wk[1])/abs(wk[1])*100) if wk[1] else None
        if rev is None: continue
        if not nm:
            nm = str(basic(code).get("CMP_NM_KOR", code))
        # 마지막으로 '유의미하게 상향'된 날(직전값 대비 +0.3% 초과 스텝) + 경과일수
        lastup=None
        for i in range(1, len(ser)):
            p0=ser[i-1][1]
            if p0 and (ser[i][1]-p0)/abs(p0) > 0.003: lastup=ser[i][0]
        dsince=((dt.datetime.strptime(last[0],"%Y%m%d")-dt.datetime.strptime(lastup,"%Y%m%d")).days
                if lastup else None)
        # 저베이스(턴어라운드): base가 시계열 최댓값의 10% 미만 → %가 튐. 스케일무관(금액/EPS 공통).
        mx=max((abs(v) for _,v in ser), default=0.0)
        turnaround = mx>0 and abs(base[1]) < 0.10*mx
        out.append(dict(code=code, name=nm, rev_pct=round(rev,1),
                        rev_1w=round(rev1w,1) if rev1w is not None else None,
                        base_조=round(base[1]/1e9,2), last_조=round(last[1]/1e9,2),
                        n=len(ser), asof=last[0], last_up=lastup, days_since=dsince,
                        turnaround=turnaround))
    out.sort(key=lambda x:-x["rev_pct"])
    return out[:top] if top else out

# ==================================================================
# CS9  추정 상향 이벤트 스터디 : 과거 컨센 상향 시점의 주가 반응
# ==================================================================
def revision_events(jcode, yyyymm, icode="121500", term=CON, up_thresh=3.0, win=5, min_gap=15):
    """추정 상향 '이벤트' 탐지 — 컨센 시계열에서 최근 win 스냅샷 누적 상승 ≥ up_thresh% 인 날.
    min_gap 스냅샷 이내 중복은 제거. 반환 [(CNS_DT, jump%)]."""
    s = cons_series(jcode, yyyymm, icode, term)
    ev=[]; last=-10**9
    for i in range(win, len(s)):
        b=s[i-win][1]; c=s[i][1]
        if b and (c-b)/abs(b)*100 >= up_thresh and (i-last)>=min_gap:
            ev.append((s[i][0], round((c-b)/abs(b)*100,1))); last=i
    return ev

def revision_event_study(jcode, yyyymm="202512", icode="121500", term=CON,
                         up_thresh=3.0, horizons=(1,5,20), name=""):
    """과거 추정 상향 이벤트 전후 주가 반응. 각 이벤트일 이상 첫 거래일=D0,
    D0 대비 +h거래일 수익률. 반환: 이벤트 수 + 지평선별 평균/승률 + 개별."""
    from news_gongsi_lab import TODAY_MAX
    ev = revision_events(jcode, yyyymm, icode, term, up_thresh)
    if not ev:
        return dict(jcode=jcode, name=name, n_events=0)
    ds=[e[0] for e in ev]
    s0=(dt.datetime.strptime(min(ds),"%Y%m%d")-dt.timedelta(days=15)).strftime("%Y%m%d")
    e0=min((dt.datetime.strptime(max(ds),"%Y%m%d")+dt.timedelta(days=max(horizons)*2+15)).strftime("%Y%m%d"), TODAY_MAX)
    fam,H = pick_fam(jcode, s0, e0)
    H=sorted(H, key=lambda r:str(r.get("F12506")))
    days=[str(r.get("F12506")) for r in H]
    close=[to_f(r.get("F15001")) for r in H]
    def d0idx(d):
        for i,dd in enumerate(days):
            if dd>=d: return i
        return None
    detail=[]; agg={h:[] for h in horizons}
    for d,jump in ev:
        i=d0idx(d)
        if i is None: continue
        rr={}
        for h in horizons:
            if i+h < len(close) and close[i]:
                r=(close[i+h]/close[i]-1)*100; rr[h]=round(r,2); agg[h].append(r)
            else: rr[h]=None
        detail.append(dict(date=d, jump=jump, d0=days[i], rets=rr))
    summ={h:(dict(avg=round(sum(v)/len(v),2), win=round(sum(1 for x in v if x>0)/len(v)*100,0), n=len(v))
             if v else None) for h,v in agg.items()}
    return dict(jcode=jcode, name=name or str(basic(jcode).get("CMP_NM_KOR","")),
                yyyymm=yyyymm, metric=cons_name(icode), n_events=len(detail),
                summary=summ, events=detail, fam=fam)

def upgraded_then_reaction(universe_top=60, yyyymm_screen=None, yyyymm_hist="202512",
                           icode="121500", top=8, up_thresh=3.0, horizons=(1,5,20)):
    """CS8+CS9 결합: 최근 상향 상위 종목을 뽑고, 각 종목의 '과거' 상향 이벤트 주가반응을 붙인다.
    반환: [dict(name, recent_rev, n_events, avg_ret_by_horizon)]."""
    picks = revision_screen(yyyymm=yyyymm_screen, icode=icode, universe_top=universe_top, top=top)
    out=[]
    for p in picks:
        es = revision_event_study(p["code"], yyyymm_hist, icode, up_thresh=up_thresh,
                                  horizons=horizons, name=p["name"])
        out.append(dict(name=p["name"], code=p["code"], recent_rev=p["rev_pct"],
                        last_up=p.get("last_up"), days_since=p.get("days_since"),
                        asof=p.get("asof"), turnaround=p["turnaround"],
                        n_events=es["n_events"], summary=es.get("summary")))
    return out

# ---------------- 포맷 헬퍼 ----------------
def _jo(x):
    """천원 단위 금액 → 조/억 문자열.  (IFRS·컨센 금액계정은 천원: 값÷1e9=조, 값÷1e5=억)"""
    if x is None: return "-"
    jo = x/1e9
    return f"{jo:,.2f}조" if abs(jo)>=1 else f"{x/1e5:,.0f}억"
def _pct(x): return f"{x:+.1f}%" if isinstance(x,(int,float)) else "-"

# ---------------- CLI 데모 ----------------
def demo(jcode="005930", yyyymm="202512"):
    _try_utf8()
    b = basic(jcode); nm = str(b.get("CMP_NM_KOR",""))
    print(f"\n{'='*70}\n■ {nm}({jcode}) 펀더멘털 입체분석 데모 — 대상 {yyyymm}\n{'='*70}")

    print(f"\n[CS1] 어닝 서프라이즈 (컨센 발표직전 vs 실제, 연결)")
    def _fmt(k, x):
        if x is None: return "-"
        return f"{x:,.0f}원" if "EPS" in k else _jo(x)
    for k,v in earnings_surprise(jcode, yyyymm).items():
        print(f"  {k:14s} 컨센 {_fmt(k,v['consensus']):>12}  실제 {_fmt(k,v['actual']):>12}"
              f"  →  {_pct(v['surprise_pct'])}  (컨센 {v['asof']}, 발표 {v['announce']})")

    print(f"\n[CS2] 추정 리비전 모멘텀 (영업이익, 연결)")
    r = estimate_revision(jcode, yyyymm, "121500")
    o=r["overall"]
    if o:
        print(f"  영업이익 추정 {_jo(o['from_'][1])}({o['from_'][0]}) → {_jo(o['to'][1])}({o['to'][0]})  전체{_pct(o['pct'])} ({r['n_snap']}스냅샷)")
        for lbl,k in [("1주","rev_1w"),("1개월","rev_1m"),("3개월","rev_3m")]:
            c=r[k]
            if c: print(f"    최근{lbl} {_jo(c['from_'][1])}→{_jo(c['to'][1])} {_pct(c['pct'])}")

    print(f"\n[CS3] 실적발표 이벤트 스터디")
    es = earnings_event_study(jcode, yyyymm)
    if "error" not in es:
        print(f"  발표일 {es['announce']} (D0={es['d0']}, {es['fam']})  D0등락 {_pct(es['d0_return'])}")
        print(f"  발표전 {es['ret_pre'] and round(es['ret_pre'],1)}% / 발표후 {es['ret_post'] and round(es['ret_post'],1)}%")
        print(f"  외국인 순매수: 발표전 {es['foreign_net_before']:,}주 / 발표후 {es['foreign_net_after']:,}주")
        print(f"  기관   순매수: 발표전 {es['inst_net_before']:,}주 / 발표후 {es['inst_net_after']:,}주")

    print(f"\n[CS4] 밸류에이션 스냅샷 (연결 컨센 최신)")
    v = valuation(jcode, yyyymm)
    def _g(x,fmt="{:.1f}"): return fmt.format(x) if isinstance(x,(int,float)) else "-"
    print(f"  PER {_g(v['per'])}  PBR {_g(v['pbr'])}  PSR {_g(v['psr'])}  ROE {_g(v['roe'])}%  "
          f"OPM {_g(v['opm'])}%  순이익률 {_g(v['npm'])}%  배당수익률 {_g(v['div_yield'])}%  배당성향 {_g(v['payout'])}%")

    print(f"\n[CS6] 지분구조 / 유통물량")
    ow = ownership(jcode, "202412")
    if ow["control_block"]:
        print(f"  지배주주블록: {ow['control_block']['name']}  {ow['control_pct']}%  → 추정유통 {ow['est_float_pct']}%")
    for h in ow["holders"][:5]:
        print(f"    {h['name'][:22]:24s} {h['pct']:5.2f}%  {h['rel'][:14]}")

    print(f"\n[CS5] 사업 프로파일")
    bp = business_profile(jcode, yyyymm)
    if bp["comment"]: print(f"  소개: {bp['comment'][0][:60]}")
    print(f"  매출구성: " + ", ".join(f"{p}({v:.0f}%)" for p,v in bp["sales_mix"][:5]))
    if bp["market_share"]: print(f"  점유율:   " + ", ".join(f"{p} {r:.0f}%" for p,c,r in bp["market_share"][:4]))

    print(f"\n[CS7] 다년 재무 트렌드 (실제→컨센, 연결)")
    ft = fundamental_trend(jcode)
    for row in ft["actual"]:
        print(f"  {row['yymm']}  매출 {_jo(row['revenue']):>9}  영익 {_jo(row['op']):>9}  OPM {row['opm'] and round(row['opm'],1)}%")
    for row in ft["forecast"]:
        print(f"  {row['yymm']}* 매출 {_jo(row['revenue_est']):>9}  영익 {_jo(row['op_est']):>9}  OPM {row['opm'] and round(row['opm'],1)}%  (컨센)")
    if not ft["forecast"] and ft["forecast_dropped"]:
        drp = ", ".join(r["yymm"] for r in ft["forecast_dropped"])
        print(f"  (향후 컨센 {drp} 은 sanity 필터 제외 — 원거리 추정 팽창, 피드 신뢰도 낮음)")
    print()

def _try_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass

if __name__ == "__main__":
    _try_utf8()
    args = sys.argv[1:]
    if args and args[0]=="demo":
        j = args[1] if len(args)>1 else "005930"
        y = args[2] if len(args)>2 else "202512"
        demo(j, y)
    elif args and args[0]=="screen":
        # python comp_fundamentals_lab.py screen [영업이익|EPS|매출액] [예측연월] [유니버스크기]
        metric = {"영업이익":"121500","EPS":"312000","매출액":"121000","순이익":"122700"}.get(
                    args[1] if len(args)>1 else "영업이익", "121500")
        y = args[2] if len(args)>2 else None
        n = int(args[3]) if len(args)>3 else 60
        res = revision_screen(yyyymm=y, icode=metric, universe_top=n, top=20)
        print(f"■ 최근 1개월 컨센 상향 종목 (지표 {cons_name(metric)}, 시총상위 {n}, 연결)\n")
        print(f"{'종목':14s}{'1M리비전':>9}{'1주':>8}  {'마지막상향일':>10}{'경과':>5}  비고")
        for r in res:
            ta=" ⚠턴어라운드" if r["turnaround"] else ""
            w=f"{r['rev_1w']:+.1f}%" if r['rev_1w'] is not None else "-"
            lu=r.get("last_up") or "-"; ds=f"{r['days_since']}일" if r.get("days_since") is not None else "-"
            print(f"  {r['name'][:12]:13s}{r['rev_pct']:+7.1f}%{w:>8}  {lu:>10}{ds:>5}{ta}")
    else:
        print(__doc__)
