-- NXT 애프터/프리 -> KRX 시초가 연구용 스키마 (MySQL 8.0, InnoDB)
--
-- 적재 규모 (2026-08-19 실측. 이전 주석의 추정치는 여러 항목에서 크게 빗나가 있었다)
--   nxt_tick     : 3.10억 행 · 21.7GB   (데이터 17.5 + 인덱스 4.2)
--   bar_1m       : 0.27억 행 ·  1.7GB
--   client_tick  : 0.02억 행 ·  0.3GB
--   nxt_expected : 32.8만 행           애프터 개장 단일가의 예상체결 시계열
--   nxt_universe : 23.4만 행
--   합계         : 약 23.7GB
--
--   빗나갔던 지점: nxt_tick 을 1.1억 행으로 봤는데 실제 3.10억이다. '보관창 67거래일분'을
--   전제했지만 실제로는 보관창 밖 구간까지 쌓여 있고, 만료 전에 받아둔 날이 계속 남는다.
--   bar_1m 은 반대로 1.4억 행 예상에 0.27억뿐이다 -- 틱이 한도를 다 써서 1분봉이 거의
--   못 돌았다. 디스크 25~35GB 추정만 우연히 맞았다(23.7GB).
--
--   앞으로: --missing 25,611건(06-08~08-07)을 다 받으면 약 3.6억 행이 순증해 7억 행 규모가
--   된다. 지금 21.7GB 에서 행당 약 70바이트이므로 +25GB 안팎을 예상한다.
--
--   mysql -u root -p < nxt_krx_schema.sql

CREATE DATABASE IF NOT EXISTS nxt_krx
  CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE nxt_krx;

-- ---------------------------------------------------------------- 거래일 달력
-- m002/hist_info(코스피 지수)에서 채운다. D+1(익일 KRX) 계산의 기준.
CREATE TABLE IF NOT EXISTS trading_day (
  trade_date DATE NOT NULL,
  seq        INT  NOT NULL,          -- 0부터 증가. 익일 = seq+1
  PRIMARY KEY (trade_date),
  UNIQUE KEY uk_seq (seq)
) ENGINE=InnoDB;

-- ------------------------------------------------------- NXT 일별 실거래 유니버스
-- nxt_universe.py 산출물(rank_invest_date 기반, 상폐 종목 포함).
-- 이 표의 (trade_date, code) 가 모든 수집의 드라이버다.
CREATE TABLE IF NOT EXISTS nxt_universe (
  trade_date DATE     NOT NULL,
  code       CHAR(6)  NOT NULL,
  market     ENUM('KOSPI','KOSDAQ') NOT NULL,   -- KRX 라우팅: KOSPI->m001, KOSDAQ->m003
  name       VARCHAR(64) NULL,                  -- 상폐 종목은 공란(코드는 정확)
  listed_now TINYINT(1)  NOT NULL DEFAULT 1,
  PRIMARY KEY (trade_date, code),
  KEY ix_code (code)
) ENGINE=InnoDB;

