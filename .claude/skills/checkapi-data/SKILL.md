---
name: checkapi-data
description: >
  KOSCOM CHECK API로 한국 자본시장 데이터를 조회·분석할 때 사용한다. 사용자가 API 명세를
  잘 모르는 상태에서 "이런 걸 분석하고 싶은데 어떤 데이터를 쓰지?", "삼성전자 일별 시세/거래량
  뽑아줘", 특정 지표(시가총액·외국인 순매수·등락률·채권 금리·파생 미결제 등)를 가져오려 할 때
  발동한다. 하는 일: (1) 분석 의도를 듣고 맞는 CHECK API endpoint 후보를 찾아주고, (2) 그
  endpoint를 어떤 파라미터로 호출하며 응답이 어떤 형식(F-code 필드)인지 설명하고, (3) 필요하면
  여러 endpoint를 실제로 호출·결합해 데이터까지 만들어 준다. 트리거: "CHECK API", "checkapi",
  "체크api", "kquant", 한국 주식/지수/ETF/채권/파생/FX/공시 데이터 조회, "어떤 endpoint",
  "무슨 API 써야". 한국 시장 데이터를 CHECK로 가져오려는 요청이면 단어가 정확히 없어도 적용한다.
---

# CHECK API Data (한국 자본시장 데이터 조회·분석)

이 스킬은 사용자가 **CHECK API 명세를 몰라도** 자연어로 분석 의도를 말하면,
맞는 endpoint를 찾아 **호출 방법과 응답 형식을 설명하고**, 원하면 **실제 데이터까지
(필요 시 여러 endpoint를 결합해) 조회**해 주기 위한 것이다.

지식 베이스와 스크립트는 모두 이 리포(`check-api-krx-dl`) 안에 있다. 스크립트는
표준 라이브러리만 쓰므로 별도 설치가 필요 없다. `python` 이 없으면 `py` 로 실행한다.

> **설치·등록 IP·`.env`·claude.ai 웹 제약 등 환경 세팅은 리포 루트 [SETUP.md](../../../SETUP.md) 참조.**
> 실데이터는 **KOSCOM 등록 IP** PC의 Claude Code(샌드박스 밖)에서만 나온다.

## 핵심 운영 규칙 (반드시 지킬 것)

1. **호출은 POST + 요청 본문.** GET/쿼리스트링은 자격증명이 맞아도 인증 거부된다.
   (스크립트가 이미 POST로 처리하므로 직접 curl 짜지 말 것.)
2. **실호출은 등록 IP에서만 된다.** 자격증명이 정확해도 등록 외 IP(사내 프록시,
   클라우드, **에이전트 샌드박스**)로 나가면 `cust_id 또는 auth_key가 정확하지 않습니다`로
   거부된다. 따라서 `call_checkapi.py` 는 **샌드박스 밖에서 실행**해야 한다
   (Claude Code Bash tool의 경우 `dangerouslyDisableSandbox: true`).
   `search_endpoints.py` / `get_endpoint_spec.py` 는 네트워크를 쓰지 않으므로 샌드박스 안에서 실행해도 된다.
3. **응답 필드는 F-code.** 각 endpoint의 `res` 정의가 F-code→한글 디코더다.
   `call_checkapi.py` 가 자동 디코딩한다.
4. **자격증명이 없으면** 명세 설명·호출 예시까지만 하고, 실데이터는 못 준다고 명확히 말한다.

## 표준 작업 흐름

### 1) 의도 파악
사용자의 분석 목적을 확인한다. 모호하면 딱 필요한 것만 되묻는다:
대상(종목/지수/업종/시장), 기간, 원하는 지표/관점(가격·거래량·수급·재무·파생 등).

### 2) endpoint 후보 찾기
`scripts/search_endpoints.py` 로 후보를 좁힌다. 지표명(예: `시가총액`, `외국인`,
`순매수`)이나 데이터 종류(예: `일별 시세`, `틱`, `재무`)를 검색어로 넣는다.

```bash
python .claude/skills/checkapi-data/scripts/search_endpoints.py 일별 시세 주식
python .claude/skills/checkapi-data/scripts/search_endpoints.py 외국인 순매수 --domain stock
```

