# CHECK API Parameter Dictionary

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| - | - | X | 조회기간에 따라서 30초 이상 소요될 수 있습니다. |
| auth_key | String | O | API 인증키 |
| check_code | String | O | 지표코드 (ex : USISMMAM) |
| codelist | String | O | 종목코드 리스트 ( '247540', '086520', '091990' ) |
| criteria_code | String | O | 정렬코드 (종목투자자별순매수거래량8-기관: F06508_08 등 아래 Data-Set 참조) |
| cust_id | String | O | CHECK 단말 고객번호 10자리 (ex : NS00000001) |
| data_list | String | X | 조회항목 리스트 ( F16013, F16002, F15001 ) / 입력하지 않으면 전체 Data Set 조회 — **아래 주의** |
| dcnt | String | X | 데이터 갯수 (ex : 100, default : 전체) |
| dwm_type | String | O | 주기구분 1자리 (ex : '1') |
| edate | String | O | 조회 마지막 날짜 8자리 (ex: 20220801) |
| eyear | String | X | 조회 마지막 년도 4자리 (ex: 2022, 해당년도 미포함) |
| F12506 | String | O | 조회 대상일자 (ex : 20230228) |
| F14729 | String | X | 시장종류 리스트 ( '11', '12', '13' ) ** 샘플 참고 |
| F16357 | String | O | 코스콤 회사코드 (ex : 2988) |
| gubun | String | O | 1 : 52주 신고가, 2 : 52주 신저가, 3 : 역사적 신고가, 4 : 역사적 신저가 |
| icode | String | O | 계정코드 6자리 (ex : 110000) |
| inst_cd | String | O | 제공처 1자리 (ex : '0') |
| jcode | String | O | 조회대상 업종코드 (ex : 51) |
| ncode | String | O | 뉴스 코드 12자리 (ex: 220N00000451) |
| ndate | String | O | 뉴스 일자 8자리 (ex: 20230314) |
| order | String | X | ASC : 시간별 오름차순, DESC : 시간별 내림차순 (default : ASC) |
| sdate | String | O | 조회 시작 날짜 8자리 (ex: 20210801) |
| sort_code | String | O | 정렬순서코드 (0: 내림차순, 1:오름차순) |
| syear | String | X | 조회 시작 년도 4자리 (ex: 2021, 해당년도 포함) |
| term | String | O | 조회 데이터 주기 (ex:daily, weekly, monthly, quarterly, YTD, yearly) |
| up_code | String | X | 업종코드 ('1' 로 고정, NXT 업종 활성화되면 반영) |
| yyyymm | String | O | 만기년월 (ex : 202112) |

## `data_list` 주의 (실측)

**일 사용량 한도(1,000,000,000 bytes / `cust_id`)를 지키는 가장 중요한 수단**이다. 응답 필드를 골라 받으면
바이트가 수십 분의 1이 된다(`rank_invest_date` 123필드 → 3필드에서 1.1GB → 48MB).

- ⚠ **존재하지 않는 F-code를 오류 없이 조용히 버린다.** 요청한 개수와 반환된 필드 개수를 반드시 대조할 것.
  (실제 사례: 매수거래량을 `F06506_12`로 넣었으나 실제 코드는 `F06507_12` — 경고 없이 필드만 사라졌다.)
- ⚠ **명세에 없어도 동작하는 endpoint가 있다.** NXT 패밀리(m222/m223)는 2/23개만 문서화돼 있으나
  `rank_invest_date`·`hist_info` 등에서 실제로 동작한다. 명세에 없다고 포기하지 말고 1회 호출로 probe 할 것.
