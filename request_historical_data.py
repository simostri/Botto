


import json
import pandas as pd
import mplfinance as mpf
import talib
# Disable SSL Warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def read_historical_data(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data

def input_parameters():
    indicator_type = input("Enter indicator type (e.g., 'SMA', 'EMA'): ")
    period = int(input("Enter period for the indicator: "))
    return indicator_type, period


def add_indicators(df, indicator_type, period):
    if indicator_type == 'SMA':
        df['SMA'] = talib.SMA(df['Close'], timeperiod=period)
    elif indicator_type == 'EMA':
        df['EMA'] = talib.EMA(df['Close'], timeperiod=period)
    # Add more conditions for other indicators
    return df

def preprocess_data(data, indicator_type, period):
    df = pd.DataFrame(data['data'])

    # Convert timestamp to datetime and set as index
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df.set_index('t', inplace=True)

    # Rename columns to match mplfinance format
    df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close'}, inplace=True)

    # Add TA-Lib indicators
    df = add_indicators(df, indicator_type, period)

    return df


def plotCandlestick(df, indicator_type):
    # Decide which indicator to plot
    if indicator_type == 'SMA':
        indicator_plot = df['SMA']
    elif indicator_type == 'EMA':
        indicator_plot = df['EMA']
    # Add more conditions for other indicators

    # Plotting
    ap = [mpf.make_addplot(indicator_plot, color='blue')]
    mpf.plot(df, type='candle', style='charles', title='S&P 500 Price Action', addplot=ap)


def calculate_bollinger_bands(df, window=20, no_of_stds=2):
    rolling_mean = df['Close'].rolling(window=window).mean()
    rolling_std = df['Close'].rolling(window=window).std()
    df['Upper Band'] = rolling_mean + (rolling_std * no_of_stds)
    df['Lower Band'] = rolling_mean - (rolling_std * no_of_stds)
    return df

def backtest_strategy(df):
    # Calculate Bollinger Bands
    df = calculate_bollinger_bands(df)

    # Initialize columns for signals
    df['Position'] = None

    # Generate trading signals
    for i in range(len(df)):
        if df['Close'].iloc[i] < df['Lower Band'].iloc[i]:
            df['Position'].iloc[i] = 1  # Buy
        elif df['Close'].iloc[i] > df['Upper Band'].iloc[i]:
            df['Position'].iloc[i] = -1  # Sell
        else:
            df['Position'].iloc[i] = 0  # Neutral

    # Calculate daily returns and strategy returns
    df['Market Return'] = df['Close'].pct_change()
    df['Strategy Return'] = df['Market Return'] * df['Position'].shift(1)

    # Calculate cumulative returns
    df['Cumulative Market Returns'] = (1 + df['Market Return']).cumprod()
    df['Cumulative Strategy Returns'] = (1 + df['Strategy Return']).cumprod()

    return df


if __name__ == "__main__":
    file_path = 'historical_data_2M_5min.json'
    data = read_historical_data(file_path)
    indicator_type, period = input_parameters()
    data = preprocess_data(data, indicator_type, period)
    plotCandlestick(data, indicator_type)
    backtest_results = backtest_strategy(data)
