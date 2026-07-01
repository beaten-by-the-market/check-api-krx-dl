# kquant Backtest / Analysis

## 백테스트 핵심 함수

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

## 기술 분석 문서 노출 함수

| 함수 | 설명 | 시그니처 |
| --- | --- | --- |
| sma | 단순이동평균(SMA: Simple Moving Average) 계산 함수 | `sma( df: 'pd.DataFrame', length: 'int'=10, column: 'str'='CLOSE', out_column: 'Optional[str]'=None, inplace: 'bool'=False, ) -> pd.DataFrame` |
| entropy | 이동 엔트로피(Entropy) | `entropy( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=10, inplace: 'bool'=False, ) -> pd.DataFrame` |
| kurtosis | 이동 첨도 (Rolling Kurtosis) | `kurtosis( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| mad | 이동 평균절대편차 (Rolling Mean Absolute Deviation) | `mad( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| median | 이동 중앙값 (Rolling Median) | `median( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| quantile | 이동 분위수 (Rolling Quantile) | `quantile( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, q: 'float'=0.0, inplace: 'bool'=False, ) -> pd.DataFrame` |
| skew | 이동 왜도 (Rolling Skew) | `skew( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| stdev | 이동 표준편차 (Rolling Standard Deviation) | `stdev( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| variance | 이동 분산 (Rolling Variance) | `variance( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| zscore | 이동 Z-스코어 (Rolling Z Score) | `zscore( df: 'pd.DataFrame', column: 'str'='CLOSE', length: 'int'=30, inplace: 'bool'=False, ) -> pd.DataFrame` |
| above | A 시계열 값이 B 시계열 값 이상이면 True, 미만이면 False를 반환하는 함수 | `above( df: 'pd.DataFrame', column_a: 'str', column_b: 'str', out_column: 'str'='ABOVE', inplace: 'bool'=False, ) -> pd.DataFrame` |
| above_value | 시계열 값이 기준 설정값 이상이면 True, 미만이면 False를 반환하는 함수 | `above_value( df: 'pd.DataFrame', column: 'str', value: 'float', out_column: 'str'='ABOVE', inplace: 'bool'=False, ) -> pd.DataFrame` |
| below | A 시계열 값이 B 시계열 값 이하이면 True, 초과면 False를 반환하는 함수 | `below( df: 'pd.DataFrame', column_a: 'str', column_b: 'str', out_column: 'str'='BELOW', inplace: 'bool'=False, ) -> pd.DataFrame` |
| below_value | 시계열 값이 기준 설정값 이하이면 True, 초과면 False를 반환하는 함수 | `below_value( df: 'pd.DataFrame', column: 'str', value: 'float', out_column: 'str'='BELOW', inplace: 'bool'=False, ) -> pd.DataFrame` |
| cross | 두 시그널이 교차하는 지점을 찾아내는 함수 | `cross( df: 'pd.DataFrame', column_a: 'str', column_b: 'str', out_column_up: 'str'='CROSS_UP', out_column_down: 'str'='CROSS_DOWN', inplace: 'bool'=False, ) -> pd.DataFrame` |
| cross_value | 시그널이 설정값을 교차하는 지점을 찾아내는 함수 | `cross_value( df: 'pd.DataFrame', column: 'str', value: 'float', out_column_up: 'str'='CROSS_UP', out_column_down: 'str'='CROSS_DOWN', inplace: 'bool'=False, ) -> pd.DataFrame` |

## 주의

- wheel 내부에는 더 많은 `.pyd` 모듈이 있지만 공식 문서 링크에 노출된 함수만 위 목록에 포함했다.
- 백테스트는 상한가/하한가/공매도/미수 허용 여부에 따라 사용자 경고 타입을 낼 수 있다.
- 실전 매매 체결 모델이 아니라 일봉 기준 검증용으로 보는 것이 안전하다.
