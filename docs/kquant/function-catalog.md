# kquant Function Catalog

## analysis.stock.backtest

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| add_order_from_signals | 시그널 열의 값을 이용하여 매매수량을 계산하는 함수 | `add_order_from_signals( df: 'pd.DataFrame', buy_signal: 'str', sell_signal: 'str', ) -> pd.DataFrame` |
| backtest_plot_stock_daily | 백테스트 결과를 챠트로 시각화하는 함수 | `backtest_plot_stock_daily( df_result: 'pd.DataFrame', title: 'Optional[str]'=None, height: 'Optional[int]'=800, width: 'Optional[int]'=None, ) -> go.Figure` |
| backtest_stats_stock_daily | 백테스트의 성능 평가를 위한 함수 | `backtest_stats_stock_daily( df_result: 'pd.DataFrame', days_in_year: 'int'=252, ) -> pd.Series` |
| backtest_stock_daily | 단일 주식의 일간기준 백테스트 수행 | `backtest_stock_daily( symbol: 'str', order: 'Union[pd.DataFrame, Callable[[str, dt.datetime, pd.DataFrame, pd.DataFrame, logging.Logger], int]]', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, init_cash: 'int'=0, close_on_end: 'bool'=False, allow_loan: 'bool'=False, broker_fee_percent: 'float'=0.0, exchange_fee_percent: 'float'=0.0, trade_tax_percent: 'float'=0.0, slippage_tick: 'int'=0, return_position: 'bool'=False, use_notadj: 'bool'=False, logger: 'Optional[logging.Logger]'=None, logname: 'Optional[str]'=None, logpath: 'Optional[str]'=None, loglevel: 'Optional[int]'=None, return_logger: 'Optional[bool]'=False, ) -> Union[pd.DataFrame, tuple[pd.DataFrame, pd.DataFrame], tuple[pd.DataFrame, logging.Logger], tuple[pd.DataFrame, pd.DataFrame, logging.Logger]]` |
| backtest_stock_port_daily | 주식 포트폴리오의 일간기준 백테스트 수행 | `backtest_stock_port_daily( order: 'Union[pd.DataFrame, Callable[[dt.datetime, dict[str, pd.DataFrame], dict[str, pd.DataFrame], logging.Logger], list[tuple[str, int]]]]', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, init_cash: 'int'=0, close_on_end: 'bool'=False, allow_loan: 'bool'=False, broker_fee_percent: 'float'=0.0, exchange_fee_percent: 'float'=0.0, trade_tax_percent: 'float'=0.0, slippage_tick: 'int'=0, return_position: 'bool'=False, use_notadj: 'bool'=False, logger: 'Optional[logging.Logger]'=None, logname: 'Optional[str]'=None, logpath: 'Optional[str]'=None, loglevel: 'Optional[int]'=None, return_logger: 'Optional[bool]'=False, ) -> Union[dict[str, pd.DataFrame], tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]], tuple[dict[str, pd.DataFrame], logging.Logger], tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], logging.Logger]]` |
| backtest_update_stock_daily | 단일 주식의 일간기준 백테스트 결과를 하루 단위로 업데이트하는 함수 | `backtest_update_stock_daily( symbol: 'str', order: 'int'=0, date: 'DATE_IN'=None, df_result: 'Optional[pd.DataFrame]'=None, df_position: 'Optional[pd.DataFrame]'=None, init_cash: 'int'=0, trade_close: 'bool'=False, allow_loan: 'bool'=False, broker_fee_percent: 'float'=0.0, exchange_fee_percent: 'float'=0.0, trade_tax_percent: 'float'=0.0, slippage_tick: 'int'=0, use_notadj: 'bool'=False, logger: 'Optional[logging.Logger]'=None, logname: 'Optional[str]'=None, logpath: 'Optional[str]'=None, loglevel: 'Optional[int]'=None, return_logger: 'Optional[bool]'=False, ) -> tuple[pd.DataFrame, pd.DataFrame] | tuple[pd.DataFrame, pd.DataFrame, logging.Logger]` |
| backtest_update_stock_port_daily | 복수 주식의 일간기준 백테스트 결과를 하루 단위로 업데이트하는 함수 | `backtest_update_stock_port_daily( symbols_and_orders: 'list[tuple[str, int]]', date: 'DATE_IN', dict_df_result: 'Optional[dict[str, pd.DataFrame]]'=None, dict_df_position: 'Optional[dict[str, pd.DataFrame]]'=None, init_cash: 'int'=0, trade_close: 'bool'=False, allow_loan: 'bool'=False, broker_fee_percent: 'float'=0.0, exchange_fee_percent: 'float'=0.0, trade_tax_percent: 'float'=0.0, slippage_tick: 'int'=0, use_notadj: 'bool'=False, logger: 'Optional[logging.Logger]'=None, logname: 'Optional[str]'=None, logpath: 'Optional[str]'=None, loglevel: 'Optional[int]'=None, return_logger: 'Optional[bool]'=False, ) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]] | tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], logging.Logger]` |
| handle_stock_merge | 액면병합을 처리하는 함수 | `handle_stock_merge( ratio: 'int', df_position: 'pd.DataFrame', ) -> tuple[pd.DataFrame, float]` |
| handle_stock_split | 액면분할을 처리하는 함수 | `handle_stock_split( ratio: 'int', df_position: 'pd.DataFrame', ) -> pd.DataFrame` |

