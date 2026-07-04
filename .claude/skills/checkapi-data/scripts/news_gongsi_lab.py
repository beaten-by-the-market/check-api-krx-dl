# -*- coding: utf-8 -*-
"""news_gongsi_lab — 공시/뉴스 피드를 시세·수급·공매도·대차와 결합해 분석하는 도구 모음.

CHECK API의 news/gongsi 피드(/news/gongsi/*, /news/news/*)를 시세(hist)·수급(invest)·
공매도(short)·대차(loan)·순위(rank)와 결합해 이벤트 스터디/횡단면/시계열을 돌린다.

■ 핵심 개념 (실측으로 검증된 것)
- 시장 라우팅: KOSPI = stock/m001, KOSDAQ = stock/m003. 종목코드만으론 구분 불가 →
  pick_fam()이 m001 조회 후 비면 m003으로 폴백. (공시 MTVCD 300=거래소/KOSPI, 320=코스닥)
- 조인 키: 공시/뉴스 종목코드(NCD) = 시세 jcode ; DATE = 시세 입회일(F12506) = sdate/edate.
- 뉴스는 종목 태그(NCD)가 없다 → 종목별 뉴스는 news_jong(jcode)로만. 공시 basic엔 NCD 있음.
- 대형주(삼성전자 등) 한 달 뉴스는 수천 건이라 한 번에 조회 시 프록시 502 →
  news_stock_chunked()로 8일 단위로 쪼개 합친다.
- 반드시 등록 IP·샌드박스 밖에서 실행 (call()이 로컬에서 POST). 자격증명은 .env에서 자동 로드.

■ 빠른 사용
    import news_gongsi_lab as lab
    print(lab.event_study("유상증자", "005930", "20260616"))   # 공시 이벤트 전후 반응
    lab.news_stock_chunked("005930", "20260601", "20260703")   # 종목 뉴스(대형주 안전)

CLI 데모:  python news_gongsi_lab.py demo
"""
from __future__ import annotations
import json, time, urllib.parse, urllib.request, urllib.error, datetime as dt, collections, csv

from _common import load_env  # 같은 scripts/ 폴더

BASE = "https://checkapi.koscom.co.kr"
_ENV = load_env()
_CID, _AK = _ENV.get("CHECK_CUST_ID"), _ENV.get("CHECK_AUTH_KEY")

# 데이터가 존재하는 최종 거래일(이후 날짜로 window가 넘어가지 않게 클램프). 필요 시 갱신.
TODAY_MAX = "20260703"

# 뉴스원코드(MTVCD) 범례 — news_mtvcd 실측
SRC = {'0':'시장조치','200':'서울경제','210':'매일경제','220':'한국경제','230':'머니투데이',
 '240':'이데일리','250':'로이터','261':'체크시황','270':'아시아경제','275':'아주경제',
 '280':'전자신문','281':'뉴시스','282':'뉴스토마토','283':'한경TV','284':'이투데이',
 '285':'연합뉴스','290':'뉴스핌','291':'조선비즈','295':'파이낸셜','297':'인포스탁시황',
 '298':'인포스탁','299':'FX해외','300':'거래소공시','302':'KOSPI주식','303':'KOSPI선물',
 '304':'KOSPI옵션','309':'채권공시','310':'선물옵션공시','311':'시장감시공시','320':'코스닥공시',
 '330':'코넥스공시','332':'금현물공시','333':'탄소배출권','360':'K-OTC','500':'CHECK시황'}

def src_name(mtvcd):
    """뉴스원코드(MTVCD)→이름. ★ API는 INT 필드를 Python int로 준다(MTVCD/SEQ 등).
    SRC 키는 문자열이라 반드시 str로 조회해야 이름이 나온다(int로 조회하면 조용히 숫자만 반환)."""
    return SRC.get(str(mtvcd), str(mtvcd))

