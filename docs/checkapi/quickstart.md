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
curl "https://checkapi.koscom.co.kr/stock/m001/hist_info?cust_id=$CHECK_CUST_ID&auth_key=$CHECK_AUTH_KEY&jcode=005930&sdate=20250101&edate=20250131"
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

response = requests.get(f"{BASE_URL}/stock/m001/hist_info", params=params, timeout=60)
response.raise_for_status()
data = response.json()
print(data)
```

## 응답 처리 원칙

- `success: true`이면 `results`를 pandas DataFrame으로 변환한다.
- `success: false`이면 `message` 또는 `errmsg`를 사용자에게 그대로 보여준다.
- `data_list`를 비우면 전체 필드를 조회한다. 네트워크/응답 크기를 줄이고 싶으면 필요한 F-code만 쉼표로 넘긴다.
