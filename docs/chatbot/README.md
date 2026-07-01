# Chatbot Guide

이 문서는 CHECK API/kquant 질의에 답하는 챗봇을 위한 운영 규칙입니다.

## 기본 원칙

1. 사용자가 Python/pandas 중심으로 데이터를 원하면 kquant 함수를 먼저 찾는다.
2. kquant에 없는 endpoint는 CHECK API raw 호출로 안내한다.
3. 실제 데이터 호출에는 `cust_id`/`auth_key` 또는 kquant `set_api`가 필요하다고 명확히 말한다.
4. 인증키 없이 실제 값을 만들어내지 않는다.
5. 날짜는 `YYYYMMDD` 또는 kquant가 받는 날짜 입력 형식으로 구체화한다.
6. 사용자가 시장을 말하지 않으면 종목 코드로 KOSPI/KOSDAQ 구분이 필요할 수 있다고 설명한다.

## 우선 참조 파일

- kquant 함수 찾기: `../kquant/function-catalog.md`
- kquant와 CHECK API 매핑: `../kquant/checkapi-mapping.md`
- raw endpoint 찾기: `../checkapi/endpoint-catalog.md`
- response F-code 찾기: `../catalogs/checkapi-response-fields.csv`
- 에러 처리: `../checkapi/errors.md`