# ---------------- low level ----------------
# ※ 타입 규칙: CHECK API는 명세 타입을 그대로 준다 —
#   INT/NUMERIC/DECIMAL 필드(MTVCD·SEQ·DSEQ·F12506·가격 등) → Python int/float,
#   CHAR/VARCHAR 필드(DATE·TIME·TITLE·CODE·NCD 등) → str.
#   (call_checkapi.py --csv 경로만 전부 문자열화됨.) 숫자계산은 to_i/to_f로, 정렬키·문자열연산엔
#   반드시 str()로 감싼다(INT 필드에 .isdigit()/슬라이싱/문자열 + 하면 크래시·오정렬).
def call(apiurl, _retry=3, **params):
    if not _CID or not _AK:
        raise SystemExit("CHECK_CUST_ID / CHECK_AUTH_KEY 를 .env/환경변수에서 찾지 못했습니다.")
    data = urllib.parse.urlencode({"cust_id": _CID, "auth_key": _AK, **params}).encode()
    last = None
    for attempt in range(_retry):
        try:
            req = urllib.request.Request(BASE + apiurl, data=data)  # POST
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode("utf-8"))
            if isinstance(d, dict) and d.get("success") is False:
                msg = str(d.get("message") or d)
                if "no data" in msg.lower() or "데이터가 없" in msg:
                    return []   # 조회결과 없음은 에러가 아니라 빈 결과
                raise RuntimeError(msg)
            res = d.get("results", d) if isinstance(d, dict) else d
            return res if isinstance(res, list) else [res]
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                ConnectionError, OSError) as ex:
            last = ex
            time.sleep(1.5 * (attempt + 1))  # 502/타임아웃/연결끊김 재시도
    raise RuntimeError(f"call 실패({apiurl}): {last}  (등록 IP·샌드박스 밖에서 실행했는지 확인)")

def to_i(x):
    try: return int(float(x))
    except Exception: return 0
def to_f(x):
    try: return float(x)
    except Exception: return 0.0

def drange(center, pre=25, post=25):
    """center(YYYYMMDD) 기준 [pre일 전, post일 후] 문자열. TODAY_MAX로 상한 클램프."""
    c = dt.datetime.strptime(center, "%Y%m%d")
    s = (c - dt.timedelta(days=pre)).strftime("%Y%m%d")
    e = min((c + dt.timedelta(days=post)).strftime("%Y%m%d"), TODAY_MAX)
    return s, e

# ---------------- 시장 라우팅 + 시세/수급 ----------------
_FAM = {}
def pick_fam(jcode, s, e):
    """(fam, hist_rows). m001(KOSPI) 우선, 비면 m003(KOSDAQ)."""
    h = call("/stock/m001/hist_info", jcode=jcode, sdate=s, edate=e)
    if h:
        _FAM[jcode] = "m001"; return "m001", h
    h = call("/stock/m003/hist_info", jcode=jcode, sdate=s, edate=e)
    _FAM[jcode] = "m003"; return "m003", h

def fam_of(jcode, probe=("20260601", "20260603")):
    if jcode not in _FAM:
        pick_fam(jcode, *probe)
    return _FAM.get(jcode, "m001")

def hist(jcode, s, e, fam=None):   return call(f"/stock/{fam or fam_of(jcode)}/hist_info", jcode=jcode, sdate=s, edate=e)
def invest(jcode, s, e, fam=None): return call(f"/stock/{fam or fam_of(jcode)}/invest_hist", jcode=jcode, sdate=s, edate=e)
def short(jcode, s, e, fam=None):  return call(f"/stock/{fam or fam_of(jcode)}/short_hist_info", jcode=jcode, sdate=s, edate=e)
def loan(jcode, s, e, fam=None):   return call(f"/stock/{fam or fam_of(jcode)}/loan_hist_info", jcode=jcode, sdate=s, edate=e)

