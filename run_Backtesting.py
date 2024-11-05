import json
import pandas as pd
import talib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import time
import datetime
import pandas_ta as ta
import pandas as pd
from backtesting.test import SMA
from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import crossover
import backtesting
import numpy as np
backtesting.set_bokeh_output(notebook=False)

# Disable SSL Warnings
#import urllib3

def EMA(arr: pd.Series,n: int) -> pd.Series:
    return talib.EMA(arr, timeperiod=n)


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


class DollarCostAveraging(Strategy):
    n1 = 50
    n2 = 50

    # Do as much initial computation as possible
    def init(self):
        close = self.data.Close
        self.sma = self.I(SMA, close, self.n1) 
        #self.ema = self.I(EMA, close, self.n2) 
        self.ema = self.I(EMA, close, self.n2) 
        
        self.cross = self.sma -self.ema
        self.sma_diff = np.diff(self.sma,prepend=np.nan)
        
        sma_peak = (self.sma_diff[:-1] >= 0) & (self.sma_diff[1:] < 0)
        self.sma_peak = np.insert(sma_peak, 0, False)
        
        self.sma_valley = np.insert((self.sma_diff[:-1] <= 0) & (self.sma_diff[1:] > 0), 0, False)
        self.Sell_Signal =(self.cross > 0) & self.sma_peak
        self.Buy_Signal = (self.cross < 0) & self.sma_valley
        global Data
        Data = pd.DataFrame({
            'Close': close,
            'Open': self.data.Open,
            'High': self.data.High,
            'Low': self.data.Low,
            'Volume': self.data.Volume,
            'SMA': self.sma,
            'EMA': self.ema,
            'SMA_Diff': self.sma_diff,
            'SMA_Peak': self.sma_peak,
            'SMA_Valley': self.sma_valley,
            'Cross': self.cross,
            'Buy_Signal': (self.cross < 0) & self.sma_valley,
            'Sell_Signal': (self.cross > 0) & self.sma_peak
        }, index=self.data.index)
        
    def next(self):
        if self.Buy_Signal[-1]==True:#self.cross[-1] < 0 & self.sma_valley[-1]:
            print('bought')
            self.buy()
            
        elif self.Sell_Signal[-1]==True and self.data.Close[-1] >= self.trades[0].entry_price*1.2:
            self.position.close()
            print('sold')
            self.closed_trades


file_path = 'historical_data_1y_1h.json'
data = read_historical_data(file_path)
data = preprocess_data(data)
bt = Backtest(data, DollarCostAveraging, cash=1000, commission=.002, exclusive_orders=False)
stats = bt.run()
print('plotting')
bt.plot(filename='test_plot')
print('plot done')
print(stats)

