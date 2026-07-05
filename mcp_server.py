"""로컬 MCP 서버 — CHECK API (Claude Desktop / Claude Code용, stdio 방식).

Claude Desktop config(`%APPDATA%\\Claude\\claude_desktop_config.json`)에 등록하면
앱이 이 프로세스를 **자동 실행**한다(수동 구동 불필요):

  {
    "mcpServers": {
      "checkapi": {
        "command": "python",
        "args": ["C:/Users/Peter/github/check-api-krx-dl/mcp_server.py"],
        "env": { "CHECK_CUST_ID": "<10자리>", "CHECK_AUTH_KEY": "<32자리>" }
      }
    }
  }

- **로컬 프로세스**라 CHECK 호출이 이 PC(등록 IP)로 나감 → 실데이터 OK.
- 자격증명은 config의 env 또는 리포 `.env`에서 읽는다(대화·클라우드로 안 감).
- 필요: `pip install mcp`

노출 툴: search_endpoints / get_endpoint_spec / call_checkapi / search_codes
(검증된 스킬 로직 재사용 — `.claude/skills/checkapi-data/scripts`)
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent / ".claude" / "skills" / "checkapi-data" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _common import (  # noqa: E402  스킬 공용 모듈 재사용
    all_specs, find_spec, normalize_apiurl, load_env, market_name, fcode_decoder, domain_family,
)
from search_endpoints import score as _ep_score  # noqa: E402
from search_codes import ALIAS as _CODE_ALIAS  # noqa: E402

BASE_URL = "https://checkapi.koscom.co.kr"
CACHE = SCRIPTS.parent / "cache" / "code_catalog.json"

try:
    from mcp.server.fastmcp import FastMCP
    _MCP = FastMCP("checkapi")
except ImportError:
    _MCP = None


# ── 실호출 (POST + F-code 디코딩) ──────────────────────────────
def _post(apiurl: str, params: dict) -> list[dict]:
    env = load_env()  # .env + os.environ(config env) 둘 다 커버
    cid, ak = env.get("CHECK_CUST_ID"), env.get("CHECK_AUTH_KEY")
    if not cid or not ak:
        raise RuntimeError("CHECK_CUST_ID/CHECK_AUTH_KEY 없음 — MCP config의 env 또는 리포 .env에 설정")
    payload = {"cust_id": cid, "auth_key": ak, **{k: v for k, v in params.items() if v is not None}}
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(f"{BASE_URL}{apiurl}", data=data)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            d = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}")
    if d.get("success") is False:
        raise RuntimeError(f"{d.get('message') or d.get('errmsg')} (등록 IP에서 실행 중인지 확인)")
    return d.get("results", []) or []


# ── 툴 코어 로직 (mcp 없이도 테스트 가능하도록 평범한 함수로) ──────────
def do_search_endpoints(query: str, domain: str = "") -> str:
    tokens = [t for t in query.split() if t.strip()]
    specs = all_specs()
    if domain:
        specs = [s for s in specs if domain_family(s["apiurl"])[0] == domain]
    scored = [(_ep_score(s, tokens), s) for s in specs] if tokens else [(0, s) for s in specs]
    scored = [(sc, s) for sc, s in scored if sc > 0 or not tokens]
    scored.sort(key=lambda x: (-x[0], x[1]["apiurl"]))
    top = scored[:15]
    if not top:
        return f"'{query}' 후보 없음. (없음 판정 전 search_codes로 코드 카탈로그도 확인)"
    out = []
    for sc, s in top:
        mkt = market_name(s["apiurl"])
        mk = f"  ◀ {mkt}" if mkt else ""
        req = [p["name"] for p in s.get("param", []) if p.get("req") == "O" and p["name"] not in ("cust_id", "auth_key")]
        out.append(f"{s['apiurl']}  [{s.get('title','')}]{mk}  필수:{','.join(req) or '-'}  응답필드 {len(s.get('res', []))}")
    return "\n".join(out)


def do_get_endpoint_spec(apiurl: str) -> str:
    apiurl = normalize_apiurl(apiurl)
    s = find_spec(apiurl)
    if not s:
        return f"'{apiurl}' endpoint 없음"
    L = [f"# {s['apiurl']}  {s.get('title','')}  ({s.get('type','')})", "## 파라미터"]
    for p in s.get("param", []):
        L.append(f"  {p['name']} ({p.get('type','')}, {'필수' if p.get('req')=='O' else '선택'}): {p.get('desc','')}")
    L.append(f"## 응답 필드({len(s.get('res', []))}) — 키는 F-code")
    for f in s.get("res", []):
        L.append(f"  {f.get('name',''):<12} = {f.get('desc','')}")
    return "\n".join(L)


def do_call_checkapi(apiurl: str, params: dict | None = None, limit: int = 20, decode: bool = True) -> str:
    apiurl = normalize_apiurl(apiurl)
    try:
        rows = _post(apiurl, params or {})
    except Exception as e:  # noqa: BLE001
        return f"[실패] {e}"
    spec = find_spec(apiurl)
    dec = fcode_decoder(spec) if (spec and decode) else {}
    shown = [({dec.get(k, k): v for k, v in r.items()} if dec else r) for r in rows[:limit]]
    return json.dumps({"apiurl": apiurl, "rows": len(rows), "shown": len(shown), "data": shown},
                      ensure_ascii=False, indent=2)


def do_search_codes(query: str, catalog: str = "") -> str:
    if not CACHE.exists():
        return "코드 캐시 없음 → 등록 IP에서 'python .claude/skills/checkapi-data/scripts/cache_codes.py' 1회 실행."
    entries = json.loads(CACHE.read_text(encoding="utf-8"))
    tokens = [t.lower() for t in query.split() if t.strip()]
    variants = [[t] + _CODE_ALIAS.get(t, []) for t in tokens]

    def sc(e):
        name, code = e["name"].lower(), e["code"].lower()
        tot = 0
        for vs in variants:
            if any(v in name for v in vs):
                tot += 3
            elif any(v in code for v in vs):
                tot += 1
            else:
                return 0
        return tot

    hits = [(sc(e), e) for e in entries]
    hits = [(s, e) for s, e in hits if s > 0 and (not catalog or catalog in e["catalog"])]
    hits.sort(key=lambda x: (-x[0], len(x[1]["name"])))
    top = [e for _, e in hits[:20]]
    if not top:
        return f"'{query}' 코드 없음(캐시 {len(entries):,}). 여기에도 없으면 범위 밖 가능성."
    return "\n".join(f"[{e['catalog']}] {e['code']}  {e['name']}\n    호출: {e['howto']}" for e in top)


# ── MCP 툴 등록 ────────────────────────────────────────────────
if _MCP is not None:
    @_MCP.tool()
    def search_endpoints(query: str, domain: str = "") -> str:
        """분석 의도/키워드로 CHECK API endpoint 후보를 찾는다(오프라인, 네트워크 불필요).
        domain 필터: stock/future/bond/ext/news/etc. 예: query='외국인 순매수', domain='stock'."""
        return do_search_endpoints(query, domain)

    @_MCP.tool()
    def get_endpoint_spec(apiurl: str) -> str:
        """endpoint의 필수/선택 파라미터와 응답 F-code 필드를 반환(오프라인). 예: apiurl='/stock/m001/hist_info'."""
        return do_get_endpoint_spec(apiurl)

    @_MCP.tool()
    def call_checkapi(apiurl: str, params: dict | None = None, limit: int = 20, decode: bool = True) -> str:
        """CHECK API를 실제 POST 호출해 데이터 반환. F-code→한글 컬럼 자동 디코딩(decode=False로 원본).
        등록 IP 로컬에서만 성공. 예: apiurl='/stock/m001/hist_info',
        params={'jcode':'005930','sdate':'20260703','edate':'20260703'}."""
        return do_call_checkapi(apiurl, params, limit, decode)

    @_MCP.tool()
    def search_codes(query: str, catalog: str = "") -> str:
        """코드 카탈로그(지수·지표물·FX·해외금리·경제지표·종목) 검색 — 명세에 없고 코드로만 존재하는 능력용.
        예: query='원달러'→bond/m023 00USDSP, 'WTI'→USCOMCL1D, '삼성전자'→005930. (cache_codes.py 캐시 필요)"""
        return do_search_codes(query, catalog)


if __name__ == "__main__":
    if _MCP is None:
        sys.exit("mcp 패키지가 필요합니다: pip install mcp")
    _MCP.run()  # 기본 stdio 전송 — Claude Desktop/Code가 자동 실행
