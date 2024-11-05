import yfinance as yf
import csv
import os
import time
from datetime import datetime

# Define the list of tickers here
tickers = ['VBK', 'VBR', 'VUG', 'VTV', 'SGLD.MI']  # Add your desired tickers

# Set CSV file path
current_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_directory, 'tickers_oclh_data.csv')

# Function to get historical oclh data for a ticker
def get_historical_data(ticker):
    stock = yf.Ticker(ticker)
    # Download historical data from 2000 to present
    hist = stock.history(start="2000-01-01", interval="1d")
    hist = hist.reset_index()  # Reset index to include Date as a column
    hist['Ticker'] = ticker  # Add ticker column for identification
    
    # Format DateTime consistently
    hist['DateTime'] = hist['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return hist[['DateTime', 'Ticker', 'Open', 'Close', 'High', 'Low']]

# Function to save historical data to the CSV file (initial setup)
def save_historical_data_to_csv():
    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['DateTime', 'Ticker', 'Open', 'Close', 'High', 'Low'])
            writer.writeheader()
            
            for ticker in tickers:
                hist_data = get_historical_data(ticker)
                for _, row in hist_data.iterrows():
                    writer.writerow(row.to_dict())
                print(f"Historical data for {ticker} saved.")

# Function to get latest oclh data for a ticker
def get_latest_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='1d', interval='1m')
    last_row = hist.iloc[-1]
    oclh_data = {
        'DateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Ticker': ticker,
        'Open': last_row['Open'],
        'Close': last_row['Close'],
        'High': last_row['High'],
        'Low': last_row['Low']
    }
    return oclh_data

# Function to append real-time data to the CSV file
def append_to_csv(oclh_data):
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['DateTime', 'Ticker', 'Open', 'Close', 'High', 'Low'])
        writer.writerow(oclh_data)

# Main function to initialize with historical data and then track real-time data
def track_tickers_price_every_minute():
    save_historical_data_to_csv()
    while True:
        for ticker in tickers:
            oclh_data = get_latest_data(ticker)
            append_to_csv(oclh_data)
            print(f"Time: {oclh_data['DateTime']} | Ticker: {oclh_data['Ticker']} | Close Price: {oclh_data['Close']}")
        time.sleep(5)

# To start the function, uncomment the following line:
track_tickers_price_every_minute()