# ---------------- 공시 / 뉴스 ----------------
def gongsi_day(s, e, dcnt=20000):        return call("/news/gongsi/gongsi_basic", sdate=s, edate=e, dcnt=str(dcnt))
def gongsi_stock(jcode, s, e, dcnt=500): return call("/news/gongsi/gongsi_jong", jcode=jcode, sdate=s, edate=e, dcnt=str(dcnt))
def gongsi_body(ndate, ncode):           return call("/news/gongsi/gongsi_body", ndate=ndate, ncode=ncode)
def news_day(s, e, dcnt=30000):          return call("/news/news/news_basic", sdate=s, edate=e, dcnt=str(dcnt))
def news_stock(jcode, s, e, dcnt=1000):  return call("/news/news/news_jong", jcode=jcode, sdate=s, edate=e, dcnt=str(dcnt))
def news_body(ndate, ncode):             return call("/news/news/news_body", ndate=ndate, ncode=ncode)

def news_stock_chunked(jcode, s, e, step=8, dcnt=3000):
    """대형주 한 번에 조회 시 502 → step일 단위로 쪼개 합친다."""
    d0 = dt.datetime.strptime(s, "%Y%m%d"); d1 = dt.datetime.strptime(e, "%Y%m%d")
    out, cur = [], d0
    while cur <= d1:
        ce = min(cur + dt.timedelta(days=step - 1), d1)
        try:
            out += news_stock(jcode, cur.strftime("%Y%m%d"), ce.strftime("%Y%m%d"), dcnt=dcnt)
        except Exception:
            pass
        cur = ce + dt.timedelta(days=1)
    return out

# ---------------- 이벤트 스터디 ----------------
def event_study(name, jcode, edate, want_short=False, want_loan=False, want_gongsi=False,
                want_news=False, win=6):
    """공시/뉴스 이벤트일(edate) 기준 시세+수급(+공매도/대차/공시타임라인/뉴스) 전후 반응.

    반환 dict: D0등락률, D0..D+win 누적수익률, 거래량배수(직전5일평균 대비),
    투자자 순매수(외국인 F06508_11 / 기관 _08 / 개인 _10, 천주),
    (옵션) 공매도대금·잔고비중, 대차잔고량, 종목 공시 타임라인(gongsi_stock), 뉴스량.
    시장경보류 공시는 대개 장마감 후 발표 → D0는 '이벤트일 이상 첫 거래일'로 잡는다.
    """
    s, e = drange(edate)
    fam, H = pick_fam(jcode, s, e)
    I = invest(jcode, s, e, fam)
    Hd = {str(r["F12506"]): r for r in H}
    Id = {str(r["F12506"]): r for r in I}
    days = sorted(Hd.keys())
    if len(days) < 2:
        return {"name": name, "jcode": jcode, "시장": fam, "err": f"거래일부족(rows={len(days)}) — 장기 정지 가능"}
    d0 = edate if edate in days else next((d for d in days if d >= edate), days[-1])
    i0 = max(1, days.index(d0))
    pre = days[max(0, i0 - 5):i0]
    pre_vol = sum(to_i(Hd[d]["F15015"]) for d in pre) / max(1, len(pre))
    base = to_i(Hd[days[i0 - 1]]["F15001"])
    def cret(k):
        if i0 + k >= len(days): return None
        px = to_i(Hd[days[i0 + k]]["F15001"])
        return round((px / base - 1) * 100, 2) if base else None
    cum = {f"D+{k}": cret(k) for k in range(win) if cret(k) is not None}
    vr = {f"D+{k}": round(to_i(Hd[days[i0 + k]]["F15015"]) / pre_vol, 2)
          for k in range(win) if i0 + k < len(days) and pre_vol}
    post = days[i0:i0 + win]
    def net(code): return sum(to_i(Id[d].get(f"F06508_{code}", 0)) for d in post if d in Id)
    out = {"name": name, "jcode": jcode, "시장": fam, "event": edate, "D0": d0,
           "D0_ret%": to_f(Hd[d0]["F15004"]), "cum_ret%": cum, "vol_x": vr,
           "netbuy_천주": {"외국인": round(net("11")/1000), "기관": round(net("08")/1000),
                          "개인": round(net("10")/1000)}}
    if want_short:
        S = {str(r["F12506"]): r for r in short(jcode, s, e, fam)}
        out["공매도대금_백만"] = {d[4:]: round(to_i(S[d]["F33095"]) / 1e6) for d in post if d in S}
        out["공매도잔고비중%"] = {d[4:]: to_f(S[d]["F19298"]) for d in post if d in S}
    if want_loan:
        L = {str(r["F12506"]): r for r in loan(jcode, s, e, fam)}
        # F14212 대차잔고량, F14213 금액, F14216 비율
        out["대차잔고량"] = {d[4:]: to_i(L[d]["F14212"]) for d in ([days[i0-1]] + post) if d in L}
    if want_gongsi:
        # 이벤트 종목의 공시 타임라인(이벤트일 ±7일) — 이벤트 앞뒤에 어떤 공시가 더 있었나
        gw_s = (dt.datetime.strptime(edate, "%Y%m%d") - dt.timedelta(days=7)).strftime("%Y%m%d")
        gw_e = min((dt.datetime.strptime(edate, "%Y%m%d") + dt.timedelta(days=7)).strftime("%Y%m%d"), TODAY_MAX)
        try:
            gj = gongsi_stock(jcode, gw_s, gw_e)
            out["공시타임라인"] = [{"일자": str(r["DATE"]), "시간": str(r["TIME"])[:4], "유형": classify_gongsi(r["TITLE"]),
                                 "제목": strip_corp(r["TITLE"])} for r in
                                sorted(gj, key=lambda r: str(r["DATE"]) + str(r["TIME"]))]
        except Exception as ex:
            out["공시타임라인"] = f"조회실패: {str(ex)[:60]}"
    if want_news:
        nw_s = (dt.datetime.strptime(edate, "%Y%m%d") - dt.timedelta(days=5)).strftime("%Y%m%d")
        nw_e = min((dt.datetime.strptime(edate, "%Y%m%d") + dt.timedelta(days=3)).strftime("%Y%m%d"), TODAY_MAX)
        try:
            nj = news_stock(jcode, nw_s, nw_e)
            byd = collections.Counter(str(r["DATE"]) for r in nj)
            out["뉴스량_일자별"] = dict(sorted(byd.items()))
        except Exception as ex:
            out["뉴스량_일자별"] = f"조회실패: {str(ex)[:60]}"
    return out

