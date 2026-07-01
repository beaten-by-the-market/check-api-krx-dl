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

## 처리 가이드

- `access_denied`: `cust_id`, `auth_key` 재확인
- `jcode_denied`: 종목코드/업종코드 시장 구분 재확인
- `date_denied`: `YYYYMMDD` 형식 및 조회 가능 기간 확인
- `term_denied`: `daily`, `weekly`, `monthly`, `quarterly`, `YTD`, `yearly` 등 endpoint 설명에 맞는 값 사용
- `criteria_code_denied`: 순위 조회 기준 필드가 해당 endpoint의 Data Set에 있는지 확인
