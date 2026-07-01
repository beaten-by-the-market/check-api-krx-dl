# CHECK API Domain: future

Endpoint count: 331

## m005

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m005/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m005/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist |  | 38 |
| /future/m005/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m005/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m005/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m005/hoga_info_port | 호가정보 | cust_id, auth_key, codelist |  | 24 |
| /future/m005/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m005/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 22 |
| /future/m005/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 20 |
| /future/m005/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m005/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m005/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m005/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m005/tick_date | 체결정보 | cust_id, auth_key, jcode, edate |  | 25 |
| /future/m005/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m006

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m006/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 48 |
| /future/m006/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 48 |
| /future/m006/code_info | 코드정보 | cust_id, auth_key |  | 11 |
| /future/m006/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m006/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m006/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m006/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m006/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 22 |
| /future/m006/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 20 |
| /future/m006/invest_basic_info | 기본정보 | cust_id, auth_key |  | 80 |
| /future/m006/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 81 |
| /future/m006/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 81 |
| /future/m006/old_code_info | 과거 종목(코드정보) | cust_id, auth_key, yyyymm |  | 6 |
| /future/m006/old_hist_info | 과거종목(일별정보) | cust_id, auth_key, jcode, sdate, edate |  | 13 |
| /future/m006/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m006/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m012

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m012/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 46 |
| /future/m012/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 46 |
| /future/m012/code_info | 코드정보 | cust_id, auth_key |  | 11 |
| /future/m012/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m012/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m012/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m012/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m012/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 22 |
| /future/m012/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 20 |
| /future/m012/invest_basic_info | 기본정보 | cust_id, auth_key |  | 80 |
| /future/m012/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 81 |
| /future/m012/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 81 |
| /future/m012/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m012/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m013

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m013/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m013/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m013/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m013/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m013/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m013/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m013/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m013/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m013/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m016

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m016/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 39 |
| /future/m016/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 39 |
| /future/m016/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m016/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m016/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m016/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m016/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m016/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m016/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m016/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m016/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m016/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m017

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m017/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 39 |
| /future/m017/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 39 |
| /future/m017/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m017/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m017/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m017/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m017/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m017/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m017/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m017/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m017/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m017/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m018

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m018/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m018/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m018/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m018/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m018/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m018/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m018/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m018/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m018/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m019

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m019/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m019/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m019/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m019/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m019/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m019/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m019/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m019/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m019/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m062

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m062/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 39 |
| /future/m062/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 39 |
| /future/m062/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m062/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m062/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m062/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m062/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m062/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m062/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m062/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m062/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m062/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m067

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m067/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m067/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m067/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m067/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m067/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m067/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m067/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m067/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m067/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m067/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m067/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m067/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m067/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m067/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m091

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m091/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m091/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m091/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m091/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m091/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m091/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m091/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m091/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 22 |
| /future/m091/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 20 |
| /future/m091/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m091/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m100

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m100/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m100/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m100/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m100/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m100/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m100/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m100/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m100/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m100/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m100/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m100/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m103

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m103/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m103/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m103/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m103/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m103/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m103/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m103/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m103/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m103/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m103/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m103/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m103/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m103/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m103/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m104

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m104/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 48 |
| /future/m104/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 48 |
| /future/m104/code_info | 코드정보 | cust_id, auth_key |  | 11 |
| /future/m104/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m104/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m104/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m104/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m104/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m104/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m104/invest_basic_info | 기본정보 | cust_id, auth_key |  | 80 |
| /future/m104/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 81 |
| /future/m104/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 81 |
| /future/m104/old_code_info | 과거 종목(코드정보) | cust_id, auth_key, yyyymm |  | 6 |
| /future/m104/old_hist_info | 과거종목(일별정보) | cust_id, auth_key, jcode, sdate, edate |  | 13 |
| /future/m104/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m104/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m105

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m105/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m105/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m105/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m105/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m105/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m105/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m105/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m105/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m105/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m180

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m180/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 48 |
| /future/m180/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 48 |
| /future/m180/code_info | 코드정보 | cust_id, auth_key |  | 11 |
| /future/m180/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m180/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m180/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m180/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m180/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m180/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m181

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m181/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m181/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m181/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m181/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m181/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m181/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m181/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m181/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m181/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m182

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m182/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 48 |
| /future/m182/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 48 |
| /future/m182/code_info | 코드정보 | cust_id, auth_key |  | 11 |
| /future/m182/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m182/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m182/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m182/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m182/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m182/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m182/invest_basic_info | 기본정보 | cust_id, auth_key |  | 80 |
| /future/m182/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 81 |
| /future/m182/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 81 |
| /future/m182/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m182/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m221

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m221/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 39 |
| /future/m221/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 39 |
| /future/m221/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m221/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m221/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m221/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m221/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m221/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m221/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m221/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m221/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m221/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m232

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m232/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m232/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist |  | 38 |
| /future/m232/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m232/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m232/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m232/hoga_info_port | 호가정보 | cust_id, auth_key, codelist |  | 24 |
| /future/m232/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m232/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 22 |
| /future/m232/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 20 |
| /future/m232/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m232/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m232/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m232/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m232/tick_date | 체결정보 | cust_id, auth_key, jcode, edate |  | 25 |
| /future/m232/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m233

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m233/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m233/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist |  | 38 |
| /future/m233/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m233/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m233/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m233/hoga_info_port | 호가정보 | cust_id, auth_key, codelist |  | 24 |
| /future/m233/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m233/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 22 |
| /future/m233/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 20 |
| /future/m233/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m233/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m233/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m233/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m233/tick_date | 체결정보 | cust_id, auth_key, jcode, edate |  | 25 |
| /future/m233/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m234

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m234/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 48 |
| /future/m234/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 48 |
| /future/m234/code_info | 코드정보 | cust_id, auth_key |  | 11 |
| /future/m234/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m234/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m234/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m234/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m234/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 22 |
| /future/m234/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 20 |
| /future/m234/invest_basic_info | 기본정보 | cust_id, auth_key |  | 80 |
| /future/m234/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 81 |
| /future/m234/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 81 |
| /future/m234/old_code_info | 과거 종목(코드정보) | cust_id, auth_key, yyyymm |  | 6 |
| /future/m234/old_hist_info | 과거종목(일별정보) | cust_id, auth_key, jcode, sdate, edate |  | 13 |
| /future/m234/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m234/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m235

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m235/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 48 |
| /future/m235/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 48 |
| /future/m235/code_info | 코드정보 | cust_id, auth_key |  | 11 |
| /future/m235/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m235/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m235/hoga_info_port | 호가정보(복수종목) | cust_id, auth_key, codelist |  | 24 |
| /future/m235/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m235/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 22 |
| /future/m235/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 20 |
| /future/m235/invest_basic_info | 기본정보 | cust_id, auth_key |  | 80 |
| /future/m235/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 81 |
| /future/m235/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 81 |
| /future/m235/old_code_info | 과거 종목(코드정보) | cust_id, auth_key, yyyymm |  | 6 |
| /future/m235/old_hist_info | 과거종목(일별정보) | cust_id, auth_key, jcode, sdate, edate |  | 13 |
| /future/m235/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m235/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m236

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m236/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m236/basic_info_port | 기본정보(복수종목) | cust_id, auth_key, codelist |  | 38 |
| /future/m236/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m236/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m236/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m236/hoga_info_port | 호가정보 | cust_id, auth_key, codelist |  | 24 |
| /future/m236/hoga_info_port_top | 호가정보(복수종목_최우선) | cust_id, auth_key, codelist |  | 6 |
| /future/m236/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 22 |
| /future/m236/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 20 |
| /future/m236/invest_basic_info | 기본정보 | cust_id, auth_key |  | 40 |
| /future/m236/invest_hist_info | 기본정보 | cust_id, auth_key, sdate, edate |  | 41 |
| /future/m236/invest_intra_info | 주기정보(30초) | cust_id, auth_key |  | 41 |
| /future/m236/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m236/tick_date | 체결정보 | cust_id, auth_key, jcode, edate |  | 25 |
| /future/m236/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m237

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m237/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 39 |
| /future/m237/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 39 |
| /future/m237/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m237/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m237/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m237/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m237/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m237/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m237/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m238

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m238/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 38 |
| /future/m238/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 38 |
| /future/m238/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m238/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m238/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m238/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m238/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m238/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m238/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |

## m239

| API URL | 제목 | 필수 파라미터 | 선택 파라미터 | 응답 필드 수 |
| --- | --- | --- | --- | --- |
| /future/m239/basic_info | 기본정보 | cust_id, auth_key, jcode |  | 39 |
| /future/m239/basic_info_port | 기본정보 | cust_id, auth_key, codelist |  | 39 |
| /future/m239/code_info | 코드정보 | cust_id, auth_key |  | 8 |
| /future/m239/hist_info | 일별정보 | cust_id, auth_key, jcode, sdate, edate |  | 20 |
| /future/m239/hoga_info | 호가정보 | cust_id, auth_key, jcode |  | 24 |
| /future/m239/intra_date | 주기정보(10초) | cust_id, auth_key, jcode, edate |  | 18 |
| /future/m239/intra_info | 주기정보(10초) | cust_id, auth_key, jcode |  | 16 |
| /future/m239/term_hist_info | 일별정보 | cust_id, auth_key, jcode, term, sdate, edate |  | 18 |
| /future/m239/tick_info | 체결정보 | cust_id, auth_key, jcode |  | 25 |