스크립트는 후보만 좁혀 준다. **어느 것이 의도에 맞는지는 결과(제목·응답필드 수·도메인)를
보고 판단**한다. 도메인 감: `stock` 주식, `future` 파생, `bond` 채권, `ext` 해외,
`news` 뉴스/공시, `etc` 경제/기업/재무.

**endpoint 제목은 전부 일반명(`기본정보`/`일별정보`/`순위정보`)이고 실제 지표는 응답 필드에 산다.**
그래서 검색이 `기본정보(전체)` 류만 줄 때가 있는데, 이때는:
- "상위/순위"(거래대금·등락률·시총·거래량 상위) → `/stock/m001/rank` + `criteria_code`
- "개별종목 종합"(외국인보유율·상한가·시총 등) → `/stock/m001/basic_info_all`(150필드 만능)
- **특정 지표명(베이시스·괴리율·신용융자·과열·액면 등)** → `search_fields.py <지표>` 로 응답필드를 역검색.
  이 지표들은 제목엔 없고 **필드에만** 있어서 `search_endpoints`로는 안 잡힌다.
시황분석 질문은 먼저 `references/market-analysis.md`(시나리오→endpoint 치트시트)를 참조한다.

**"검색 안 됨" ≠ "없음" — "없음" 판정 전 4단계를 모두 확인한다.**
제목/필드 검색이 비어도 능력은 대개 **코드 카탈로그·파라미터·메뉴**에 숨어 있다(실전에서 지수·원달러·
해외금리·WTI를 이 단계 누락으로 "없음" 오판했다). 순서대로:
1. **필드** — `search_fields.py <지표>` (제목엔 없고 res 필드에만: 베이시스·과열 `F34989` 등).
2. **코드목록** — **`search_codes.py <키워드>`** 로 code_info/checkcode 카탈로그(35,340개)를 검색.
   **명세엔 없고 코드로만** 존재하는 능력이 여기 있다: 지수(m002/m004/m167)·지표물(`bond/m058/jipyo_list`)·
   원/달러(`bond/m023` 00USDSP)·해외금리(`bond/m025` GBUS10Y)·경제지표 30,316개(`USUST10YRD`·`USDXYD`·`USCOMCL1D`)·종목명↔코드.
   예: `search_codes.py 원달러` → `00USDSP`. (최초 1회 `cache_codes.py`로 캐시 생성 — 등록 IP·샌드박스 밖)
3. **파라미터·결합** — 날짜/코드로 되는지(국고채 = `jipyo_list edate` → `m038` F15175 수익률).
4. **메뉴맵** — 사람이 보는 메뉴명↔패밀리(외국환중개·해외금리·해외환율 등) → `references/market-analysis.md`.

4단계 모두 비면 그때 범위 밖(확정 부재: VI·VKOSPI·투자자예탁금·배당락/권리락·국내주식 배당/PER·
**Brent/두바이 유가·투자주체별 공매도** — 상세 `references/market-analysis.md`). ※ 해외 주가지수·위안/달러는 구독(유형1)으로 가능.

**"없음"은 잠정 판정 — 근거가 오면 반드시 재탐색한다.** (이 스킬 개발 중 "없음"이라 했다가
지수·원달러·과열·국채·US10년·WTI를 뒤늦게 찾은 게 6회+. "없음"은 절대 단정이 아니다.)
신호의 강도로 대응을 가른다:
- **CHECK API 자체 소스**(`checkapi.koscom.co.kr/intro`·명세·API 탐색기·live `code_info`/`checkcode`·단말 메뉴):
  **강한 신호 → 있으면 API에 있다.** 못 찾았으면 내 검색 방식 문제 → 필드·코드·파라미터·미탐색 endpoint·코드 변형으로
  **끝까지 다시 판다.** (intro 페이지는 checkapi-specs.json의 원천이므로 거기 보이면 반드시 존재.)
- **별개 상품**(Excel 프리미엄·타 단말기 매뉴얼): **약한 신호 — 카탈로그가 다를 수 있다.**
  힌트로만 쓰고, 코드체계가 API와 다를 수 있음을 감안(실측: Excel 원유코드 144xxx는 API에서 502).
