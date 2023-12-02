import json
import pandas as pd
import mplfinance as mpf
import talib
# Disable SSL Warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


if __name__ == "__main__":
    file_path = 'historical_data_2M_5min.json'
    data = read_historical_data(file_path)
    indicator_type, period = input_parameters()
    data = preprocess_data(data, indicator_type, period)
    plotCandlestick(data, indicator_type)
    backtest_results = backtest_strategy(data)