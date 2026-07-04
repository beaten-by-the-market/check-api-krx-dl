"""지표(응답 필드) 이름으로 어느 endpoint에 있는지 역방향으로 찾는다.

사용법:
    python search_fields.py 베이시스
    python search_fields.py 괴리율 --domain future --limit 15

왜 필요한가:
- endpoint 제목은 전부 일반명(기본정보/일별정보)이라, 특정 지표(베이시스·괴리율·신용융자 등)는
  '제목'이 아니라 '응답 필드 설명'에만 있다. search_endpoints(제목 위주)로는 놓치기 쉽다.
- 이 스크립트는 응답 필드 설명을 직접 뒤져 "그 지표가 있는 endpoint와 F-code"를 알려준다.
- '검색이 안 되니 없다'는 false-negative를 막는다. 여기서도 안 나오면 진짜 범위 밖에 가깝다.

네트워크·키 불필요.
"""

from __future__ import annotations

import argparse

from _common import all_specs, domain_family, _force_utf8_stdout


def main() -> None:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="응답 필드(지표) 역검색")
    ap.add_argument("term", help="지표명 일부 (예: 베이시스, 괴리율, 신용)")
    ap.add_argument("--domain", help="도메인 필터: stock/future/bond/ext/news/etc")
    ap.add_argument("--limit", type=int, default=20, help="보여줄 endpoint 수")
    args = ap.parse_args()

    needle = args.term.lower()
    hits = []  # (endpoint, [(fcode, desc), ...])
    for s in all_specs():
        if args.domain and domain_family(s["apiurl"])[0] != args.domain:
            continue
        matched = [(f.get("name", ""), f.get("desc", "")) for f in s.get("res", [])
                   if needle in (f.get("desc", "") or "").lower()]
        if matched:
            hits.append((s["apiurl"], s.get("title", ""), matched))

    hits.sort(key=lambda h: (-len(h[2]), h[0]))

    if not hits:
        print(f"'{args.term}' 를 응답 필드에서 찾지 못했습니다. → CHECK API 범위 밖일 가능성이 높습니다.")
        print("  (환율/FX·VI·지수값·코스피200 등 확인된 범위 밖 목록은 references/market-analysis.md 참조)")
        return

    total_ep = len(hits)
    print(f"'{args.term}' 를 가진 endpoint {total_ep}개 (필드 매치 많은 순)\n")
    for apiurl, title, matched in hits[: args.limit]:
        dom, fam = domain_family(apiurl)
        print(f"- {apiurl}  [{title}]  ({len(matched)}개 필드)")
        for fcode, desc in matched[:4]:
            print(f"    {fcode} = {desc}")
        if len(matched) > 4:
            print(f"    ... 외 {len(matched) - 4}개")
    if total_ep > args.limit:
        print(f"\n... 총 {total_ep}개 endpoint 중 {args.limit}개 표시 (--limit 로 조정)")
    print("\n다음 단계: get_endpoint_spec.py <apiurl> 로 파라미터/전체 필드를 확인하세요.")


if __name__ == "__main__":
    main()