# ---------------- 뉴스 감성(제목) — 간이 사전 ----------------
POS = ['급등','상한가','신고가','최고가','호실적','흑자전환','흑자','수주','수혜','상향','돌파',
       '강세','반등','기대','최대','성장','호조','유치','흥행','목표가']
NEG = ['급락','하한가','적자','부진','소송','횡령','하향','약세','우려','리스크','철회','불성실',
       '상장폐지','경고','반토막','폭락','손실','논란','의혹','제재','매도']
def sentiment(title: str) -> int:
    """제목 감성 순점수(양수=호재 성향). 뉴스량 많은 대형주는 절대점수보다 건당평균으로 볼 것."""
    return sum(title.count(k) for k in POS) - sum(title.count(k) for k in NEG)

# ---------------- 공시 제목 정리/분류 ----------------
import re as _re
def strip_corp(title: str) -> str:
    """공시 제목 앞의 회사명/법인표기를 대충 떼어 유형만 남긴다(표시용)."""
    t = title.strip()
    t = _re.sub(r'^\(주\)\s*', '', t)
    t = _re.sub(r'^주식회사\s*', '', t)
    return t

_GCAT = [
 ("시장경보", ['투자주의','투자경고','투자위험','단기과열','공매도 과열','소수계좌','매매관여','불성실공시']),
 ("조회공시", ['조회공시','풍문','해명']),
 ("자본거래", ['유상증자','무상증자','전환사채','신주인수권','교환사채','자기주식','감자','주식매수선택권','교환청구']),
 ("실적/공정", ['(잠정)','영업실적','공정공시','장래사업','실적']),
 ("지배구조", ['최대주주변경','합병','분할','대표이사','경영권','타법인','양수','양도','출자']),
 ("배당", ['배당']),
 ("상장상태", ['상장폐지','관리종목','매매거래정지','정리매매','신규상장','추가상장','변경상장','상장예정']),
 ("계약/투자", ['공급계약','수주','신규시설투자','투자판단','담보제공']),
 ("파생", ['가격제한폭','주식선물','주식옵션']),
 ("ETP", ['ETF','ETN','상장지수','유동성공급','LP']),
]
def classify_gongsi(title: str) -> str:
    for cat, kws in _GCAT:
        if any(k in title for k in kws):
            return cat
    return "기타"

