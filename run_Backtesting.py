import json
import pandas as pd
import talib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

import datetime
import pandas_ta as ta
import pandas as pd

from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import crossover
import backtesting
import numpy as np
#backtesting.set_bokeh_output(notebook=False)

# Disable SSL Warnings
import urllib3


def read_historical_data(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data

def preprocess_data(data):
    df = pd.DataFrame(data['data'])
    # Convert timestamp to datetime and set as index
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df.set_index('t', inplace=True)

    # Rename columns to match mplfinance format
    df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close'}, inplace=True)
    df['Volume'] = 0
    return df


class SmaCross(Strategy):
    n1 = 20
    n2 = 20

    # Do as much initial computation as possible
    def init(self):
        close = self.data.Close
        self.sma = talib.SMA(close , timeperiod=self.n1)
        self.ema = talib.EMA(close , timeperiod=self.n2)
    
        self.cross = self.sma -self.ema
        sma_diff = np.diff(self.sma)
        self.sma_diff = np.insert(sma_diff, 0, np.nan)
        self.sma_peak = (sma_diff[:-1] >= 0) & (sma_diff[1:] < 0)
        self.sma_valley = (sma_diff[:-1] <= 0) & (sma_diff[1:] > 0)
        print('bought')
        
    def next(self):
        if self.cross[-1] < 0 and self.sma_valley[-1]:
            price = self.data.Close[-1]
            self.buy(tp=1.02*price)
            print('bought')
        elif (self.cross[-1] > 0 and self.sma_peak[-1]): #or (self.data.Close - self.data.Price >=1.03)
            self.position.close()
            print('sold')


file_path = 'historical_data_1y_1h.json'
data = read_historical_data(file_path)
data = preprocess_data(data)
bt = Backtest(data, SmaCross, cash=1000, commission=.002)
stats = bt.run()
print(stats)
#bt.plot()
