# CHECK API Domain: stock

Endpoint count: 250

## m001

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m001/basic_info | 기본정보 | cust_id, auth_key, jcode | data_list | 12 |
| /stock/m001/basic_info_all | 기본정보(전체) | cust_id, auth_key, jcode | data_list | 150 |
| /stock/m001/basic_info_all_port | 기본정보(전체_복수종목) | cust_id, auth_key, codelist | data_list | 150 |
| /stock/m001/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist | data_list | 12 |
| /stock/m001/code_etf_info | 코드정보(ETF) | cust_id, auth_key | data_list | 6 |
| /stock/m001/code_etn_info | 코드정보(ETN) | cust_id, auth_key | data_list | 6 |
| /stock/m001/code_info | 코드정보 | cust_id, auth_key | data_list | 6 |
| /stock/m001/credit_hist_info | 신용잔고 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 22 |
| /stock/m001/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 23 |
| /stock/m001/hist_info_port | 일별정보 | cust_id, auth_key, codelist, edate | data_list | 23 |
| /stock/m001/hoga_info | 호가정보 | cust_id, auth_key, jcode | data_list | 82 |
| /stock/m001/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist | data_list | 82 |
| /stock/m001/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist | data_list | 10 |
| /stock/m001/intra_date | 주기정보(1분) | cust_id, auth_key, jcode, edate | data_list | 26 |
| /stock/m001/intra_info | 주기정보(10초) | cust_id, auth_key, jcode | data_list | 27 |
| /stock/m001/invest_hist | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 122 |
| /stock/m001/invest_info_port | 투자자 정보(복수종목) | cust_id, auth_key, codelist | data_list | 121 |
| /stock/m001/loan_hist_info | 대차잔고 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 10 |
| /stock/m001/mass_hist_info | 대량매매 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 35 |
| /stock/m001/member_date | 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - | 10 |
| /stock/m001/new_high | 신고가/신저가 | cust_id, auth_key, gubun | data_list | 13 |
| /stock/m001/program | 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  | 23 |
| /stock/m001/program_all | 프로그램매매-일중(전체) | cust_id, auth_key, edate |  | 22 |
| /stock/m001/program_all_basic | 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list | 19 |
| /stock/m001/program_basic | 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list | 26 |
| /stock/m001/rank | 순위정보 | cust_id, auth_key, up_code, criteria_code | data_list | 15 |
| /stock/m001/rank_invest | 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code | data_list | 121 |
| /stock/m001/rank_invest_date | 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | data_list, - | 123 |
| /stock/m001/rank_mass_date | 순위정보(대량매매-기간합산) | cust_id, auth_key, criteria_code, sdate, edate | - | 33 |
| /stock/m001/rank_short_date | 순위정보(공매도-기간합산) | cust_id, auth_key, criteria_code, sdate, edate | - | 7 |
| /stock/m001/short_hist_info | 공매도 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 10 |
| /stock/m001/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 17 |
| /stock/m001/tick_date | 체결정보 | cust_id, auth_key, jcode, edate |  | 36 |
| /stock/m001/tick_info | 체결정보 | cust_id, auth_key, jcode | order, dcnt | 37 |
| /stock/m001/upjong_info | 소속업종정보 | cust_id, auth_key, jcode |  | 2 |

## m002

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m002/basic_info | 기본정보 | cust_id, auth_key, jcode | data_list | 27 |
| /stock/m002/code_info | 코드정보 | cust_id, auth_key | data_list | 3 |
| /stock/m002/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 18 |
| /stock/m002/intra_date | 주기정보(1분) | cust_id, auth_key, jcode, edate | data_list | 13 |
| /stock/m002/intra_info | 주기정보(10초) | cust_id, auth_key, jcode | data_list | 14 |
| /stock/m002/invest_basic_info | 투자자 기본정보 | cust_id, auth_key, jcode | data_list | 121 |
| /stock/m002/invest_hist_info | 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 122 |
| /stock/m002/invest_intra_date | 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list | 122 |
| /stock/m002/invest_intra_info | 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list | 122 |
| /stock/m002/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate | data_list | 16 |
| /stock/m002/tick_info | 체결정보 | cust_id, auth_key, jcode | data_list | 30 |