## analysis.stock.ta.moving_average

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| sma | 단순이동평균(SMA: Simple Moving Average) 계산 함수 | `sma( df: 'pd.DataFrame', length: 'int'=10, column: 'str'='CLOSE', out_column: 'Optional[str]'=None, inplace: 'bool'=False, ) -> pd.DataFrame` |

## analysis.stock.ta.statistics

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| entropy | 이동 엔트로피(Entropy) | `entropy( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=10, inplace: 'bool'=False, ) -> pd.DataFrame` |
| kurtosis | 이동 첨도 (Rolling Kurtosis) | `kurtosis( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| mad | 이동 평균절대편차 (Rolling Mean Absolute Deviation) | `mad( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| median | 이동 중앙값 (Rolling Median) | `median( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| quantile | 이동 분위수 (Rolling Quantile) | `quantile( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, q: 'float'=0.0, inplace: 'bool'=False, ) -> pd.DataFrame` |
| skew | 이동 왜도 (Rolling Skew) | `skew( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| stdev | 이동 표준편차 (Rolling Standard Deviation) | `stdev( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| variance | 이동 분산 (Rolling Variance) | `variance( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| zscore | 이동 Z-스코어 (Rolling Z Score) | `zscore( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |

## analysis.stock.ta.utility

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| above | A 시계열 값이 B 시계열 값 이상이면 True, 미만이면 False를 반환하는 함수 | `above( df: 'pd.DataFrame', column_a: 'str', column_b: 'str', out_column: 'str'='ABOVE', inplace: 'bool'=False, ) -> pd.DataFrame` |
| above_value | 시계열 값이 기준 설정값 이상이면 True, 미만이면 False를 반환하는 함수 | `above_value( df: 'pd.DataFrame', column: 'str', value: 'float', out_column: 'str'='ABOVE', inplace: 'bool'=False, ) -> pd.DataFrame` |
| below | A 시계열 값이 B 시계열 값 이하이면 True, 초과면 False를 반환하는 함수 | `below( df: 'pd.DataFrame', column_a: 'str', column_b: 'str', out_column: 'str'='BELOW', inplace: 'bool'=False, ) -> pd.DataFrame` |
| below_value | 시계열 값이 기준 설정값 이하이면 True, 초과면 False를 반환하는 함수 | `below_value( df: 'pd.DataFrame', column: 'str', value: 'float', out_column: 'str'='BELOW', inplace: 'bool'=False, ) -> pd.DataFrame` |
| cross | 두 시그널이 교차하는 지점을 찾아내는 함수 | `cross( df: 'pd.DataFrame', column_a: 'str', column_b: 'str', out_column_up: 'str'='CROSS_UP', out_column_down: 'str'='CROSS_DOWN', inplace: 'bool'=False, ) -> pd.DataFrame` |
| cross_value | 시그널이 설정값을 교차하는 지점을 찾아내는 함수 | `cross_value( df: 'pd.DataFrame', column: 'str', value: 'float', out_column_up: 'str'='CROSS_UP', out_column_down: 'str'='CROSS_DOWN', inplace: 'bool'=False, ) -> pd.DataFrame` |

## api

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| get_api | 설정된 CHECK-API 서비스용 API ID 및 API KEY를 반환하는 함수 | `get_api() -> tuple[str, str]` |
| set_api | CHECK-API 서비스용 API ID 및 API KEY를 설정 및 저장하는 함수 | `set_api( api_id: 'str', api_key: 'str', )` |

## chart

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| chart_candle | 일간 캔들챠트를 출력하는 함수 | `chart_candle( df: 'pd.DataFrame', overlay: 'Optional[dict[Union[str, pd.Series], Any]]'=None, date: 'Optional[Union[str, pd.Series]]'=None, open: 'Optional[Union[str, pd.Series]]'=None, high: 'Optional[Union[str, pd.Series]]'=None, low: 'Optional[Union[str, pd.Series]]'=None, close: 'Optional[Union[str, pd.Series]]'=None, volume: 'Optional[Union[str, pd.Series]]'=None, start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, title: 'Optional[str]'=None, height: 'Optional[int]'=None, width: 'Optional[int]'=None, **candle_opt, ) -> go.Figure` |
| chart_line | 일간 라인챠트를 출력하는 함수 | `chart_line( df: 'pd.DataFrame', overlay: 'Optional[dict[Union[str, pd.Series], dict[str, Any]]]'=None, date: 'Optional[Union[str, pd.Series]]'=None, close: 'Optional[Union[str, pd.Series]]'=None, volume: 'Optional[Union[str, pd.Series]]'=None, start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, title: 'Optional[str]'=None, height: 'Optional[int]'=None, width: 'Optional[int]'=None, row_heights: 'Optional[list[float]]'=None, **line_opt, ) -> go.Figure` |

## data.company

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| account_code | 재무제표 계정 코드 정보를 담은 데이터프레임을 출력하는 함수 | `account_code() -> pd.DataFrame` |
| account_code_search | 한글 계정명이 해당 문자열을 포함하는 계정코드를 반환하는 함수 | `account_code_search( keyword: 'str', ) -> pd.DataFrame` |
| account_history | 재무제표 계정의 과거기록을 출력하는 함수 | `account_history( symbol: 'Union[str, List[str]]', account_code: 'str', period: "Literal['y', 'q']"='y', consolidated: 'bool'=True, pivot: 'bool'=False, ) -> pd.DataFrame` |
| company_info | 기업 일반정보를 반환하는 함수 | `company_info( symbol: 'str', ) -> pd.Series` |
| latest_yearmonth | 기업의 최신 재무제표 발표 기준 연월을 출력하는 함수 | `latest_yearmonth( symbol: 'str', ) -> str` |

## data.disclosure

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| disclosure_stock | 주식 공시 정보를 반환하는 함수 | `disclosure_stock( symbol: 'str', date: 'DATE_IN'=None, count: 'int'=100, ) -> pd.DataFrame` |

## data.ficc.daily

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| daily_fx_swap | 외환스왑 일간정보를 반환하는 함수 | `daily_fx_swap( symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |

## data.ficc.info

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| info_bond | 장내채권 발행 정보를 출력하는 함수 | `info_bond( symbol: 'str', ) -> pd.DataFrame` |
| info_fx_swap | 외환스왑 종목 정보를 출력하는 함수 | `info_fx_swap( symbol: 'str', ) -> pd.DataFrame` |

## data.ficc.symbol

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| symbol_bond | 채권 종목 코드를 반환하는 함수 | `symbol_bond() -> pd.DataFrame` |
| symbol_bond_ktb | 장내 국채 종목 코드를 반환하는 함수 | `symbol_bond_ktb() -> pd.DataFrame` |
| symbol_fx | 외환정보 종목 목록을 반환하는 함수 | `symbol_fx() -> pd.DataFrame` |
| symbol_fx_swap | 외환스왑 종목 목록을 반환하는 함수 | `symbol_fx_swap() -> pd.DataFrame` |

## data.news

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| news_stock | 주식 뉴스 정보를 반환하는 함수 | `news_stock( symbol: 'str', date: 'DATE_IN'=None, count: 'int'=1000, ) -> pd.DataFrame` |

## data.stock.daily

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| daily_block_stock | 주식 종목의 일자별 대량매매 정보를 반환하는 함수 | `daily_block_stock( symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| daily_fund | 상장 펀드 종목의 일간정보를 반환하는 함수 | `daily_fund( symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| daily_index | 업종의 일간정보를 반환하는 함수 | `daily_index( market: 'str', symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| daily_investor_index | 특정 업종지수의 과거 일간 투자자 정보를 반환하는 함수 | `daily_investor_index( market: 'str', symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| daily_kosdaq_index | 코스닥 업종의 일간정보를 반환하는 함수 | `daily_kosdaq_index( symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| daily_kospi_index | 거래소 업종의 일간정보를 반환하는 함수 | `daily_kospi_index( symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| daily_lend_stock | 주식 종목의 일자별 대차잔고 정보를 반환하는 함수 | `daily_lend_stock( symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| daily_margin_stock | 주식 종목의 일자별 신용잔고 및 대주 정보를 반환하는 함수 | `daily_margin_stock( symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| daily_short_stock | 주식 종목의 일자별 공매도 정보를 반환하는 함수 | `daily_short_stock( symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| daily_stock | 주식 종목의 일간정보를 반환하는 함수 | `daily_stock( symbol: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |

## data.stock.info

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| info_basic_fund | 상장 펀드의 정보를 출력하는 함수 | `info_basic_fund( symbol: 'str', as_frame: 'bool'=False, ) -> Union[pd.Series, pd.DataFrame]` |
| info_basic_index | 업종/지수의 정보를 출력하는 함수 | `info_basic_index( market: 'str', symbol: 'str', as_frame: 'bool'=False, ) -> Union[pd.Series, pd.DataFrame]` |
| info_basic_stock | 단일 주식 종목의 간단한 현재 상태 정보를 출력하는 함수 | `info_basic_stock( symbol: 'str', as_frame: 'bool'=False, ) -> Union[pd.Series, pd.DataFrame]` |
| info_basic_stocks | 복수 주식 종목의 간단한 현재 상태 정보를 출력하는 함수 | `info_basic_stocks( symbols: 'list[str]', ) -> pd.DataFrame` |
| info_stock | 단일 주식 종목의 모든 현재 상태 정보를 출력하는 함수 | `info_stock( symbol: 'str', as_frame: 'bool'=False, ) -> Union[pd.Series, pd.DataFrame]` |
| info_stocks | 복수 주식종목들의 모든 현재 상태 정보를 출력하는 함수 | `info_stocks( symbols: 'list[str]', ) -> pd.DataFrame` |

## data.stock.intra

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| intra_fund | 상장 펀드 종목의 당일 일중(intraday) 시장정보를 반환하는 함수 | `intra_fund( symbol: 'str', ) -> pd.DataFrame` |
| intra_index | 업종 지수의 당일 일중(intraday) 10초/1분 단위 시장정보를 반환하는 함수 | `intra_index( market: 'str', symbol: 'str', interval: "Literal['10S', '1M']"='1M', ) -> pd.DataFrame` |
| intra_kosdaq_index | 코스닥 업종 지수의 당일 일중(intraday) 시장정보를 반환하는 함수 | `intra_kosdaq_index( symbol: 'str', interval: "Literal['10S', '1M']"='1M', ) -> pd.DataFrame` |
| intra_kospi_index | 거래소 업종 지수의 당일 일중(intraday) 시장정보를 반환하는 함수 | `intra_kospi_index( symbol: 'str', interval: "Literal['10S', '1M']"='1M', ) -> pd.DataFrame` |
| intra_stock | 주식 종목의 당일 일중(intraday) 시장정보를 반환하는 함수 | `intra_stock( symbol: 'str', date: 'DATE_IN'=None, interval: "Literal['10S', '1M']"='1M', ) -> pd.DataFrame` |
| quote_stock | 주식 종목의 호가 정보를 반환하는 함수 | `quote_stock( symbol: 'str', ) -> pd.Series` |
| trade_fund | 상장 펀드의 당일 일중(intraday) 틱데이터를 반환하는 함수 | `trade_fund( symbol: 'str', ) -> pd.DataFrame` |
| trade_index | 예상지수를 포함한 업종 지수의 당일 일중(intraday) 틱데이터를 반환하는 함수 | `trade_index( market: 'str', symbol: 'str', ) -> pd.DataFrame` |
| trade_stock | 예상 체결가를 포함한 주식 종목의 체결 틱데이터 정보를 반환하는 함수 | `trade_stock( symbol: 'str', count: 'int', loc: 'str'='last', ) -> pd.DataFrame` |

## data.stock.period

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| period_fund | 상장 펀드 종목의 주/월/분기/연도별 주기 정보를 반환하는 함수 | `period_fund( symbol: 'str', period: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| period_index | 업종/지수의 주/월/분기/연도별 주기 정보를 반환하는 함수 | `period_index( market: 'str', symbol: 'str', period: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |
| period_stock | 주식 종목의 주/월/분기/연도별 주기 정보를 반환하는 함수 | `period_stock( symbol: 'str', period: 'str', start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, ) -> pd.DataFrame` |

## data.stock.rank

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| rank_stocks | 당일의 주식 전종목 정보를 기준 순위별로 정렬하여 출력하는 함수 | `rank_stocks( order_key: 'str'='MARKETCAP', ) -> pd.DataFrame` |

## data.stock.sum

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| sum_block_stocks | 종목별 대량매매 기간합산 정보를 반환하는 함수 | `sum_block_stocks( start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, market: 'str | None'=None, ) -> pd.DataFrame` |
| sum_broker_stocks | 회원사별 매매집계 기간합산 정보를 반환하는 함수 | `sum_broker_stocks( start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, market: 'str | None'=None, ) -> pd.DataFrame` |
| sum_investor_stocks | 전종목의 투자자 기간합산 정보를 반환하는 함수 | `sum_investor_stocks( start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, market: 'str | None'=None, ) -> pd.DataFrame` |
| sum_short_stocks | 종목별 공매도 기간합산 정보를 반환하는 함수 | `sum_short_stocks( start_date: 'DATE_IN'=None, end_date: 'DATE_IN'=None, market: 'str | None'=None, ) -> pd.DataFrame` |

## data.stock.symbol

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| get_stock_market | 주식 종목의 해당 시장을 나타내는 문자열을 반환하는 함수 | `get_stock_market( symbol: 'str', ) -> str` |
| get_stock_type | 주식 종목의 상품 증권그룹(유형 코드)를 반환하는 함수 | `get_stock_type( symbol: 'str', ) -> str` |
| symbol_fund | 상장 펀드 목록을 반환하는 함수 | `symbol_fund() -> pd.DataFrame` |
| symbol_index | 한국거래소(유가증권시장 및 코스닥시장) 지수 목록을 반환하는 함수 | `symbol_index() -> pd.DataFrame` |
| symbol_kosdaq_index | 코스닥시장 지수 목록을 반환하는 함수 | `symbol_kosdaq_index() -> pd.DataFrame` |
| symbol_kosdaq_stock | 코스닥시장 종목 목록을 반환하는 함수 | `symbol_kosdaq_stock() -> pd.DataFrame` |
| symbol_kospi_index | 유가증권시장 지수 목록을 반환하는 함수 | `symbol_kospi_index() -> pd.DataFrame` |
| symbol_kospi_stock | 유가증권시장 종목 목록을 반환하는 함수 | `symbol_kospi_stock() -> pd.DataFrame` |
| symbol_search_index | 지수 종목코드를 검색하는 함수 | `symbol_search_index( *keyword_list: 'str', ) -> pd.DataFrame` |
| symbol_search_stock | 주식 종목코드를 검색하는 함수 | `symbol_search_stock( *keyword_list: 'str', ) -> pd.DataFrame` |
| symbol_stock | 한국거래소(유가증권시장 및 코스닥시장) 종목 목록을 반환하는 함수 | `symbol_stock() -> pd.DataFrame` |

## types

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| DATE_IN | 날짜 정보를 인수로 받는 대부분의 kquant 함수의 인수 타입은 DATE_IN 타입입니다. | `` |
| KQuantDuplicatedSymbolInPort | 포트폴리오 주문시 중복된 종목코드가 있는 경우 발생하는 사용자 경고 | `` |
| KQuantInvalidSymbol | 올바르지 않은 주식 종목 단축코드 사용시 발생하는 사용자 경고 | `` |
| KQuantLowerLimit | 하한가 종목 매수시 발생하는 사용자 경고 | `` |
| KQuantNotAllowLoan | 보유 현금보다 많은 현금이 필요한 매수 주문시 발생하는 사용자 경고 | `` |
| KQuantNotAllowShort | 보유하지 않거나 보유수량보다 많은 매도 주문시 발생하는 사용자 경고 | `` |
| KQuantUpperLimit | 상한가 종목 매수시 발생하는 사용자 경고 | `` |

## utils

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| display_html | HTML 문자열을 화면에 표시 | `display_html( content: 'str', )` |
| ticksize | 주식 호가가격단위 | `ticksize( price: 'int', up: 'bool'=True, ) -> int` |
