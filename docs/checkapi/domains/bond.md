# CHECK API Domain: bond

Endpoint count: 60

## etc

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/etc/bondbasket | 채권현금흐름 | cust_id, auth_key, jcode |  | 5 |
| /bond/etc/bondbasket_hist | 채권현금흐름 | cust_id, auth_key, jcode, sdate, edate |  | 5 |
| /bond/etc/cdcp_hist | CD/CP시가평가 일별 | cust_id, auth_key, jcode, sdate, edate |  | 8 |

## m020

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m020/tick_info | 장외호가정보(종목별) | cust_id, auth_key, jcode | data_list | 24 |
| /bond/m020/tick_total_info | 장외호가정보(전체) | cust_id, auth_key | F14729, data_list, - | 24 |

## m023

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m023/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 20 |
| /bond/m023/code_info | 코드정보 | cust_id, auth_key |  | 2 |
| /bond/m023/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 18 |
| /bond/m023/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 17 |

## m025

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m025/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 8 |
| /bond/m025/code_info | 코드정보 | cust_id, auth_key |  | 4 |
| /bond/m025/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 12 |

## m026

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m026/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 13 |
| /bond/m026/code_info | 코드정보 | cust_id, auth_key |  | 2 |
| /bond/m026/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 14 |
| /bond/m026/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 13 |

## m037

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m037/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 8 |
| /bond/m037/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist |  | 8 |
| /bond/m037/code_info | 코드정보 | cust_id, auth_key |  | 5 |
| /bond/m037/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 4 |

## m038

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m038/basic_info | 기본정보 | cust_id, auth_key, jcode | data_list | 132 |
| /bond/m038/code_info | 코드정보 | cust_id, auth_key | data_list | 4 |
| /bond/m038/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list | 24 |
| /bond/m038/tick_info | 체결정보(장내체결+장외15분 체결) | cust_id, auth_key, jcode | data_list | 16 |
| /bond/m038/tick_total_info | 체결정보(장내체결+장외15분 체결) | cust_id, auth_key | F14729, data_list, - | 16 |

## m043

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m043/hist_info | 일별체결(만기별) | cust_id, auth_key, inst_cd, dwm_type, sdate, edate |  | 6 |

## m048

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m048/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 27 |
| /bond/m048/code_info | 코드정보 | cust_id, auth_key |  | 3 |
| /bond/m048/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 21 |
| /bond/m048/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |

## m050

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m050/tick_info | 통합채권 호가(장내체결+K-bond 호가) | cust_id, auth_key, jcode | data_list | 21 |
| /bond/m050/tick_total_info | 통합채권 호가(장내체결+K-bond 호가) | cust_id, auth_key | F14729, data_list, - | 21 |

## m056

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m056/basic_info | 콜-기본정보 | cust_id, auth_key, jcode |  | 7 |
| /bond/m056/call_tick | 콜-체결 | cust_id, auth_key, jcode |  | 21 |
| /bond/m056/code_info | 코드정보 | cust_id, auth_key |  | 2 |
| /bond/m056/hist_info | 콜-일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 4 |

## m058

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m058/basic_info | 채권발행정보 | cust_id, auth_key, jcode |  | 204 |
| /bond/m058/credit_group_info | 채권 신용그룹코드-명 맵핑 정보 | cust_id, auth_key |  | 2 |
| /bond/m058/jipyo_list | 지표물 리스트 | cust_id, auth_key, edate |  | 10 |
| /bond/m058/m058hadre | 발행정보-상세 | cust_id, auth_key, jcode |  | 19 |
| /bond/m058/m058hcsfw | 채권현금흐름 | cust_id, auth_key, jcode |  | 12 |
| /bond/m058/m058hfrncsfw | FRN_현금흐름 | cust_id, auth_key, jcode |  | 18 |
| /bond/m058/m058hfrnrefe | FRN-상세 | cust_id, auth_key, jcode |  | 16 |
| /bond/m058/m058hmkvld | 시가평가(익일) | cust_id, auth_key, jcode |  | 21 |
| /bond/m058/m058hmkvld_hist | 시가평가(익일)-일별 | cust_id, auth_key, jcode, sdate, edate |  | 21 |
| /bond/m058/m058umkvld | 시가평가(당일) | cust_id, auth_key, jcode |  | 21 |
| /bond/m058/m058umkvld_hist | 시가평가(당일)-일별 | cust_id, auth_key, jcode, sdate, edate |  | 21 |

## m060

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m060/code_info | 코드정보 | cust_id, auth_key |  | 2 |
| /bond/m060/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /bond/m060/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 20 |

## m074

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m074/m074htsyd | 발행기관별 민평커브 | cust_id, auth_key, F12506, F16357 |  | 8 |
| /bond/m074/m074htsyd_hist | 발행기관별 민평커브 | cust_id, auth_key, F16357, sdate, edate |  | 8 |

## m097

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m097/basic_info | 최종호가수익률 | cust_id, auth_key, jcode |  | 15 |
| /bond/m097/hist_info | 최종호가수익률 | cust_id, auth_key, jcode, sdate, edate |  | 5 |

## m161

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /bond/m161/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 16 |
| /bond/m161/code_info | 코드정보 | cust_id, auth_key |  | 5 |
| /bond/m161/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 16 |
| /bond/m161/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 35 |
| /bond/m161/tick_info | 체결정보 | cust_id, auth_key, jcode | data_list | 10 |
| /bond/m161/tick_info_by_jipyo | 체결정보(지표코드) | cust_id, auth_key, jcode | data_list | 10 |
