"""코스닥시장 일일동향(장종료 후 보고서) 재현 — EOD 배치.

사용법:
    python kosdaq_daily.py 20260703

- 등록 IP 호스트·샌드박스 밖에서 실행.
- hist 기반(지수·투자자·업종·공매도)은 과거일 조회 가능.
- 당일 스냅샷(종목동향 종목수·특징주)은 '그날 저녁 실행' 기준(basic_info/rank는 날짜 파라미터 없음).
- 신용잔고(시장 총계)는 지원한다: credit_historical()=정확(F14076 종목별 합산, 과거일 OK),
  sec_credit_approx()=당일 근사(--fast-credit). 달러-원도 bond/m023 00USDSP로 조회 가능(매크로 대시보드 참조).
  해외 주가지수(니케이·상해·항셍·대만·S&P500 등)·글로벌 금리도 economic으로 재현됨(정정) — 미국 다우/나스닥만 부재.
투자자 번호는 지수레벨(m004) 기준: 금융투자=1·투신=3·연기금=6·기관=8·개인=10·외국인=11
(개별종목 m001과 번호 체계가 다름 — 실측 확인).
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from _common import load_env, _force_utf8_stdout

BASE_URL = "https://checkapi.koscom.co.kr"
KOSDAQ = "1"  # m004 jcode: 코스닥 종합

INVESTORS = {  # 순매수거래대금(F06511_NN), 억원
    "외국인": "F06511_11", "기관": "F06511_08", "금융투자": "F06511_01",
    "투신": "F06511_03", "연기금": "F06511_06", "개인": "F06511_10",
}
# 업종지수(code_info)에서 '지수/파생상품' 성격을 걸러 전통 업종만 남기는 제외 패턴
_NON_SECTOR = re.compile(r"150|KRX|코스피|TR|NTR|레버|인버스|커버드|배당|ESG|초대형|비중상한|Governance|Leader|리츠|CSI|대형주|중형주|소형주|^KOSDAQ$")


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


def bulk_basic_info(codes: list[str]) -> list[dict]:
    """basic_info_all_port로 복수종목을 한 번에 조회 (숫자코드는 1,771개도 1회 OK).

    [코스콤 버그 우회 — 2026-07-04 신고, 수정 대기 중]
    basic_info_all_port(codelist)는 '영숫자 6자리' 종목코드(신형 코드: 스팩 + 최근 상장
    보통주 다수, 예: 0001A0 덕양에너젠)가 codelist에 하나라도 섞이면 배치 전체가
    {"success":false,"message":"Error while performing Query."}로 실패한다.
    - 대조: 동일 코드를 단일종목 endpoint(basic_info_all, jcode)로 조회하면 정상.
    - 즉 codelist 처리 경로 한정 버그. 상세는 리포 루트 checkapi_bugreport_*.txt 참조.

    대응(향후 자동 복원형):
      1) 먼저 '전체 코드'로 시도한다. → 코스콤이 수정하면 이 경로가 그대로 성공하여
         영숫자 종목까지 자동 포함된다(코드 수정 불필요).
      2) 실패하면(현재 상태) '숫자코드만' 남겨 재시도한다(영숫자 종목 누락 = 근사).
    """
    if not codes:
        return []
    try:
        # 낙관적 경로: 전체 포함. 버그 수정 후 이 줄이 그대로 정답이 됨.
        return post("/stock/m003/basic_info_all_port", codelist=",".join(codes))
    except RuntimeError:
        numeric = [c for c in codes if c.isdigit()]
        if len(numeric) == len(codes):
            raise  # 영숫자 이슈가 아니라면(전부 숫자) 그대로 전파
        # 폴백(버그 수정 전 임시): 영숫자 코드 제외하고 재시도 → 그 종목만 누락됨
        return post("/stock/m003/basic_info_all_port", codelist=",".join(numeric))


def _n(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def sec_index(date: str) -> dict:
    r = post("/stock/m004/hist_info", jcode=KOSDAQ, sdate=date, edate=date)
    if not r:
        return {}
    x = r[0]
    out = {
        "close": _n(x.get("F15001")), "chg": _n(x.get("F15472")), "chg_pct": _n(x.get("F15004")),
        "vol_eok": _n(x.get("F15015")) / 1e5,        # 천주 -> 억주
        "amt_jo": _n(x.get("F15023")) / 1e6,         # 백만원 -> 조원 (KRX)
        "cap_jo": _n(x.get("F15028")) / 1e12,        # 원 -> 조원
        "short_eok": _n(x.get("F33095")) / 1e8,      # 공매도거래대금(원) -> 억원
    }
    # 통합(KRX+NXT) 코스닥 거래대금 병기 — m229 hist_info(거래대금·거래량만). 지수값·등락률은 KRX.
    try:
        u = post("/stock/m229/hist_info", jcode=KOSDAQ, sdate=date, edate=date)
        if u:
            out["amt_unified_jo"] = _n(u[0].get("F15023")) / 1e6
    except Exception:
        pass
    return out


def sec_investor(date: str) -> dict:
    r = post("/stock/m004/invest_hist_info", jcode=KOSDAQ, sdate=date, edate=date)
    if not r:
        return {}
    x = r[0]
    return {name: _n(x.get(fc)) / 1e8 for name, fc in INVESTORS.items()}


def sec_breadth() -> dict:
    r = post("/stock/m004/basic_info", jcode=KOSDAQ)  # 당일 스냅샷(날짜 파라미터 없음)
    if not r:
        return {}
    x = r[0]
    return {"up": _n(x.get("F08002")), "down": _n(x.get("F08004")), "flat": _n(x.get("F08005")),
            "upper": _n(x.get("F08001")), "lower": _n(x.get("F08003"))}


def sec_sectors(date: str, n: int = 3) -> list[dict]:
    codes = post("/stock/m004/code_info")
    sectors = [c for c in codes if not _NON_SECTOR.search(str(c.get("F16002", "")))]
    out = []
    for c in sectors:
        try:
            r = post("/stock/m004/hist_info", jcode=str(c.get("F16013")), sdate=date, edate=date)
        except RuntimeError:
            continue
        if r:
            out.append({"name": c.get("F16002", ""), "chg_pct": _n(r[0].get("F15004"))})
    out.sort(key=lambda s: s["chg_pct"])
    return {"worst": out[:n], "best": out[-n:][::-1]}


def credit_historical(date: str, retries: int = 2) -> dict:
    """[기본] 정확 시장 신용융자잔고 — credit_hist_info를 종목별 순차 조회해 F14076 합산.

    - F14076(융자잔고금액)은 **금액 직접 제공**(단위: 천원) → 비율×시총 '환산' 절차가 없다.
      실측: 코스닥 전체 합 8.09조 ≈ 리포트 8.1조.
    - **과거일 조회 가능**(sdate=edate=date). 영숫자 코드도 단일 jcode라 정상(코스콤 _port 버그 무관).
    - **순차만** 사용(멀티스레드 금지 — 서버 동시연결 제한, references/usage.md). 전체 1,821종목 ≈ 약 2분.
    - 일시 실패분은 retries회 재시도로 보완.
    """
    codes = [str(c.get("F16013")) for c in post("/stock/m003/code_info") if c.get("F16013")]
    total_thousand = 0.0
    pending = codes
    for _ in range(retries + 1):
        still: list[str] = []
        for c in pending:
            try:
                r = post("/stock/m003/credit_hist_info", jcode=c, sdate=date, edate=date)
            except Exception:  # noqa: BLE001  RuntimeError + 간헐 SSL/네트워크 오류(서버가 가끔 연결 끊음) 모두 재시도 대상
                still.append(c)
                continue
            if r:
                total_thousand += _n(r[0].get("F14076"))
        pending = still
        if not pending:
            break
    return {"credit_jo": total_thousand / 1e9,  # 천원 합 -> 조원
            "covered": len(codes) - len(pending), "failed": len(pending)}


def sec_credit_approx() -> dict:
    """[옵션 --fast-credit] 당일 근사 신용잔고 = Σ(F14091 비율 × F15028 시총). 빠름(벌크 2.3초)이나 근사.

    금액 전용 필드가 없어 비율×시총 환산(근사, ~7.4조). basic_info_all_port는 당일 스냅샷.
    영숫자 코드는 코스콤 _port 버그로 폴백 시 누락 가능(bulk_basic_info 주석 참조).
    정확·과거일은 credit_historical(기본)을 쓸 것.
    """
    codes = [str(c.get("F16013")) for c in post("/stock/m003/code_info") if c.get("F16013")]
    rows = bulk_basic_info(codes)
    total = sum((_n(r.get("F14091")) / 100.0) * _n(r.get("F15028")) for r in rows)
    return {"credit_jo": total / 1e12, "covered": len(rows), "dropped": len(codes) - len(rows), "approx": True}


def sec_features(n: int = 3) -> list[dict]:
    try:
        r = post("/stock/m003/rank", up_code="1", criteria_code="F15004")  # 등락률(당일)
    except RuntimeError:
        return []
    rows = sorted(r, key=lambda x: -_n(x.get("F15004")))
    top = [{"name": x.get("F16002") or x.get("F16013"), "chg_pct": _n(x.get("F15004"))} for x in rows[:n]]
    # 휴장/미개장이면 rank 당일 등락률이 모두 0 → 무의미하므로 제외
    if not top or all(abs(t["chg_pct"]) < 0.01 for t in top):
        return []
    return top


def sign(v: float, dp: int = 0, unit: str = "") -> str:
    return f"{v:+,.{dp}f}{unit}"


def main() -> None:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="코스닥시장 일일동향 재현")
    ap.add_argument("date", help="조회일 YYYYMMDD")
    ap.add_argument("--fast-credit", action="store_true",
                    help="신용잔고를 당일 근사(비율×시총, 벌크 2.3초)로. 기본은 과거치 정확(순차 ~2분)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    idx = sec_index(args.date)
    inv = sec_investor(args.date)
    brd = sec_breadth()
    sct = sec_sectors(args.date)
    feat = sec_features()
    try:
        cred = sec_credit_approx() if args.fast_credit else credit_historical(args.date)
    except RuntimeError:
        cred = {}

    if args.json:
        print(json.dumps({"date": args.date, "index": idx, "investor": inv, "breadth": brd,
                          "sectors": sct, "features": feat, "credit": cred}, ensure_ascii=False, indent=2))
        return

    L = [f"[코스닥시장 일일동향 {args.date[:4]}.{args.date[4:6]}.{args.date[6:]}] — CHECK API 재현", ""]
    if idx:
        amt_txt = f"거래대금 {idx['amt_jo']:.1f}조"
        if idx.get("amt_unified_jo") is not None:
            amt_txt += f" [통합 {idx['amt_unified_jo']:.1f}조]"   # KRX+NXT
        L.append(f"▣ 지수  {idx['close']:,.2f}p {sign(idx['chg'], 2)}p ({sign(idx['chg_pct'], 2, '%')})"
                 f"   거래량 {idx['vol_eok']:.1f}억주  {amt_txt}  시총 {idx['cap_jo']:.2f}조")
    if inv:
        parts = "  ".join(f"{k} {sign(v)}" for k, v in inv.items())
        L.append(f"▣ 투자자(억원)  {parts}")
    if brd:
        L.append(f"▣ 종목동향  상승 {brd['up']:.0f}[상한 {brd['upper']:.0f}]  "
                 f"하락 {brd['down']:.0f}[하한 {brd['lower']:.0f}]  보합 {brd['flat']:.0f}")
    if feat:
        L.append("  특징주(등락률 상위, 당일): " + ", ".join(f"{f['name']}({sign(f['chg_pct'], 2, '%')})" for f in feat))
    if sct:
        L.append("▣ 업종  약세 " + ", ".join(f"{s['name']}({sign(s['chg_pct'], 2, '%')})" for s in sct["worst"]))
        L.append("        강세 " + ", ".join(f"{s['name']}({sign(s['chg_pct'], 2, '%')})" for s in sct["best"]))
    if idx:
        L.append(f"▣ 공매도금액  {idx['short_eok']:,.0f}억원")
    if cred:
        if cred.get("approx"):
            note = f" (영숫자코드 {cred['dropped']}종목 누락)" if cred.get("dropped") else ""
            L.append(f"▣ 신용융자잔고(당일 근사)  {cred['credit_jo']:.1f}조  [비율×시총, {cred['covered']}종목{note}]")
        else:
            note = f" (실패 {cred['failed']}종목)" if cred.get("failed") else ""
            L.append(f"▣ 신용융자잔고  {cred['credit_jo']:.2f}조  [credit_hist_info F14076, {cred['covered']}종목{note}]")
    L.append("")
    L.append("※ 신용잔고 기본=과거치 정확(F14076 금액, 환산 없음, 순차 ~2분). --fast-credit=당일 근사(비율×시총, 2.3초).")
    L.append("※ 해외증시·달러-원은 CHECK 범위 밖. 종목동향 종목수·특징주는 '당일' 스냅샷.")
    print("\n".join(L))


if __name__ == "__main__":
    main()
