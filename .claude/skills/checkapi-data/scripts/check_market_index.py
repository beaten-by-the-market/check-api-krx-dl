# -*- coding: utf-8 -*-
"""드리프트 체크: _common.MARKET_NAMES(런타임 소스) ↔ docs/checkapi/market-index.md(사람용 문서).

두 곳에 손으로 유지하는 시장명↔코드 매핑이 어긋나지 않게 강제한다.
MARKET_NAMES의 모든 패밀리 코드가 문서에 들어 있는지 검사 → 없으면 exit 1.
(방식 'B-lite': 자동 생성은 안 하고, 어긋나면 커밋을 막는다. pre-commit 훅에서 호출.)

사용:  python check_market_index.py            # OK면 exit 0, 드리프트면 목록 출력 후 exit 1
"""
from __future__ import annotations
import sys
from _common import MARKET_NAMES, find_repo_root, _force_utf8_stdout


def find_missing() -> list[tuple[str, str]]:
    """market-index.md에 없는 (dom/fam, 시장명) 목록."""
    doc = (find_repo_root() / "docs" / "checkapi" / "market-index.md").read_text(encoding="utf-8")
    missing = []
    for key, label in MARKET_NAMES.items():
        fam = key.split("/", 1)[1]        # 'future/m221' -> 'm221', 'etc/cons' -> 'cons'
        if fam not in doc:                # 패밀리 코드가 문서에 등장하지 않으면 드리프트
            missing.append((key, label))
    return missing


def main() -> int:
    _force_utf8_stdout()
    missing = find_missing()
    if not missing:
        print(f"OK — MARKET_NAMES {len(MARKET_NAMES)}개 전부 market-index.md에 문서화됨.")
        return 0
    print("드리프트 감지: 아래 MARKET_NAMES 항목이 docs/checkapi/market-index.md에 없습니다.")
    print("→ _common.py의 MARKET_NAMES와 market-index.md를 동기화한 뒤 다시 커밋하세요.\n")
    for key, label in missing:
        print(f"  - {key}   ({label})")
    return 1


if __name__ == "__main__":
    sys.exit(main())