## m003

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m003/basic_info | 기본정보 | cust_id, auth_key, jcode | data_list | 12 |
| /stock/m003/basic_info_all | 기본정보(전체) | cust_id, auth_key, jcode | data_list | 102 |
| /stock/m003/basic_info_all_port | 기본정보(전체_복수종목) | cust_id, auth_key, codelist | data_list | 102 |
| /stock/m003/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist | data_list | 12 |
| /stock/m003/code_info | 코드정보 | cust_id, auth_key | data_list | 6 |
| /stock/m003/credit_hist_info | 신용잔고 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 22 |
| /stock/m003/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 22 |
| /stock/m003/hoga_info | 호가정보 | cust_id, auth_key, jcode | data_list | 46 |
| /stock/m003/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist | data_list | 46 |
| /stock/m003/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist | data_list | 6 |
| /stock/m003/intra_date | 주기정보(1분) | cust_id, auth_key, jcode, edate | data_list | 19 |
| /stock/m003/intra_info | 주기정보(10초) | cust_id, auth_key, jcode | data_list | 20 |
| /stock/m003/invest_hist | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 122 |
| /stock/m003/invest_info_port | 투자자 정보(복수종목) | cust_id, auth_key, codelist | data_list | 121 |
| /stock/m003/loan_hist_info | 대차잔고 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 10 |
| /stock/m003/mass_hist_info | 대량매매 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 35 |
| /stock/m003/member_date | 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - | 10 |
| /stock/m003/new_high | 신고가/신저가 | cust_id, auth_key, gubun | data_list | 13 |
| /stock/m003/program | 기본정보 | cust_id, auth_key, jcode, edate |  | 23 |
| /stock/m003/program_all | 프로그램매매-일중(전체) | cust_id, auth_key, edate |  | 22 |
| /stock/m003/program_all_basic | 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list | 19 |
| /stock/m003/program_basic | 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list | 26 |
| /stock/m003/rank | 순위정보 | cust_id, auth_key, up_code, criteria_code | data_list | 15 |
| /stock/m003/rank_invest | 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code | data_list | 121 |
| /stock/m003/rank_invest_date | 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | data_list, - | 123 |
| /stock/m003/rank_mass_date | 순위정보(대량매매-기간합산) | cust_id, auth_key, criteria_code, sdate, edate | - | 33 |
| /stock/m003/rank_short_date | 순위정보(공매도-기간합산) | cust_id, auth_key, criteria_code, sdate, edate | - | 7 |
| /stock/m003/short_hist_info | 공매도 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 10 |
| /stock/m003/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate | data_list | 16 |
| /stock/m003/tick_date | 체결정보 | cust_id, auth_key, jcode, edate | data_list | 36 |
| /stock/m003/tick_info | 체결정보 | cust_id, auth_key, jcode | data_list, order, dcnt | 37 |
| /stock/m003/upjong_info | 소속업종정보 | cust_id, auth_key, jcode |  | 2 |

## m004

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m004/basic_info | 기본정보 | cust_id, auth_key, jcode | data_list | 27 |
| /stock/m004/code_info | 코드정보 | cust_id, auth_key | data_list | 3 |
| /stock/m004/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 18 |
| /stock/m004/intra_date | 주기정보(1분) | cust_id, auth_key, jcode, edate | data_list | 13 |
| /stock/m004/intra_info | 주기정보(10초) | cust_id, auth_key, jcode | data_list | 14 |
| /stock/m004/invest_basic_info | 투자자 기본정보 | cust_id, auth_key, jcode | data_list | 121 |
| /stock/m004/invest_hist_info | 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 122 |
| /stock/m004/invest_intra_date | 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list | 122 |
| /stock/m004/invest_intra_info | 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list | 122 |
| /stock/m004/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate | data_list | 16 |
| /stock/m004/tick_info | 체결정보 | cust_id, auth_key, jcode | data_list | 30 |

## m008

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m008/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 12 |
| /stock/m008/code_info | 코드정보 | cust_id, auth_key |  | 4 |
| /stock/m008/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 14 |
| /stock/m008/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 19 |
| /stock/m008/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 11 |
| /stock/m008/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 28 |

## m009

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m009/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 12 |
| /stock/m009/code_info | 코드정보 | cust_id, auth_key |  | 4 |
| /stock/m009/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 14 |
| /stock/m009/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 19 |
| /stock/m009/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 11 |
| /stock/m009/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 28 |

## m010

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m010/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 12 |
| /stock/m010/code_info | 코드정보 | cust_id, auth_key |  | 4 |
| /stock/m010/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 14 |
| /stock/m010/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 11 |
| /stock/m010/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 28 |

## m118

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m118/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 12 |
| /stock/m118/code_info | 코드정보 | cust_id, auth_key |  | 4 |
| /stock/m118/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 14 |
| /stock/m118/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 46 |
| /stock/m118/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 19 |
| /stock/m118/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 11 |
| /stock/m118/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 30 |

## m121

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m121/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 27 |
| /stock/m121/code_info | 코드정보 | cust_id, auth_key |  | 3 |
| /stock/m121/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 33 |
| /stock/m121/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 14 |
| /stock/m121/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 31 |
| /stock/m121/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 30 |

