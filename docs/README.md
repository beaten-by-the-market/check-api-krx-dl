# CHECK API / kquant Knowledge Base

이 폴더는 CHECK API 공식 SPA 명세와 KOSCOM kquant 문서를 바탕으로 만든 작업용 지식 베이스입니다. 목적은 두 가지입니다.

1. 챗봇이 API/함수/파라미터 질문에 일관되게 답할 수 있게 한다.
2. 사용자의 CHECK API 인증 정보가 있을 때 데이터를 실제로 불러오는 코드를 빠르게 작성할 수 있게 한다.

## 폴더 구조

- `checkapi/`: 원천 CHECK API REST endpoint 문서
- `kquant/`: Python 패키지 `kquant` 사용 문서와 CHECK API 매핑
- `chatbot/`: 챗봇 답변 규칙, 조회 라우팅, 검색 인덱스
- `catalogs/`: CSV 형태의 endpoint/function catalog
- `examples/python/`: 바로 실행 가능한 Python 예제 클라이언트

## 빠른 판단

- Python에서 주식/지수/펀드/일부 채권/FX 데이터를 편하게 가져올 때는 먼저 `kquant`를 쓴다.
- kquant에 없는 endpoint, 파생/해외/뉴스/공시/기타 재무 endpoint는 CHECK API raw 호출을 쓴다.
- 실제 데이터 조회에는 CHECK API의 `cust_id`와 `auth_key`가 필요하다.
- 인증 정보가 없으면 명세 설명과 코드 예시는 가능하지만 실제 데이터는 받을 수 없다.

## 원천 산출물

- `../checkapi-specs.json`: CHECK API 전체 명세 747개
- `../kquant-docs.json`: kquant 문서 96개 함수/타입
