# 설치·사용 가이드 (checkapi-data 스킬)

이 스킬로 **실데이터**까지 쓰려면 **KOSCOM에 등록된 IP**의 PC에서 **Claude Code**로 실행해야 한다.
(등록 외 IP·클라우드·에이전트 샌드박스로 나가면 CHECK 서버가 인증을 거부한다.)

---

## 새 PC(같은 등록 IP)에서 세팅

### 준비물 (1회 설치)
- **Git**, **Python 3.x**(`python` 또는 `py` 명령), **Claude Code**
- 스킬 스크립트는 **표준 라이브러리만** 사용 → pip 설치 불필요.
  (단, `gen_python.py`가 생성하는 스니펫을 *실행*할 때만 `requests`/`pandas` 필요.)

### 절차

**1) 리포 가져오기**
```bash
git clone https://github.com/beaten-by-the-market/check-api-krx-dl.git
cd check-api-krx-dl
# 이미 있으면: git pull origin main
```
→ 스킬(`.claude/skills/checkapi-data`), 명세(`checkapi-specs.json`), 설정(`.claude/settings.json`)이 함께 온다.

**2) `.env` 생성 — ★ git에 없음, 직접 만들어야 함**
리포 **루트**에 `.env` 파일:
```
CHECK_CUST_ID=<10자리 고객번호>
CHECK_AUTH_KEY=<32자리 인증키>
```
기존 PC의 `.env` 값을 그대로 옮기면 된다. `.gitignore`에 있어 절대 커밋되지 않는다.

**3) 등록 IP 확인**
스크립트는 이 PC의 **공인 IP**로 CHECK 서버에 나간다. 그 IP가 KOSCOM 등록 IP와 같아야 한다
(같은 사무실/네트워크면 보통 동일). 확인:
```bash
python verify_checkapi.py        # success=True 가 나오면 IP·인증 정상
```

**4) Claude Code에서 스킬 인식**
새 PC의 Claude Code로 **이 리포 폴더를 열면**(`cd check-api-krx-dl` 후 `claude` 실행) `.claude/skills/checkapi-data`가
**자동 인식**된다(프로젝트 스킬). 확인: "코스피 지수 뽑아줘" 같은 요청 → 스킬 발동.

**5) 코드 카탈로그 캐시 생성 — `search_codes` 쓰려면 1회**
```bash
python .claude/skills/checkapi-data/scripts/cache_codes.py
```
→ `cache/code_catalog.json` 생성(gitignore라 PC마다 1회). 등록 IP에서 실행.

### 실행 시 핵심 주의 — 샌드박스 밖에서
실데이터 스크립트(`call_checkapi`·`market_brief`·`kosdaq_daily`·`short_daily`·`cache_codes`)는 **샌드박스 밖**에서 돌려야 한다.
- Claude Code의 Bash 기본 샌드박스는 **프록시 IP**로 나가 등록 IP가 아님 → 인증 거부.
  Claude에게 시키면 `dangerouslyDisableSandbox`로 실행하도록 SKILL.md에 명시돼 있고, 직접 터미널에서 `python …` 으로 돌리면 당연히 등록 IP로 나간다.
- **동시 연결 금지**: CHECK 서버는 IP당 동시 연결을 제한 → 멀티스레드/병렬 금지, 순차만.

### 요약 — `git pull` 후 추가로 필요한 것
| 항목 | git pull로 옴? | 추가 조치 |
|---|---|---|
| 스킬·명세·설정 | ✅ | — |
| **`.env`(인증키)** | ❌ | **직접 생성** |
| Python / Claude Code | ❌ | 설치 |
| 코드 캐시(`search_codes`용) | ❌ | `cache_codes.py` 1회 |
| 등록 IP | — | 같은 네트워크 확인(`verify_checkapi.py`) |

→ **`git pull` + `.env` 생성 + (선택) 캐시 1회** 면 새 PC에서 완전히 동작한다.

---

## claude.ai 웹에 올릴 경우 (제약 있음)

claude.ai 웹앱에도 스킬 업로드는 가능하나(Pro/Max/Team/Enterprise + 코드실행), **실데이터는 안 된다**:
claude.ai 코드실행 샌드박스는 **Anthropic 서버 IP**라 등록 IP가 아님 → 실호출이 전부 인증 거부된다.

| 스크립트 | claude.ai 웹 |
|---|---|
| `search_endpoints`·`search_fields`·`get_endpoint_spec`·`gen_python` (오프라인) | ✅ (specs 번들 시) |
| `call_checkapi`·`market_brief`·`kosdaq_daily`·`short_daily`·`cache_codes`·`search_codes`(캐시 필요) | ❌ IP 거부/캐시 없음 |

- 업로드하려면 `checkapi-specs.json`을 **스킬 폴더 안에 번들**하고 `_common.find_repo_root()`가 거기서 찾도록 수정,
  `.env`·`cache/`는 **제외**, SKILL.md가 폴더 안에 오도록 zip(30MB 미만).
- 결론: **실데이터까지 쓰려면 등록 IP 머신의 Claude Code가 정답.** claude.ai 웹은 "탐색·설명·코드생성" 오프라인 용도로만.