## m167

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m167/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 27 |
| /stock/m167/code_info | 코드정보 | cust_id, auth_key |  | 3 |
| /stock/m167/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 33 |
| /stock/m167/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 14 |
| /stock/m167/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 31 |
| /stock/m167/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 30 |

## m168

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m168/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 17 |
| /stock/m168/code_info | 코드정보 | cust_id, auth_key |  | 3 |
| /stock/m168/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 33 |
| /stock/m168/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 14 |
| /stock/m168/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 31 |
| /stock/m168/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 30 |

## m222

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m222/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 12 |
| /stock/m222/basic_info_all | 기본정보(전체) | cust_id, auth_key, jcode |  | 152 |
| /stock/m222/basic_info_all_port | 기본정보(전체_복수종목) | cust_id, auth_key, codelist |  | 152 |
| /stock/m222/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist |  | 12 |
| /stock/m222/code_info | 코드정보 | cust_id, auth_key |  | 6 |
| /stock/m222/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 22 |
| /stock/m222/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 46 |
| /stock/m222/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 46 |
| /stock/m222/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /stock/m222/intra_date | 주기정보(1분) | cust_id, auth_key, jcode, edate |  | 26 |
| /stock/m222/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 27 |
| /stock/m222/invest_info_port | 투자자 정보(복수종목) | cust_id, auth_key, codelist |  | 121 |
| /stock/m222/member_date | 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - | 10 |
| /stock/m222/program | 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  | 23 |
| /stock/m222/program_all | 프로그램매매-일중(전체) | cust_id, auth_key, edate |  | 22 |
| /stock/m222/program_all_basic | 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list | 19 |
| /stock/m222/program_basic | 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list | 26 |
| /stock/m222/rank | 순위정보 | cust_id, auth_key, criteria_code | up_code | 15 |
| /stock/m222/rank_invest | 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code |  | 121 |
| /stock/m222/rank_invest_date | 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | - | 123 |
| /stock/m222/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 16 |
| /stock/m222/tick_date | 체결정보 | cust_id, auth_key, jcode, edate |  | 36 |
| /stock/m222/tick_info | 체결정보 | cust_id, auth_key, jcode | order, dcnt | 37 |

## m223

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m223/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 12 |
| /stock/m223/basic_info_all | 기본정보(전체) | cust_id, auth_key, jcode |  | 152 |
| /stock/m223/basic_info_all_port | 기본정보(전체_복수종목) | cust_id, auth_key, codelist |  | 152 |
| /stock/m223/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist |  | 12 |
| /stock/m223/code_info | 코드정보 | cust_id, auth_key |  | 6 |
| /stock/m223/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 22 |
| /stock/m223/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 46 |
| /stock/m223/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 46 |
| /stock/m223/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /stock/m223/intra_date | 주기정보(1분) | cust_id, auth_key, jcode, edate |  | 26 |
| /stock/m223/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 27 |
| /stock/m223/invest_info_port | 투자자 정보(복수종목) | cust_id, auth_key, codelist |  | 121 |
| /stock/m223/member_date | 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - | 10 |
| /stock/m223/program | 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  | 23 |
| /stock/m223/program_all | 프로그램매매-일중(전체) | cust_id, auth_key, edate |  | 22 |
| /stock/m223/program_all_basic | 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list | 19 |
| /stock/m223/program_basic | 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list | 26 |
| /stock/m223/rank | 순위정보 | cust_id, auth_key, criteria_code | up_code | 15 |
| /stock/m223/rank_invest | 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code |  | 121 |
| /stock/m223/rank_invest_date | 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | - | 123 |
| /stock/m223/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 16 |
| /stock/m223/tick_date | 체결정보 | cust_id, auth_key, jcode, edate |  | 36 |
| /stock/m223/tick_info | 체결정보 | cust_id, auth_key, jcode | order, dcnt | 37 |

