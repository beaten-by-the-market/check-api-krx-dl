"""checkapi-data 스킬 스크립트 공용 모듈.

- 리포 루트(checkapi-specs.json 이 있는 곳)를 상위 경로에서 자동 탐색.
- 명세(checkapi-specs.json) 로드/캐시.
- .env 에서 CHECK 자격증명 로드.
표준 라이브러리만 사용한다 (requests/pandas 불필요).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _force_utf8_stdout() -> None:
    # Windows 콘솔에서 한글이 깨지지 않게 UTF-8 강제.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "checkapi-specs.json").exists():
            return parent
    raise FileNotFoundError(
        "checkapi-specs.json 을 상위 경로에서 찾지 못했습니다. "
        "이 스킬은 check-api-krx-dl 리포 안에서 실행해야 합니다."
    )


_SPECS = None


def load_specs() -> dict:
    global _SPECS
    if _SPECS is None:
        with open(find_repo_root() / "checkapi-specs.json", encoding="utf-8") as fh:
            _SPECS = json.load(fh)
    return _SPECS


def all_specs() -> list[dict]:
    return load_specs()["specs"]


def find_spec(apiurl: str) -> dict | None:
    for s in all_specs():
        if s["apiurl"] == apiurl:
            return s
    return None


def search_specs_by_substring(needle: str) -> list[dict]:
    n = needle.lower()
    return [s for s in all_specs() if n in s["apiurl"].lower()]


def normalize_apiurl(arg: str) -> str:
    """apiurl 인자를 실제 값으로 정규화한다.

    - 선행 슬래시 유무를 흡수한다.
    - Git Bash(MSYS)가 '/stock/...' 를 'C:/Program Files/Git/stock/...' 로
      바꿔버린 경우, 실제 apiurl로 끝나는 것을 되찾는다.
    """
    a = arg.replace("\\", "/")
    if find_spec(a):
        return a
    cand = "/" + a.lstrip("/")
    if find_spec(cand):
        return cand
    matches = [s["apiurl"] for s in all_specs() if a.endswith(s["apiurl"])]
    if matches:
        return max(matches, key=len)
    return cand


def domain_family(apiurl: str) -> tuple[str, str]:
    parts = apiurl.strip("/").split("/")
    dom = parts[0] if parts else ""
    fam = parts[1] if len(parts) > 1 else ""
    return dom, fam


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    path = find_repo_root() / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("CHECK_CUST_ID", "CHECK_AUTH_KEY"):
        if not env.get(k) and os.environ.get(k):
            env[k] = os.environ[k]
    return env


def fcode_decoder(spec: dict) -> dict[str, str]:
    """endpoint 의 res 정의로 F-code -> 한글 설명 매핑을 만든다."""
    out: dict[str, str] = {}
    for r in spec.get("res", []):
        name = (r.get("name") or "").strip()
        desc = (r.get("desc") or "").strip()
        if name:
            out[name] = desc or name
    return out
