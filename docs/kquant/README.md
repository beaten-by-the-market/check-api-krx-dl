# kquant

`kquant`는 KOSCOM이 배포한 Python 패키지입니다. CHECK API 일부 endpoint를 pandas DataFrame/Series 중심 함수로 감싸고, 차트/백테스트/기술 분석 유틸을 제공합니다.

## 패키지 정보

- 최신 확인 버전: 0.3.6
- Python: >=3.9
- 라이선스: Commercial
- PyPI: https://pypi.org/project/kquant/0.3.6/
- GitHub 문서 저장소: https://github.com/koscom/kquant

## 문서 기준 규모

- 공개 함수/타입 문서: 96
- 데이터 조회 함수: 58
- CHECK API endpoint를 직접 감싸는 함수: 44
- 연결된 CHECK API endpoint: 62

## 설치

```bash
pip install kquant
```

## 기본 사용

```python
import kquant as kq

kq.set_api("발급받은 API ID", "발급받은 API KEY")
df = kq.daily_stock("005930")
print(df.tail())
```

## 언제 kquant를 쓰나

- 주식/지수/펀드/일부 채권/FX 데이터를 pandas로 바로 받고 싶을 때
- 백테스트/차트/기술 지표 계산까지 이어갈 때
- CHECK API F-code를 직접 다루기보다 표준 컬럼명(`OPEN`, `HIGH`, `LOW`, `CLOSE`, `VOLUME`)을 쓰고 싶을 때
