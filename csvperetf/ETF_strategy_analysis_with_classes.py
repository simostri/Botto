import pandas as pd
import matplotlib.pyplot as plt

class ETFPortfolioSimulator:
    def __init__(self, path, portfolio_files, comparison_file, initial_budget, allocations, rebalance_period=6):
        self.path = path
        self.portfolio_files = portfolio_files
        self.portfolio_names = portfolio_names
        self.comparison_file = comparison_file
        self.initial_budget = initial_budget
        self.allocations = allocations
        self.rebalance_period = rebalance_period
        self.portfolio_data = []
        self.comparison_data = None

    def load_data(self):
        for file, name in zip(portfolio_files, portfolio_etfs):
            df = pd.read_csv(path + file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
            df = df[df.index >= '2012-06-01']
            df.rename(columns={'Close': name}, inplace=True)
            portfolio_data.append(df)
        
        self.comparison_data = pd.read_csv(self.path + self.comparison_file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
        self.comparison_data = self.comparison_data[self.comparison_data.index >= '2012-06-01']

    def calculate_investment_values(self):
        # Implementation needed for calculating daily returns and rebalancing
        pass

    def rebalance_portfolio(self):
        # Implementation for portfolio rebalancing logic
        pass

    def plot_results(self):
        # Plotting logic for the investment values over time
        pass

# Usage
path = "/home/simone/Finance/csvperetf/"
portfolio_files = ['VBK.csv', 'VBR.csv', 'VUG.csv', 'VTV.csv']
portfolio_names= [
    'Vanguard Small-Cap Growth Index Fund',
    'Vanguard Small-Cap Value Index Fund',
    'Vanguard Growth Index Fund',
    'Vanguard Value Index Fund']

allocations = [0.25, 0.25, 0.25, 0.25]
comparison_file = 'VOO.csv'
comparison_name = 'Vanguard S&P 500'
initial_budget = 10000

simulator = ETFPortfolioSimulator(path, portfolio_files, comparison_file, initial_budget, allocations)
simulator.load_data()
# Additional methods to perform calculations and plotting would be called here
