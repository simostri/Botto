import quandl
import pandas as pd
import matplotlib.pyplot as plt

# Set your Quandl API key
quandl.ApiConfig.api_key = 'LFz89yQvKn-ywskWRxAS'

# Fetch the dataset from Quandl (Replace 'DATASET_CODE' with the code for Vanguard Total World Stock ETF)
data = quandl.get('DATASET_CODE', start_date='2010-01-01', end_date='2020-12-31')

# Calculate moving averages
short_window = 40
long_window = 100
data['Short_MA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
data['Long_MA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

# Generate signals
data['Signal'] = 0.0
data['Signal'][short_window:] = np.where(data['Short_MA'][short_window:] > data['Long_MA'][short_window:], 1.0, 0.0)

# Calculate daily returns
data['Returns'] = data['Close'].pct_change()

# Calculate strategy returns
data['Strategy_Returns'] = data['Returns'] * data['Signal'].shift(1)

# Plotting
plt.figure(figsize=(12,8))
plt.plot(data['Close'], label='Vanguard All World')
plt.plot(data['Short_MA'], label='40-day Moving Average')
plt.plot(data['Long_MA'], label='100-day Moving Average')
plt.plot(data['Signal'], label='Buy/Sell Signal', alpha=0.5)
plt.title('Vanguard All World ETF Trading Strategy')
plt.legend()
plt.show()
