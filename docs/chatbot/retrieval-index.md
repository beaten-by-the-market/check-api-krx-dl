# Retrieval Index

챗봇 검색용 축약 인덱스입니다.

| 종류 | 키 | 검색어/설명 | 필수 | 보조 |
| --- | --- | --- | --- | --- |
| checkapi | /bond/etc/bondbasket | bond etc 채권현금흐름 | cust_id, auth_key, jcode |  |
| checkapi | /bond/etc/bondbasket_hist | bond etc 채권현금흐름 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/etc/cdcp_hist | bond etc CD/CP시가평가 일별 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m020/tick_info | bond m020 장외호가정보(종목별) | cust_id, auth_key, jcode | data_list |
| checkapi | /bond/m020/tick_total_info | bond m020 장외호가정보(전체) | cust_id, auth_key | F14729, data_list, - |
| checkapi | /bond/m023/basic_info | bond m023 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m023/code_info | bond m023 코드정보 | cust_id, auth_key |  |
| checkapi | /bond/m023/hist_info | bond m023 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m023/term_hist_info | bond m023 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /bond/m025/basic_info | bond m025 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m025/code_info | bond m025 코드정보 | cust_id, auth_key |  |
| checkapi | /bond/m025/hist_info | bond m025 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m026/basic_info | bond m026 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m026/code_info | bond m026 코드정보 | cust_id, auth_key |  |
| checkapi | /bond/m026/hist_info | bond m026 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m026/term_hist_info | bond m026 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /bond/m037/basic_info | bond m037 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m037/basic_info_port | bond m037 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /bond/m037/code_info | bond m037 코드정보 | cust_id, auth_key |  |
| checkapi | /bond/m037/hist_info | bond m037 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m038/basic_info | bond m038 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /bond/m038/code_info | bond m038 코드정보 | cust_id, auth_key | data_list |
| checkapi | /bond/m038/hist_info | bond m038 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /bond/m038/tick_info | bond m038 체결정보(장내체결+장외15분 체결) | cust_id, auth_key, jcode | data_list |
| checkapi | /bond/m038/tick_total_info | bond m038 체결정보(장내체결+장외15분 체결) | cust_id, auth_key | F14729, data_list, - |
| checkapi | /bond/m043/hist_info | bond m043 일별체결(만기별) | cust_id, auth_key, inst_cd, dwm_type, sdate, edate |  |
| checkapi | /bond/m048/basic_info | bond m048 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m048/code_info | bond m048 코드정보 | cust_id, auth_key |  |
| checkapi | /bond/m048/hist_info | bond m048 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m048/term_hist_info | bond m048 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /bond/m050/tick_info | bond m050 통합채권 호가(장내체결+K-bond 호가) | cust_id, auth_key, jcode | data_list |
| checkapi | /bond/m050/tick_total_info | bond m050 통합채권 호가(장내체결+K-bond 호가) | cust_id, auth_key | F14729, data_list, - |
| checkapi | /bond/m056/basic_info | bond m056 콜-기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m056/call_tick | bond m056 콜-체결 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m056/code_info | bond m056 코드정보 | cust_id, auth_key |  |
| checkapi | /bond/m056/hist_info | bond m056 콜-일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m058/basic_info | bond m058 채권발행정보 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m058/credit_group_info | bond m058 채권 신용그룹코드-명 맵핑 정보 | cust_id, auth_key |  |
| checkapi | /bond/m058/jipyo_list | bond m058 지표물 리스트 | cust_id, auth_key, edate |  |
| checkapi | /bond/m058/m058hadre | bond m058 발행정보-상세 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m058/m058hcsfw | bond m058 채권현금흐름 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m058/m058hfrncsfw | bond m058 FRN_현금흐름 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m058/m058hfrnrefe | bond m058 FRN-상세 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m058/m058hmkvld | bond m058 시가평가(익일) | cust_id, auth_key, jcode |  |
| checkapi | /bond/m058/m058hmkvld_hist | bond m058 시가평가(익일)-일별 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m058/m058umkvld | bond m058 시가평가(당일) | cust_id, auth_key, jcode |  |
| checkapi | /bond/m058/m058umkvld_hist | bond m058 시가평가(당일)-일별 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m060/code_info | bond m060 코드정보 | cust_id, auth_key |  |
| checkapi | /bond/m060/hist_info | bond m060 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m060/term_hist_info | bond m060 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /bond/m074/m074htsyd | bond m074 발행기관별 민평커브 | cust_id, auth_key, F12506, F16357 |  |
| checkapi | /bond/m074/m074htsyd_hist | bond m074 발행기관별 민평커브 | cust_id, auth_key, F16357, sdate, edate |  |
| checkapi | /bond/m097/basic_info | bond m097 최종호가수익률 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m097/hist_info | bond m097 최종호가수익률 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m161/basic_info | bond m161 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m161/code_info | bond m161 코드정보 | cust_id, auth_key |  |
| checkapi | /bond/m161/hist_info | bond m161 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /bond/m161/hoga_info | bond m161 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /bond/m161/tick_info | bond m161 체결정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /bond/m161/tick_info_by_jipyo | bond m161 체결정보(지표코드) | cust_id, auth_key, jcode | data_list |
| checkapi | /etc/comp/comp_basic | etc comp 기업 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /etc/comp/comp_comment | etc comp 기업소개 | cust_id, auth_key, jcode |  |
| checkapi | /etc/comp/comp_holder | etc comp 기업 주주현황 | cust_id, auth_key, jcode, yyyymm |  |
| checkapi | /etc/comp/comp_market | etc comp 기업 시장점유율 | cust_id, auth_key, jcode, yyyymm |  |
| checkapi | /etc/comp/comp_market_hist | etc comp 기업 시장점유율 추이 | cust_id, auth_key, jcode |  |
| checkapi | /etc/comp/comp_sales | etc comp 기업 매출액 구성비 | cust_id, auth_key, jcode, yyyymm |  |
| checkapi | /etc/comp/comp_sales_hist | etc comp 기업 매출액 구성비 추이 | cust_id, auth_key, jcode |  |
| checkapi | /etc/cons/comp_cons | etc cons 컨센서스 회계년도 전체 | cust_id, auth_key, jcode, yyyymm |  |
| checkapi | /etc/cons/comp_cons_code | etc cons 컨센서스 계정코드 일람 | cust_id, auth_key |  |
| checkapi | /etc/cons/comp_cons_hist | etc cons 컨센서스 계정별 추이 | cust_id, auth_key, jcode, icode | sdate, edate |
| checkapi | /etc/cons/comp_cons_item | etc cons 컨센서스 회계년도 계정별 | cust_id, auth_key, jcode, yyyymm, icode |  |
| checkapi | /etc/economic/checkcode | etc economic 경제지표 코드정보 | cust_id, auth_key |  |
| checkapi | /etc/economic/indicator | etc economic 경제지표 | cust_id, auth_key, check_code | syear, eyear |
| checkapi | /etc/gaap/comp_gaap | etc gaap GAAP 회계년도 전체 | cust_id, auth_key, jcode, yyyymm |  |
| checkapi | /etc/gaap/comp_gaap_code | etc gaap GAAP 계정코드 일람 | cust_id, auth_key |  |
| checkapi | /etc/gaap/comp_gaap_hist | etc gaap GAAP 계정별 추이 | cust_id, auth_key, jcode, icode | sdate, edate |
| checkapi | /etc/gaap/comp_gaap_item | etc gaap GAAP 회계년도 계정별 | cust_id, auth_key, jcode, yyyymm, icode |  |
| checkapi | /etc/ifrs/comp_ifrs | etc ifrs IFRS 회계년도 전체 | cust_id, auth_key, jcode, yyyymm |  |
| checkapi | /etc/ifrs/comp_ifrs_code | etc ifrs IFRS 계정코드 일람 | cust_id, auth_key |  |
| checkapi | /etc/ifrs/comp_ifrs_hist | etc ifrs IFRS 계정별 추이 | cust_id, auth_key, jcode, icode | sdate, edate |
| checkapi | /etc/ifrs/comp_ifrs_item | etc ifrs IFRS 회계년도 계정별 | cust_id, auth_key, jcode, yyyymm, icode |  |
| checkapi | /etc/ifrs/comp_perf_date | etc ifrs 실적발표일 | cust_id, auth_key, jcode |  |
| checkapi | /etc/trend/trend_bank | etc trend 금융기관 수신고 - 은행 | cust_id, auth_key, sdate, edate | dcnt |
| checkapi | /etc/trend/trend_comp | etc trend 금융기관 수신고 - 종금 | cust_id, auth_key, sdate, edate | dcnt |
| checkapi | /etc/trend/trend_inv | etc trend 금융기관 수신고 - 투신 | cust_id, auth_key, sdate, edate | dcnt |
| checkapi | /etc/trend/trend_secu | etc trend 금융기관 수신고 - 증권사 | cust_id, auth_key, sdate, edate | dcnt |
| checkapi | /ext/m174/basic_info | ext m174 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m174/code_info | ext m174 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m174/hist_info | ext m174 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m184/basic_info | ext m184 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m184/code_info | ext m184 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m184/hist_info | ext m184 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m184/intra_info | ext m184 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m184/term_hist_info | ext m184 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m185/basic_info | ext m185 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m185/code_info | ext m185 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m185/hist_info | ext m185 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m185/intra_info | ext m185 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m185/term_hist_info | ext m185 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m186/basic_info | ext m186 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m186/code_info | ext m186 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m186/hist_info | ext m186 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m186/intra_info | ext m186 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m186/term_hist_info | ext m186 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m187/basic_info | ext m187 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m187/code_info | ext m187 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m187/hist_info | ext m187 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m187/intra_info | ext m187 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m187/term_hist_info | ext m187 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m188/basic_info | ext m188 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m188/code_info | ext m188 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m188/hist_info | ext m188 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m188/intra_info | ext m188 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m188/term_hist_info | ext m188 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m193/basic_info | ext m193 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m193/code_info | ext m193 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m193/hist_info | ext m193 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m193/intra_info | ext m193 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m193/term_hist_info | ext m193 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m194/basic_info | ext m194 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m194/basic_info_port | ext m194 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /ext/m194/code_info | ext m194 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m194/hist_info | ext m194 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m194/intra_info | ext m194 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m194/term_hist_info | ext m194 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m194/tick_info | ext m194 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m195/basic_info | ext m195 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m195/basic_info_port | ext m195 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /ext/m195/code_info | ext m195 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m195/hist_info | ext m195 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m195/intra_info | ext m195 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m195/term_hist_info | ext m195 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m195/tick_info | ext m195 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m196/basic_info | ext m196 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m196/basic_info_port | ext m196 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /ext/m196/code_info | ext m196 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m196/hist_info | ext m196 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m196/intra_info | ext m196 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m196/term_hist_info | ext m196 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m196/tick_info | ext m196 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m197/basic_info | ext m197 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m197/basic_info_port | ext m197 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /ext/m197/code_info | ext m197 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m197/hist_info | ext m197 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m197/intra_info | ext m197 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m197/term_hist_info | ext m197 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m197/tick_info | ext m197 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m198/basic_info | ext m198 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m198/basic_info_port | ext m198 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /ext/m198/code_info | ext m198 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m198/hist_info | ext m198 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m198/intra_info | ext m198 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /ext/m198/term_hist_info | ext m198 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /ext/m198/tick_info | ext m198 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m215/basic_info | ext m215 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /ext/m215/basic_info_port | ext m215 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /ext/m215/code_info | ext m215 코드정보 | cust_id, auth_key |  |
| checkapi | /ext/m215/hist_info | ext m215 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /ext/m215/term_hist_info | ext m215 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m005/basic_info | future m005 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m005/basic_info_port | future m005 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m005/code_info | future m005 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m005/hist_info | future m005 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m005/hoga_info | future m005 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m005/hoga_info_port | future m005 호가정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m005/hoga_info_port_top | future m005 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m005/intra_date | future m005 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m005/intra_info | future m005 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m005/invest_basic_info | future m005 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m005/invest_hist_info | future m005 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m005/invest_intra_info | future m005 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m005/term_hist_info | future m005 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m005/tick_date | future m005 체결정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m005/tick_info | future m005 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m006/basic_info | future m006 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m006/basic_info_port | future m006 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m006/code_info | future m006 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m006/hist_info | future m006 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m006/hoga_info | future m006 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m006/hoga_info_port | future m006 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m006/hoga_info_port_top | future m006 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m006/intra_date | future m006 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m006/intra_info | future m006 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m006/invest_basic_info | future m006 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m006/invest_hist_info | future m006 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m006/invest_intra_info | future m006 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m006/old_code_info | future m006 과거 종목(코드정보) | cust_id, auth_key, yyyymm |  |
| checkapi | /future/m006/old_hist_info | future m006 과거종목(일별정보) | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m006/term_hist_info | future m006 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m006/tick_info | future m006 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m012/basic_info | future m012 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m012/basic_info_port | future m012 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m012/code_info | future m012 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m012/hist_info | future m012 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m012/hoga_info | future m012 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m012/hoga_info_port | future m012 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m012/hoga_info_port_top | future m012 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m012/intra_date | future m012 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m012/intra_info | future m012 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m012/invest_basic_info | future m012 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m012/invest_hist_info | future m012 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m012/invest_intra_info | future m012 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m012/term_hist_info | future m012 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m012/tick_info | future m012 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m013/basic_info | future m013 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m013/basic_info_port | future m013 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m013/code_info | future m013 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m013/hist_info | future m013 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m013/hoga_info | future m013 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m013/intra_date | future m013 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m013/intra_info | future m013 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m013/term_hist_info | future m013 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m013/tick_info | future m013 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m016/basic_info | future m016 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m016/basic_info_port | future m016 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m016/code_info | future m016 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m016/hist_info | future m016 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m016/hoga_info | future m016 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m016/intra_date | future m016 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m016/intra_info | future m016 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m016/invest_basic_info | future m016 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m016/invest_hist_info | future m016 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m016/invest_intra_info | future m016 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m016/term_hist_info | future m016 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m016/tick_info | future m016 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m017/basic_info | future m017 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m017/basic_info_port | future m017 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m017/code_info | future m017 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m017/hist_info | future m017 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m017/hoga_info | future m017 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m017/intra_date | future m017 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m017/intra_info | future m017 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m017/invest_basic_info | future m017 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m017/invest_hist_info | future m017 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m017/invest_intra_info | future m017 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m017/term_hist_info | future m017 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m017/tick_info | future m017 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m018/basic_info | future m018 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m018/basic_info_port | future m018 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m018/code_info | future m018 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m018/hist_info | future m018 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m018/hoga_info | future m018 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m018/intra_date | future m018 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m018/intra_info | future m018 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m018/term_hist_info | future m018 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m018/tick_info | future m018 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m019/basic_info | future m019 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m019/basic_info_port | future m019 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m019/code_info | future m019 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m019/hist_info | future m019 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m019/hoga_info | future m019 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m019/intra_date | future m019 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m019/intra_info | future m019 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m019/term_hist_info | future m019 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m019/tick_info | future m019 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m062/basic_info | future m062 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m062/basic_info_port | future m062 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m062/code_info | future m062 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m062/hist_info | future m062 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m062/hoga_info | future m062 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m062/intra_date | future m062 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m062/intra_info | future m062 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m062/invest_basic_info | future m062 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m062/invest_hist_info | future m062 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m062/invest_intra_info | future m062 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m062/term_hist_info | future m062 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m062/tick_info | future m062 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m067/basic_info | future m067 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m067/basic_info_port | future m067 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m067/code_info | future m067 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m067/hist_info | future m067 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m067/hoga_info | future m067 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m067/hoga_info_port | future m067 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m067/hoga_info_port_top | future m067 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m067/intra_date | future m067 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m067/intra_info | future m067 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m067/invest_basic_info | future m067 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m067/invest_hist_info | future m067 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m067/invest_intra_info | future m067 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m067/term_hist_info | future m067 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m067/tick_info | future m067 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m091/basic_info | future m091 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m091/basic_info_port | future m091 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m091/code_info | future m091 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m091/hist_info | future m091 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m091/hoga_info | future m091 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m091/hoga_info_port | future m091 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m091/hoga_info_port_top | future m091 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m091/intra_date | future m091 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m091/intra_info | future m091 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m091/term_hist_info | future m091 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m091/tick_info | future m091 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m100/basic_info | future m100 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m100/basic_info_port | future m100 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m100/code_info | future m100 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m100/hist_info | future m100 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m100/hoga_info | future m100 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m100/hoga_info_port | future m100 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m100/hoga_info_port_top | future m100 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m100/intra_date | future m100 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m100/intra_info | future m100 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m100/term_hist_info | future m100 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m100/tick_info | future m100 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m103/basic_info | future m103 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m103/basic_info_port | future m103 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m103/code_info | future m103 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m103/hist_info | future m103 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m103/hoga_info | future m103 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m103/hoga_info_port | future m103 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m103/hoga_info_port_top | future m103 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m103/intra_date | future m103 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m103/intra_info | future m103 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m103/invest_basic_info | future m103 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m103/invest_hist_info | future m103 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m103/invest_intra_info | future m103 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m103/term_hist_info | future m103 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m103/tick_info | future m103 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m104/basic_info | future m104 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m104/basic_info_port | future m104 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m104/code_info | future m104 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m104/hist_info | future m104 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m104/hoga_info | future m104 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m104/hoga_info_port | future m104 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m104/hoga_info_port_top | future m104 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m104/intra_date | future m104 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m104/intra_info | future m104 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m104/invest_basic_info | future m104 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m104/invest_hist_info | future m104 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m104/invest_intra_info | future m104 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m104/old_code_info | future m104 과거 종목(코드정보) | cust_id, auth_key, yyyymm |  |
| checkapi | /future/m104/old_hist_info | future m104 과거종목(일별정보) | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m104/term_hist_info | future m104 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m104/tick_info | future m104 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m105/basic_info | future m105 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m105/basic_info_port | future m105 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m105/code_info | future m105 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m105/hist_info | future m105 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m105/hoga_info | future m105 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m105/intra_date | future m105 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m105/intra_info | future m105 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m105/term_hist_info | future m105 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m105/tick_info | future m105 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m180/basic_info | future m180 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m180/basic_info_port | future m180 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m180/code_info | future m180 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m180/hist_info | future m180 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m180/hoga_info | future m180 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m180/intra_date | future m180 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m180/intra_info | future m180 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m180/term_hist_info | future m180 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m180/tick_info | future m180 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m181/basic_info | future m181 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m181/basic_info_port | future m181 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m181/code_info | future m181 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m181/hist_info | future m181 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m181/hoga_info | future m181 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m181/intra_date | future m181 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m181/intra_info | future m181 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m181/term_hist_info | future m181 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m181/tick_info | future m181 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m182/basic_info | future m182 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m182/basic_info_port | future m182 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m182/code_info | future m182 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m182/hist_info | future m182 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m182/hoga_info | future m182 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m182/hoga_info_port | future m182 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m182/hoga_info_port_top | future m182 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m182/intra_date | future m182 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m182/intra_info | future m182 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m182/invest_basic_info | future m182 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m182/invest_hist_info | future m182 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m182/invest_intra_info | future m182 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m182/term_hist_info | future m182 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m182/tick_info | future m182 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m221/basic_info | future m221 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m221/basic_info_port | future m221 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m221/code_info | future m221 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m221/hist_info | future m221 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m221/hoga_info | future m221 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m221/intra_date | future m221 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m221/intra_info | future m221 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m221/invest_basic_info | future m221 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m221/invest_hist_info | future m221 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m221/invest_intra_info | future m221 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m221/term_hist_info | future m221 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m221/tick_info | future m221 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m232/basic_info | future m232 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m232/basic_info_port | future m232 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m232/code_info | future m232 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m232/hist_info | future m232 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m232/hoga_info | future m232 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m232/hoga_info_port | future m232 호가정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m232/hoga_info_port_top | future m232 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m232/intra_date | future m232 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m232/intra_info | future m232 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m232/invest_basic_info | future m232 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m232/invest_hist_info | future m232 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m232/invest_intra_info | future m232 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m232/term_hist_info | future m232 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m232/tick_date | future m232 체결정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m232/tick_info | future m232 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m233/basic_info | future m233 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m233/basic_info_port | future m233 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m233/code_info | future m233 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m233/hist_info | future m233 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m233/hoga_info | future m233 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m233/hoga_info_port | future m233 호가정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m233/hoga_info_port_top | future m233 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m233/intra_date | future m233 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m233/intra_info | future m233 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m233/invest_basic_info | future m233 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m233/invest_hist_info | future m233 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m233/invest_intra_info | future m233 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m233/term_hist_info | future m233 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m233/tick_date | future m233 체결정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m233/tick_info | future m233 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m234/basic_info | future m234 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m234/basic_info_port | future m234 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m234/code_info | future m234 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m234/hist_info | future m234 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m234/hoga_info | future m234 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m234/hoga_info_port | future m234 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m234/hoga_info_port_top | future m234 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m234/intra_date | future m234 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m234/intra_info | future m234 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m234/invest_basic_info | future m234 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m234/invest_hist_info | future m234 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m234/invest_intra_info | future m234 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m234/old_code_info | future m234 과거 종목(코드정보) | cust_id, auth_key, yyyymm |  |
| checkapi | /future/m234/old_hist_info | future m234 과거종목(일별정보) | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m234/term_hist_info | future m234 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m234/tick_info | future m234 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m235/basic_info | future m235 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m235/basic_info_port | future m235 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m235/code_info | future m235 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m235/hist_info | future m235 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m235/hoga_info | future m235 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m235/hoga_info_port | future m235 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m235/hoga_info_port_top | future m235 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m235/intra_date | future m235 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m235/intra_info | future m235 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m235/invest_basic_info | future m235 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m235/invest_hist_info | future m235 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m235/invest_intra_info | future m235 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m235/old_code_info | future m235 과거 종목(코드정보) | cust_id, auth_key, yyyymm |  |
| checkapi | /future/m235/old_hist_info | future m235 과거종목(일별정보) | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m235/term_hist_info | future m235 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m235/tick_info | future m235 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m236/basic_info | future m236 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m236/basic_info_port | future m236 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /future/m236/code_info | future m236 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m236/hist_info | future m236 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m236/hoga_info | future m236 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m236/hoga_info_port | future m236 호가정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m236/hoga_info_port_top | future m236 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /future/m236/intra_date | future m236 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m236/intra_info | future m236 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m236/invest_basic_info | future m236 기본정보 | cust_id, auth_key |  |
| checkapi | /future/m236/invest_hist_info | future m236 기본정보 | cust_id, auth_key, sdate, edate |  |
| checkapi | /future/m236/invest_intra_info | future m236 주기정보(30초) | cust_id, auth_key |  |
| checkapi | /future/m236/term_hist_info | future m236 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m236/tick_date | future m236 체결정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m236/tick_info | future m236 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m237/basic_info | future m237 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m237/basic_info_port | future m237 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m237/code_info | future m237 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m237/hist_info | future m237 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m237/hoga_info | future m237 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m237/intra_date | future m237 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m237/intra_info | future m237 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m237/term_hist_info | future m237 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m237/tick_info | future m237 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m238/basic_info | future m238 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m238/basic_info_port | future m238 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m238/code_info | future m238 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m238/hist_info | future m238 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m238/hoga_info | future m238 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m238/intra_date | future m238 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m238/intra_info | future m238 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m238/term_hist_info | future m238 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m238/tick_info | future m238 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m239/basic_info | future m239 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m239/basic_info_port | future m239 기본정보 | cust_id, auth_key, codelist |  |
| checkapi | /future/m239/code_info | future m239 코드정보 | cust_id, auth_key |  |
| checkapi | /future/m239/hist_info | future m239 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /future/m239/hoga_info | future m239 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /future/m239/intra_date | future m239 주기정보(10초) | cust_id, auth_key, jcode, edate |  |
| checkapi | /future/m239/intra_info | future m239 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /future/m239/term_hist_info | future m239 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /future/m239/tick_info | future m239 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /news/gongsi/gongsi_basic | news gongsi 공시-제목-전체-일별 구간 | cust_id, auth_key, sdate, edate | dcnt |
| checkapi | /news/gongsi/gongsi_body | news gongsi 공시-본문 | cust_id, auth_key, ndate, ncode |  |
| checkapi | /news/gongsi/gongsi_jong | news gongsi 공시-제목-종목별-일별 구간 | cust_id, auth_key, jcode, sdate, edate | dcnt |
| checkapi | /news/news/news_basic | news news 뉴스-제목-전체-일별 구간 | cust_id, auth_key, sdate, edate | dcnt |
| checkapi | /news/news/news_body | news news 뉴스-본문 | cust_id, auth_key, ndate, ncode |  |
| checkapi | /news/news/news_jong | news news 뉴스-제목-종목별-일별 구간 | cust_id, auth_key, jcode, sdate, edate | dcnt |
| checkapi | /news/news/news_mtvcd | news news 뉴스-뉴스원 | cust_id, auth_key |  |
| checkapi | /stock/m001/basic_info | stock m001 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m001/basic_info_all | stock m001 기본정보(전체) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m001/basic_info_all_port | stock m001 기본정보(전체_복수종목) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m001/basic_info_port | stock m001 기본정보(복수종목) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m001/code_etf_info | stock m001 코드정보(ETF) | cust_id, auth_key | data_list |
| checkapi | /stock/m001/code_etn_info | stock m001 코드정보(ETN) | cust_id, auth_key | data_list |
| checkapi | /stock/m001/code_info | stock m001 코드정보 | cust_id, auth_key | data_list |
| checkapi | /stock/m001/credit_hist_info | stock m001 신용잔고 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m001/hist_info | stock m001 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m001/hist_info_port | stock m001 일별정보 | cust_id, auth_key, codelist, edate | data_list |
| checkapi | /stock/m001/hoga_info | stock m001 호가정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m001/hoga_info_port | stock m001 호가정보(복수종목) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m001/hoga_info_port_top | stock m001 호가정보(복수종목_최우선) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m001/intra_date | stock m001 주기정보(1분) | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m001/intra_info | stock m001 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m001/invest_hist | stock m001 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m001/invest_info_port | stock m001 투자자 정보(복수종목) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m001/loan_hist_info | stock m001 대차잔고 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m001/mass_hist_info | stock m001 대량매매 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m001/member_date | stock m001 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m001/new_high | stock m001 신고가/신저가 | cust_id, auth_key, gubun | data_list |
| checkapi | /stock/m001/program | stock m001 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m001/program_all | stock m001 프로그램매매-일중(전체) | cust_id, auth_key, edate |  |
| checkapi | /stock/m001/program_all_basic | stock m001 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list |
| checkapi | /stock/m001/program_basic | stock m001 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m001/rank | stock m001 순위정보 | cust_id, auth_key, up_code, criteria_code | data_list |
| checkapi | /stock/m001/rank_invest | stock m001 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code | data_list |
| checkapi | /stock/m001/rank_invest_date | stock m001 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | data_list, - |
| checkapi | /stock/m001/rank_mass_date | stock m001 순위정보(대량매매-기간합산) | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m001/rank_short_date | stock m001 순위정보(공매도-기간합산) | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m001/short_hist_info | stock m001 공매도 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m001/term_hist_info | stock m001 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m001/tick_date | stock m001 체결정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m001/tick_info | stock m001 체결정보 | cust_id, auth_key, jcode | order, dcnt |
| checkapi | /stock/m001/upjong_info | stock m001 소속업종정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m002/basic_info | stock m002 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m002/code_info | stock m002 코드정보 | cust_id, auth_key | data_list |
| checkapi | /stock/m002/hist_info | stock m002 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m002/intra_date | stock m002 주기정보(1분) | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m002/intra_info | stock m002 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m002/invest_basic_info | stock m002 투자자 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m002/invest_hist_info | stock m002 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m002/invest_intra_date | stock m002 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m002/invest_intra_info | stock m002 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m002/term_hist_info | stock m002 일별정보 | cust_id, auth_key, jcode, term, sdate, edate | data_list |
| checkapi | /stock/m002/tick_info | stock m002 체결정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m003/basic_info | stock m003 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m003/basic_info_all | stock m003 기본정보(전체) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m003/basic_info_all_port | stock m003 기본정보(전체_복수종목) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m003/basic_info_port | stock m003 기본정보(복수종목) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m003/code_info | stock m003 코드정보 | cust_id, auth_key | data_list |
| checkapi | /stock/m003/credit_hist_info | stock m003 신용잔고 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m003/hist_info | stock m003 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m003/hoga_info | stock m003 호가정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m003/hoga_info_port | stock m003 호가정보(복수종목) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m003/hoga_info_port_top | stock m003 호가정보(복수종목_최우선) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m003/intra_date | stock m003 주기정보(1분) | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m003/intra_info | stock m003 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m003/invest_hist | stock m003 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m003/invest_info_port | stock m003 투자자 정보(복수종목) | cust_id, auth_key, codelist | data_list |
| checkapi | /stock/m003/loan_hist_info | stock m003 대차잔고 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m003/mass_hist_info | stock m003 대량매매 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m003/member_date | stock m003 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m003/new_high | stock m003 신고가/신저가 | cust_id, auth_key, gubun | data_list |
| checkapi | /stock/m003/program | stock m003 기본정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m003/program_all | stock m003 프로그램매매-일중(전체) | cust_id, auth_key, edate |  |
| checkapi | /stock/m003/program_all_basic | stock m003 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list |
| checkapi | /stock/m003/program_basic | stock m003 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m003/rank | stock m003 순위정보 | cust_id, auth_key, up_code, criteria_code | data_list |
| checkapi | /stock/m003/rank_invest | stock m003 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code | data_list |
| checkapi | /stock/m003/rank_invest_date | stock m003 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | data_list, - |
| checkapi | /stock/m003/rank_mass_date | stock m003 순위정보(대량매매-기간합산) | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m003/rank_short_date | stock m003 순위정보(공매도-기간합산) | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m003/short_hist_info | stock m003 공매도 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m003/term_hist_info | stock m003 일별정보 | cust_id, auth_key, jcode, term, sdate, edate | data_list |
| checkapi | /stock/m003/tick_date | stock m003 체결정보 | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m003/tick_info | stock m003 체결정보 | cust_id, auth_key, jcode | data_list, order, dcnt |
| checkapi | /stock/m003/upjong_info | stock m003 소속업종정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m004/basic_info | stock m004 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m004/code_info | stock m004 코드정보 | cust_id, auth_key | data_list |
| checkapi | /stock/m004/hist_info | stock m004 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m004/intra_date | stock m004 주기정보(1분) | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m004/intra_info | stock m004 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m004/invest_basic_info | stock m004 투자자 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m004/invest_hist_info | stock m004 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m004/invest_intra_date | stock m004 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m004/invest_intra_info | stock m004 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m004/term_hist_info | stock m004 일별정보 | cust_id, auth_key, jcode, term, sdate, edate | data_list |
| checkapi | /stock/m004/tick_info | stock m004 체결정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m008/basic_info | stock m008 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m008/code_info | stock m008 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m008/hist_info | stock m008 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m008/intra_info | stock m008 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m008/term_hist_info | stock m008 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m008/tick_info | stock m008 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m009/basic_info | stock m009 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m009/code_info | stock m009 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m009/hist_info | stock m009 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m009/intra_info | stock m009 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m009/term_hist_info | stock m009 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m009/tick_info | stock m009 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m010/basic_info | stock m010 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m010/code_info | stock m010 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m010/hist_info | stock m010 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m010/term_hist_info | stock m010 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m010/tick_info | stock m010 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m118/basic_info | stock m118 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m118/code_info | stock m118 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m118/hist_info | stock m118 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m118/hoga_info | stock m118 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m118/intra_info | stock m118 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m118/term_hist_info | stock m118 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m118/tick_info | stock m118 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m121/basic_info | stock m121 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m121/code_info | stock m121 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m121/hist_info | stock m121 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m121/intra_info | stock m121 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m121/term_hist_info | stock m121 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m121/tick_info | stock m121 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m167/basic_info | stock m167 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m167/code_info | stock m167 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m167/hist_info | stock m167 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m167/intra_info | stock m167 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m167/term_hist_info | stock m167 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m167/tick_info | stock m167 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m168/basic_info | stock m168 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m168/code_info | stock m168 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m168/hist_info | stock m168 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m168/intra_info | stock m168 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m168/term_hist_info | stock m168 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m168/tick_info | stock m168 체결정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m222/basic_info | stock m222 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m222/basic_info_all | stock m222 기본정보(전체) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m222/basic_info_all_port | stock m222 기본정보(전체_복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m222/basic_info_port | stock m222 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m222/code_info | stock m222 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m222/hist_info | stock m222 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m222/hoga_info | stock m222 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m222/hoga_info_port | stock m222 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m222/hoga_info_port_top | stock m222 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m222/intra_date | stock m222 주기정보(1분) | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m222/intra_info | stock m222 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m222/invest_info_port | stock m222 투자자 정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m222/member_date | stock m222 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m222/program | stock m222 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m222/program_all | stock m222 프로그램매매-일중(전체) | cust_id, auth_key, edate |  |
| checkapi | /stock/m222/program_all_basic | stock m222 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list |
| checkapi | /stock/m222/program_basic | stock m222 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m222/rank | stock m222 순위정보 | cust_id, auth_key, criteria_code | up_code |
| checkapi | /stock/m222/rank_invest | stock m222 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code |  |
| checkapi | /stock/m222/rank_invest_date | stock m222 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | - |
| checkapi | /stock/m222/term_hist_info | stock m222 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m222/tick_date | stock m222 체결정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m222/tick_info | stock m222 체결정보 | cust_id, auth_key, jcode | order, dcnt |
| checkapi | /stock/m223/basic_info | stock m223 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m223/basic_info_all | stock m223 기본정보(전체) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m223/basic_info_all_port | stock m223 기본정보(전체_복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m223/basic_info_port | stock m223 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m223/code_info | stock m223 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m223/hist_info | stock m223 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m223/hoga_info | stock m223 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m223/hoga_info_port | stock m223 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m223/hoga_info_port_top | stock m223 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m223/intra_date | stock m223 주기정보(1분) | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m223/intra_info | stock m223 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m223/invest_info_port | stock m223 투자자 정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m223/member_date | stock m223 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m223/program | stock m223 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m223/program_all | stock m223 프로그램매매-일중(전체) | cust_id, auth_key, edate |  |
| checkapi | /stock/m223/program_all_basic | stock m223 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list |
| checkapi | /stock/m223/program_basic | stock m223 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m223/rank | stock m223 순위정보 | cust_id, auth_key, criteria_code | up_code |
| checkapi | /stock/m223/rank_invest | stock m223 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code |  |
| checkapi | /stock/m223/rank_invest_date | stock m223 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | - |
| checkapi | /stock/m223/term_hist_info | stock m223 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m223/tick_date | stock m223 체결정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m223/tick_info | stock m223 체결정보 | cust_id, auth_key, jcode | order, dcnt |
| checkapi | /stock/m224/basic_info | stock m224 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m224/basic_info_all | stock m224 기본정보(전체) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m224/basic_info_all_port | stock m224 기본정보(전체_복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m224/basic_info_port | stock m224 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m224/code_info | stock m224 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m224/hist_info | stock m224 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m224/hoga_info | stock m224 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m224/hoga_info_port | stock m224 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m224/hoga_info_port_top | stock m224 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m224/intra_date | stock m224 주기정보(1분) | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m224/intra_info | stock m224 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m224/invest_info_port | stock m224 투자자 정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m224/member_date | stock m224 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m224/program | stock m224 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m224/program_all | stock m224 프로그램매매-일중(전체) | cust_id, auth_key, edate |  |
| checkapi | /stock/m224/program_all_basic | stock m224 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list |
| checkapi | /stock/m224/program_basic | stock m224 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m224/rank | stock m224 순위정보 | cust_id, auth_key, criteria_code | up_code |
| checkapi | /stock/m224/rank_invest | stock m224 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code |  |
| checkapi | /stock/m224/rank_invest_date | stock m224 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | - |
| checkapi | /stock/m224/term_hist_info | stock m224 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m224/tick_date | stock m224 체결정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m224/tick_info | stock m224 체결정보 | cust_id, auth_key, jcode | order, dcnt |
| checkapi | /stock/m225/basic_info | stock m225 기본정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m225/basic_info_all | stock m225 기본정보(전체) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m225/basic_info_all_port | stock m225 기본정보(전체_복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m225/basic_info_port | stock m225 기본정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m225/code_info | stock m225 코드정보 | cust_id, auth_key |  |
| checkapi | /stock/m225/hist_info | stock m225 일별정보 | cust_id, auth_key, jcode, sdate, edate |  |
| checkapi | /stock/m225/hoga_info | stock m225 호가정보 | cust_id, auth_key, jcode |  |
| checkapi | /stock/m225/hoga_info_port | stock m225 호가정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m225/hoga_info_port_top | stock m225 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m225/intra_date | stock m225 주기정보(1분) | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m225/intra_info | stock m225 주기정보(10초) | cust_id, auth_key, jcode |  |
| checkapi | /stock/m225/invest_info_port | stock m225 투자자 정보(복수종목) | cust_id, auth_key, codelist |  |
| checkapi | /stock/m225/member_date | stock m225 회원사 매매집계 | cust_id, auth_key, criteria_code, sdate, edate | - |
| checkapi | /stock/m225/program | stock m225 프로그램매매-일중 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m225/program_all | stock m225 프로그램매매-일중(전체) | cust_id, auth_key, edate |  |
| checkapi | /stock/m225/program_all_basic | stock m225 전체 프로그램매매(기본정보) | cust_id, auth_key | data_list |
| checkapi | /stock/m225/program_basic | stock m225 프로그램매매(기본정보) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m225/rank | stock m225 순위정보 | cust_id, auth_key, criteria_code | up_code |
| checkapi | /stock/m225/rank_invest | stock m225 순위정보(투자자-당일) | cust_id, auth_key, criteria_code, sort_code |  |
| checkapi | /stock/m225/rank_invest_date | stock m225 순위정보(투자자-기간합산) | cust_id, auth_key, criteria_code, sort_code, sdate, edate | - |
| checkapi | /stock/m225/term_hist_info | stock m225 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  |
| checkapi | /stock/m225/tick_date | stock m225 체결정보 | cust_id, auth_key, jcode, edate |  |
| checkapi | /stock/m225/tick_info | stock m225 체결정보 | cust_id, auth_key, jcode | order, dcnt |
| checkapi | /stock/m226/basic_info | stock m226 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m226/code_info | stock m226 코드정보 | cust_id, auth_key | data_list |
| checkapi | /stock/m226/hist_info | stock m226 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m226/invest_basic_info | stock m226 투자자 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m226/invest_hist_info | stock m226 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m226/invest_intra_date | stock m226 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m226/invest_intra_info | stock m226 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m227/basic_info | stock m227 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m227/code_info | stock m227 코드정보 | cust_id, auth_key | data_list |
| checkapi | /stock/m227/hist_info | stock m227 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m227/invest_basic_info | stock m227 투자자 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m227/invest_hist_info | stock m227 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m227/invest_intra_date | stock m227 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m227/invest_intra_info | stock m227 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m228/basic_info | stock m228 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m228/code_info | stock m228 코드정보 | cust_id, auth_key | data_list |
| checkapi | /stock/m228/hist_info | stock m228 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m228/invest_basic_info | stock m228 투자자 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m228/invest_hist_info | stock m228 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m228/invest_intra_date | stock m228 투자자 주기정보(10초) | cust_id, auth_key, jcode, edate | data_list |
| checkapi | /stock/m228/invest_intra_info | stock m228 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m229/basic_info | stock m229 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m229/code_info | stock m229 코드정보 | cust_id, auth_key | data_list |
| checkapi | /stock/m229/hist_info | stock m229 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m229/invest_basic_info | stock m229 투자자 기본정보 | cust_id, auth_key, jcode | data_list |
| checkapi | /stock/m229/invest_hist_info | stock m229 투자자 일별정보 | cust_id, auth_key, jcode, sdate, edate | data_list |
| checkapi | /stock/m229/invest_intra_info | stock m229 투자자 주기정보(10초) | cust_id, auth_key, jcode | data_list |
| kquant | add_order_from_signals | analysis.stock.backtest 시그널 열의 값을 이용하여 매매수량을 계산하는 함수 |  |  |
| kquant | backtest_plot_stock_daily | analysis.stock.backtest 백테스트 결과를 챠트로 시각화하는 함수 |  |  |
| kquant | backtest_stats_stock_daily | analysis.stock.backtest 백테스트의 성능 평가를 위한 함수 |  |  |
| kquant | backtest_stock_daily | analysis.stock.backtest 단일 주식의 일간기준 백테스트 수행 |  |  |
| kquant | backtest_stock_port_daily | analysis.stock.backtest 주식 포트폴리오의 일간기준 백테스트 수행 |  |  |
| kquant | backtest_update_stock_daily | analysis.stock.backtest 단일 주식의 일간기준 백테스트 결과를 하루 단위로 업데이트하는 함수 |  |  |
| kquant | backtest_update_stock_port_daily | analysis.stock.backtest 복수 주식의 일간기준 백테스트 결과를 하루 단위로 업데이트하는 함수 |  |  |
| kquant | handle_stock_merge | analysis.stock.backtest 액면병합을 처리하는 함수 |  |  |
| kquant | handle_stock_split | analysis.stock.backtest 액면분할을 처리하는 함수 |  |  |
| kquant | sma | analysis.stock.ta.moving_average 단순이동평균(SMA: Simple Moving Average) 계산 함수 |  |  |
| kquant | entropy | analysis.stock.ta.statistics 이동 엔트로피(Entropy) |  |  |
| kquant | kurtosis | analysis.stock.ta.statistics 이동 첨도 (Rolling Kurtosis) |  |  |
| kquant | mad | analysis.stock.ta.statistics 이동 평균절대편차 (Rolling Mean Absolute Deviation) |  |  |
| kquant | median | analysis.stock.ta.statistics 이동 중앙값 (Rolling Median) |  |  |
| kquant | quantile | analysis.stock.ta.statistics 이동 분위수 (Rolling Quantile) |  |  |
| kquant | skew | analysis.stock.ta.statistics 이동 왜도 (Rolling Skew) |  |  |
| kquant | stdev | analysis.stock.ta.statistics 이동 표준편차 (Rolling Standard Deviation) |  |  |
| kquant | variance | analysis.stock.ta.statistics 이동 분산 (Rolling Variance) |  |  |
| kquant | zscore | analysis.stock.ta.statistics 이동 Z-스코어 (Rolling Z Score) |  |  |
| kquant | above | analysis.stock.ta.utility A 시계열 값이 B 시계열 값 이상이면 True, 미만이면 False를 반환하는 함수 |  |  |
| kquant | above_value | analysis.stock.ta.utility 시계열 값이 기준 설정값 이상이면 True, 미만이면 False를 반환하는 함수 |  |  |
| kquant | below | analysis.stock.ta.utility A 시계열 값이 B 시계열 값 이하이면 True, 초과면 False를 반환하는 함수 |  |  |
| kquant | below_value | analysis.stock.ta.utility 시계열 값이 기준 설정값 이하이면 True, 초과면 False를 반환하는 함수 |  |  |
| kquant | cross | analysis.stock.ta.utility 두 시그널이 교차하는 지점을 찾아내는 함수 |  |  |
| kquant | cross_value | analysis.stock.ta.utility 시그널이 설정값을 교차하는 지점을 찾아내는 함수 |  |  |
| kquant | get_api | api 설정된 CHECK-API 서비스용 API ID 및 API KEY를 반환하는 함수 |  |  |
| kquant | set_api | api CHECK-API 서비스용 API ID 및 API KEY를 설정 및 저장하는 함수 |  |  |
| kquant | chart_candle | chart 일간 캔들챠트를 출력하는 함수 |  |  |
| kquant | chart_line | chart 일간 라인챠트를 출력하는 함수 |  |  |
| kquant | account_code | data.company 재무제표 계정 코드 정보를 담은 데이터프레임을 출력하는 함수 |  |  |
| kquant | account_code_search | data.company 한글 계정명이 해당 문자열을 포함하는 계정코드를 반환하는 함수 |  |  |
| kquant | account_history | data.company 재무제표 계정의 과거기록을 출력하는 함수 |  |  |
| kquant | company_info | data.company 기업 일반정보를 반환하는 함수 |  |  |
| kquant | latest_yearmonth | data.company 기업의 최신 재무제표 발표 기준 연월을 출력하는 함수 |  |  |
| kquant | disclosure_stock | data.disclosure 주식 공시 정보를 반환하는 함수 |  |  |
| kquant | daily_fx_swap | data.ficc.daily 외환스왑 일간정보를 반환하는 함수 |  |  |
| kquant | info_bond | data.ficc.info 장내채권 발행 정보를 출력하는 함수 |  |  |
| kquant | info_fx_swap | data.ficc.info 외환스왑 종목 정보를 출력하는 함수 |  |  |
| kquant | symbol_bond | data.ficc.symbol 채권 종목 코드를 반환하는 함수 |  | /bond/m038/code_info |
| kquant | symbol_bond_ktb | data.ficc.symbol 장내 국채 종목 코드를 반환하는 함수 |  | /bond/m161/code_info |
| kquant | symbol_fx | data.ficc.symbol 외환정보 종목 목록을 반환하는 함수 |  | /bond/m023/code_info |
| kquant | symbol_fx_swap | data.ficc.symbol 외환스왑 종목 목록을 반환하는 함수 |  | /bond/m026/code_info |
| kquant | news_stock | data.news 주식 뉴스 정보를 반환하는 함수 |  |  |
| kquant | daily_block_stock | data.stock.daily 주식 종목의 일자별 대량매매 정보를 반환하는 함수 |  | /stock/m001/mass_hist_info /stock/m003/mass_hist_info |
| kquant | daily_fund | data.stock.daily 상장 펀드 종목의 일간정보를 반환하는 함수 |  | /stock/m008/hist_info |
| kquant | daily_index | data.stock.daily 업종의 일간정보를 반환하는 함수 |  | /stock/m002/hist_info /stock/m004/hist_info |
| kquant | daily_investor_index | data.stock.daily 특정 업종지수의 과거 일간 투자자 정보를 반환하는 함수 |  | /stock/m002/invest_hist_info /stock/m004/invest_hist_info |
| kquant | daily_kosdaq_index | data.stock.daily 코스닥 업종의 일간정보를 반환하는 함수 |  | /stock/m004/hist_info |
| kquant | daily_kospi_index | data.stock.daily 거래소 업종의 일간정보를 반환하는 함수 |  | /stock/m002/hist_info |
| kquant | daily_lend_stock | data.stock.daily 주식 종목의 일자별 대차잔고 정보를 반환하는 함수 |  | /stock/m001/loan_hist_info /stock/m003/loan_hist_info |
| kquant | daily_margin_stock | data.stock.daily 주식 종목의 일자별 신용잔고 및 대주 정보를 반환하는 함수 |  | /stock/m001/credit_hist_info /stock/m003/credit_hist_info |
| kquant | daily_short_stock | data.stock.daily 주식 종목의 일자별 공매도 정보를 반환하는 함수 |  | /stock/m001/short_hist_info /stock/m003/short_hist_info |
| kquant | daily_stock | data.stock.daily 주식 종목의 일간정보를 반환하는 함수 |  | /stock/m001/hist_info /stock/m003/hist_info |
| kquant | info_basic_fund | data.stock.info 상장 펀드의 정보를 출력하는 함수 |  | /stock/m008/basic_info |
| kquant | info_basic_index | data.stock.info 업종/지수의 정보를 출력하는 함수 |  | /stock/m002/basic_info /stock/m004/basic_info |
| kquant | info_basic_stock | data.stock.info 단일 주식 종목의 간단한 현재 상태 정보를 출력하는 함수 |  | /stock/m001/basic_info /stock/m003/basic_info |
| kquant | info_basic_stocks | data.stock.info 복수 주식 종목의 간단한 현재 상태 정보를 출력하는 함수 |  | /stock/m001/basic_info_port /stock/m003/basic_info_port |
| kquant | info_stock | data.stock.info 단일 주식 종목의 모든 현재 상태 정보를 출력하는 함수 |  | /stock/m001/basic_info_all /stock/m003/basic_info_all |
| kquant | info_stocks | data.stock.info 복수 주식종목들의 모든 현재 상태 정보를 출력하는 함수 |  | /stock/m001/basic_info_all /stock/m003/basic_info_all |
| kquant | intra_fund | data.stock.intra 상장 펀드 종목의 당일 일중(intraday) 시장정보를 반환하는 함수 |  | /stock/m008/intra_info |
| kquant | intra_index | data.stock.intra 업종 지수의 당일 일중(intraday) 10초/1분 단위 시장정보를 반환하는 함수 |  | /stock/m002/intra_info /stock/m004/intra_info |
| kquant | intra_kosdaq_index | data.stock.intra 코스닥 업종 지수의 당일 일중(intraday) 시장정보를 반환하는 함수 |  | /stock/m004/intra_info |
| kquant | intra_kospi_index | data.stock.intra 거래소 업종 지수의 당일 일중(intraday) 시장정보를 반환하는 함수 |  | /stock/m002/intra_info |
| kquant | intra_stock | data.stock.intra 주식 종목의 당일 일중(intraday) 시장정보를 반환하는 함수 |  | /stock/m001/intra_info /stock/m003/intra_info /stock/m001/intra_date /stock/m003/intra_date |
| kquant | quote_stock | data.stock.intra 주식 종목의 호가 정보를 반환하는 함수 |  | /stock/m001/hoga_info /stock/m003/hoga_info |
| kquant | trade_fund | data.stock.intra 상장 펀드의 당일 일중(intraday) 틱데이터를 반환하는 함수 |  | /stock/m008/tick_info |
| kquant | trade_index | data.stock.intra 예상지수를 포함한 업종 지수의 당일 일중(intraday) 틱데이터를 반환하는 함수 |  | /stock/m002/tick_info /stock/m004/tick_info |
| kquant | trade_stock | data.stock.intra 예상 체결가를 포함한 주식 종목의 체결 틱데이터 정보를 반환하는 함수 |  | /stock/m001/tick_info /stock/m003/tick_info |
| kquant | period_fund | data.stock.period 상장 펀드 종목의 주/월/분기/연도별 주기 정보를 반환하는 함수 |  | /stock/m008/term_hist_info |
| kquant | period_index | data.stock.period 업종/지수의 주/월/분기/연도별 주기 정보를 반환하는 함수 |  | /stock/m002/term_hist_info /stock/m004/term_hist_info |
| kquant | period_stock | data.stock.period 주식 종목의 주/월/분기/연도별 주기 정보를 반환하는 함수 |  | /stock/m001/term_hist_info /stock/m003/term_hist_info |
| kquant | rank_stocks | data.stock.rank 당일의 주식 전종목 정보를 기준 순위별로 정렬하여 출력하는 함수 |  | /stock/m001/rank /stock/m003/rank |
| kquant | sum_block_stocks | data.stock.sum 종목별 대량매매 기간합산 정보를 반환하는 함수 |  | /stock/m001/rank_mass_date /stock/m003/rank_mass_date |
| kquant | sum_broker_stocks | data.stock.sum 회원사별 매매집계 기간합산 정보를 반환하는 함수 |  | /stock/m001/member_date /stock/m003/member_date |
| kquant | sum_investor_stocks | data.stock.sum 전종목의 투자자 기간합산 정보를 반환하는 함수 |  | /stock/m001/rank_invest_date /stock/m003/rank_invest_date |
| kquant | sum_short_stocks | data.stock.sum 종목별 공매도 기간합산 정보를 반환하는 함수 |  | /stock/m001/rank_short_date /stock/m003/rank_short_date |
| kquant | get_stock_market | data.stock.symbol 주식 종목의 해당 시장을 나타내는 문자열을 반환하는 함수 |  |  |
| kquant | get_stock_type | data.stock.symbol 주식 종목의 상품 증권그룹(유형 코드)를 반환하는 함수 |  |  |
| kquant | symbol_fund | data.stock.symbol 상장 펀드 목록을 반환하는 함수 |  | /stock/m008/code_info |
| kquant | symbol_index | data.stock.symbol 한국거래소(유가증권시장 및 코스닥시장) 지수 목록을 반환하는 함수 |  | /stock/m002/code_info /stock/m004/code_info |
| kquant | symbol_kosdaq_index | data.stock.symbol 코스닥시장 지수 목록을 반환하는 함수 |  | /stock/m004/code_info |
| kquant | symbol_kosdaq_stock | data.stock.symbol 코스닥시장 종목 목록을 반환하는 함수 |  | /stock/m003/code_info |
| kquant | symbol_kospi_index | data.stock.symbol 유가증권시장 지수 목록을 반환하는 함수 |  | /stock/m002/code_info |
| kquant | symbol_kospi_stock | data.stock.symbol 유가증권시장 종목 목록을 반환하는 함수 |  | /stock/m001/code_info |
| kquant | symbol_search_index | data.stock.symbol 지수 종목코드를 검색하는 함수 |  |  |
| kquant | symbol_search_stock | data.stock.symbol 주식 종목코드를 검색하는 함수 |  |  |
| kquant | symbol_stock | data.stock.symbol 한국거래소(유가증권시장 및 코스닥시장) 종목 목록을 반환하는 함수 |  | /stock/m001/code_info /stock/m003/code_info |
| kquant | DATE_IN | types 날짜 정보를 인수로 받는 대부분의 kquant 함수의 인수 타입은 DATE_IN 타입입니다. |  |  |
| kquant | KQuantDuplicatedSymbolInPort | types 포트폴리오 주문시 중복된 종목코드가 있는 경우 발생하는 사용자 경고 |  |  |
| kquant | KQuantInvalidSymbol | types 올바르지 않은 주식 종목 단축코드 사용시 발생하는 사용자 경고 |  |  |
| kquant | KQuantLowerLimit | types 하한가 종목 매수시 발생하는 사용자 경고 |  |  |
| kquant | KQuantNotAllowLoan | types 보유 현금보다 많은 현금이 필요한 매수 주문시 발생하는 사용자 경고 |  |  |
| kquant | KQuantNotAllowShort | types 보유하지 않거나 보유수량보다 많은 매도 주문시 발생하는 사용자 경고 |  |  |
| kquant | KQuantUpperLimit | types 상한가 종목 매수시 발생하는 사용자 경고 |  |  |
| kquant | display_html | utils HTML 문자열을 화면에 표시 |  |  |
| kquant | ticksize | utils 주식 호가가격단위 |  |  |
