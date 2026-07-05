# 실시간 호가(KRX·NXT·통합) DB 적재 — 세팅·시나리오

CHECK API의 10단계 호가를 주기 폴링해 PostgreSQL/TimescaleDB에 적재하는 파이프라인.
스크립트 `scripts/hoga_ingest.py`, 스키마 `scripts/hoga_schema.sql`. (전부 실호출 검증, 2026-07)

## 거래소 패밀리 (실측 확정)
| 거래소 | 코스피 | 코스닥 | 비고 |
| --- | --- | --- | --- |
| **KRX(거래소)** | m001 | m003 | 기존 정규시장 |
| **NXT(넥스트레이드)** | m222 | m223 | 2025 출범 대체거래소 |
| **통합(KRX+NXT)** | m224 | m225 | 두 거래소 최선호가(SOR/NBBO성) |
| (업종·투자자) | m226·m228 | m227·m229 | NXT/통합 업종·투자자 |

호가 endpoint: `/stock/{fam}/hoga_info`(jcode 단건) · `hoga_info_port`(codelist 복수종목 1콜).
응답 46필드 = 10단계 매도/매수 호가·잔량 + 매도/매수 10단계잔량합·직전대비.
F-code: 매도호가 F14501~F14510, 매도잔량 F14511~F14520, 매수호가 F14531~F14540,
매수잔량 F14541~F14550, 매도총잔량 F14565, 매수총잔량 F14567, 직전대비 F14566/F14568,
단축코드 F16013, 국제표준코드 F16012.

**실측(2026-07 휴장일)**: 세 거래소 모두 `hoga_info_port` 응답(휴장엔 마지막 스냅샷). 예 —
삼성전자 KRX 매수 309,500/매도 310,000 vs **NXT 314,500/315,000**(≈1.6% 괴리), 통합은 NXT측 반영.
잔량합도 거래소별 상이(KRX ask_tot 1,219,054 vs NXT 313,048). spec의 `state=off`는 낡은 표기, 실제 작동.

## 핵심 제약 (설계 전제)
- **REST POST 스냅샷 — 스트리밍/웹소켓 없음.** "실시간"=주기 폴링(초 단위). 진짜 tick-by-tick·
  마이크로초 지연이 필요하면 CHECK가 아니라 거래소 직결 피드(멀티캐스트/FIX)로 가야 한다.
- **등록 IP·샌드박스 밖**에서만 실데이터. 사내 프록시/클라우드/에이전트 샌드박스로 나가면 인증 거부.
- **hoga_info엔 거래소 타임스탬프가 없다** → 수집시각(ts)을 서버에서 찍는다(폴링 시점 기준).
- **폴링 부하**: `hoga_info_port`는 복수종목을 1콜로 → 종목 N개를 한 번에. 라운드 지연 실측 ~0.15초/거래소.
  전종목(수천)·초 단위면 콜/부하가 커지므로 워치리스트·간격을 현실적으로 잡는다(아래 사이징).

## 세팅 순서
1. **DB**: PostgreSQL + TimescaleDB 확장. `psql -d marketdata -f hoga_schema.sql`
   → `hoga_book` 하이퍼테이블(1일 청크, 7일 후 압축, segmentby=venue,code) + `hoga_l1` 뷰(스프레드·중간가·불균형).
2. **.env** (등록 IP PC): `CHECK_CUST_ID` `CHECK_AUTH_KEY` + `PG_DSN=postgresql://user:pw@host:5432/marketdata`
3. **워치리스트** `watchlist.json`: `{"kospi":["005930","000660"],"kosdaq":["247540"]}`
4. **검증(네트워크·DB 불필요)**: `python hoga_ingest.py --selftest` → 46필드 파서·매핑 확인.
5. **배선 확인(등록 IP, 적재 없이)**: `python hoga_ingest.py --venues krx,nxt,unified --once --dry-run --ignore-session`
6. **실적재(장중)**: `python hoga_ingest.py --watchlist watchlist.json --venues krx,nxt,unified --interval 1.0`
   - `in_session()`이 평일 09:00~15:30만 폴링(NXT 연장시간 포함하려면 상한을 20:00로 조정).
   - 상시 구동은 서비스로: Windows=작업 스케줄러(장 시작 트리거)·nssm, Linux=systemd 유닛 또는 cron@09:00 기동/15:40 종료.

## 저장 사이징 (대략)
- 1스냅샷 ≈ 40개 정수(호가/잔량)+메타 → 압축 전 ~300~500B/행. 압축 후 호가 반복성으로 10~20x↓.
- 예: 종목 100 × 3거래소 × 1초 × 6.5시간 ≈ 700만 행/일 → 압축 전 ~2~3GB/일, 압축 후 ~150~300MB/일.
- 간격을 늘리거나(변화 시에만 적재), 관심종목만 좁히면 급감. `hoga_book`에 **직전과 동일 스냅샷 skip**
  로직을 추가하면(코드에서 last-hash 비교) 저장량이 크게 준다(대형주 제외 대부분 초당 무변화).

## 활용 시나리오 (적재 후)
- **거래소 간 괴리/차익**: 같은 종목의 KRX vs NXT 중간가·스프레드 시계열 → 괴리 확대 구간 탐지.
  `SELECT ts,venue,mid FROM hoga_l1 WHERE code='005930' ORDER BY ts,venue;`
- **호가 불균형(imbalance)**: `hoga_l1.imbalance_l1`(=(bid1-ask1잔량)/합) 시계열 → 단기 방향 신호.
- **유동성 프로파일**: 10단계 잔량합(ask_tot/bid_tot) 추이 → 매수/매도벽 형성·소멸.
- **플래시 이벤트 미시근거**: [flash-intraday-analysis.md]의 1분봉 급변과 호가창 붕괴를 결합.
- **통합 최선호가 검증**: 통합(m224/m225)이 실제로 KRX·NXT 최선을 반영하는지 교차검증.

## 함정
- **NXT 연장거래시간**: NXT는 정규장 외 시간대도 거래 → 스냅샷 시각이 KRX와 달라 괴리가 시간차일 수 있음.
  ts(수집시각)와 함께 거래소별 세션 시간을 감안해 해석.
- **state=off 메타데이터**에 현혹되지 말 것 — 실측으로 반환 확인됨. 단 장 국면·종목별로 빈 응답 가능성은
  장중 재확인.
- **psycopg2 필요**(적재 시). 없으면 `--dry-run`/`--selftest`는 동작(파싱만). 배포 시 `pip install psycopg2-binary`.
- 폴링 간격을 너무 촘촘히(같은 종목 <1초)면 API 부하·중복(ON CONFLICT DO NOTHING로 중복은 흡수).