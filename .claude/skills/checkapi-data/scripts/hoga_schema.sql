-- hoga_schema.sql — 실시간 호가(10단계 order book) 적재용 PostgreSQL/TimescaleDB 스키마
-- 소스: CHECK API /stock/{fam}/hoga_info(_port)  (46필드: 10단계 매수/매도 호가+잔량+총잔량)
-- 거래소 패밀리: KRX m001(코스피)/m003(코스닥) · NXT m222/m223 · 통합 m224/m225
-- 실행:  psql -d marketdata -f hoga_schema.sql   (TimescaleDB 확장 설치돼 있어야 함)

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 호가 스냅샷: 1행 = (시각, 거래소, 종목)의 10단계 호가창 전체.
-- 호가 배열은 [1]=최우선. 가격/잔량 10단계를 배열로 담아 컬럼 폭발을 피한다.
CREATE TABLE IF NOT EXISTS hoga_book (
    ts          timestamptz NOT NULL,          -- 수집 시각(폴링 시점, 서버 로컬 KST)
    venue       text        NOT NULL,          -- 'krx' | 'nxt' | 'unified'
    market      text        NOT NULL,          -- 'kospi' | 'kosdaq'
    code        text        NOT NULL,          -- 단축코드 6 (F16013)
    isin        text,                           -- 국제표준코드 (F16012)
    ask_px      integer[]   NOT NULL,           -- 매도호가 1..10 (F14501..F14510)
    ask_qty     bigint[]    NOT NULL,           -- 매도호가잔량 1..10 (F14511..F14520)
    bid_px      integer[]   NOT NULL,           -- 매수호가 1..10 (F14531..F14540)
    bid_qty     bigint[]    NOT NULL,           -- 매수호가잔량 1..10 (F14541..F14550)
    ask_tot     bigint,                         -- 매도 10단계 잔량합 (F14565)
    bid_tot     bigint,                         -- 매수 10단계 잔량합 (F14567)
    ask_tot_d   bigint,                         -- 매도 잔량합 직전대비 (F14566)
    bid_tot_d   bigint,                         -- 매수 잔량합 직전대비 (F14568)
    PRIMARY KEY (venue, code, ts)
);

-- 하이퍼테이블: ts 기준 1일 청크. 대량 시계열을 자동 파티셔닝.
SELECT create_hypertable('hoga_book', 'ts',
       chunk_time_interval => interval '1 day', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_hoga_code_ts ON hoga_book (code, ts DESC);
CREATE INDEX IF NOT EXISTS idx_hoga_venue_ts ON hoga_book (venue, ts DESC);

-- 압축: 7일 지난 청크는 압축(호가는 반복이 많아 10~20x 압축률). segmentby=종목/거래소.
ALTER TABLE hoga_book SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'venue, code',
    timescaledb.compress_orderby   = 'ts DESC'
);
SELECT add_compression_policy('hoga_book', interval '7 days', if_not_exists => TRUE);

-- 보존: 원한다면 오래된 원본 자동 삭제(예: 90일). 필요 없으면 주석 처리.
-- SELECT add_retention_policy('hoga_book', interval '90 days', if_not_exists => TRUE);

-- 최우선(L1) 편의 뷰: 스프레드·중간가·호가불균형을 바로 쓸 수 있게.
CREATE OR REPLACE VIEW hoga_l1 AS
SELECT ts, venue, market, code,
       bid_px[1] AS bid1, ask_px[1] AS ask1,
       bid_qty[1] AS bid_qty1, ask_qty[1] AS ask_qty1,
       (ask_px[1] - bid_px[1])                                   AS spread,
       (ask_px[1] + bid_px[1]) / 2.0                             AS mid,
       CASE WHEN (bid_qty[1] + ask_qty[1]) > 0
            THEN (bid_qty[1] - ask_qty[1])::numeric / (bid_qty[1] + ask_qty[1])
       END                                                       AS imbalance_l1,
       ask_tot, bid_tot
FROM hoga_book;

-- 거래소 간 괴리 분석용 뷰: 같은 종목·시점의 KRX vs NXT vs 통합 중간가 비교(근접 매칭은 쿼리에서).
-- 예)  SELECT code, ts, venue, mid FROM hoga_l1 WHERE code='005930' ORDER BY ts, venue;

-- 적재 로그(선택): 폴링 라운드별 수집 건수/지연 기록.
CREATE TABLE IF NOT EXISTS hoga_ingest_log (
    run_ts     timestamptz NOT NULL DEFAULT now(),
    venue      text, market text,
    n_codes    integer, n_rows integer,
    latency_ms integer, note text
);
