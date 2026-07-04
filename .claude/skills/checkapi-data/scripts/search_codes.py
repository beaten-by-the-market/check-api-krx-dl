"""코드 카탈로그(code_info/checkcode)를 키워드로 검색한다.

`search_endpoints`(제목)·`search_fields`(응답필드)가 못 보는 **'코드로만 존재하는' 능력**을 찾는다:
지수·지표물·FX·해외금리·경제지표(30,316개) 등. 이들은 명세에 없고 code_info/checkcode의 코드로만 있다.

사용법:
    python search_codes.py 원달러
    python search_codes.py WTI
    python search_codes.py US10년 국채
    python search_codes.py 삼성전자 --limit 5

전제: `cache_codes.py`를 1회 실행해 ../cache/code_catalog.json 을 만들어 둔다(네트워크 불필요, 오프라인 검색).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import _force_utf8_stdout

CACHE = Path(__file__).resolve().parent.parent / "cache" / "code_catalog.json"

# 한글 검색어 → 영어 코드/이름 별칭 (FX·지수 등은 이름이 영어라 한글로는 직접 안 걸림)
ALIAS = {
    "원달러": ["usdkrw", "usd-krw"], "달러원": ["usdkrw", "usd-krw"], "원/달러": ["usdkrw", "usd-krw"],
    "위안": ["cnh", "cny"], "위안달러": ["usdcny", "cnh"], "달러위안": ["usdcny", "cnh"],
    "엔": ["jpy"], "엔달러": ["usdjpy", "jpy"], "유로": ["eur"], "유로달러": ["eurusd", "eur"],
    "달러지수": ["달러화", "usdxy"], "달러인덱스": ["달러화", "usdxy"],
    "환율": ["-krw", "krw)"],
}


def main() -> None:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="코드 카탈로그 검색")
    ap.add_argument("terms", nargs="+", help="검색어(공백으로 여러 개)")
    ap.add_argument("--catalog", help="카탈로그 필터(부분일치): 지수/경제지표/해외금리/외국환 등")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not CACHE.exists():
        raise SystemExit(f"코드 캐시가 없습니다: {CACHE}\n먼저 'python cache_codes.py'를 등록 IP·샌드박스 밖에서 1회 실행하세요.")
    entries = json.loads(CACHE.read_text(encoding="utf-8"))

    tokens = [t.lower() for t in args.terms if t.strip()]
    # 각 토큰의 검색 후보(원문 + 별칭)
    variants = [[t] + ALIAS.get(t, []) for t in tokens]

    def score(e: dict) -> int:
        name = e["name"].lower()
        code = e["code"].lower()
        total = 0
        for vs in variants:  # 토큰마다: 이름 매치>코드 매치, 하나도 없으면 탈락
            if any(v in name for v in vs):
                total += 3
            elif any(v in code for v in vs):
                total += 1
            else:
                return 0
        return total

    hits = [(score(e), e) for e in entries]
    hits = [(sc, e) for sc, e in hits if sc > 0]
    if args.catalog:
        hits = [(sc, e) for sc, e in hits if args.catalog in e["catalog"]]
    hits.sort(key=lambda x: (-x[0], len(x[1]["name"])))
    top = [e for _, e in hits[: args.limit]]

    if args.json:
        print(json.dumps(top, ensure_ascii=False, indent=2))
        return
    if not top:
        print(f"'{' '.join(args.terms)}' 에 맞는 코드가 없습니다 (캐시 {len(entries):,}개). "
              "여기에도 없으면 CHECK API 범위 밖일 가능성이 높습니다.")
        return
    print(f"검색어: {' '.join(args.terms)}  |  매치 {len(hits)}개 중 상위 {len(top)}\n")
    for e in top:
        print(f"  [{e['catalog']}] {e['code']}  {e['name']}")
        print(f"      호출: {e['howto']}")
    if len(hits) > len(top):
        print(f"\n... 총 {len(hits)}개 (--limit 로 조정, --catalog 로 카탈로그 필터)")


if __name__ == "__main__":
    main()
