# kquant Data Loading Recipes

## 인증 정보 설정

```python
import kquant as kq

kq.set_api("API_ID", "API_KEY")
api_id, api_key = kq.get_api()
```

`get_api()`는 설정 파일이 없으면 `FileNotFoundError`를 낼 수 있습니다.

## 종목 목록

```python
import kquant as kq

stocks = kq.symbol_stock()
kospi = kq.symbol_kospi_stock()
kosdaq = kq.symbol_kosdaq_stock()
funds = kq.symbol_fund()
```

## 일봉

```python
df = kq.daily_stock("005930", start_date="20250101", end_date="20250131")
fund = kq.daily_fund("069500")
kospi_index = kq.daily_kospi_index("001")
```

## 일중/체결/호가

```python
minute = kq.intra_stock("005930", interval="1M")
tick = kq.trade_stock("005930", count=100, loc="last")
quote = kq.quote_stock("005930")
```

## 투자자/공매도/대차/신용/대량매매

```python
investor = kq.sum_investor_stocks(start_date="20250101", end_date="20250131")
short = kq.daily_short_stock("005930")
lend = kq.daily_lend_stock("005930")
margin = kq.daily_margin_stock("005930")
block = kq.daily_block_stock("005930")
```

## kquant에 없는 데이터

kquant mapping에 없는 endpoint는 `examples/python/checkapi_raw_client.py`의 `CheckApiClient`를 사용한다.
