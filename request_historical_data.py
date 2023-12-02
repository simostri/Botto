


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
    with open('config.json', 'r') as file:
        config = json.load(file)
    
    return config['indicators']


def add_indicators(df, indicator_type, period):
    if indicator_type == 'SMA':
        df['SMA'] = talib.SMA(df['Close'], timeperiod=period)
    elif indicator_type == 'EMA':
        df['EMA'] = talib.EMA(df['Close'], timeperiod=period)
    # Add more conditions for other indicators
    return df

def preprocess_data(data, indicators):
    df = pd.DataFrame(data['data'])

    # Convert timestamp to datetime and set as index
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df.set_index('t', inplace=True)

    # Rename columns to match mplfinance format
    df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close'}, inplace=True)

    # Add TA-Lib indicators for all specified in config
    for indicator in indicators:
        df = add_indicators(df, indicator['type'], indicator['period'])

    return df



def plotCandlestick(df, indicators):
    ap = []  # List to store additional plots

    # Loop through each indicator in the list
    for indicator in indicators:
        if indicator['type'] == 'SMA':
            ap.append(mpf.make_addplot(df['SMA'], color='blue', label='SMA ' + str(indicator['period'])))
        elif indicator['type'] == 'EMA':
            ap.append(mpf.make_addplot(df['EMA'], color='green', label='EMA ' + str(indicator['period'])))
        # Add more conditions for other indicators
    # Plot trade entry points
    entry_points = df[df['Trade Entry'] != 0]
    ap.append(mpf.make_addplot(entry_points['Trade Entry'], type='scatter', markersize=100, marker='^', color='green'))

    # Plot trade exit points
    exit_points = df[df['Trade Exit'] != 0]
    ap.append(mpf.make_addplot(exit_points['Trade Exit'], type='scatter', markersize=100, marker='v', color='red'))

    # Plotting with all the indicators and trade points
    mpf.plot(df, type='candle', style='charles', title='S&P 500 Price Action', addplot=ap, figratio=(16, 9), figscale=1.2)

    # Plotting with all the indicators
    mpf.plot(df, type='candle', style='charles', title='S&P 500 Price Action', addplot=ap, figratio=(16, 9), figscale=1.2)




def backtest_strategy(df, indicators):
    initial_balance = 1000  # Starting balance in euros
    trade_amount = 100     # Amount in euros invested per trade
    df['Balance'] = initial_balance
    df['entered'] = 0
    df['Trade Entry'] = 0
    df['Trade Exit'] = 0

    for indicator in indicators:
        indicator_name = indicator['type'] + ' ' + str(indicator['period'])
        # Add your indicator-specific logic here

    df['Cross'] = df['SMA'] - df['EMA']
    df['SMA_Diff'] = df['SMA'].diff()
    df['SMA_Peak'] = (df['SMA_Diff'].shift(1) > 0) & (df['SMA_Diff'] < 0)
    df['SMA_Valley'] = (df['SMA_Diff'].shift(1) < 0) & (df['SMA_Diff'] > 0)
    df['Position'] = 0

    for i in range(1, len(df)):
        if df['entered'].iloc[i-1] == 0:  # Not currently in a trade
            if df['Cross'].iloc[i] < 0 and df['SMA_Valley'].iloc[i]:  # Buy condition
                df['Position'].iloc[i] = 1
                df['entered'].iloc[i] = 1
            elif df['Cross'].iloc[i] > 0 and df['SMA_Peak'].iloc[i]:  # Sell condition
                df['Position'].iloc[i] = -1
                df['entered'].iloc[i] = 0
        else:
            # Continue the current trade
            df['entered'].iloc[i] = df['entered'].iloc[i-1]
            if df['Position'].iloc[i-1] == 1 and df['Cross'].iloc[i] > 0:  # Exit condition for buy trade
                df['Position'].iloc[i] = -1
                df['entered'].iloc[i] = 0
                # Mark trade entry and exit
    if df['Position'].iloc[i] == 1 and df['entered'].iloc[i] == 1:
        df['Trade Entry'].iloc[i] = df['Close'].iloc[i]
    elif df['Position'].iloc[i] == -1 and df['entered'].iloc[i] == 0:
        df['Trade Exit'].iloc[i] = df['Close'].iloc[i]

    # Calculate trade returns and update balance
    df['Trade Return'] = df['Close'].pct_change() * df['Position'].shift(1)
    for i in range(1, len(df)):
        if df['Position'].iloc[i] == 1:
            df['Balance'].iloc[i] = df['Balance'].iloc[i-1] - trade_amount
        elif df['Position'].iloc[i] == -1:
            df['Balance'].iloc[i] = df['Balance'].iloc[i-1] + trade_amount * (1 + df['Trade Return'].iloc[i])
        else:
            df['Balance'].iloc[i] = df['Balance'].iloc[i-1]

    return df



if __name__ == "__main__":
    file_path = 'historical_data_2M_5min.json'
    data = read_historical_data(file_path)
    indicators = input_parameters()
    print(indicators)  # Check the structure of indicators

    # Apply all indicators
    df = preprocess_data(data, indicators)


    backtest_results = backtest_strategy(df, indicators)

    # Plot with all indicators and trade points
    plotCandlestick(backtest_results, indicators)
