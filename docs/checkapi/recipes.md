# CHECK API Recipes

## 주식 종목 코드 목록

- KOSPI: `/stock/m001/code_info`
- KOSDAQ: `/stock/m003/code_info`
- 주요 파라미터: `cust_id`, `auth_key`

## 삼성전자 일봉

- endpoint: `/stock/m001/hist_info`
- 필수: `cust_id`, `auth_key`, `jcode=005930`, `sdate=YYYYMMDD`, `edate=YYYYMMDD`
- 대표 응답: 날짜(`F12506`), 단축코드(`F16013`), 현재가/시고저/거래량/거래대금

## 코스닥 종목 일봉

- endpoint: `/stock/m003/hist_info`
- 필수 파라미터는 KOSPI와 동일하고 시장 endpoint만 다르다.

## 호가/체결

- 호가: `/stock/m001/hoga_info`, `/stock/m003/hoga_info`
- 체결: `/stock/m001/tick_info`, `/stock/m003/tick_info`
- 일자별 체결: `/stock/m001/tick_date`, `/stock/m003/tick_date`

## 기간봉

- 주식: `/stock/m001/term_hist_info`, `/stock/m003/term_hist_info`
- `term`: `daily`, `weekly`, `monthly`, `quarterly`, `YTD`, `yearly`

## kquant에 없는 도메인

파생(`future`), 해외(`ext`), 뉴스/공시(`news`), 기타 재무/경제(`etc`)는 raw CHECK API 호출을 기본으로 한다. endpoint는 [endpoint-catalog.md](endpoint-catalog.md)에서 검색한다.
