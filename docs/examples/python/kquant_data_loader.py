"""kquant data loading examples.

Run:
    pip install kquant

Before use, either call kq.set_api(...) once or provide credentials in your
environment and call set_api from those values.
"""

from __future__ import annotations

import os

import kquant as kq


def configure_from_env() -> None:
    api_id = os.environ.get("CHECK_API_ID") or os.environ.get("CHECK_CUST_ID")
    api_key = os.environ.get("CHECK_API_KEY") or os.environ.get("CHECK_AUTH_KEY")
    if not api_id or not api_key:
        raise RuntimeError("Set CHECK_API_ID/CHECK_API_KEY or CHECK_CUST_ID/CHECK_AUTH_KEY.")
    kq.set_api(api_id, api_key)


def load_samsung_daily():
    return kq.daily_stock("005930", start_date="20250101", end_date="20250131")


def load_stock_universe():
    return kq.symbol_stock()


def load_intraday(symbol: str = "005930"):
    return kq.intra_stock(symbol, interval="1M")


if __name__ == "__main__":
    configure_from_env()
    print(load_samsung_daily().tail())
