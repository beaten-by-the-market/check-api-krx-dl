"""Small CHECK API raw client.

Environment variables:
    CHECK_CUST_ID: CHECK terminal customer id
    CHECK_AUTH_KEY: CHECK API auth key
"""

from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests


class CheckApiClient:
    def __init__(
        self,
        cust_id: str | None = None,
        auth_key: str | None = None,
        base_url: str = "https://checkapi.koscom.co.kr",
        timeout: int = 60,
    ) -> None:
        self.cust_id = cust_id or os.environ["CHECK_CUST_ID"]
        self.auth_key = auth_key or os.environ["CHECK_AUTH_KEY"]
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, apiurl: str, **params: Any) -> dict[str, Any]:
        payload = {
            "cust_id": self.cust_id,
            "auth_key": self.auth_key,
            **{k: v for k, v in params.items() if v is not None},
        }
        response = requests.get(f"{self.base_url}{apiurl}", params=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        if data.get("success") is False:
            raise RuntimeError(data.get("message") or data.get("errmsg") or data)
        return data

    def dataframe(self, apiurl: str, **params: Any) -> pd.DataFrame:
        data = self.request(apiurl, **params)
        results = data.get("results", data)
        return pd.DataFrame(results if isinstance(results, list) else [results])


if __name__ == "__main__":
    client = CheckApiClient()
    df = client.dataframe(
        "/stock/m001/hist_info",
        jcode="005930",
        sdate="20250101",
        edate="20250131",
    )
    print(df.tail())
