# CHECK API Quickstart

## 인증 정보

- `cust_id`: CHECK 단말 고객번호 10자리
- `auth_key`: API 인증키

인증이 틀리면 일반적으로 다음 형태가 내려옵니다.

```json
{"success": false, "message": "cust_id 또는 auth_key가 정확하지 않습니다."}
```

## curl 예시

```bash
# 파라미터는 -d (요청 본문)로 전달. GET/쿼리스트링은 인증 거부됨.
curl -X POST "https://checkapi.koscom.co.kr/stock/m001/hist_info" \
  -d "cust_id=$CHECK_CUST_ID" \
  -d "auth_key=$CHECK_AUTH_KEY" \
  -d "jcode=005930" \
  -d "sdate=20250101" \
  -d "edate=20250131"
```

## Python requests 예시

```python
import os
import requests

BASE_URL = "https://checkapi.koscom.co.kr"

params = {
    "cust_id": os.environ["CHECK_CUST_ID"],
    "auth_key": os.environ["CHECK_AUTH_KEY"],
    "jcode": "005930",
    "sdate": "20250101",
    "edate": "20250131",
}

# 파라미터는 params(쿼리스트링)가 아니라 data(요청 본문)로 전달해야 합니다.
response = requests.post(f"{BASE_URL}/stock/m001/hist_info", data=params, timeout=60)
response.raise_for_status()
data = response.json()
print(data)
```

## 응답 처리 원칙

- `success: true`이면 `results`를 pandas DataFrame으로 변환한다.
- `success: false`이면 `message` 또는 `errmsg`를 사용자에게 그대로 보여준다.
- `data_list`를 비우면 전체 필드를 조회한다. 네트워크/응답 크기를 줄이고 싶으면 필요한 F-code만 쉼표로 넘긴다.

## 응답 필드는 F-code다

`results`의 각 행은 컬럼명이 한글이 아니라 **F-code**입니다. 예를 들어 `/stock/m001/hist_info` 응답은 이렇게 내려옵니다.

```json
{"F12506": 20250605, "F16013": "005930", "F15001": "59100", "F15010": "59900", "F15011": "57900"}
```

| F-code | 의미 |
| --- | --- |
| F12506 | 입회일 |
| F16013 | 단축코드 |
| F15001 | 현재가 |
| F15010 | 고가 |
| F15011 | 저가 |

사람이 읽는 컬럼명으로 바꾸려면 `../catalogs/checkapi-response-fields.csv`(전체 F-code 사전) 또는 `../../checkapi-specs.json`의 `specs[].res`로 **F-code → 설명**을 매핑하세요. endpoint마다 내려오는 F-code 집합이 다르므로, 클라이언트/MCP에서는 해당 endpoint의 `res` 정의를 기준으로 디코딩하는 것이 안전합니다.
