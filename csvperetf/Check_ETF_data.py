import pandas as pd
from plot_utils import (
    plot_total_investment, 
    plot_individual_investments, 
    plot_no_rebalance_vs_comparison, 
    plot_percentage_increase_no_rebalance, 
    plot_selected_etfs_percentage_increase
)

class ETFPortfolioSimulator:
    def __init__(self, path, portfolios, initial_budget):
        self.path = path
        self.portfolios = portfolios
        self.initial_budget = initial_budget
        self.portfolio_data = []
        self.investment_values = []
        self.investment_values_no_rebalance = []
        self.total_investments = []
        self.total_investments_no_rebalance = []
        self.percentage_increase_no_rebalance = []
        self.rebalance_dates = []

    def load_data(self, start_date='2017-03-01', end_date=None):
        for portfolio_files, _, etf_names in self.portfolios:
            portfolio_df_list = []
            for file, etf_name in zip(portfolio_files, etf_names):
                df = pd.read_csv(self.path + file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
                if end_date:
                    df = df[(df.index >= start_date) & (df.index <= end_date)]
                else:
                    df = df[df.index >= start_date]
                df.rename(columns={'Close': etf_name}, inplace=True)
                df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0]) - 1
                portfolio_df_list.append(df)
            self.portfolio_data.append(portfolio_df_list)

    def calculate_investment_values(self):
        dates = self.portfolio_data[0][0].index[:-1]
        self.rebalance_dates = dates[dates.month % 6 == dates[0].month % 6]
        
        for n, (portfolio_files, allocations, etf_names) in enumerate(self.portfolios):
            quota_invested = [self.initial_budget * allocation for allocation in allocations]
            current_investments = quota_invested.copy()
            investment_values_over_time = {name: [] for name in etf_names}
            total_investment_over_time = []
            for date in dates:
                if date in self.rebalance_dates:
                    period_date_zero = date
                    total_value = sum(current_investments)
                    quota_invested = [total_value * allocation for allocation in allocations]
                
                percentage_increase = [1 for _ in allocations]
                for i, df in enumerate(self.portfolio_data[n]):
                    percentage_increase[i] = (df.loc[date].values[0] / df.loc[period_date_zero].values[0])
                    current_investments[i] = quota_invested[i] * percentage_increase[i]
                    investment_values_over_time[etf_names[i]].append(current_investments[i])
                
                total_investment_over_time.append(sum(current_investments))
            
            self.investment_values.append({name: pd.Series(data=investment_values_over_time[name], index=dates) for name in etf_names})
            self.total_investments.append(pd.Series(data=total_investment_over_time, index=dates))

    def calculate_investment_values_no_rebalance(self):
        dates = self.portfolio_data[0][0].index[:-1]
        
        for n, (portfolio_files, allocations, etf_names) in enumerate(self.portfolios):
            quota_invested = [self.initial_budget * allocation for allocation in allocations]
            investment_values_no_rebalance = {name: [] for name in etf_names}
            total_investment_no_rebalance_over_time = []
            
            for date in dates:
                current_investments = quota_invested.copy()
                for i, df in enumerate(self.portfolio_data[n]):
                    percentage_increase = (df.loc[date].values[0] / df.loc[dates[0]].values[0])
                    current_investments[i] = quota_invested[i] * percentage_increase
                    investment_values_no_rebalance[etf_names[i]].append(current_investments[i])
                
                total_investment_no_rebalance_over_time.append(sum(current_investments))
            
            self.investment_values_no_rebalance.append({name: pd.Series(data=investment_values_no_rebalance[name], index=dates) for name in etf_names})
            self.total_investments_no_rebalance.append(pd.Series(data=total_investment_no_rebalance_over_time, index=dates))

    def calculate_percentage_increase_no_rebalance(self):
        dates = self.portfolio_data[0][0].index[:-1]
        
        for n, (portfolio_files, allocations, etf_names) in enumerate(self.portfolios):
            percentage_increase_no_rebalance = {name: [] for name in etf_names}
            
            for date in dates:
                for i, df in enumerate(self.portfolio_data[n]):
                    percentage_increase = (df.loc[date].values[0] / df.loc[dates[0]].values[0])
                    percentage_increase_no_rebalance[etf_names[i]].append(percentage_increase)
            
            self.percentage_increase_no_rebalance.append({name: pd.Series(data=percentage_increase_no_rebalance[name], index=dates) for name in etf_names})

# Usage
path = "/home/simone/Finance/Botto/csvperetf/"
portfolios = [
    # Portfolio definitions as in the original script...
]
initial_budget = 10000

simulator = ETFPortfolioSimulator(path, portfolios, initial_budget)
simulator.load_data(start_date='2020-01-01', end_date='2024-05-20')
simulator.calculate_investment_values()
simulator.calculate_investment_values_no_rebalance()
simulator.calculate_percentage_increase
