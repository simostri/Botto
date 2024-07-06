import pandas as pd
import matplotlib.pyplot as plt

class ETFPortfolioSimulator:
    def __init__(self, path, portfolio_files, comparison_file, initial_budget, comparison_budget, allocations, etf_names):
        self.path = path
        self.portfolio_files = portfolio_files
        self.comparison_file = comparison_file
        self.initial_budget = initial_budget
        self.comparison_budget = comparison_budget
        self.allocations = allocations
        self.etf_names = etf_names
        self.portfolio_data = []
        self.comparison_data = None
        self.investment_values = []
        self.rebalance_dates = []

    def load_data(self, start_date = '2017-03-01'):
        # Load portfolio ETF data
        for file, etf_name in zip(self.portfolio_files, self.etf_names[:-1]):
            df = pd.read_csv(self.path + file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
            df = df[df.index >= start_date]
            df.rename(columns={'Close': etf_name}, inplace=True)
            df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0]) - 1  # Calculate pct_revenue
            self.portfolio_data.append(df)

        # Load comparison ETF data
        self.comparison_data = pd.read_csv(self.path + self.comparison_file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
        self.comparison_data = self.comparison_data[self.comparison_data.index >= start_date]
        self.comparison_data.rename(columns={'Close': self.etf_names[-1]}, inplace=True)
        self.comparison_data['pct_revenue'] = (self.comparison_data[self.etf_names[-1]] / self.comparison_data[self.etf_names[-1]].iloc[0]) - 1

    def calculate_investment_values(self):
        dates = self.portfolio_data[0].index[:-1]
        self.rebalance_dates = dates[dates.month % 6 == dates[0].month % 6]  # Rebalance every 6 months
        
        quota_invested = [self.initial_budget * allocation for allocation in self.allocations]
        current_investments = quota_invested.copy()  # Reset current investments for each period
        investment_values_over_time = {name: [] for name in self.etf_names[:-1]}
        
        for date in dates:
            if date in self.rebalance_dates:
                period_date_zero = date
                print("--------------------------------------------------------------")
                print(f"REBALANCE DATE IS {date}")
                formatted_current_investments = [f"{investment:.0f}" for investment in current_investments]
                print(f"current_investments before rebalancing: {formatted_current_investments}")
                total_value = sum(current_investments)
                quota_invested = [total_value * allocation for allocation in self.allocations]
                formatted_quota_invested = [f"{investment:.0f}" for investment in quota_invested]
                print(f"current_investments after rebalancing: {formatted_quota_invested}")
                print("--------------------------------------------------------------")

            
            # Calculate current values
            percentage_increase = [1 for _ in self.allocations]
        
            for i, df in enumerate(self.portfolio_data):
                #print(f"date: {date}")
                #print(f"current investment before: {current_investments}")
                percentage_increase[i] = (df.loc[date].values[0] / df.loc[period_date_zero].values[0])
                current_investments[i] = quota_invested[i] * percentage_increase[i]
                investment_values_over_time[self.etf_names[i]].append(current_investments[i])
                #print(f"current investment: {current_investments}")
                #print(f"percentage increase: {percentage_increase}")
                #print("--------------------------------------------------------------")
        
        for name in self.etf_names[:-1]:
            self.investment_values.append(pd.Series(data=investment_values_over_time[name], index=dates))
        
        # Calculate investment value for the comparison ETF
        percentage_comparison = (self.comparison_data / self.comparison_data.iloc[0]) - 1
        self.comparison_investment = self.comparison_budget * (1 + percentage_comparison)

    def plot_results(self):
        # Combine all investment values
        total_investment_df = pd.concat(self.investment_values, axis=1).sum(axis=1)
        total_comparison_investment = self.comparison_investment[self.etf_names[-1]]

        # Plotting the investment values over time
        plt.figure(figsize=(14, 7))
        plt.plot(total_investment_df.index, total_investment_df, label='Total Portfolio Investment')
        plt.plot(total_comparison_investment.index, total_comparison_investment, label='Comparison ETF Investment', linestyle='--')
        plt.title('Investment Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Investment Value ($)')
        plt.legend()
        plt.grid(True)
        plt.show()
        
    def plot_individual_investments(self):
        # Plotting each ETF's percentage revenue over time
        plt.figure(figsize=(14, 7))
        for df, etf_name in zip(self.portfolio_data, self.etf_names[:-1]):
            plt.plot(df.index, df['pct_revenue'], label=etf_name)
        plt.plot(self.comparison_data.index, self.comparison_data['pct_revenue'], label=self.etf_names[-1], linestyle='--')
        
        plt.title('Percentage Revenue Over Time')
        plt.xlabel('Date')
        plt.ylabel('Percentage Revenue')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_no_rebalance_vs_comparison(self):
        # Calculate total investment value without rebalancing
        dates = self.portfolio_data[0].index[:-1]
        quota_invested = [self.initial_budget * allocation for allocation in self.allocations]
        investment_values_no_rebalance = {name: [] for name in self.etf_names[:-1]}
        
        for date in dates:
            current_investments = quota_invested.copy()
            for i, df in enumerate(self.portfolio_data):
                percentage_increase = (df.loc[date].values[0] / df.loc[dates[0]].values[0])
                current_investments[i] = quota_invested[i] * percentage_increase
                investment_values_no_rebalance[self.etf_names[i]].append(current_investments[i])
        
        total_investment_no_rebalance_df = pd.DataFrame(investment_values_no_rebalance, index=dates).sum(axis=1)
        total_comparison_investment = self.comparison_investment[self.etf_names[-1]]
        
        # Plotting the investment values over time without rebalancing
        plt.figure(figsize=(14, 7))
        plt.plot(total_investment_no_rebalance_df.index, total_investment_no_rebalance_df, label='Total Portfolio Investment (No Rebalance)')
        plt.plot(total_comparison_investment.index, total_comparison_investment, label='Comparison ETF Investment', linestyle='--')
        plt.title('Investment Value Over Time (No Rebalance)')
        plt.xlabel('Date')
        plt.ylabel('Investment Value ($)')
        plt.legend()
        plt.grid(True)
        plt.show()

    def get_attributes(self):
        return self.__dict__

# Usage
path = "/home/simone/Finance/Botto/csvperetf/"
portfolio_files = ['VBK.csv', 'VBR.csv', 'VUG.csv', 'VTV.csv', 'SGLD.MI.csv']
comparison_file = 'VOO.csv'
initial_budget = 10000  # Total budget for portfolio
comparison_budget = 10000  # Budget for comparison ETF
allocations = [0.05, 0.1, 0.7, 0.1, 0.05]  # Equal allocation for simplicity
etf_names = [
    'Vanguard Small-Cap Growth Index Fund',
    'Vanguard Small-Cap Value Index Fund',
    'Vanguard Growth Index Fund',
    'Vanguard Value Index Fund',
    'Invesco Physical Gold',
    'Vanguard S&P 500'
]

simulator = ETFPortfolioSimulator(path, portfolio_files, comparison_file, initial_budget, comparison_budget, allocations, etf_names)
simulator.load_data(start_date = '2017-03-01')
simulator.calculate_investment_values()
simulator.plot_results()

# Plot individual ETF investment values
simulator.plot_individual_investments()

# Plot no rebalance vs comparison
simulator.plot_no_rebalance_vs_comparison()