- 사용자가 "공식 화면에서 봤다"고 하면 **반박하지 말고 그 단서(endpoint/필드/코드명)로 재조사**한다.

**지수 값은 된다(한때 오판했던 부분).** 코스피/코스닥 지수·업종 지수는 **m002(코스피)/m004(코스닥)**
레벨에서 조회한다: `m002/code_info`로 지수코드 확인(코스피 종합=`1`), `m002/hist_info jcode=<코드>`로
지수값·등락률·거래대금, `m002/invest_hist_info`로 시장 단위 투자자 수급. 상세 `references/market-analysis.md`.

### 3) 호출 형식·응답 형식 설명
고른 endpoint를 `scripts/get_endpoint_spec.py` 로 펼쳐, **필수/선택 파라미터와
응답 F-code 필드**를 사용자에게 설명한다. 이게 "어떻게 호출하고 무엇이 오는지" 답이다.

```bash
python .claude/skills/checkapi-data/scripts/get_endpoint_spec.py /stock/m001/hist_info
```

### 3.5) 산출물 제안 (endpoint 확정 직후 항상)
endpoint를 확정해 설명했으면, 한 줄로 산출물을 제안한다:

> "이 endpoint로 ① 출력 예시 ② 파이썬 코드 ③ CSV 저장 중 필요한 걸 만들어드릴까요?"

- **① 출력 예시** — 키 유무로 갈린다:
  - 키 없음 → `get_endpoint_spec.py` 의 응답 필드 정의로 **스키마 예시**를 보여주고 "실데이터 아님"을 명시.
  - 키 있음 → `call_checkapi.py ... --limit 3` 로 **진짜 샘플 행**.
- **② 파이썬 코드** — 손으로 쓰지 말고 `scripts/gen_python.py <apiurl>` 로 생성한다.
  해당 endpoint의 필수 파라미터·F-code 디코딩이 정확히 박힌 실행가능 스니펫이 나온다.

  ```bash
  python .claude/skills/checkapi-data/scripts/gen_python.py /stock/m001/invest_hist
  ```
- **③ CSV** — `call_checkapi.py ... --csv out.csv` (키 필요).

사용자가 특정 산출물만 원하면 그것만, "다 줘"면 셋 다 만든다. 키가 없으면 ②③ 중 ②(코드)는
그대로 주되 "실행하려면 인증키+등록 IP 필요"를 덧붙인다.

### 4) 실제 조회 (자격증명 + 등록 IP 있을 때)
`scripts/call_checkapi.py` 로 호출한다. F-code는 자동으로 한글 컬럼이 된다.
**샌드박스 밖에서 실행**할 것.

```bash
python .claude/skills/checkapi-data/scripts/call_checkapi.py \
  /stock/m001/hist_info jcode=005930 sdate=20250602 edate=20250605
```

큰 결과는 `--csv out.csv` 로 저장하고, 원본이 필요하면 `--raw` 또는 `--json` 을 쓴다.

### 5) 여러 endpoint 결합
한 endpoint로 답이 안 나오면 여러 개를 호출해 합친다. 계획을 먼저 세운다:
- **무엇을 각각 어디서** 가져올지 (endpoint별 역할)
- **어떤 키로 결합**할지 — 흔한 조인 키: 종목코드(`단축코드`/F16013, `jcode`), 일자(`입회일`/F12506, `sdate`/`edate`).
- 종목 리스트가 필요하면 보통 `.../code_info`(코드 목록) 계열을 먼저 호출해 코드를 얻고,
  그 코드로 상세/시세 endpoint를 반복 호출한다.

각 호출은 `call_checkapi.py ... --csv` 로 저장한 뒤 병합(공통 키 기준)해 최종 표/분석을 만든다.
루프 호출이 많으면 임시 스크립트를 만들어 돌려도 된다(같은 `_common` 모듈 재사용 가능).

