import matplotlib.pyplot as plt
import time
import os
import pandas as pd
import psutil  # To monitor system resources

# Set the file path for monitoring updates
file_path = 'tickers_oclh_data.csv'

# Function to plot initial data and then update with the latest point
def live_plot_csv(file_path):
    # Load the initial CSV data
    df = pd.read_csv(file_path)
    
    # Extract the unique tickers to plot each one separately
    tickers = df['Ticker'].unique()
    
    # Initialize the plotting structure
    fig, axs = plt.subplots(len(tickers), 1, figsize=(10, 8), sharex=True)
    fig.suptitle('Live Close Price for Stocks', fontsize=16)
    
    # Dictionary to keep track of each ticker's data for dynamic updates
    ticker_data = {ticker: df[df['Ticker'] == ticker] for ticker in tickers}
    
    # Create initial plots for each ticker
    lines = {}
    for i, ticker in enumerate(tickers):
        ticker_df = ticker_data[ticker]
        axs[i].set_title(f'{ticker} Close Price')
        axs[i].set_ylabel('Close Price')
        axs[i].grid()
        axs[i].tick_params(axis='x', rotation=45)
        
        line, = axs[i].plot(pd.to_datetime(ticker_df['DateTime']), ticker_df['Close'], label=ticker)
        lines[ticker] = line

    plt.tight_layout()
    plt.ion()  # Enable interactive mode for live updating

    last_updated = os.path.getmtime(file_path)
    while True:
        current_mtime = os.path.getmtime(file_path)
        
        # Measure CPU and memory usage before the update
        cpu_usage = psutil.cpu_percent(interval=None)  # Current CPU usage in percentage
        memory_info = psutil.virtual_memory()          # Memory usage details
        memory_usage = memory_info.percent             # Current memory usage in percentage
        
        # Print resource usage details
        print(f"CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}%")

        if current_mtime != last_updated:
            df = pd.read_csv(file_path)
            last_updated = current_mtime  # Update last modified time

            for i, ticker in enumerate(tickers):
                ticker_df = df[df['Ticker'] == ticker]
                
                # Update x and y data
                lines[ticker].set_xdata(pd.to_datetime(ticker_df['DateTime']))
                lines[ticker].set_ydata(ticker_df['Close'])
                
                # Rescale the plot view
                axs[i].relim()
                axs[i].autoscale_view()
                
            fig.canvas.flush_events()  # Update without pausing
            plt.pause(0.1)

        time.sleep(5)

# Run the live plot function
live_plot_csv(file_path)
