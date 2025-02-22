import json
import yfinance as yf
import os
import time
import random
from datetime import datetime

def download_etf_data(json_file, save_path="./data/"):
    # Load ETF tickers from JSON
    with open(json_file, "r") as file:
        etf_data = json.load(file)
    etfs = etf_data.get("etfs", [])
    
    if not etfs:
        print("No ETF tickers found in JSON file.")
        return
    
    # Create directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)
    
    for etf in etfs:
        ticker = etf["ticker"]
        print(f"Downloading data for {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            
            # Try fetching full history, fallback to 10 years if empty
            data = stock.history(period="max", interval="1d")
            if data.empty:
                print(f"No full history for {ticker}, trying last 10 years...")
                data = stock.history(period="10y", interval="1d")
            if data.empty:
                print(f"No full history for {ticker}, trying last 10 years...")
                data = stock.history(period="5y", interval="1d")
            if data.empty:
                print(f"No full history for {ticker}, trying last 10 years...")
                data = stock.history(period="2y", interval="1d")
            
            if data.empty:
                print(f"No data found for {ticker}, skipping...")
                continue
            
            file_path = os.path.join(save_path, f"{ticker}.csv")
            data.to_csv(file_path)
            print(f"Saved {ticker} data to {file_path}")
        except Exception as e:
            print(f"Error with {ticker}: {e}")
        
        time.sleep(random.uniform(1, 3))  # Random delay to avoid rate limits

if __name__ == "__main__":
    download_etf_data("etf_tickers.json")