# ---------------- 시세→공시 역방향 스크리닝 (price-first) ----------------
# ETP(ETF/ETN 등) 이름 토큰 — rank 결과에 섞여 나오므로 개별주만 볼 때 제외.
_ETP_TOK = ['ETF','ETN','KODEX','TIGER','KBSTAR','ARIRANG','ACE','SOL ','PLUS ','HANARO','KOSEF',
            'RISE ','TIMEFOLIO','히어로즈','마이티','FOCUS','파워','KOACT','TREX','상장지수','레버리지','인버스']
def _is_etp(name: str) -> bool:
    return any(tok in name for tok in _ETP_TOK)

def market_snapshot(fam="both", exclude_etp=True):
    """현재(최신 거래일) 전체 종목 시세 스냅샷. rank는 날짜 파라미터가 없어 '오늘'만 된다.
    반환: [{code,name,fam,price,prev,ret,vol,amt,mktcap}]  (ret%=(현재가-전일종가)/전일종가)
    거래대금(F15023)로 정렬 호출하나 등락률/거래량 필드도 함께 와서 재정렬 가능."""
    fams = ["m001", "m003"] if fam == "both" else [fam]
    out = []
    for fm in fams:
        for r in call(f"/stock/{fm}/rank", up_code="1", criteria_code="F15023"):
            name = str(r.get("F16002", "")).strip()
            if exclude_etp and _is_etp(name):
                continue
            price, prev = to_i(r.get("F15001")), to_i(r.get("F03003"))
            out.append({"code": str(r.get("F16013", "")).strip(), "name": name, "fam": fm,
                        "price": price, "prev": prev,
                        "ret": round((price/prev-1)*100, 2) if prev else 0.0,
                        "vol": to_i(r.get("F15015")), "amt": to_i(r.get("F15023")),
                        "mktcap": to_i(r.get("F15028"))})
    return out

_SNAP_KEY = {"등락률": "ret", "거래대금": "amt", "거래량": "vol", "시가총액": "mktcap", "주가": "price"}
def screen_today(by="등락률", top=20, direction="top", exclude_etp=True, snap=None):
    """오늘(최신일) 스크리너. by=등락률/거래대금/거래량/시가총액, direction=top(상위)/bottom(하위)."""
    snap = snap if snap is not None else market_snapshot(exclude_etp=exclude_etp)
    key = _SNAP_KEY[by]
    ordered = sorted(snap, key=lambda x: x[key], reverse=(direction == "top"))
    return ordered[:top]

