# CHECK API Domain: etc

Endpoint count: 26

## comp

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /etc/comp/comp_basic | 기업 기본정보 | cust_id, auth_key, jcode |  | 30 |
| /etc/comp/comp_comment | 기업소개 | cust_id, auth_key, jcode |  | 6 |
| /etc/comp/comp_holder | 기업 주주현황 | cust_id, auth_key, jcode, yyyymm |  | 10 |
| /etc/comp/comp_market | 기업 시장점유율 | cust_id, auth_key, jcode, yyyymm |  | 6 |
| /etc/comp/comp_market_hist | 기업 시장점유율 추이 | cust_id, auth_key, jcode |  | 6 |
| /etc/comp/comp_sales | 기업 매출액 구성비 | cust_id, auth_key, jcode, yyyymm |  | 5 |
| /etc/comp/comp_sales_hist | 기업 매출액 구성비 추이 | cust_id, auth_key, jcode |  | 5 |

## cons

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /etc/cons/comp_cons | 컨센서스 회계년도 전체 | cust_id, auth_key, jcode, yyyymm |  | 6 |
| /etc/cons/comp_cons_code | 컨센서스 계정코드 일람 | cust_id, auth_key |  | 10 |
| /etc/cons/comp_cons_hist | 컨센서스 계정별 추이 | cust_id, auth_key, jcode, icode | sdate, edate | 6 |
| /etc/cons/comp_cons_item | 컨센서스 회계년도 계정별 | cust_id, auth_key, jcode, yyyymm, icode |  | 6 |

## economic

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /etc/economic/checkcode | 경제지표 코드정보 | cust_id, auth_key |  | 15 |
| /etc/economic/indicator | 경제지표 | cust_id, auth_key, check_code | syear, eyear | 12 |

## gaap

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /etc/gaap/comp_gaap | GAAP 회계년도 전체 | cust_id, auth_key, jcode, yyyymm |  | 6 |
| /etc/gaap/comp_gaap_code | GAAP 계정코드 일람 | cust_id, auth_key |  | 12 |
| /etc/gaap/comp_gaap_hist | GAAP 계정별 추이 | cust_id, auth_key, jcode, icode | sdate, edate | 6 |
| /etc/gaap/comp_gaap_item | GAAP 회계년도 계정별 | cust_id, auth_key, jcode, yyyymm, icode |  | 6 |

## ifrs

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /etc/ifrs/comp_ifrs | IFRS 회계년도 전체 | cust_id, auth_key, jcode, yyyymm |  | 6 |
| /etc/ifrs/comp_ifrs_code | IFRS 계정코드 일람 | cust_id, auth_key |  | 12 |
| /etc/ifrs/comp_ifrs_hist | IFRS 계정별 추이 | cust_id, auth_key, jcode, icode | sdate, edate | 6 |
| /etc/ifrs/comp_ifrs_item | IFRS 회계년도 계정별 | cust_id, auth_key, jcode, yyyymm, icode |  | 6 |
| /etc/ifrs/comp_perf_date | 실적발표일 | cust_id, auth_key, jcode |  | 7 |

## trend

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /etc/trend/trend_bank | 금융기관 수신고 - 은행 | cust_id, auth_key, sdate, edate | dcnt | 4 |
| /etc/trend/trend_comp | 금융기관 수신고 - 종금 | cust_id, auth_key, sdate, edate | dcnt | 4 |
| /etc/trend/trend_inv | 금융기관 수신고 - 투신 | cust_id, auth_key, sdate, edate | dcnt | 8 |
| /etc/trend/trend_secu | 금융기관 수신고 - 증권사 | cust_id, auth_key, sdate, edate | dcnt | 3 |