### 5.5) 공시·뉴스 분석 (news/gongsi + 시세 결합)
공시(`/news/gongsi/*`)·뉴스(`/news/news/*`)를 시세·수급·공매도·대차·순위와 결합하는
이벤트 스터디/횡단면/시계열은 `scripts/news_gongsi_lab.py` 헬퍼로 바로 돌린다.
시나리오 지도·함정·실측 소견은 **`references/news-gongsi-analysis.md`** 참조(전부 실호출 검증됨).
```python
import news_gongsi_lab as lab   # scripts/ 에서 실행, 등록 IP·샌드박스 밖
lab.event_study("무상증자", "000500", "20260616", want_gongsi=True)  # 공시 이벤트 전후+종목 공시타임라인
lab.event_study("공매도과열", "058470", "20260612", want_short=True)
lab.news_stock_chunked("005930", "20260601", "20260703")     # 대형주 뉴스(502 회피용 분할)
lab.notable_movers("20260601", "20260703")                   # 시세→공시: 기간 주목주 발굴+공시
```
시세에서 시작하는(price-first) 스크리닝 러너: `python scenarios_price_first.py`(PS1~PS7: 등락률·거래대금·
변동성·거래대금급증·신고가·종합주목도 → 각 종목 공시목록). `rank`는 날짜 파라미터가 없어 당일 스크리너는 최신일만.
핵심 함정(상세는 레퍼런스): **시장 라우팅 m001(KOSPI)/m003(KOSDAQ)** — 종목코드만으론 구분 불가,
안 맞추면 코스닥이 빈 결과 · **뉴스엔 종목태그(NCD) 없음** → 종목뉴스는 `news_jong`만 ·
**대형주 뉴스 502** → 분할 조회 · 시장경보류 공시는 **장마감 후 발표**라 D0=이벤트일 이상 첫 거래일.

### 5.6) 펀더멘털 분석 (기업정보·IFRS·컨센서스 결합)
기업정보(`/etc/comp/*`)·IFRS 실제재무(`/etc/ifrs/*`)·컨센서스 추정(`/etc/cons/*`)을 서로/시세·수급와
결합하는 어닝서프라이즈·리비전·이벤트스터디·밸류에이션·지분구조는 `scripts/comp_fundamentals_lab.py`로 돌린다.
시나리오 지도·구조·함정은 **`references/comp-fundamentals-analysis.md`** 참조(전부 실호출 검증됨).
```python
import comp_fundamentals_lab as f    # scripts/ 에서 실행, 등록 IP·샌드박스 밖
f.earnings_surprise("005930","202512")           # CS1 컨센(발표직전) vs 실제 서프라이즈
f.estimate_revision("005930","202512","121500")  # CS2 추정 리비전(생성일자 시계열, 1주/1개월/3개월)
f.earnings_event_study("005930","202512")        # CS3 발표일 전후 주가·외국인/기관 수급
f.peer_valuation(["005930","000660"],"202512")   # CS4 피어 밸류에이션 횡단면(PER/PBR/ROE/OPM)
f.business_profile("005930"); f.ownership("005930","202412"); f.fundamental_trend("005930")  # CS5/6/7
# 전체 데모:  python comp_fundamentals_lab.py demo 005930 202512
```
핵심(상세는 레퍼런스): **TERM_TYP 1x=별도·3x=연결 / x1=누적·x2=분기**(밸류 표준=연결 31) ·
금액=**천원**(÷1e9=조), 비율(ROE/OPM)=**소수분수 ×100** · 컨센↔IFRS **계정코드 다름**(브리지 필요) ·
컨센은 **생성일자별 스냅샷=리비전 히스토리 내장** · **원거리 향후컨센 팽창**(sanity gate로 거름) ·
**목표주가·투자의견·리비전카운트·Fwd.12M은 이 피드 미제공**(빈 값) · 응답키 오타 `BB_COMM_RATE`·`TERM_TYPE`.

## 항상 지킬 답변 원칙
- endpoint를 고르면 **왜 그것인지**(제목/응답필드 근거)와 **파라미터·응답필드 의미**를 함께 설명한다.
- 후보가 여러 개면 차이를 짧게 비교해 사용자가 고르게 한다.
- 실호출 전, 어떤 파라미터로 부를지 사용자에게 한 번 확인한다(특히 기간·종목).