def period_metrics(jcode, s, e, fam=None):
    """기간 [s,e] 시세 파생지표. hist_info 기반(과거일 가능)."""
    fam = fam or fam_of(jcode)
    H = sorted(hist(jcode, s, e, fam), key=lambda r: r["F12506"])
    if len(H) < 2:
        return {"jcode": jcode, "fam": fam, "err": f"거래일부족({len(H)})"}
    closes = [to_i(r["F15001"]) for r in H]
    highs = [to_i(r["F15010"]) for r in H]
    lows = [to_i(r["F15011"]) for r in H]
    amts = [to_i(r["F15023"]) for r in H]
    rets = [to_f(r["F15004"]) for r in H]
    half = len(amts) // 2 or 1
    a1 = sum(amts[:half]) / half
    a2 = sum(amts[half:]) / max(1, len(amts) - half)
    return {"jcode": jcode, "fam": fam, "n": len(H),
            "기간수익률%": round((closes[-1]/closes[0]-1)*100, 2) if closes[0] else 0,
            "최대일간변동%": round(max(abs(x) for x in rets), 2),
            "평균거래대금_억": round(sum(amts)/len(amts)/1e8, 1),
            "거래대금증가율": round(a2/a1, 2) if a1 else 0,
            "신고가돌파": closes[-1] >= max(highs[:-1]) if len(highs) > 1 else False,
            "신저가이탈": closes[-1] <= min(lows[:-1]) if len(lows) > 1 else False,
            "종가": closes[-1]}

def abnormal_turnover(jcode, s, e, fam=None):
    """최근 5거래일 거래대금 / 직전 기간 평균 = 이상거래대금 배수."""
    fam = fam or fam_of(jcode)
    H = sorted(hist(jcode, s, e, fam), key=lambda r: r["F12506"])
    amts = [to_i(r["F15023"]) for r in H]
    if len(amts) < 8:
        return None
    base = sum(amts[:-5]) / max(1, len(amts) - 5)
    recent = sum(amts[-5:]) / 5
    return round(recent/base, 2) if base else None

def disclosures_of(jcode, s, e, cats=None):
    """종목의 공시 목록(gongsi_stock) — 정정 제외, 유형분류 포함. cats로 유형 필터."""
    out = []
    for r in sorted(gongsi_stock(jcode, s, e), key=lambda r: str(r["DATE"]) + str(r["TIME"])):
        if "(정정)" in r["TITLE"]:
            continue
        c = classify_gongsi(r["TITLE"])
        if cats and c not in cats:
            continue
        out.append({"일자": str(r["DATE"]), "시간": str(r["TIME"])[:4], "유형": c,
                    "제목": strip_corp(r["TITLE"])[:50], "코드": str(r["CODE"]),
                    "MTVCD": str(r["MTVCD"])})  # ★ MTVCD는 INT라 str()로 정규화(소비측 .isdigit()/SRC조회 안전)
    return out

def explain_stock(jcode, s, e, with_news=False, name=""):
    """시세 급변 종목의 '왜' — 기간 시세지표 + 그 기간 공시목록(+뉴스량)."""
    m = period_metrics(jcode, s, e)
    res = {"jcode": jcode, "name": name, "지표": m,
           "공시": disclosures_of(jcode, s, e) if "err" not in m else []}
    if with_news:
        try:
            res["뉴스건수"] = len(news_stock_chunked(jcode, s, e))
        except Exception:
            res["뉴스건수"] = None
    return res

def notable_movers(s, e, universe_top=150, top=15, exclude_etp=True):
    """일정기간 '주목할 시황'이 난 기업 발굴(시세→공시).
    ① 현재 거래대금 상위 universe_top을 유동성 유니버스로 삼고(rank는 오늘만 가능),
    ② 각 종목의 [s,e] 기간지표를 계산,
    ③ 주목도 = |기간수익률| + 2·최대일간변동 + 30·|거래대금증가율-1| 로 랭크,
    ④ 상위 top 종목에 공시목록을 붙인다.
    ※ 유니버스는 '현재' 유동종목 기준이라 과거 상장폐지/신규종목은 빠질 수 있음(근사)."""
    snap = market_snapshot(exclude_etp=exclude_etp)
    universe = sorted(snap, key=lambda x: x["amt"], reverse=True)[:universe_top]
    scored = []
    for u in universe:
        m = period_metrics(u["code"], s, e, u["fam"])
        if "err" in m:
            continue
        score = abs(m["기간수익률%"]) + 2*m["최대일간변동%"] + 30*abs(m["거래대금증가율"]-1)
        scored.append((round(score, 1), u["name"], u["code"], u["fam"], m))
    scored.sort(key=lambda t: t[0], reverse=True)
    out = []
    for sc, nm, code, fm, m in scored[:top]:
        out.append({"주목도": sc, "name": nm, "code": code,
                    "기간수익률%": m["기간수익률%"], "최대일간변동%": m["최대일간변동%"],
                    "거래대금증가율": m["거래대금증가율"], "신고가": m["신고가돌파"],
                    "공시": disclosures_of(code, s, e)})
    return out

