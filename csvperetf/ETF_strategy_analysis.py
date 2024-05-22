import pandas as pd
import matplotlib.pyplot as plt

# File names and their corresponding ETF names
class ETFPortfolioSimulator:
    def __init__(self, path, portfolio_files, comparison_file, initial_budget, allocations, rebalance_period=6):
        self.path = path
        self.portfolio_files = portfolio_files
        self.comparison_file = comparison_file
        self.initial_budget = initial_budget
        self.allocations = allocations
        self.rebalance_period = rebalance_period
        self.portfolio_data = []
        self.comparison_data = None
        
    def load_data(self):
        for file in self.portfolio_files:
            df = pd.read_csv(self.path + file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
            df = df[df.index >= '2012-06-01']
            self.portfolio_data.append(df)
        
        self.comparison_data = pd.read_csv(self.path + self.comparison_file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
        self.comparison_data = self.comparison_data[self.comparison_data.index >= '2012-06-01']
        
        
path = "/home/simone/Finance/csvperetf/"
portfolio_files = ['VBK.csv', 'VBR.csv', 'VUG.csv', 'VTV.csv']
comparison_file = 'VOO.csv'
initial_budget = 10000
comparison_budget = 10000
allocations = [0.25, 0.25, 0.25, 0.25]

"""
file_names = ['VBK.csv', 'VBR.csv', 'VUG.csv', 'VTV.csv', 'VOO.csv']
etf_names = [
    'Vanguard Small-Cap Growth Index Fund',
    'Vanguard Small-Cap Value Index Fund',
    'Vanguard Growth Index Fund',
    'Vanguard Value Index Fund',
    'Vanguard S&P 500'
]
# Separate ETFs into portfolio and comparison
portfolio_files = file_names[:-1]
portfolio_etfs = etf_names[:-1]
comparison_file = file_names[-1]
comparison_etf = etf_names[-1]
"""

# Reading and storing data
path = "/home/simone/Finance/csvperetf/"
portfolio_frames = []
comparison_frame = None
investment_values = []

for file, name, allocation in zip(portfolio_files, portfolio_etfs, allocations):
    # Read each CSV file, parse dates in the first column and set it as index
    df = pd.read_csv(path + file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
    # Filter the data to start from June 2012
    df = df[df.index >= '2012-06-01']
    # Rename 'Close' to the ETF's name for clarity in the plot
    df.rename(columns={'Close': name}, inplace=True)
    # Calculate percentage change from the first value
    percentage_df = (df / df.iloc[0]) - 1
    # Calculate investment value over time
    investment_value = initial_budget * allocation * (1 + percentage_df)
    investment_values.append(investment_value)

# Process the comparison ETF
comparison_df = pd.read_csv(path + comparison_file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
comparison_df = comparison_df[comparison_df.index >= '2012-06-01']
comparison_df.rename(columns={'Close': comparison_etf}, inplace=True)
percentage_comparison = (comparison_df / comparison_df.iloc[0]) - 1
comparison_investment = comparison_budget * (1 + percentage_comparison)

# Combine all investment values
total_investment_df = pd.concat(investment_values, axis=1).sum(axis=1)
total_comparison_investment = comparison_investment

# Plotting the investment values over time
plt.figure(figsize=(14, 7))
plt.plot(total_investment_df.index, total_investment_df, label='Total Portfolio Investment')
plt.plot(total_comparison_investment.index, total_comparison_investment[comparison_etf], label='Comparison ETF Investment', linestyle='--')
plt.title('Investment Value Over Time')
plt.xlabel('Date')
plt.ylabel('Investment Value ($)')
plt.legend()
plt.grid(True)
plt.show()

