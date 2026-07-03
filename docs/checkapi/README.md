# CHECK API

CHECK API는 `https://checkapi.koscom.co.kr`를 base URL로 사용하는 금융 데이터 REST API입니다.

## 규모

- 전체 endpoint: 747
- 도메인: bond, etc, ext, future, news, stock
- 고유 입력 파라미터: 28
- 고유 응답 필드: 1592
- 고유 에러 코드: 7

## 기본 호출 형태

```text
POST https://checkapi.koscom.co.kr{apiurl}
Content-Type: application/x-www-form-urlencoded

cust_id=...&auth_key=...&jcode=...
```

**반드시 `POST`로 호출하고 파라미터는 요청 본문(body)에 담아야 합니다.** `GET`으로 보내거나, `POST`라도 파라미터를 URL 쿼리스트링에 넣으면 자격증명이 맞아도 `{"success": false, "message": "cust_id 또는 auth_key가 정확하지 않습니다."}`로 거부됩니다. 본문 형식은 form-urlencoded와 JSON 둘 다 동작합니다.

대부분 endpoint는 `cust_id`, `auth_key`가 필수입니다. 일부 조회는 `jcode`, `sdate`, `edate`, `term`, `codelist`, `data_list` 등을 추가로 받습니다.

## 자주 쓰는 공통 파라미터

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| cust_id | O | CHECK 단말 고객번호 10자리 (ex : NS00000001) |
| auth_key | O | API 인증키 |
| data_list | X | 조회항목 리스트 ( F16013, F16002, F15001 ) / 입력하지 않으면 전체 Data Set 조회 |
| jcode | O | 조회대상 업종코드 (ex : 51) |
| codelist | O | 종목코드 리스트 ( '247540', '086520', '091990' ) |
| sdate | O | 조회 시작 날짜 8자리 (ex: 20210801) |
| edate | O | 조회 마지막 날짜 8자리 (ex: 20220801) |
| term | O | 조회 데이터 주기 (ex:daily, weekly, monthly, quarterly, YTD, yearly) |
| up_code | X | 업종코드 ('1' 로 고정, NXT 업종 활성화되면 반영) |
| criteria_code | O | 정렬코드 (종목투자자별순매수거래량8-기관: F06508_08 등 아래 Data-Set 참조) |
| dcnt | X | 데이터 갯수 (ex : 100, default : 전체) |

## 문서 읽는 순서

1. [quickstart.md](quickstart.md): raw API 호출 방식
2. [endpoint-catalog.md](endpoint-catalog.md): 전체 endpoint 한눈에 보기
3. [domains/](domains/): 도메인별 상세 목록
4. [recipes.md](recipes.md): 데이터 조회 목적별 예시
5. [errors.md](errors.md): 에러 처리
