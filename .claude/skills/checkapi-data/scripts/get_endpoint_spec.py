"""endpoint 하나의 호출 형식(파라미터)과 응답 형식(F-code 필드)을 출력한다.

사용법:
    python get_endpoint_spec.py /stock/m001/hist_info
    python get_endpoint_spec.py hist_info        # 부분 일치 시 후보 나열
    python get_endpoint_spec.py /stock/m001/hist_info --json

- 네트워크 호출 없음. 사용자에게 "이 endpoint를 이렇게 호출하고 이런 응답이 온다"를
  설명하기 위한 근거 자료를 제공한다.
"""

from __future__ import annotations

import argparse
import json

from _common import all_specs, domain_family, find_spec, normalize_apiurl, _force_utf8_stdout


def resolve(apiurl: str) -> dict | list[dict]:
    apiurl = normalize_apiurl(apiurl)
    exact = find_spec(apiurl)
    if exact:
        return exact
    n = apiurl.lower().strip("/")
    cands = [s for s in all_specs() if n in s["apiurl"].lower()]
    if len(cands) == 1:
        return cands[0]
    return cands


def main() -> None:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description="CHECK API endpoint 스펙 조회")
    ap.add_argument("apiurl", help="apiurl (정확값 또는 부분 문자열)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    res = resolve(args.apiurl)
    if isinstance(res, list):
        if not res:
            print(f"'{args.apiurl}' 에 해당하는 endpoint가 없습니다.")
        else:
            print(f"'{args.apiurl}' 부분 일치 후보 {len(res)}개 — 정확한 apiurl로 다시 조회하세요:")
            for s in res[:30]:
                print(f"  {s['apiurl']}  ({s.get('title','')})")
        return

    spec = res
    if args.json:
        print(json.dumps(spec, ensure_ascii=False, indent=2))
        return

    dom, fam = domain_family(spec["apiurl"])
    print(f"# {spec['apiurl']}")
    print(f"제목: {spec.get('title','')}")
    print(f"도메인/패밀리: {dom}/{fam}   (type: {spec.get('type','')})")
    print(f"호출: POST https://checkapi.koscom.co.kr{spec['apiurl']}  (파라미터는 요청 본문)")

    print("\n## 입력 파라미터")
    for p in spec.get("param", []):
        req = "필수" if p.get("req") == "O" else "선택"
        print(f"  - {p['name']} ({p.get('type','')}, {req}): {p.get('desc','')}")

    print(f"\n## 응답 필드 ({len(spec.get('res', []))}개)  — 각 행의 키는 F-code")
    for r in spec.get("res", []):
        print(f"  - {r.get('name',''):<10} = {r.get('desc','')}  ({r.get('type','')})")

    if spec.get("err"):
        print("\n## 에러")
        for e in spec["err"]:
            print(f"  - {e.get('errmsg','')}: {e.get('detail','') or e.get('desc','')}")

    req_extra = [p["name"] for p in spec.get("param", [])
                 if p.get("req") == "O" and p["name"] not in ("cust_id", "auth_key")]
    example = "  ".join([f"{p}=..." for p in req_extra])
    print("\n## 실제 조회 예시")
    print(f"  python call_checkapi.py {spec['apiurl']} {example}".rstrip())


if __name__ == "__main__":
    main()
