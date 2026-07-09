# CHECK API 사용 규칙 요약 (스킬 참고용)

## 인증
- `.env` 에 `CHECK_CUST_ID`(10자리), `CHECK_AUTH_KEY`(발급 인증키).
- 스크립트가 자동 주입하므로 값을 직접 다루거나 출력하지 말 것.

## 호출 형식
- `POST https://checkapi.koscom.co.kr{apiurl}`, 파라미터는 **요청 본문**(form-urlencoded 또는 JSON).
- **GET/쿼리스트링 금지** — 자격증명이 맞아도 `{"success": false, "message": "cust_id 또는 auth_key가 정확하지 않습니다."}` 로 거부됨.

## IP 제한 (중요)
- 발급 시 등록한 IP에서만 호출 허용.
- 등록 외 IP(사내 프록시, 클라우드/컨테이너, **에이전트 샌드박스**)면 자격증명이 정확해도 위와 동일한 인증 실패로 응답.
- 즉 인증 실패 메시지는 "키 오류" 또는 "IP 미등록" 둘 다 의미할 수 있다.
- => 실호출 스크립트(`call_checkapi.py`)는 **등록 IP 호스트에서, 샌드박스 밖**으로 실행.

## 동시 호출(멀티스레드/병렬) 금지 — 순차만
- CHECK 서버는 **IP/인증당 동시 연결을 사실상 제한**한다. 병렬로 여러 요청을 동시에 보내면
  TCP는 수립되나 **동시 TLS/응답이 스톨**되어 대부분 타임아웃 실패한다.
- 실측(credit_hist_info 100종목): **8스레드 → 91% 실패**(평균 2,317ms) vs **1스레드 순차 → 안정**(63ms/건).
- 대량 종목 반복 조회도 **순차로 충분히 빠르다**: 전체 코스닥 1,821종목 순차 ≈ **115초(~2분)**.
- => ThreadPool/asyncio 동시요청 쓰지 말 것. 반복은 단일 연결 순차 루프로.

## 일 사용량 한도 = 1GB (중요, 실측)
- **1,000,000,000 bytes / 일, `cust_id` 단위**(IP 단위 아님 — 같은 고객번호를 공유하면 서로 갉아먹는다).
- 초과 시 모든 endpoint가 `일 최대 사용량 1,000,000,000Bytes를 초과했습니다.` 로 실패. 일 단위 리셋.
- **아껴야 할 자원은 호출 수가 아니라 응답 바이트다.** 실측 역전 사례: `rank_invest_date`(123필드)로
  662회 호출 = **1.1GB(한도 초과)** vs `hist_info`(22필드)로 2,652회 호출 = **175MB**.
- **`data_list` 로 필요한 F-code만 지정하면 수십 분의 1**이 된다(123필드→3필드: 1.1GB→48MB).
- ⚠ `data_list` 는 **존재하지 않는 F-code를 오류 없이 조용히 버린다.** 요청·반환 필드 개수를 대조할 것.
- ⚠ `data_list` 가 **명세에 없어도 동작하는 endpoint가 있다**(NXT 패밀리는 2/23만 문서화, 실제론 지원).

## rate limit
- **시계열 조회는 초당 1회.** 초과 시 `시계열 데이터의 조회는 1초에 1회로 제한됩니다.`
- `hist_info` 등 반복 호출은 **≥1.15초 간격**. (동시 호출 금지는 위 절 참조.)

## 응답 형식
- 성공: `{"success": true, "results": [ {F-code: 값, ...}, ... ]}`.
- 각 행의 키는 **F-code**. endpoint의 `res` 정의(`name`=F-code, `desc`=한글)가 디코더다.
- `call_checkapi.py` 가 자동으로 한글 컬럼으로 변환(원본은 `--raw`).
- 실패: `success: false` + `message`/`errmsg`. 사용자에게 그대로 전달.
- **`success:false` 를 빈 결과로 흘리지 말 것.** 한도 초과·rate limit은 **HTTP 200 + `success:false`** 로
  온다. `results or []` 로 처리하면 **"데이터 0건"으로 조용히 기록**된다(실제 사고: 코스닥 305일이 빈 값으로
  채워진 채 "완료" 출력). 예외로 올리고, 대량 수집 후엔 **커버 범위를 출력해 완전성을 검사**한다.

## 조회 범위 제한
- `rank_invest_date` 등 기간합산 계열: **조회기간 1년 초과 불가**(`param_denied`).
- 응답이 지나치게 크면 **HTTP 502**(1년치 단일 호출 등) → **월 단위로 분할**.

## 자주 쓰는 파라미터
| 이름 | 필수 | 의미 |
| --- | --- | --- |
| cust_id / auth_key | O | 자격증명(자동 주입) |
| jcode | 상황에 따라 O | 종목/업종 코드 |
| codelist | 일부 O | 복수 종목코드 리스트 |
| sdate / edate | 기간조회 O | 시작/종료일 `YYYYMMDD` |
| term | 일부 O | daily/weekly/monthly/quarterly/YTD/yearly |
| data_list | X | 조회할 F-code만 지정(미입력 시 전체) |
| dcnt | X | 데이터 개수 |

## 여러 endpoint 결합 시 조인 키
- 종목: `단축코드`(F16013) ↔ 다른 endpoint의 `jcode`.
- 일자: `입회일`(F12506) ↔ `sdate`/`edate`.
- 종목 목록이 먼저 필요하면 `.../code_info` 계열로 코드를 얻어 상세 endpoint를 반복 호출.

## 도메인
stock(주식) · future(파생) · bond(채권) · ext(해외) · news(뉴스/공시) · etc(경제/기업/재무)

## kquant 대안
주식/지수/펀드/일부 채권·FX는 파이썬 `kquant` 패키지로도 조회 가능(`docs/kquant/`). raw endpoint가 번거로울 때 검토.
