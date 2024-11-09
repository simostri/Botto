


import json
import pandas as pd
import talib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
# Disable SSL Warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # Suppress specific SettingWithCopyWarning



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
    # Convert datetime index to matplotlib date format
    df['Date'] = [mdates.date2num(d) for d in df.index]
    quotes = [tuple(x) for x in df[['Date', 'Open', 'High', 'Low', 'Close']].values]

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(16, 9))

    # Plot candlestick chart
    candlestick_ohlc(ax, quotes, width=0.6/(24*60), colorup='green', colordown='red', alpha=0.8)

    # Plot indicators
    for indicator in indicators:
        if indicator['type'] == 'SMA':
            ax.plot(df['Date'], df['SMA'], label='SMA ' + str(indicator['period']), color='blue',linewidth=1)
        elif indicator['type'] == 'EMA':
            ax.plot(df['Date'], df['EMA'], label='EMA ' + str(indicator['period']), color='green',linewidth=1)

    # Plot trade entry and exit points
    entry_points = df[df['Position'] == 1]
    exit_points = df[df['Position'] == -1]
    if not entry_points.empty:
        ax.scatter(entry_points['Date'], entry_points['Close'], color='lime', marker='^', s=100, label='Entry Points')
    if not exit_points.empty:
        ax.scatter(exit_points['Date'], exit_points['Close'], color='fuchsia', marker='v', s=100, label='Exit Points')

    # Formatting and showing the plot
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.legend()
    plt.title('S&P 500 Price Action')
    plt.show()

def backtest_strategy(df):
    
    initial_balance = 1000  # Starting balance in euros
    balance = initial_balance
    trade_amount = 100     # Amount in euros invested per trade
    df['entered'] = 0
    df['Trade Entry'] = 0
    df['Trade Exit'] = 0


    df['Cross'] = df['SMA'] - df['EMA']
    df['SMA_Diff'] = df['SMA'].diff()
    df['SMA_Peak'] = (df['SMA_Diff'].shift(1) > 0) & (df['SMA_Diff'] < 0)
    df['SMA_Valley'] = (df['SMA_Diff'].shift(1) < 0) & (df['SMA_Diff'] > 0)
    df['Position'] = 0

    
    for i in range(1, len(df)):

        ## Not in a trade
        if df['entered'].iloc[i-1] == 0:  # Not currently in a trade
            if df['Cross'].iloc[i] < 0 and df['SMA_Valley'].iloc[i]:  # Buy condition
                df['Position'].iloc[i] = 1
                df['entered'].iloc[i] = 1
                Price1 = df['Close'].iloc[i]
                #balance = initial_balance - trade_amount


        ## In a trade
        if df['entered'].iloc[i-1] == 1 and balance is not 0:  #currently in a trade
            if df['Cross'].iloc[i] < 0 and df['SMA_Valley'].iloc[i]:  # Buy condition
                df['Position'].iloc[i] = 1
                df['entered'].iloc[i] = 1
                Price = df['Close'].iloc[i]
                
            # Sell condition        
            if df['Cross'].iloc[i] > 0 and df['SMA_Peak'].iloc[i] and df['Close'].iloc[i]>=Price1*1.05:  # Sell condition
                df['Position'].iloc[i] = -1
                df['entered'].iloc[i] = 0
                #balance = balance + trade_amount
            else:
                
                # Continue the current trade
                df['entered'].iloc[i] = df['entered'].iloc[i-1]
    # Calculate returns
    return df

    # Variables to keep track of the current trade
    
def Calculate_returns(df):    
    initial_balance = 1000  # Starting balance in euros
    balance = initial_balance
    trade_amount = 100     # Amount in euros invested per trade
    currently_traded = 0
    current_exit_price = None
    total_return_percentage = 0
    Trades = pd.DataFrame(columns=['Time_entry', 'Price_entry', 'Time_exit', 'Price_exit', 'Return_Percentage', 'Return_Euro'])    
    Current_trades = pd.DataFrame(columns=['Time_entry', 'Price_entry'])
    avg_entry_price = 0
    
    # Calculate returns and record trades
    for i in range(1, len(df)-1):
        if df['Position'].iloc[i] == 1:
            time_entry = df.index[i+1]
            Current_trades = Current_trades._append({'Time_entry': time_entry, 'Price_entry': df['Close'].iloc[i+1]}, ignore_index=True)
            current_exit_price = None  # Reset exit price for new trade
            avg_entry_price = sum(Current_trades['Price_entry'])/len(Current_trades)
            currently_traded += currently_traded + trade_amount
            
        elif df['Position'].iloc[i] == -1 and avg_entry_price is not 0 and df['entered'].iloc[i-1]:
            time_exit= df.index[i+1]
            avg_entry_price = sum(Current_trades['Price_entry'])/len(Current_trades)
            current_exit_price = df['Close'].iloc[i]
            # Calculate returns
            return_percentage = (current_exit_price - avg_entry_price) / avg_entry_price * 0.9
            return_euro = return_percentage * trade_amount*len(Current_trades)
            
            # Record the trade
            Trades = Trades._append({
            'Time_entry': time_entry, 
            'Price_entry': avg_entry_price, 
            'Time_exit': time_exit, 
            'Price_exit': current_exit_price, 
            'Return_Percentage': return_percentage, 
            'Return_Euro': return_euro
        }, ignore_index=True)

            # Update total return
            balance = balance + return_euro
            total_return_percentage = (balance + return_euro)/initial_balance
            Current_trades = pd.DataFrame(columns=['Time_entry', 'Price_entry'])
            avg_entry_price = 0
    
    index_percentage =(df['Close'].iloc[-1]-df['Close'].iloc[1])/df['Close'].iloc[1]*0.8 +1
    index_return = index_percentage*initial_balance
            
    print(f"Final Balance: {balance}")
    print(f"Return Percentage: {total_return_percentage}")
    print(f"Return of the index:{index_return}")
    print(f"percentage of the index:{index_percentage}")
    return Trades



if __name__ == "__main__":
    file_path = 'historical_data_1y_1h.json'
    data = read_historical_data(file_path)
    indicators = input_parameters()
    df = preprocess_data(data, indicators)
    df = backtest_strategy(df)
    Trades = Calculate_returns(df)
    plotCandlestick(df, indicators)