# ---------------- 전체종목 기간 벌크 ----------------
# 시장별로 벌크 가능 여부가 다르다(실측):
#  - KOSPI(m001): hist_info_port(codelist, edate) 존재 → '날짜 루프'로 전종목×기간을 싸게 수집
#    (한 달 ≈ 거래일수 × codelist청크 콜). 과거일 조회 OK.
#  - KOSDAQ(m003): hist_info_port 없음(404). 일별 벌크 endpoint가 없어 종목별 hist_info 루프뿐
#    (전 코스닥이면 ~수천 콜). basic_info_all_port는 codelist만=현재일이라 과거 기간 불가.
def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def trading_days(s, e, probe="005930"):
    """기간 내 실제 거래일 목록(대형주 hist의 F12506)."""
    return sorted(str(r["F12506"]) for r in hist(probe, s, e, "m001"))

def hist_port(codes, edate):
    """[KOSPI 전용] N종목 × 1일 벌크(과거일 OK). codes=코드 리스트.
    ※ m003(코스닥)엔 hist_info_port가 없다(404). 코스닥 과거 기간은 종목별 hist_info 루프뿐."""
    if not codes:
        return []
    return call("/stock/m001/hist_info_port", codelist=",".join(codes), edate=edate)

def basic_all_port(codes, fam, numeric_only=True, chunk=1500):
    """[현재일 전용] N종목 × 오늘 벌크 크로스섹션(basic_info_all_port, 100+필드:
    외국인보유율·상한가·시총·등락 등). m001/m003 둘 다 있음.
    ※ 코스콤 버그: codelist에 '영숫자 6자리'(스팩·최근상장) 코드가 1개라도 섞이면
      'Error while performing Query'로 배치 전체가 실패한다(실측). 숫자코드만 보내면
      전 코스닥 1,771종목도 한 콜에 성공 → numeric_only=True(기본)로 숫자코드만.
    ※ edate는 무시되고 항상 현재일이다(과거일 불가)."""
    if numeric_only:
        codes = [c for c in codes if len(c) == 6 and c.isdigit()]
    out = []
    for ch in _chunks(codes, chunk):
        try:
            out += call(f"/stock/{fam}/basic_info_all_port", codelist=",".join(ch))
        except Exception:
            pass
    return out

def bulk_hist_period(codes_by_fam, sdate, edate, numeric_only=True, chunk=800, m003_limit=None):
    """종목 × 기간 시세 수집. 반환: (data, days)  data[code] = {date: row}.
    codes_by_fam = {'m001':[...], 'm003':[...]}.
    - m001: hist_info_port 날짜 루프(벌크, 저비용).
    - m003: 종목별 hist_info 루프(고비용). m003_limit로 상위 N개만 돌 수 있음(None=전체).
    ※ codelist에 영숫자 6자리(스팩·신규)가 섞이면 배치 실패 버그 → numeric_only=True로 숫자코드만."""
    days = trading_days(sdate, edate)
    data = {}
    # KOSPI: 날짜 루프 벌크
    kospi = codes_by_fam.get("m001", [])
    if numeric_only:
        kospi = [c for c in kospi if len(c) == 6 and c.isdigit()]
    for day in days:
        for ch in _chunks(kospi, chunk):
            try:
                rows = hist_port(ch, day)
            except Exception:
                rows = []   # 그 날/청크만 건너뜀
            for r in rows:
                data.setdefault(str(r["F16013"]).strip(), {})[day] = r
    # KOSDAQ: 종목별 루프(벌크 endpoint 없음)
    kosdaq = codes_by_fam.get("m003", [])
    if numeric_only:
        kosdaq = [c for c in kosdaq if len(c) == 6 and c.isdigit()]
    if m003_limit is not None:
        kosdaq = kosdaq[:m003_limit]
    for code in kosdaq:
        try:
            for r in hist(code, sdate, edate, "m003"):
                data.setdefault(str(r["F16013"]).strip(), {})[str(r["F12506"])] = r
        except Exception:
            pass
    return data, days

