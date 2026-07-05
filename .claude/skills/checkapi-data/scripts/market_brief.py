"""장마감 시황 요약을 CHECK API로 재현한다 (지수·등락·거래대금·시장 투자자 수급).

사용법:
    python market_brief.py 20230412
    python market_brief.py 20230412 --json

- **등록 IP 호스트에서, 샌드박스 밖으로 실행**할 것 (실호출).
- 확정·검증된 부분: KOSPI/KOSDAQ 지수값·등락률·거래대금, 시장 단위 투자자 순매수(억원).
  (실측 대조: 2023-04-12 KOSPI 2550.64/+0.11%, KOSDAQ 890.62/-0.93%)
- 이 브리프는 KRX 원본 재현에 집중해 국내 지수·선물·수급만 담는다. 아래는 참고:
  · 환율·금리·유가는 사실 CHECK로 조회된다(정정): 원/달러 `bond/m023 00USDSP`(실측 1,525.6),
    국고채 지표금리 `bond/m058 jipyo_list`+`bond/m038` F15175(3Y 3.745, edate로 그날 지표물→과거일 OK),
    미국10Y `bond/m025 GBUS10Y`, 달러지수·WTI `etc/economic/indicator`. → 매크로 대시보드로 함께 볼 것.
  · 진짜 범위 밖: 해외 주가지수(니케이·상해 등), 브렌트/두바이 현물 유가.
  · KRX300 = m167 jcode 300(실측 확정) — INDICES에 포함돼 있고, NXT 대응 통합지수는 없다.
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from _common import load_env, _force_utf8_stdout

BASE_URL = "https://checkapi.koscom.co.kr"

# 지수(업종) 레벨: m002=코스피, m004=코스닥. jcode=지수(업종)코드. 코스피/코스닥 종합=1 (실측 확인).
INDICES = [
    {"label": "KOSPI", "family": "m002", "code": "1"},    # m002=코스피 지수, 종합=1
    {"label": "KOSDAQ", "family": "m004", "code": "1"},   # m004=코스닥 지수, 종합=1
    {"label": "KRX300", "family": "m167", "code": "300"}, # m167=KRX 통합지수, KRX300=300
]
# KRX 지수패밀리 → 통합(KRX+NXT) 지수패밀리 (거래대금·거래량만; 지수값·등락률은 KRX). m167(KRX300)은 NXT 대응 없음.
_UNI_IDX = {"m002": "m228", "m004": "m229"}

# 투자자 순매수 거래대금 F-code (references/investor-codes.md): 외국인=11, 기관=8, 개인=10
INVESTOR = {"외국인": "F06511_11", "기관": "F06511_08", "개인": "F06511_10"}

# 지수선물 최근월물: family별. 최근월물은 code_info의 F16169='Y'로 선택.
FUTURES = [
    {"label": "KOSPI200", "family": "m005"},   # KOSPI200 선물
    {"label": "KOSDAQ150", "family": "m067"},  # KOSDAQ150(KSQ150) 선물
    {"label": "KRX300", "family": "m181"},     # KRX300 선물
]


def post(apiurl: str, **params: str) -> list[dict]:
    env = load_env()
    cust_id, auth_key = env.get("CHECK_CUST_ID"), env.get("CHECK_AUTH_KEY")
    if not cust_id or not auth_key:
        raise SystemExit("CHECK_CUST_ID / CHECK_AUTH_KEY 를 .env 또는 환경변수에서 찾지 못했습니다.")
    payload = {"cust_id": cust_id, "auth_key": auth_key, **params}
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(f"{BASE_URL}{apiurl}", data=data)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            d = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {apiurl}")
    if d.get("success") is False:
        msg = d.get("message") or d.get("errmsg") or d
        raise RuntimeError(f"{msg} (등록 IP·샌드박스 밖에서 실행했는지 확인)")
    return d.get("results", []) or []


def _num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def index_block(idx: dict, date: str) -> dict:
    """지수 값·등락률·거래대금(+전일대비). hist_info를 소폭 구간으로 받아 당일/전일 추출."""
    start = (datetime.strptime(date, "%Y%m%d") - timedelta(days=16)).strftime("%Y%m%d")
    rows = post(f"/stock/{idx['family']}/hist_info", jcode=idx["code"], sdate=start, edate=date)
    rows.sort(key=lambda r: str(r.get("F12506", "")), reverse=True)  # 입회일 내림차순
    if not rows or str(rows[0].get("F12506")) != date:
        return {"label": idx["label"], "missing": True}
    cur = rows[0]
    prev_amt = _num(rows[1].get("F15023")) if len(rows) > 1 else None
    amt = _num(cur.get("F15023"))  # 거래대금(백만원, KRX)
    out = {
        "label": idx["label"],
        "close": _num(cur.get("F15001")),      # 현재가(지수) — KRX 공식
        "chg_pct": _num(cur.get("F15004")),    # 등락율 — KRX 공식
        "amount_jo": amt / 1_000_000,          # 백만원 -> 조원 (KRX 재현)
        "amount_delta_jo": (amt - prev_amt) / 1_000_000 if prev_amt is not None else None,
    }
    # 통합(KRX+NXT) 거래대금 병기. 통합 지수패밀리(m228/m229)는 거래대금·거래량만(지수값·등락률 없음).
    uni_fam = _UNI_IDX.get(idx["family"])
    if uni_fam:
        try:
            ur = [r for r in post(f"/stock/{uni_fam}/hist_info", jcode=idx["code"], sdate=start, edate=date)
                  if str(r.get("F12506")) == date]
            if ur:
                out["amount_unified_jo"] = _num(ur[0].get("F15023")) / 1_000_000
        except RuntimeError:
            pass
    # 시장 투자자 순매수(억원). 일부 지수(KRX300=m167 등)엔 없으므로 실패해도 넘어간다.
    try:
        inv = post(f"/stock/{idx['family']}/invest_hist_info", jcode=idx["code"], sdate=date, edate=date)
        if inv:
            r = inv[0]
            out["flow"] = {name: _num(r.get(fc)) / 100_000_000 for name, fc in INVESTOR.items()}
    except RuntimeError:
        pass
    return out


def futures_block(f: dict, date: str) -> dict:
    """지수선물 최근월물(F16169='Y')의 가격·등락률·거래량·베이시스."""
    codes = post(f"/future/{f['family']}/code_info")
    front = next(
        (c for c in codes
         if c.get("F16169") == "Y"
         and "선물" in (c.get("F16002") or "") and "스프레드" not in (c.get("F16002") or "")),
        None,
    )
    if not front:
        return {"label": f["label"], "missing": True}
    rows = post(f"/future/{f['family']}/hist_info", jcode=front["F16013"], sdate=date, edate=date)
    if not rows:
        return {"label": f["label"], "contract": front.get("F16002", ""), "missing": True}
    r = rows[0]
    return {
        "label": f["label"],
        "contract": front.get("F16002", ""),
        "close": _num(r.get("F15001")),
        "chg_pct": _num(r.get("F15004")),
        "volume": _num(r.get("F15015")),
        "basis": _num(r.get("F04001")),         # 시장베이시스
        "theory_basis": _num(r.get("F04002")),  # 이론베이시스
    }


def _ktb_yield(date: str, maturity: str) -> float | None:
    """국고채 지표금리(%) — jipyo_list가 그날 만기별 지표물 ISIN을 주면 m038로 수익률 조회.
    같은 만기에 명목·물가채가 섞여 나올 수 있어(물가채 실질수익률이 훨씬 낮음) 명목 지표물을
    max(F15175)로 고른다(실측: 만기10 = 물가 1.560 vs 명목 4.168 → 4.168 채택)."""
    try:
        jl = post("/bond/m058/jipyo_list", edate=date)
    except RuntimeError:
        return None
    isins = [str(r.get("F16013")) for r in jl if str(r.get("F14131")) == str(maturity)]
    best = None
    for isin in isins:
        try:
            y = post("/bond/m038/hist_info", jcode=isin, sdate=date, edate=date)
        except RuntimeError:
            continue
        if y:
            v = _num(y[0].get("F15175"))
            if v and (best is None or v > best):
                best = v
    return best


def _econ_latest(check_code: str, date: str) -> tuple[float, str] | None:
    """경제지표(달러지수·WTI 등) — date 이하 최신 (DATA_VALUE, TIME). 갱신지연 있어 날짜 병기."""
    try:
        rows = post("/etc/economic/indicator", check_code=check_code)
    except RuntimeError:
        return None
    cand = sorted((r for r in rows if str(r.get("TIME", "")) <= date), key=lambda r: str(r.get("TIME")))
    if not cand:
        cand = sorted(rows, key=lambda r: str(r.get("TIME", "")))
    if not cand:
        return None
    last = cand[-1]
    return _num(last.get("DATA_VALUE")), str(last.get("TIME", ""))


def macro_block(date: str) -> dict:
    """KRX Brief '기타' 섹션 재현 — 금리·환율·유가 (전부 CHECK 실호출).
    원/달러(bond/m023), 국고채 3Y/10Y(bond/m058+m038), 미국10Y(bond/m025 GBUS10Y),
    달러지수·WTI(etc/economic). 실패 항목은 None으로 두고 렌더에서 건너뛴다.
    ※ 위안/달러·Brent·해외지수는 CHECK 범위 밖/구독 필요 → 여기서 산출하지 않음."""
    out: dict = {}
    try:
        r = post("/bond/m023/basic_info", jcode="00USDSP")
        if r:
            out["usdkrw"] = _num(r[0].get("F15001"))       # 현재가(spot)
            out["usdkrw_base"] = _num(r[0].get("F15183"))  # 당일 매매기준율
    except RuntimeError:
        pass
    out["ktb3y"] = _ktb_yield(date, "3")
    out["ktb10y"] = _ktb_yield(date, "10")
    try:
        r = post("/bond/m025/hist_info", jcode="GBUS10Y", sdate=date, edate=date)
        out["us10y"] = _num(r[0].get("F32450")) if r else None
    except RuntimeError:
        out["us10y"] = None
    dxy = _econ_latest("USDXYD", date)
    wti = _econ_latest("USCOMCL1D", date)
    out["dxy"], out["dxy_time"] = (dxy[0], dxy[1]) if dxy else (None, None)
    out["wti"], out["wti_time"] = (wti[0], wti[1]) if wti else (None, None)
    return out


def open_snapshot(idx: dict, date: str, target: int) -> dict:
    """장중 지수 스냅샷: intra_date(1분)에서 target 시각(HMMSSss) 이상 첫 값.
    KRX300(m167)은 intra_date가 없어 미지원."""
    try:
        rows = post(f"/stock/{idx['family']}/intra_date", jcode=idx["code"], edate=date)
    except RuntimeError:
        return {"label": idx["label"], "missing": True, "reason": "intra_date 미제공"}
    tkey, ckey, pkey = "F20004_02", "F20008_02", "F20041_02"
    cand = [r for r in rows if int(_num(r.get(tkey))) >= target]
    if not cand:
        return {"label": idx["label"], "missing": True, "reason": "해당 시각 데이터 없음"}
    best = min(cand, key=lambda r: int(_num(r.get(tkey))))
    t = int(_num(best.get(tkey)))
    return {
        "label": idx["label"],
        "hm": f"{t // 1000000:02d}:{(t // 10000) % 100:02d}",  # HMMSSss -> HH:MM
        "close": _num(best.get(ckey)),
        "chg_pct": _num(best.get(pkey)),
    }


def live_snapshot(idx: dict) -> dict:
    """실시간 현재값: intra_info(10초)의 마지막 버킷. KRX300(m167)도 지원(intra_info 있음).
    장중엔 현재가, 장 마감/휴장이면 최근 체결값을 준다."""
    rows = post(f"/stock/{idx['family']}/intra_info", jcode=idx["code"])
    if not rows:
        return {"label": idx["label"], "missing": True}
    last = rows[-1]
    t = int(_num(last.get("F20004_01")))
    return {
        "label": idx["label"],
        "hm": f"{t // 1000000:02d}:{(t // 10000) % 100:02d}",
        "close": _num(last.get("F20008_01")),   # Intra종가(현재가)
        "chg_pct": _num(last.get("F20041_01")),  # Intra등락률
    }


def render_live(snaps: list[dict]) -> str:
    hm = next((s["hm"] for s in snaps if not s.get("missing")), "--:--")
    lines = [f"[실시간 스냅샷]  — CHECK API ({hm} 시점 최근 체결 기준)", ""]
    lines.append("▣ <개요>")
    for s in snaps:
        if s.get("missing"):
            lines.append(f"  {s['label']}: 데이터 없음")
        else:
            lines.append(f"  {s['label']:<7}{s['close']:>9,.2f}p ({fmt_signed(s['chg_pct'], '%', 2)})")
    lines.append("")
    lines.append("※ 장중 실행 시 현재가, 장 마감/휴장 시 최근 체결값. 환율·해외지수는 CHECK 범위 밖.")
    return "\n".join(lines)


def render_open(date: str, snaps: list[dict], target: int) -> str:
    dt = datetime.strptime(date, "%Y%m%d")
    hm = f"{target // 1000000:02d}:{(target // 10000) % 100:02d}"
    lines = [f"[{dt.strftime('%Y-%m-%d')}({'월화수목금토일'[dt.weekday()]}) 장개시]  — CHECK API 재현 ({hm} 기준)", ""]
    lines.append(f"▣ <개요> ({hm} 기준)")
    for s in snaps:
        if s.get("missing"):
            lines.append(f"  {s['label']}: 미지원 ({s.get('reason', '')})")
        else:
            lines.append(f"  {s['label']:<7}{s['close']:>9,.2f}p ({fmt_signed(s['chg_pct'], '%', 2)})")
    lines.append("")
    lines.append("▣ <미구현/미지원>")
    lines.append("  KOSPI200 예상시가·괴리율: 동시호가 선물 예상체결 기반 산식 필요(시황팀 공식) — 별도")
    lines.append("  장초반 수급(억원): CHECK는 장중 '누적수량'만(대금 별도 산출 필요)")
    lines.append("  환율·해외지수: CHECK 범위 밖 → 외부 소스")
    return "\n".join(lines)


def fmt_signed(v: float, unit: str = "", dp: int = 0) -> str:
    return f"{v:+,.{dp}f}{unit}"


def render(date: str, blocks: list[dict], fut_blocks: list[dict] | None = None,
           macro: dict | None = None) -> str:
    dt = datetime.strptime(date, "%Y%m%d")
    lines = [f"[{dt.strftime('%Y-%m-%d')}({'월화수목금토일'[dt.weekday()]}) 장마감]  — CHECK API 재현", ""]

    lines.append("▣ <종합·시장별>")
    for b in blocks:
        if b.get("missing"):
            lines.append(f"  {b['label']}: 해당일 데이터 없음(휴장/미제공)")
            continue
        amt = f"{b['amount_jo']:.1f}조"
        if b["amount_delta_jo"] is not None:
            amt += f" (전일 {fmt_signed(b['amount_delta_jo'], '조', 1)})"
        if b.get("amount_unified_jo") is not None:
            amt += f" [통합 {b['amount_unified_jo']:.1f}조]"   # KRX+NXT
        lines.append(f"  {b['label']:<7}{b['close']:>9,.2f}p ({fmt_signed(b['chg_pct'], '%', 2)})   거래 {amt}")

    if fut_blocks:
        lines.append("")
        lines.append("▣ <선물 최근월물>")
        for b in fut_blocks:
            if b.get("missing"):
                lines.append(f"  {b['label']}: 데이터 없음")
                continue
            lines.append(
                f"  {b['label']:<9}{b['close']:>9,.2f} ({fmt_signed(b['chg_pct'], '%', 2)})"
                f"  거래량 {b['volume']:,.0f}  베이시스 {fmt_signed(b['basis'], 'p', 2)}(이론 {fmt_signed(b['theory_basis'], 'p', 2)})"
            )

    lines.append("")
    lines.append("▣ <수급> 시장 투자자 순매수거래대금 (억원, F06511)")
    lines.append("  ※ 공표 시황과 집계기준(정규장/전체·잠정/확정) 차이로 값이 다를 수 있음")
    for b in blocks:
        if b.get("missing") or "flow" not in b:
            continue
        f = b["flow"]
        parts = "  ".join(f"({k}) {fmt_signed(v, '', 0)}" for k, v in f.items())
        lines.append(f"  {b['label']:<7}: {parts}")

    if macro:
        lines.append("")
        lines.append("▣ <기타 — 금리·환율·유가 (CHECK 실호출)>")
        if macro.get("usdkrw"):
            base = f" (기준율 {macro['usdkrw_base']:,.1f})" if macro.get("usdkrw_base") else ""
            lines.append(f"  원/달러   {macro['usdkrw']:,.1f}{base}")
        rates = []
        if macro.get("ktb3y") is not None:  rates.append(f"국채3년 {macro['ktb3y']:.3f}%")
        if macro.get("ktb10y") is not None: rates.append(f"국채10년 {macro['ktb10y']:.3f}%")
        if macro.get("us10y") is not None:  rates.append(f"US10년 {macro['us10y']:.3f}%")
        if rates:
            lines.append("  " + "  ".join(rates))
        cmdty = []
        if macro.get("dxy") is not None: cmdty.append(f"달러지수 {macro['dxy']:.2f}" + (f"({macro['dxy_time']})" if macro.get("dxy_time") else ""))
        if macro.get("wti") is not None: cmdty.append(f"WTI ${macro['wti']:.2f}" + (f"({macro['wti_time']})" if macro.get("wti_time") else ""))
        if cmdty:
            lines.append("  " + "  ".join(cmdty))

    lines.append("")
    lines.append("▣ <미지원 — 외부 소스/구독 필요>")
    lines.append("  위안/달러·Brent 유가: CHECK 범위 밖/구독(해외시세 패키지) 필요")
    lines.append("  해외지수(니케이·상해·대만·홍콩): 해외시세 패키지 구독 시 재현 가능")
    return "\n".join(lines)


def main() -> None:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="장마감 시황 요약(CHECK API 재현)")
    ap.add_argument("date", nargs="?", help="조회일 YYYYMMDD (장마감/장개시 모드에 필요)")
    ap.add_argument("--open", metavar="HHMM", help="장개시 모드: 해당 시각 장중 스냅샷(예: 0901)")
    ap.add_argument("--live", action="store_true", help="실시간 모드: 현재값 스냅샷(intra_info, KRX300 포함)")
    ap.add_argument("--json", action="store_true", help="원자료(dict)로 출력")
    args = ap.parse_args()

    if args.live:
        snaps = []
        for idx in INDICES:
            try:
                snaps.append(live_snapshot(idx))
            except RuntimeError as e:
                snaps.append({"label": idx["label"], "missing": True, "reason": str(e)})
        if args.json:
            print(json.dumps({"live": True, "snapshot": snaps}, ensure_ascii=False, indent=2))
        else:
            print(render_live(snaps))
        return

    if not args.date:
        ap.error("장마감/장개시 모드는 date(YYYYMMDD)가 필요합니다. 실시간은 --live 사용.")

    if args.open:
        target = int(args.open) * 10000  # HHMM -> HMMSSss (예: 0901 -> 9010000)
        snaps = []
        for idx in INDICES:
            try:
                snaps.append(open_snapshot(idx, args.date, target))
            except RuntimeError as e:
                snaps.append({"label": idx["label"], "missing": True, "reason": str(e)})
        if args.json:
            print(json.dumps({"date": args.date, "at": args.open, "snapshot": snaps}, ensure_ascii=False, indent=2))
        else:
            print(render_open(args.date, snaps, target))
        return

    blocks = []
    for idx in INDICES:
        try:
            blocks.append(index_block(idx, args.date))
        except RuntimeError as e:
            blocks.append({"label": idx["label"], "missing": True, "error": str(e)})
    fut_blocks = []
    for f in FUTURES:
        try:
            fut_blocks.append(futures_block(f, args.date))
        except RuntimeError as e:
            fut_blocks.append({"label": f["label"], "missing": True, "error": str(e)})
    try:
        macro = macro_block(args.date)
    except RuntimeError:
        macro = None
    if args.json:
        print(json.dumps({"date": args.date, "blocks": blocks, "futures": fut_blocks, "macro": macro},
                         ensure_ascii=False, indent=2))
    else:
        print(render(args.date, blocks, fut_blocks, macro))


if __name__ == "__main__":
    main()
