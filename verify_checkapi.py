"""CHECK API 인증/호출 검증 스크립트 (등록 IP PC에서 직접 실행).

- .env에서 CHECK_CUST_ID / CHECK_AUTH_KEY를 읽는다 (외부 의존성 없음).
- 문서상 GET(quickstart)과 POST(예제 클라이언트) 두 방식을 모두 시도해
  어느 쪽이 실제로 통하는지 확정한다.
- 자격증명 값은 절대 그대로 출력하지 않는다 (마스킹).

실행:
    python verify_checkapi.py
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

BASE_URL = "https://checkapi.koscom.co.kr"
APIURL = "/stock/m001/hist_info"
PARAMS = {"jcode": "005930", "sdate": "20250602", "edate": "20250605"}


def load_env(path: str = ".env") -> dict[str, str]:
    env: dict[str, str] = {}
    if not os.path.exists(path):
        return env
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def mask(v: str) -> str:
    if len(v) <= 6:
        return "*" * len(v)
    return f"{v[:2]}{'*' * (len(v) - 4)}{v[-2:]}"


def summarize(body: bytes) -> str:
    try:
        d = json.loads(body.decode("utf-8"))
    except Exception:
        return f"[non-JSON] {body[:200]!r}"
    if isinstance(d, dict):
        keys = list(d.keys())
        if d.get("success") is False:
            return f"success=False  message={d.get('message') or d.get('errmsg')!r}"
        results = d.get("results", d)
        n = len(results) if isinstance(results, list) else 1
        first = results[0] if isinstance(results, list) and results else results
        return f"success={d.get('success')}  rows={n}  keys={keys}\n    first_row={json.dumps(first, ensure_ascii=False)[:300]}"
    return str(d)[:300]


def call(method: str, cust_id: str, auth_key: str) -> None:
    payload = {"cust_id": cust_id, "auth_key": auth_key, **PARAMS}
    print(f"\n=== {method} {APIURL} ===")
    try:
        if method == "GET":
            url = f"{BASE_URL}{APIURL}?{urllib.parse.urlencode(payload)}"
            req = urllib.request.Request(url)
        else:  # POST form body
            data = urllib.parse.urlencode(payload).encode()
            req = urllib.request.Request(f"{BASE_URL}{APIURL}", data=data)
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f"HTTP {resp.status}")
            print("  " + summarize(resp.read()))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}")
        print("  " + summarize(e.read()))
    except Exception as e:  # noqa: BLE001
        print(f"[error] {type(e).__name__}: {e}")


def main() -> None:
    env = load_env()
    cust_id = env.get("CHECK_CUST_ID") or os.environ.get("CHECK_CUST_ID", "")
    auth_key = env.get("CHECK_AUTH_KEY") or os.environ.get("CHECK_AUTH_KEY", "")
    if not cust_id or not auth_key:
        print("CHECK_CUST_ID / CHECK_AUTH_KEY 를 .env 또는 환경변수에서 찾지 못했습니다.")
        return
    print(f"cust_id={mask(cust_id)} (len={len(cust_id)})  auth_key={mask(auth_key)} (len={len(auth_key)})")
    call("POST", cust_id, auth_key)
    call("GET", cust_id, auth_key)
    print("\n둘 중 success=True 로 rows가 나오는 방식이 실제 규약입니다.")


if __name__ == "__main__":
    main()
