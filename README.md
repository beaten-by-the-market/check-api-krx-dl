# CHECK API / kquant — 지식 베이스 + 시황 재현 스킬

KOSCOM CHECK API와 `kquant` 패키지를 다루기 위한 **지식 베이스**와, 그 위에서
한국 시장 데이터를 조회·분석하고 **KRX 시황 리포트를 재현**하는 **Claude Code 스킬**을 담은 저장소.

## 1. Claude Code 스킬 — `.claude/skills/checkapi-data/`

자연어로 "이런 걸 분석하고 싶다"고 하면 맞는 endpoint를 찾아 호출·결합해 주는 스킬.
모든 스크립트는 표준 라이브러리만 쓰며, **등록 IP 호스트에서 실행**해야 실데이터가 나온다
(서버가 IP·인증당 동시연결을 제한하므로 **멀티스레드 금지, 순차 호출**).

- **탐색/설명**: `search_endpoints.py`(의도→endpoint), `search_fields.py`(지표명→필드),
  `search_codes.py`(코드 카탈로그 검색: 지수·FX·해외금리·경제지표·종목 — `cache_codes.py`로 1회 캐시),
  `get_endpoint_spec.py`(파라미터·응답 F-code)
- **호출/생성**: `call_checkapi.py`(POST 실호출+F-code 디코딩), `gen_python.py`(실행가능 스니펫 생성)
- **시황 리포트 재현**(KRX PDF와 실측 대조 검증):
  - `market_brief.py <YYYYMMDD>` — 지수 3종·선물 3종·시장 수급 (KRX Brief). `--live`(실시간)·`--open HHMM`(장개시 스냅샷)
  - `kosdaq_daily.py <YYYYMMDD>` — 코스닥 지수·업종·투자자·종목동향·공매도·신용잔고
  - `short_daily.py <YYYYMMDD>` — 공매도 데일리 브리프(시장별·상위종목·과열종목·잔고 `--balance`)
- **참고문서** `references/`: `market-analysis.md`(시나리오→endpoint 치트시트, 지수/선물 코드, 재현 한계),
  `investor-codes.md`(투자자 번호 범례 — 지수레벨 vs 개별종목), `usage.md`(인증/IP/POST/동시연결 규칙),
  `news-gongsi-analysis.md`(공시·뉴스 결합 분석)

핵심 규칙: **POST + 요청 본문**(GET 거부), **등록 IP에서만**, 응답은 **F-code**(각 endpoint의 `res`가 디코더).

## 2. 지식 베이스 — `docs/`

- [docs/README.md](docs/README.md): 지식 베이스 인덱스, [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md): 폴더 가이드
- [checkapi-specs.json](checkapi-specs.json): CHECK API 명세 747개(기계판독)
- [kquant-docs.json](kquant-docs.json): kquant 함수/타입 96개
- [build-knowledge-docs.js](build-knowledge-docs.js): `docs/` 재생성 스크립트

## 3. 시황 리포트 재현 예시 — `시황리포트예시/`

KRX 원본 리포트(KRX Brief·코스닥 일일동향·공매도 데일리 브리프)와, CHECK API로 재생성한 결과를 담음.
- `체크api재생성/`: 재생성 리포트(md) — 재현값을 채우고, 못 채우는 값은 `[유형N]`으로 표기
- [체크api재생성/재현유형.md](시황리포트예시/체크api재생성/재현유형.md): 유형 범례
  (유형1=추가구독 시 재현가능, 유형2=데이터 부재, 유형3=당일 스냅샷, 유형4=근사, 유형5=산식 필요)

## 4. 참고

- [checkapi_bugreport_basic_info_all_port.txt](checkapi_bugreport_basic_info_all_port.txt):
  `basic_info_all_port`가 codelist에 영숫자 6자리 종목코드가 섞이면 실패하는 버그(KOSCOM 신고용)
- 인증정보(`.env`의 `CHECK_CUST_ID`/`CHECK_AUTH_KEY`)는 gitignore되어 커밋되지 않음.
