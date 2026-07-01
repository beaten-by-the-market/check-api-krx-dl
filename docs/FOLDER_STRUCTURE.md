# Folder Structure

```text
docs/
  README.md                         전체 지식 베이스 안내
  FOLDER_STRUCTURE.md               폴더/파일 역할 설명

  checkapi/
    README.md                       CHECK API 개요
    quickstart.md                   raw REST 호출 방법
    endpoint-catalog.md             747개 endpoint 전체 목록
    parameters.md                   공통/고유 입력 파라미터 사전
    errors.md                       에러 코드와 처리 가이드
    recipes.md                      목적별 조회 레시피
    domains/
      stock.md                      주식 250개 endpoint
      future.md                     파생 331개 endpoint
      bond.md                       채권 60개 endpoint
      ext.md                        해외 73개 endpoint
      news.md                       뉴스/공시 7개 endpoint
      etc.md                        경제/기업/재무 등 26개 endpoint

  kquant/
    README.md                       kquant 개요와 설치/인증
    function-catalog.md             96개 공개 함수/타입 목록
    checkapi-mapping.md             kquant 함수 -> CHECK API endpoint 매핑
    data-loading-recipes.md         kquant 데이터 로딩 예시
    backtest-analysis.md            백테스트/기술분석 함수 설명

  chatbot/
    README.md                       챗봇 운영 원칙
    answer-playbook.md              질문 유형별 답변 템플릿
    retrieval-index.md              챗봇 검색용 축약 인덱스

  catalogs/
    checkapi-endpoints.csv          endpoint 필터용 CSV
    checkapi-response-fields.csv    F-code 응답 필드 사전 CSV
    kquant-functions.csv            kquant 함수 필터용 CSV
    chatbot-retrieval-index.csv     챗봇 검색용 CSV

  examples/
    python/
      checkapi_raw_client.py        CHECK API 직접 호출 클라이언트
      kquant_data_loader.py         kquant 데이터 로더 예제
```

## 사용 흐름

1. 무슨 데이터가 필요한지 정한다.
2. 먼저 `kquant/checkapi-mapping.md`에서 kquant 함수가 있는지 확인한다.
3. 있으면 `kquant/data-loading-recipes.md`와 `examples/python/kquant_data_loader.py`를 사용한다.
4. 없으면 `checkapi/endpoint-catalog.md`에서 endpoint를 찾고 `examples/python/checkapi_raw_client.py`를 사용한다.
5. 챗봇 답변 품질을 맞출 때는 `chatbot/README.md`와 `chatbot/answer-playbook.md`를 기준으로 한다.