## m224

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m224/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 12 |
| /stock/m224/basic_info_all | 기본정보(전체) | cust_id, auth_key, jcode |  | 152 |
| /stock/m224/basic_info_all_port | 기본정보(전체_복수종목) | cust_id, auth_key, codelist |  | 152 |
| /stock/m224/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist |  | 12 |
| /stock/m224/code_info | 코드정보 | cust_id, auth_key |  | 6 |
| /stock/m224/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 22 |
| /stock/m224/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 46 |
| /stock/m224/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 46 |
| /stock/m224/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /stock/m224/intra_date | 주기정보(1분) | cust_id, auth_key, jcode, edate |  | 26 |
| /stock/m224/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 27 |
| /stock/m224/invest_info_port | 투자자 정보(복수종목) | cust_id, auth_key, codelist |  | 121 |
| /stock/m224/member_date | 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - | 10 |
| /stock/m224/program | 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  | 23 |
| /stock/m224/program_all | 프로그램매매-일중(전체) | cust_id, auth_key, edate |  | 22 |
| /stock/m224/program_all_basic | 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list | 19 |
| /stock/m224/program_basic | 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list | 26 |
| /stock/m224/rank | 순위정보 | cust_id, auth_key, criteria_code | up_code | 15 |
| /stock/m224/rank_invest | 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code |  | 121 |
| /stock/m224/rank_invest_date | 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | - | 123 |
| /stock/m224/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 16 |
| /stock/m224/tick_date | 체결정보 | cust_id, auth_key, jcode, edate |  | 36 |
| /stock/m224/tick_info | 체결정보 | cust_id, auth_key, jcode | order, dcnt | 37 |

## m225

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m225/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 12 |
| /stock/m225/basic_info_all | 기본정보(전체) | cust_id, auth_key, jcode |  | 152 |
| /stock/m225/basic_info_all_port | 기본정보(전체_복수종목) | cust_id, auth_key, codelist |  | 152 |
| /stock/m225/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist |  | 12 |
| /stock/m225/code_info | 코드정보 | cust_id, auth_key |  | 6 |
| /stock/m225/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 22 |
| /stock/m225/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 46 |
| /stock/m225/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 46 |
| /stock/m225/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /stock/m225/intra_date | 주기정보(1분) | cust_id, auth_key, jcode, edate |  | 26 |
| /stock/m225/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 27 |
| /stock/m225/invest_info_port | 투자자 정보(복수종목) | cust_id, auth_key, codelist |  | 121 |
| /stock/m225/member_date | 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - | 10 |
| /stock/m225/program | 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  | 23 |
| /stock/m225/program_all | 프로그램매매-일중(전체) | cust_id, auth_key, edate |  | 22 |
| /stock/m225/program_all_basic | 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list | 19 |
| /stock/m225/program_basic | 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list | 26 |
| /stock/m225/rank | 순위정보 | cust_id, auth_key, criteria_code | up_code | 15 |
| /stock/m225/rank_invest | 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code |  | 121 |
| /stock/m225/rank_invest_date | 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | - | 123 |
| /stock/m225/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 16 |
| /stock/m225/tick_date | 체결정보 | cust_id, auth_key, jcode, edate |  | 36 |
| /stock/m225/tick_info | 체결정보 | cust_id, auth_key, jcode | order, dcnt | 37 |

## m226

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m226/basic_info | 기본정보 | cust_id, auth_key, jcode | data_list | 3 |
| /stock/m226/code_info | 코드정보 | cust_id, auth_key | data_list | 3 |
| /stock/m226/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 4 |
| /stock/m226/invest_basic_info | 투자자 기본정보 | cust_id, auth_key, jcode | data_list | 121 |
| /stock/m226/invest_hist_info | 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 122 |
| /stock/m226/invest_intra_date | 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list | 122 |
| /stock/m226/invest_intra_info | 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list | 122 |

## m227

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m227/basic_info | 기본정보 | cust_id, auth_key, jcode | data_list | 3 |
| /stock/m227/code_info | 코드정보 | cust_id, auth_key | data_list | 3 |
| /stock/m227/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 4 |
| /stock/m227/invest_basic_info | 투자자 기본정보 | cust_id, auth_key, jcode | data_list | 121 |
| /stock/m227/invest_hist_info | 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 122 |
| /stock/m227/invest_intra_date | 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list | 122 |
| /stock/m227/invest_intra_info | 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list | 122 |

## m228

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m228/basic_info | 기본정보 | cust_id, auth_key, jcode | data_list | 3 |
| /stock/m228/code_info | 코드정보 | cust_id, auth_key | data_list | 3 |
| /stock/m228/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 4 |
| /stock/m228/invest_basic_info | 투자자 기본정보 | cust_id, auth_key, jcode | data_list | 121 |
| /stock/m228/invest_hist_info | 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 122 |
| /stock/m228/invest_intra_date | 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list | 122 |
| /stock/m228/invest_intra_info | 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list | 122 |

## m229

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /stock/m229/basic_info | 기본정보 | cust_id, auth_key, jcode | data_list | 3 |
| /stock/m229/code_info | 코드정보 | cust_id, auth_key | data_list | 3 |
| /stock/m229/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 4 |
| /stock/m229/invest_basic_info | 투자자 기본정보 | cust_id, auth_key, jcode | data_list | 121 |
| /stock/m229/invest_hist_info | 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 122 |
| /stock/m229/invest_intra_info | 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list | 122 |