def _period_from_series(series):
    """{date:row} → 기간 파생지표(period_metrics와 동일 정의)."""
    days = sorted(series)
    if len(days) < 2:
        return None
    closes = [to_i(series[d]["F15001"]) for d in days]
    highs = [to_i(series[d]["F15010"]) for d in days]
    lows = [to_i(series[d]["F15011"]) for d in days]
    amts = [to_i(series[d]["F15023"]) for d in days]
    rets = [to_f(series[d]["F15004"]) for d in days]
    half = len(amts) // 2 or 1
    a1 = sum(amts[:half]) / half
    a2 = sum(amts[half:]) / max(1, len(amts) - half)
    return {"n": len(days),
            "기간수익률%": round((closes[-1]/closes[0]-1)*100, 2) if closes[0] else 0,
            "최대일간변동%": round(max(abs(x) for x in rets), 2),
            "평균거래대금_억": round(sum(amts)/len(amts)/1e8, 1),
            "거래대금증가율": round(a2/a1, 2) if a1 else 0,
            "신고가돌파": closes[-1] >= max(highs[:-1]) if len(highs) > 1 else False,
            "종가": closes[-1]}

def market_period_screen(sdate, edate, snap=None, numeric_only=True, min_amt_억=1, m003_limit=None):
    """전체종목 × 기간 기간지표(유니버스 상한 없음). 반환 {code:{name,fam,...지표}}.
    - KOSPI 전종목은 벌크(hist_info_port 날짜루프)로 저비용.
    - KOSDAQ은 종목루프라 비쌈 → m003_limit로 상위 N개만(거래대금순) 제한 권장(None=전체).
    - 평균거래대금 min_amt_억 미만 제외."""
    snap = snap if snap is not None else market_snapshot()
    snap = sorted(snap, key=lambda x: x["amt"], reverse=True)  # 거래대금순(m003_limit이 상위부터 되게)
    name = {x["code"]: x["name"] for x in snap}
    codes_by_fam = {"m001": [x["code"] for x in snap if x["fam"] == "m001"],
                    "m003": [x["code"] for x in snap if x["fam"] == "m003"]}
    fam_of_code = {x["code"]: x["fam"] for x in snap}
    data, days = bulk_hist_period(codes_by_fam, sdate, edate, numeric_only=numeric_only, m003_limit=m003_limit)
    out = {}
    for code, series in data.items():
        m = _period_from_series(series)
        if not m or m["평균거래대금_억"] < min_amt_억:
            continue
        m["name"] = name.get(code, code)
        m["fam"] = fam_of_code.get(code, "")
        out[code] = m
    return out

# ---------------- CSV ----------------
def read_csv(path):  return list(csv.DictReader(open(path, encoding="utf-8-sig")))

# ---------------- CLI 데모 ----------------
if __name__ == "__main__":
    import sys
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    if len(sys.argv) >= 2 and sys.argv[1] == "demo":
        print("[event_study] 무상증자 가온전선(000500) 2026-06-16")
        print(json.dumps(event_study("무상증자", "000500", "20260616"), ensure_ascii=False, indent=2))
        print("\n[event_study+short] 공매도과열 리노공업(058470) 2026-06-12")
        print(json.dumps(event_study("공매도과열", "058470", "20260612", want_short=True), ensure_ascii=False, indent=2))
    else:
        print(__doc__)
