-- NXT 애프터/프리 -> KRX 시초가 연구용 스키마 (MySQL 8.0, InnoDB)
--
-- 적재 규모 (2025-03-24 ~ 2026-07-10 기준 실측 추정)
--   nxt_universe : 약 21.5만 행   (거래일 318 x 일평균 675종목)
--   nxt_tick     : 약 1.1억 행    (보관창 67거래일분. 이후 매 거래일 +160만 행)
--   bar_1m       : 약 1.4억 행    (KRX 전기간 + NXT 틱보관창 이전 구간)
--   디스크       : 압축 적용 시 대략 25~35GB
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
CREATE TABLE IF NOT EXISTS ingest_log (
  job        VARCHAR(16) NOT NULL,   -- nxt_tick | krx_min | nxt_min
  code       CHAR(6)     NOT NULL,
  trade_date DATE        NOT NULL,
  status     ENUM('ok','empty','expired','fail') NOT NULL,
  n_rows     INT         NOT NULL DEFAULT 0,
  n_bytes    INT         NOT NULL DEFAULT 0,
  msg        VARCHAR(200) NULL,
  done_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (job, code, trade_date),
  KEY ix_done (job, done_at)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------- NXT 체결(틱)
-- /stock/m222|m223/tick_date, data_list = F15019,F15001,F15020,F15022
-- 세션: 프리 08:00~08:50 / 메인 09:00~15:20 / 애프터 15:40~20:00
-- 보관: 최근 약 101일(달력)뿐 -> 지나가면 영구 소실. 최우선 수집 대상.
-- n = API 응답 내 순번(0-based). 로컬 생성값이라 응답 바이트를 늘리지 않으면서
--     (trade_date, code) 단위 DELETE+INSERT 재적재를 멱등하게 만든다.
CREATE TABLE IF NOT EXISTS nxt_tick (
  trade_date DATE         NOT NULL,
  code       CHAR(6)      NOT NULL,
  n          INT UNSIGNED NOT NULL,
  ts         INT UNSIGNED NOT NULL,   -- F15019 체결시간 HHMMSSss (8000000 = 08:00:00.00)
  price      INT          NOT NULL,   -- F15001 현재가(체결가)
  qty        INT          NOT NULL,   -- F15020 체결량
  side       TINYINT      NULL,       -- F15022 체결성향 1:B 2:BB 4:S 5:SS 9:대량 10:바스켓 11:신고대량 27:경매매
  PRIMARY KEY (trade_date, code, n),
  KEY ix_code_ts (code, trade_date, ts)
) ENGINE=InnoDB ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8
PARTITION BY RANGE COLUMNS (trade_date) (
  PARTITION p2026q2 VALUES LESS THAN ('2026-07-01'),
  PARTITION p2026q3 VALUES LESS THAN ('2026-10-01'),
  PARTITION p2026q4 VALUES LESS THAN ('2027-01-01'),
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

-- ------------------------------------------------------------ 분석용 세션 집계 뷰
-- NXT 세션 구분. 틱 시각(HHMMSSss)을 프리/메인/애프터로 나눈다.
-- 특수 마커 레코드(F15019 = 31000000 장마감 / 41000000 시간외마감 / 51000000 장전 등)와
-- 예상체결 레코드(ts=0, qty=0)는 제외한다.
CREATE OR REPLACE VIEW nxt_tick_session AS
SELECT
  trade_date, code, ts, price, qty, side,
  CASE
    WHEN ts <  9000000 THEN 'PRE'      -- 08:00~08:50
    WHEN ts < 15300000 THEN 'MAIN'     -- 09:00~15:20
    ELSE                    'AFTER'    -- 15:40~20:00
  END AS session
FROM nxt_tick
WHERE qty > 0 AND ts BETWEEN 1 AND 23595999;
