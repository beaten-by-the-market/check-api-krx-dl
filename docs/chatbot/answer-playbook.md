# Answer Playbook

## 질문 유형별 라우팅

### "삼성전자 일봉 가져와줘"

추천 답변:

1. kquant 사용 가능 여부 확인
2. `kq.daily_stock("005930", start_date="YYYYMMDD", end_date="YYYYMMDD")` 제시
3. 인증이 없으면 `kq.set_api(...)` 먼저 안내

### "CHECK API endpoint 알려줘"

추천 답변:

1. endpoint URL
2. 필수/선택 파라미터
3. 주요 응답 필드
4. curl/Python raw 예시

### "kquant에 있나?"

추천 답변:

1. `kquant/checkapi-mapping.md`에서 함수 검색
2. 있으면 함수명/시그니처/연결 endpoint 제시
3. 없으면 raw CHECK API endpoint로 대체

### "실제로 데이터를 불러와줘"

추천 답변:

1. 로컬/환경 변수에 인증 정보가 있는지 확인
2. 있으면 `examples/python`의 클라이언트 패턴으로 호출
3. 없으면 필요한 인증 변수 이름과 실행 코드를 제공

## 답변 템플릿

```text
가능합니다. 이 데이터는 [kquant 함수명 또는 CHECK API endpoint]로 조회합니다.

필수 입력:
- ...

Python 예시:
```python
...
```

주의:
- ...
```
