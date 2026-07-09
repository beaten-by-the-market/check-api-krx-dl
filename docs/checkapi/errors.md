# CHECK API Errors

| errmsg | 영문 설명 | 한글 설명 |
| --- | --- | --- |
| access_denied | User denied access | 고객번호 또는 인증키가 유효하지 않습니다. |
| criteria_code_denied | Input code is not found | 입력한 기준코드가 유효하지 않습니다. |
| date_denied | Input date is invalid | 입력한 날짜가 유효하지 않습니다. |
| jcode_denied | Input code is not found | 입력한 종목코드가 유효하지 않습니다. |
| param_denied | Input parameter is not found | 입력한 종목코드 또는 날짜가 유효하지 않습니다. |
| term_denied | Input term is not found | 입력한 조회 데이터 주기가 유효하지 않습니다. |
| up_code_denied | Input code is not found | 입력한 업종코드가 유효하지 않습니다. |

## errmsg 없이 `message` 로만 오는 실패 (실측)

이 셋은 위 표의 `errmsg` 체계가 아니라 `{"success": false, "message": "..."}` 형태로 온다.
**HTTP 200 으로 오므로 `results or []` 로 흘리면 "데이터 0건"으로 조용히 기록된다.**

| message | 의미 | 대응 |
| --- | --- | --- |
| `일 최대 사용량 1,000,000,000Bytes를 초과했습니다.` | 일 사용량 한도(1GB, `cust_id` 단위) 소진 | 일 단위 리셋 대기. `data_list` 로 응답 바이트 절감 |
| `시계열 데이터의 조회는 1초에 1회로 제한됩니다.` | 시계열 rate limit | 호출 간 ≥1.15초 간격 |
| `cust_id 또는 auth_key가 정확하지 않습니다.` | 키 오류 **또는 미등록 IP** | 아래 `access_denied` 가이드 |

**한도 초과 vs IP 차단은 메시지로 구분된다.** 위쪽 메시지가 오면 인증·IP는 정상이고 계량기만 막힌 것이다.

`rank_invest_date` 등 기간합산 계열은 **조회기간 1년 초과 시** `param_denied` +
`조회기간은 1년을 초과할 수 없습니다.` 이며, 응답이 지나치게 크면 **HTTP 502 Proxy Error** 가 난다
(월 단위로 분할할 것).

## 처리 가이드

- `access_denied`: `cust_id`, `auth_key` 재확인. 값이 맞는데도 거부되면 **호출 IP가 발급 시 등록한 IP인지** 확인 (등록 외 IP도 같은 인증 실패로 응답)
- `jcode_denied`: 종목코드/업종코드 시장 구분 재확인
- `date_denied`: `YYYYMMDD` 형식 및 조회 가능 기간 확인
- `term_denied`: `daily`, `weekly`, `monthly`, `quarterly`, `YTD`, `yearly` 등 endpoint 설명에 맞는 값 사용
- `criteria_code_denied`: 순위 조회 기준 필드가 해당 endpoint의 Data Set에 있는지 확인
