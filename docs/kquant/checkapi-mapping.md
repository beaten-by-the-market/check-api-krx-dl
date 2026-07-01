# kquant to CHECK API Mapping

kquant 함수가 내부적으로 사용하는 CHECK API endpoint 목록입니다.

| kquant 함수 | 모듈 | 설명 | CHECK API |
| --- | --- | --- | --- |
| symbol_bond | data.ficc.symbol | 채권 종목 코드를 반환하는 함수 | /bond/m038/code_info |
| symbol_bond_ktb | data.ficc.symbol | 장내 국채 종목 코드를 반환하는 함수 | /bond/m161/code_info |
| symbol_fx | data.ficc.symbol | 외환정보 종목 목록을 반환하는 함수 | /bond/m023/code_info |
| symbol_fx_swap | data.ficc.symbol | 외환스왑 종목 목록을 반환하는 함수 | /bond/m026/code_info |
| daily_block_stock | data.stock.daily | 주식 종목의 일자별 대량매매 정보를 반환하는 함수 | /stock/m001/mass_hist_info<br>/stock/m003/mass_hist_info |
| daily_fund | data.stock.daily | 상장 펀드 종목의 일간정보를 반환하는 함수 | /stock/m008/hist_info |
| daily_index | data.stock.daily | 업종의 일간정보를 반환하는 함수 | /stock/m002/hist_info<br>/stock/m004/hist_info |
| daily_investor_index | data.stock.daily | 특정 업종지수의 과거 일간 투자자 정보를 반환하는 함수 | /stock/m002/invest_hist_info<br>/stock/m004/invest_hist_info |
| daily_kosdaq_index | data.stock.daily | 코스닥 업종의 일간정보를 반환하는 함수 | /stock/m004/hist_info |
| daily_kospi_index | data.stock.daily | 거래소 업종의 일간정보를 반환하는 함수 | /stock/m002/hist_info |
| daily_lend_stock | data.stock.daily | 주식 종목의 일자별 대차잔고 정보를 반환하는 함수 | /stock/m001/loan_hist_info<br>/stock/m003/loan_hist_info |
| daily_margin_stock | data.stock.daily | 주식 종목의 일자별 신용잔고 및 대주 정보를 반환하는 함수 | /stock/m001/credit_hist_info<br>/stock/m003/credit_hist_info |
| daily_short_stock | data.stock.daily | 주식 종목의 일자별 공매도 정보를 반환하는 함수 | /stock/m001/short_hist_info<br>/stock/m003/short_hist_info |
| daily_stock | data.stock.daily | 주식 종목의 일간정보를 반환하는 함수 | /stock/m001/hist_info<br>/stock/m003/hist_info |
| info_basic_fund | data.stock.info | 상장 펀드의 정보를 출력하는 함수 | /stock/m008/basic_info |
| info_basic_index | data.stock.info | 업종/지수의 정보를 출력하는 함수 | /stock/m002/basic_info<br>/stock/m004/basic_info |
| info_basic_stock | data.stock.info | 단일 주식 종목의 간단한 현재 상태 정보를 출력하는 함수 | /stock/m001/basic_info<br>/stock/m003/basic_info |
| info_basic_stocks | data.stock.info | 복수 주식 종목의 간단한 현재 상태 정보를 출력하는 함수 | /stock/m001/basic_info_port<br>/stock/m003/basic_info_port |
| info_stock | data.stock.info | 단일 주식 종목의 모든 현재 상태 정보를 출력하는 함수 | /stock/m001/basic_info_all<br>/stock/m003/basic_info_all |
| info_stocks | data.stock.info | 복수 주식종목들의 모든 현재 상태 정보를 출력하는 함수 | /stock/m001/basic_info_all<br>/stock/m003/basic_info_all |
| intra_fund | data.stock.intra | 상장 펀드 종목의 당일 일중(intraday) 시장정보를 반환하는 함수 | /stock/m008/intra_info |
| intra_index | data.stock.intra | 업종 지수의 당일 일중(intraday) 10초/1분 단위 시장정보를 반환하는 함수 | /stock/m002/intra_info<br>/stock/m004/intra_info |
| intra_kosdaq_index | data.stock.intra | 코스닥 업종 지수의 당일 일중(intraday) 시장정보를 반환하는 함수 | /stock/m004/intra_info |
| intra_kospi_index | data.stock.intra | 거래소 업종 지수의 당일 일중(intraday) 시장정보를 반환하는 함수 | /stock/m002/intra_info |
| intra_stock | data.stock.intra | 주식 종목의 당일 일중(intraday) 시장정보를 반환하는 함수 | /stock/m001/intra_info<br>/stock/m003/intra_info<br>/stock/m001/intra_date<br>/stock/m003/intra_date |
| quote_stock | data.stock.intra | 주식 종목의 호가 정보를 반환하는 함수 | /stock/m001/hoga_info<br>/stock/m003/hoga_info |
| trade_fund | data.stock.intra | 상장 펀드의 당일 일중(intraday) 틱데이터를 반환하는 함수 | /stock/m008/tick_info |
| trade_index | data.stock.intra | 예상지수를 포함한 업종 지수의 당일 일중(intraday) 틱데이터를 반환하는 함수 | /stock/m002/tick_info<br>/stock/m004/tick_info |
| trade_stock | data.stock.intra | 예상 체결가를 포함한 주식 종목의 체결 틱데이터 정보를 반환하는 함수 | /stock/m001/tick_info<br>/stock/m003/tick_info |
| period_fund | data.stock.period | 상장 펀드 종목의 주/월/분기/연도별 주기 정보를 반환하는 함수 | /stock/m008/term_hist_info |
| period_index | data.stock.period | 업종/지수의 주/월/분기/연도별 주기 정보를 반환하는 함수 | /stock/m002/term_hist_info<br>/stock/m004/term_hist_info |
| period_stock | data.stock.period | 주식 종목의 주/월/분기/연도별 주기 정보를 반환하는 함수 | /stock/m001/term_hist_info<br>/stock/m003/term_hist_info |
| rank_stocks | data.stock.rank | 당일의 주식 전종목 정보를 기준 순위별로 정렬하여 출력하는 함수 | /stock/m001/rank<br>/stock/m003/rank |
| sum_block_stocks | data.stock.sum | 종목별 대량매매 기간합산 정보를 반환하는 함수 | /stock/m001/rank_mass_date<br>/stock/m003/rank_mass_date |
| sum_broker_stocks | data.stock.sum | 회원사별 매매집계 기간합산 정보를 반환하는 함수 | /stock/m001/member_date<br>/stock/m003/member_date |
| sum_investor_stocks | data.stock.sum | 전종목의 투자자 기간합산 정보를 반환하는 함수 | /stock/m001/rank_invest_date<br>/stock/m003/rank_invest_date |
| sum_short_stocks | data.stock.sum | 종목별 공매도 기간합산 정보를 반환하는 함수 | /stock/m001/rank_short_date<br>/stock/m003/rank_short_date |
| symbol_fund | data.stock.symbol | 상장 펀드 목록을 반환하는 함수 | /stock/m008/code_info |
| symbol_index | data.stock.symbol | 한국거래소(유가증권시장 및 코스닥시장) 지수 목록을 반환하는 함수 | /stock/m002/code_info<br>/stock/m004/code_info |
| symbol_kosdaq_index | data.stock.symbol | 코스닥시장 지수 목록을 반환하는 함수 | /stock/m004/code_info |
| symbol_kosdaq_stock | data.stock.symbol | 코스닥시장 종목 목록을 반환하는 함수 | /stock/m003/code_info |
| symbol_kospi_index | data.stock.symbol | 유가증권시장 지수 목록을 반환하는 함수 | /stock/m002/code_info |
| symbol_kospi_stock | data.stock.symbol | 유가증권시장 종목 목록을 반환하는 함수 | /stock/m001/code_info |
| symbol_stock | data.stock.symbol | 한국거래소(유가증권시장 및 코스닥시장) 종목 목록을 반환하는 함수 | /stock/m001/code_info<br>/stock/m003/code_info |