-- --------------------------------------------------------------- 수집 체크포인트
-- (job, code, trade_date) 1건 = API 1콜. 재개·완전성 검사·바이트 회계의 근거.
-- status: ok(적재) / empty(응답 비었음) / expired(보관창 밖·상폐 등 조회불가) / fail
--         retry(보관창 안인데 서버오류 -> 재시도 대기. n_rows 칸을 재시도 횟수 카운터로 사용,
--               RETRY_MAX 회 넘으면 expired 로 굳힌다)
CREATE TABLE IF NOT EXISTS ingest_log (
  job        VARCHAR(16) NOT NULL,   -- nxt_tick | krx_min | nxt_min
  code       CHAR(6)     NOT NULL,
  trade_date DATE        NOT NULL,
  status     ENUM('ok','empty','expired','fail','retry') NOT NULL,
  n_rows     INT         NOT NULL DEFAULT 0,
  n_bytes    INT         NOT NULL DEFAULT 0,
  msg        VARCHAR(200) NULL,
  done_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (job, code, trade_date),
  KEY ix_done (job, done_at)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------- NXT 체결(틱)
-- /stock/m222|m223/tick_date, data_list = F16604,F15019,F15001,F15020,F15022
-- 세션: 프리 08:00~08:50 / 메인 09:00~15:20 / 애프터 15:40~20:00
-- 보관: 최근 약 101일(달력)뿐 -> 지나가면 영구 소실. 최우선 수집 대상.
-- n   = API 응답 내 순번(0-based). 로컬 생성값. (trade_date, code) 단위 DELETE+INSERT 재적재를 멱등하게.
-- seq = F16604 종목별저장일련번호. KOSCOM 이 원본에서 매기는 단조증가 번호로, 응답 배열 순서(n)와
--       정확히 일치한다(실측, 중복 없음). ts 가 초 해상도뿐이라(센티초 미제공, API 한계) 같은 초에
--       몰린 체결의 순서는 이 seq(=n)로만 구분된다. 초기 15거래일치는 seq 를 안 받아 NULL.
CREATE TABLE IF NOT EXISTS nxt_tick (
  trade_date DATE         NOT NULL,
  code       CHAR(6)      NOT NULL,
  n          INT UNSIGNED NOT NULL,
  seq        INT UNSIGNED NULL,       -- F16604 종목별저장일련번호(KOSCOM 원순번)
  ts         INT UNSIGNED NOT NULL,   -- F15019 체결시간 HHMMSSss, 실질 초 해상도 (8000000 = 08:00:00)
  price      INT          NOT NULL,   -- F15001 현재가(체결가)
  qty        INT          NOT NULL,   -- F15020 체결량
  -- F15022 체결성향 1:B 2:BB 4:S 5:SS 9:대량 10:바스켓 11:신고대량 27:경매매.
  -- 명세에 없는 0 과 3 이 실제로 들어오고, 그 뜻이 수집 경로(src)마다 다르다:
  --   src=NULL(API)  3 = chg_type 69(실체결 아님)가 실리는 칸. side=3 중 69 아닌 행은 2.6%.
  --   src=1(캡처)    0 = chg_type 69. 캡처분에서 side=0 <-> 69 는 완전 동치다(예외 0건).
  --                  3 은 여기선 평범한 실체결이고 69 가 한 건도 없다(하루 275~324행).
  -- 경로를 안 보고 side=3 을 69 로 다루면 캡처분에서 조용히 틀린다.
  side       TINYINT      NULL,
  -- 체결 시점의 최우선 호가·잔량(2026-07-28 이후 수집분부터. 그 이전은 NULL).
  -- 체결가와 비교하면 매도호가를 친 체결인지/매수호가를 친 체결인지, 유효 스프레드가 얼마인지 나온다.
  ask1       INT          NULL,       -- F14501 매도호가1
  bid1       INT          NULL,       -- F14531 매수호가1
  ask_qty1   INT          NULL,       -- F14511 매도호가잔량1
  bid_qty1   INT          NULL,       -- F14541 매수호가잔량1
  -- F30614 등락구분(F15006 과 같은 코드계). 1:상한 2:상승 3:보합 4:하한 5:하락 6~9:기세류.
  -- 69 = 예상체결. 실체결이 아니므로 거래량·거래대금에서 제외한다.
  --
  -- 명칭 확정(2026-08-15): F30614 의 명세만 '69:예' 에서 잘려 있고, 같은 코드계 F15317 은
  -- 온전한 '69:예상체결' 이다(저장소 명세 전체에서 '69:예상체결' 66회 / 잘린 '69:예' 14회는
  -- 전부 F30614). 단말 대비 컬럼의 '예'도 예상(체결)의 줄임이다.
  --
  -- '기세'가 아니다. 기세는 당일 무거래 종목에만 성립하고 수량이 0이며 종목·일자당 값 하나인데,
  -- 69 는 실체결도 한 종목에 붙고 수량이 있고 종목당 평균 23행이다(2026-08-12 전수).
  --
  -- ★ 69 행에서는 ts/price/qty 가 '직전 실체결'의 값이다. API 한계가 아니라 필드 선택 탓이다
  --   (2026-08-15 확인). 응답 한 행에 계열이 병렬로 들어 있고 69 행에서는 뜻이 갈린다:
  --     F15019/F15001/F15020  체결시간·현재가·체결량  <- 우리가 저장. 69 에서는 직전 체결값
  --     F30531, F30612        체결/예상체결시간        <- 진짜 시각(15:30:00 ...)
  --     F15176, F15313, F30613  예상체결가
  --     F15308, F15314, F30618  예상체결량 (증분이라 음수가 나온다)
  --   F15308 을 누적하면 15:40:00 개장 단일가 체결량과 원 단위로 일치한다(zip 덤프 12/12).
  --     005930 2026-05-04: F15020 합 73,734(무의미) / F15308 합 46,993 = 개장 체결 46,993
  --   캡처 이관분(src=1)이 '다른 것'처럼 보였던 것도 원천 차이가 아니라, 그쪽 적재기가
  --   예상체결량 칸을 저장했기 때문이다. (side 는 실제로 다르다: API 3, 캡처 0.)
  --
  --   현재 저장분 기준 성질: 69 시각이 그 종목의 마지막 실체결보다 늦은 경우 0건(28거래일
  --   271,602행 전수). (일,종목)의 79.6%는 69 가 한 시각에만 몰린다. 어느 쪽이든 실체결이
  --   아니므로 거래량에서 빼는 처리는 그대로 맞다.
  --
  -- 두 경로 모두 69 를 빼면 nxt_daily 와 수량·금액이 원 단위로 맞는다(캡처 3일 100%,
  -- API 06-08 100%). 안 맞는 건 chg_type 미수신 (일,종목)뿐이다.
  -- API 수집분은 2026-08-11 이후 수집분부터, 캡처 이관분은 처음부터 채워진다.
  chg_type   SMALLINT     NULL,
  -- 출처. NULL = CHECK API REST 수집분(이 스크립트). 1 = 수집서버 1313 캡처 이관분
  -- (client_import/import_ticks.py). 이관분은 seq·mktcap 이 없고, 메시지 경계에서
  -- bid_qty1 이 흔들릴 수 있다(실측 종목당 0.6%, 다른 컬럼은 무결).
  -- ※ ROW_FORMAT=COMPRESSED 라 ALGORITHM=INSTANT 가 안 먹는다. 컬럼 추가는 INPLACE
  --   전체 재작성이다(269M행 기준 41분). 스키마 변경은 몰아서 한 번에 할 것.
  src        TINYINT      NULL,
  PRIMARY KEY (trade_date, code, n),
  KEY ix_code_ts (code, trade_date, ts)
) ENGINE=InnoDB ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8
-- 월 단위 파티션. 매일 INSERT 되는 3거래일치가 한 달 파티션에 모여, 갱신되는 세컨더리 인덱스가
-- 그 달치로 국한된다(전체 인덱스가 아니라). buffer pool 안에 hot 파티션이 들어와 INSERT 가 빠르다.
-- 분석 쿼리도 날짜 범위로 파티션 프루닝된다. (분기 파티션은 데이터가 2026Q2 한 칸에 몰려 무용지물이었음.)
PARTITION BY RANGE COLUMNS (trade_date) (
  PARTITION p202503 VALUES LESS THAN ('2025-04-01'),
  PARTITION p202504 VALUES LESS THAN ('2025-05-01'),
  PARTITION p202505 VALUES LESS THAN ('2025-06-01'),
  PARTITION p202506 VALUES LESS THAN ('2025-07-01'),
  PARTITION p202507 VALUES LESS THAN ('2025-08-01'),
  PARTITION p202508 VALUES LESS THAN ('2025-09-01'),
  PARTITION p202509 VALUES LESS THAN ('2025-10-01'),
  PARTITION p202510 VALUES LESS THAN ('2025-11-01'),
  PARTITION p202511 VALUES LESS THAN ('2025-12-01'),
  PARTITION p202512 VALUES LESS THAN ('2026-01-01'),
  PARTITION p202601 VALUES LESS THAN ('2026-02-01'),
  PARTITION p202602 VALUES LESS THAN ('2026-03-01'),
  PARTITION p202603 VALUES LESS THAN ('2026-04-01'),
  PARTITION p202604 VALUES LESS THAN ('2026-05-01'),
  PARTITION p202605 VALUES LESS THAN ('2026-06-01'),
  PARTITION p202606 VALUES LESS THAN ('2026-07-01'),
  PARTITION p202607 VALUES LESS THAN ('2026-08-01'),
  PARTITION p202608 VALUES LESS THAN ('2026-09-01'),
  PARTITION p202609 VALUES LESS THAN ('2026-10-01'),
  PARTITION p202610 VALUES LESS THAN ('2026-11-01'),
  PARTITION p202611 VALUES LESS THAN ('2026-12-01'),
  PARTITION p202612 VALUES LESS THAN ('2027-01-01'),
  PARTITION pmax    VALUES LESS THAN (MAXVALUE)
);

-- --------------------------------------------------------------------- 1분봉
-- /stock/{fam}/intra_date, data_list = F20004_02,F20005_02,F20006_02,F20007_02,F20008_02,F20010_02,F20011_02
-- venue KRX = m001/m003 (09:00~15:30, 382봉) / NXT = m222/m223 (08:00~20:00, 최대 691봉)
-- 소급 제한 없음(2025-03-24 확인). 거래 없는 분은 봉 자체가 오지 않는다.
CREATE TABLE IF NOT EXISTS bar_1m (
  venue      ENUM('KRX','NXT') NOT NULL,
  trade_date DATE         NOT NULL,
  code       CHAR(6)      NOT NULL,
  ts         INT UNSIGNED NOT NULL,   -- F20004_02 HHMMSSss (9010000 = 09:01)
  px_open    INT          NULL,       -- F20005_02
  px_high    INT          NULL,       -- F20006_02
  px_low     INT          NULL,       -- F20007_02
  px_close   INT          NULL,       -- F20008_02
  volume     BIGINT       NULL,       -- F20010_02 분거래량
  value      BIGINT       NULL,       -- F20011_02 분거래대금
  PRIMARY KEY (trade_date, venue, code, ts),
  KEY ix_code (code, trade_date, venue, ts)
) ENGINE=InnoDB ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8
PARTITION BY RANGE COLUMNS (trade_date) (
  PARTITION p2025h1 VALUES LESS THAN ('2025-07-01'),
  PARTITION p2025h2 VALUES LESS THAN ('2026-01-01'),
  PARTITION p2026h1 VALUES LESS THAN ('2026-07-01'),
  PARTITION p2026h2 VALUES LESS THAN ('2027-01-01'),
  PARTITION pmax    VALUES LESS THAN (MAXVALUE)
);

-- ------------------------------------------------- NXT 공식 일별 거래량·거래대금
-- 출처: nxt-data-api (nextrade.co.kr 거래현황). CHECK API 한도를 쓰지 않는다.
-- nxt_daily_load.py 가 채운다. 체결 데이터 검증의 기준선(정답지) 역할.
--
-- 왜 필요한가: 틱에는 chg_type=69(실체결 아님. 기세가 아니다 -- nxt_tick.chg_type 주석 참조)가
-- 섞여 SUM(qty)가 과대계상된다.
-- 이 표와 대조하면 69 제외가 제대로 됐는지 (거래일, 종목) 단위로 확인할 수 있고,
-- chg_type 을 못 받은 구간에서도 69 수량 = 틱합계 - 공식값 으로 총량을 보정할 수 있다.
--
-- 세션이 둘로 나뉜다: 정규시장(regular_market) + 종가매매(closing_price) = 그날 전체.
-- 종가매매를 빼먹으면 소액 잔차가 남는다(실측 066570 315주, 454910 29주).
CREATE TABLE IF NOT EXISTS nxt_daily (
  trade_date DATE    NOT NULL,
  code       CHAR(6) NOT NULL,
  market     ENUM('KOSPI','KOSDAQ') NULL,   -- mktId STK/KSQ
  name       VARCHAR(64) NULL,
  reg_qty    BIGINT  NULL,                  -- 정규시장 거래량
  reg_val    BIGINT  NULL,                  -- 정규시장 거래대금
  cls_qty    BIGINT  NULL,                  -- 종가매매 거래량
  cls_val    BIGINT  NULL,                  -- 종가매매 거래대금
  qty        BIGINT  NULL,                  -- reg_qty + cls_qty (대조에 쓰는 값)
  val        BIGINT  NULL,                  -- reg_val + cls_val
  PRIMARY KEY (trade_date, code)
) ENGINE=InnoDB;

-- ----------------------------------------------- 애프터 개장 단일가의 예상체결 시계열
-- 15:30~15:40 은 주문접수뿐이고 체결은 15:40 부터다. 그 10분 동안 거래소가 '지금 체결시키면
-- 얼마에 몇 주가 체결될지'를 계속 공표하는데, 그게 예상체결가·예상체결수량이다.
--
-- 왜 nxt_tick 에 컬럼을 안 붙였나
--   예상체결이 붙는 행은 chg_type=69 뿐이고 전체의 0.28%(818,559 / 295,911,441)다. 나머지
--   99.7%가 NULL 인 컬럼 셋을 296M행에 다는 셈이다. 게다가 ROW_FORMAT=COMPRESSED 라
--   컬럼 추가가 INPLACE 전체 재작성(41분+)이다. 옆 표로 두면 둘 다 피한다.
--
-- 어디서 오나 -- API 응답에 이미 들어 있는데 TICK_FIELDS 에 없어 버려지던 칸들이다.
--   F30531  체결/예상체결시간   진짜 시각. nxt_tick.ts(F15019)는 69 행에서 직전 체결 시각이다
--   F15176  예상체결가          실측상 예외 없이 그 시점 ask1 또는 bid1 중 하나다
--   F15308  예상체결량          증분이라 음수가 나온다. 누적합 = 15:40:00 개장 단일가 체결량
--                               (zip 덤프 12/12 원 단위 일치)
--
-- n 은 nxt_tick 과 같은 체계다(응답 배열의 0-based 인덱스). 조인해서 그 시점 호가를 붙일 수 있다.
CREATE TABLE IF NOT EXISTS nxt_expected (
  trade_date DATE         NOT NULL,
  code       CHAR(6)      NOT NULL,
  n          INT UNSIGNED NOT NULL,   -- nxt_tick.n 과 동일
  exp_ts     INT UNSIGNED NULL,       -- F30531 HHMMSSss
  exp_price  INT          NULL,       -- F15176
  exp_qty    INT          NULL,       -- F15308. 증분, 음수 가능
  PRIMARY KEY (trade_date, code, n)
) ENGINE=InnoDB;

-- ------------------------------------------------- chg_type 복원 이력 (한도 미사용)
-- nxt_chg_restore.py 산출물. 보관창(100일)을 지나 F30614 을 받을 수 없는 구간의
-- chg_type 을 nxt_daily 기준선 + 부분합으로 복원한다. 복원분과 API 수신분을 구분하려고
-- (거래일, 종목) 단위로 방법과 근거를 남긴다.
--
-- 대상은 API 수집분(src IS NULL)뿐이다. 캡처 이관분(src=1)은 chg_type 이 100% 차 있고
-- 69 가 side=0 에 실려 side=3 전제가 통하지 않는다 -- 복원기가 명시적으로 거부한다.
--
-- method: allside3  그 종목 side=3 행 전부가 69   (nxt_tick.chg_type 에 기록됨)
--         subset    부분합으로 69 행을 특정        (nxt_tick.chg_type 에 기록됨)
--         subsetdup subset 과 같되, 고른 행 중에 값이 같아 서로 바꿔도 무방한 행이 있다.
--                   API-69 는 95.6%가 중복행이라 '어느 행이냐'가 원리적으로 안 갈리는데,
--                   값이 동일하므로 어느 쪽을 골라도 모든 집계가 같다. (chg_type 에 기록됨)
--         ambiguous 수량·금액 조합이 서로 다른 해가 여럿 -> 행은 미상
--         qtyonly   전제 위반/후보 없음 -> 행은 미상
-- ambiguous·qtyonly 도 qty69/val69 는 정확하다. 틱 합계 - 공식값이라 언제나 성립한다.
-- 실측 정확도(2026-08-13, 정답 있는 8거래일 4,525표본): 행 확정 88.2%, 오답 0건.
CREATE TABLE IF NOT EXISTS restore_log (
  trade_date DATE    NOT NULL,
  code       CHAR(6) NOT NULL,
  method     VARCHAR(16) NOT NULL,
  n_rows     INT     NULL,           -- 69 로 확정한 행 수 (미상이면 NULL)
  qty69      BIGINT  NULL,           -- 그 (일,종목)의 69 거래량. 항상 정확
  val69      BIGINT  NULL,
  done_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (trade_date, code)
) ENGINE=InnoDB;

-- ------------------------------------------------------------ 분석용 세션 집계 뷰
-- NXT 세션 구분. 틱 시각(HHMMSSss)을 프리/메인/애프터로 나눈다.
-- 특수 마커 레코드(F15019 = 31000000 장마감 / 41000000 시간외마감 / 51000000 장전 등)와
-- 예상체결 레코드(ts=0, qty=0)는 제외한다.
CREATE OR REPLACE VIEW nxt_tick_session AS
SELECT
  trade_date, code, ts, price, qty, side, chg_type,
  CASE
    WHEN ts <  9000000 THEN 'PRE'      -- 08:00~08:50
    WHEN ts < 15300000 THEN 'MAIN'     -- 09:00~15:20
    ELSE                    'AFTER'    -- 15:40~20:00
  END AS session
FROM nxt_tick
WHERE qty > 0 AND ts BETWEEN 1 AND 23595999
  -- 69 는 실제 체결이 아니므로 제외한다(기세가 아니다 -- nxt_tick.chg_type 주석 참조).
  -- chg_type 이 NULL 이면 구분할 수 없어 포함된다. 다만 대부분은 nxt_chg_restore.py 가
  -- 복원해 두었으므로(행 확정 88.2%), 남은 NULL 은 '69 가 아니라고 판정된 행'이거나
  -- restore_log.method 가 ambiguous/qtyonly 인 종목의 행이다. 후자만 과대계상이 남는다.
  -- 그 종목의 정확한 69 수량은 restore_log.qty69 에 있으니 총량 분석은 그걸로 보정하면 된다.
  -- 어느 (일,종목)이 완결됐는지는 restore_log.method IN ('allside3','subset') 로 판별한다.
  AND (chg_type IS NULL OR chg_type <> 69);
