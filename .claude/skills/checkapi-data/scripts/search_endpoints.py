"""분석 의도/키워드로 CHECK API endpoint 후보를 찾는다.

사용법:
    python search_endpoints.py 일별 시세 주식
    python search_endpoints.py 시가총액 --domain stock --limit 10
    python search_endpoints.py 외국인 순매수 --json

- 검색 대상: endpoint 제목, apiurl, 도메인/패밀리, 파라미터명, 응답필드(F-code) 설명.
- 지표명(예: 시가총액, 등락률)으로도 매칭되도록 응답필드 설명까지 검색한다.
- 네트워크 호출 없음(로컬 명세만 읽음). 결과는 사람이 읽는 표 또는 --json.

이 스크립트는 '후보를 좁혀 주는' 도구다. 최종적으로 어떤 endpoint가
사용자의 분석 의도에 맞는지는 결과를 보고 판단해야 한다.
"""

from __future__ import annotations

import argparse
import json

from _common import all_specs, domain_family, market_name, _force_utf8_stdout


def score(spec: dict, tokens: list[str]) -> int:
    title = spec.get("title", "")
    apiurl = spec["apiurl"]
    dom, fam = domain_family(apiurl)
    res_desc = " ".join(r.get("desc", "") for r in spec.get("res", []))
    res_name = " ".join(r.get("name", "") for r in spec.get("res", []))
    params = " ".join(p.get("name", "") for p in spec.get("param", []))
    mkt = market_name(apiurl)   # 시장명(예: '국채30년 선물', '가상자산') — 제목엔 없는 시장명 매칭용

    title_l, apiurl_l = title.lower(), apiurl.lower()
    res_desc_l, res_name_l, params_l = res_desc.lower(), res_name.lower(), params.lower()
    dom_l, fam_l, mkt_l = dom.lower(), fam.lower(), mkt.lower()

    total = 0
    matched = 0
    for t in tokens:
        tl = t.lower()
        hit = False
        if tl in mkt_l:
            # 시장명 매칭은 강한 신호(제목이 일반명이라 시장명이 유일한 단서인 경우가 많음).
            total += 3
            hit = True
        if tl in title_l:
            total += 3
            hit = True
        if tl in res_desc_l:
            # 지표는 대개 응답필드 설명에 산다. 단, 제목(더 특정한 신호)보다는 낮게.
            total += 2
            hit = True
        if tl in apiurl_l or tl in fam_l or tl in dom_l or tl in params_l or tl in res_name_l:
            total += 1
            hit = True
        if hit:
            matched += 1
    if matched == 0:
        return 0
    if matched == len(tokens):
        total += 2  # 모든 토큰이 걸린 endpoint 우대
    return total


def main() -> None:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="CHECK API endpoint 검색")
    ap.add_argument("terms", nargs="*", help="검색어(공백으로 여러 개)")
    ap.add_argument("--domain", help="도메인 필터: stock/future/bond/ext/news/etc")
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    args = ap.parse_args()

    tokens = [t for t in args.terms if t.strip()]
    specs = all_specs()
    if args.domain:
        specs = [s for s in specs if domain_family(s["apiurl"])[0] == args.domain]

    if tokens:
        scored = [(score(s, tokens), s) for s in specs]
        scored = [(sc, s) for sc, s in scored if sc > 0]
        scored.sort(key=lambda x: (-x[0], x[1]["apiurl"]))
    else:
        # 검색어 없이 도메인만 준 경우: 그 도메인 목록을 그대로 보여준다.
        scored = [(0, s) for s in sorted(specs, key=lambda s: s["apiurl"])]

    rows = []
    for sc, s in scored[: args.limit]:
        dom, fam = domain_family(s["apiurl"])
        req = [p["name"] for p in s.get("param", []) if p.get("req") == "O"]
        opt = [p["name"] for p in s.get("param", []) if p.get("req") != "O"]
        rows.append({
            "score": sc,
            "apiurl": s["apiurl"],
            "title": s.get("title", ""),
            "market": market_name(s["apiurl"]),
            "domain": dom,
            "family": fam,
            "required": [p for p in req if p not in ("cust_id", "auth_key")],
            "optional": opt,
            "res_count": len(s.get("res", [])),
        })

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    if not rows:
        print(f"'{' '.join(tokens)}' 에 맞는 endpoint를 찾지 못했습니다. 검색어를 바꿔보세요.")
        return

    print(f"검색어: {' '.join(tokens) or '(도메인 목록)'}  |  후보 {len(rows)}개\n")
    for i, r in enumerate(rows, 1):
        extra = ", ".join(r["required"]) or "-"
        mkt = f"  ◀ {r['market']}" if r.get("market") else ""
        print(f"{i:>2}. {r['apiurl']}")
        print(f"     제목: {r['title']}  [{r['domain']}/{r['family']}]{mkt}  응답필드 {r['res_count']}개")
        print(f"     추가 필수 파라미터: {extra}")
    print("\n다음 단계: get_endpoint_spec.py <apiurl> 로 파라미터/응답형식을 확인하세요.")


if __name__ == "__main__":
    main()