## 키 없이 답할 때(탐색·설명) 특히 보정할 것
키가 없으면 실데이터로 검증할 수 없어 명세 라벨만 보고 단정하다 틀리기 쉽다. 명세 전수 감사로
확인된 함정(핵심 케이스가 아니라 **전 endpoint에 걸친 패턴**):

- **보유(잔고) vs 흐름(거래/순매수) 혼동.** 개념마다 필드가 한쪽에 쏠려 있어, 원하는 쪽이
  없을 수 있다. 반드시 어느 쪽인지 구분해 답한다:
  - **외국인**: 필드는 전부 **보유**(보유율·보유주식수)뿐. **순매수(흐름)는 없다** → 투자자별
    `invest_hist`의 `F06508_11`로만 얻는다. `basic_info_all`의 외국인보유율을 순매수라 답하지 말 것.
  - **공매도**: 대부분 **거래/흐름**(수량·대금) + 잔고(공매도잔고·비중)도 있음.
  - **대차·신용융자**: 대부분 **잔고** 위주(거래/흐름 필드는 거의 없음).
- **번호/코드 전용 필드(_NN)는 범례 없이 단정 금지.** 투자자번호뿐 아니라 Intra 시간구간 등
  **번호로만 구분되는 필드군이 54개**다. 뜻이 확정된 건 `investor-codes.md`(투자자번호)뿐.
  나머지 `_NN`은 "번호별 의미는 키/Data-Set로 확인 필요"라 하고 지어내지 않는다.
- **`criteria_code`(정렬코드)는 부분목록만 안다.** rank 계열 등 **28개 endpoint**가 이걸 요구하는데
  전체 코드표는 Data-Set에 있다. `market-analysis.md`에 적힌 확인된 코드만 단정하고 나머지는 유보.
- **"검색 안 됨 ≠ 없음".** 제목 검색이 비면 `search_fields.py`로 필드까지 확인한 뒤에만 범위 밖 판정.
  베이시스·괴리율·차익/비차익·신용융자·과열·액면·상장폐지는 **필드엔 있다**(제목엔 없을 뿐).
- **명세 기준임을 밝힌다.** 키 없는 답은 "명세상 이 필드/파라미터가 있다"까지. 코드 의미·정확한
  값·정렬결과 구성은 "키로 검증 필요"로 남긴다.
- **순위(rank) 결과 구성 주의.** "상위"에 개별주식뿐 아니라 **ETF·레버리지·인버스가 섞여** 나온다(실측).
  "상위 종목"이라 뭉뚱그리지 말고 종류 필터가 필요함을 알린다.

## 자주 걸리는 함정: 투자자 구분은 번호다
투자자별 매매(`/stock/m001/invest_hist` 등)의 응답 필드는 투자자를 **이름이 아니라
번호(_01~_20)** 로 준다. "외국인 순매수" 같은 아주 흔한 질문이 명세 라벨만으로는 안 풀린다.
반드시 `references/investor-codes.md` 의 범례를 참조할 것. 핵심만:
**외국인 순매수 = `F06508_11`**, 기관 = `_08`, 개인 = `_10`, 전체 = `_12`.

## 참고 문서
- `references/market-analysis.md`: 시황분석 시나리오→endpoint 치트시트, rank/criteria_code, 범위 밖 목록
- `references/news-gongsi-analysis.md`: 공시·뉴스 분석 시나리오(이벤트스터디/횡단면/시계열·감성) 치트시트 + 결합 함정. 헬퍼 `scripts/news_gongsi_lab.py`
- `references/comp-fundamentals-analysis.md`: 기업정보·IFRS·컨센서스 결합(어닝서프라이즈/리비전/이벤트스터디/밸류에이션/지분구조) 치트시트 + 구조·함정. 헬퍼 `scripts/comp_fundamentals_lab.py`
- `references/investor-codes.md`: 투자자 구분 번호(1~20) → 이름 범례 (외국인/기관/개인 등)
- `references/usage.md`: 인증/IP제한/POST/F-code/결합 규칙 요약
- 리포 `docs/checkapi/`: endpoint 카탈로그·파라미터 사전·에러 가이드 (더 깊은 확인용)
- 리포 `docs/kquant/`: 파이썬 `kquant` 패키지로 대체 가능한 조회(주식/지수/펀드 등)
