#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 12:21:57 2025

@author: simone
"""

import pandas as pd
import matplotlib.pyplot as plt

class ETFPortfolioSimulator:
    def __init__(self, path, portfolios, initial_budget):
        self.path = path
        self.portfolios = portfolios  # List of tuples: (portfolio_files, allocations, etf_names)
        self.initial_budget = initial_budget
        self.portfolio_data = []
        self.investment_values = []  # List of dictionaries for each portfolio
        self.investment_values_no_rebalance = []  # List of dictionaries for each portfolio without rebalancing
        self.total_investments = []  # List to store total investments for each portfolio
        self.total_investments_no_rebalance = []  # List to store total investments without rebalancing for each portfolio
        self.percentage_increase_no_rebalance = []  # List to store percentage increases without rebalancing for each portfolio
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
                df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0]) - 1  # Calculate pct_revenue
                portfolio_df_list.append(df)
            self.portfolio_data.append(portfolio_df_list)


    def calculate_investment_values(self):
        dates = self.portfolio_data[0][0].index[:-1]
        self.rebalance_dates = dates[dates.month % 6 == dates[0].month % 6]  # Rebalance every 6 months
        
        for n, (portfolio_files, allocations, etf_names) in enumerate(self.portfolios):
            quota_invested = [self.initial_budget * allocation for allocation in allocations]
            current_investments = quota_invested.copy()  # Reset current investments for each period
            investment_values_over_time = {name: [] for name in etf_names}
            total_investment_over_time = []  # List to store total investment value over time
            for date in dates:
                if date in self.rebalance_dates:
                    period_date_zero = date
                    total_value = sum(current_investments)
                    quota_invested = [total_value * allocation for allocation in allocations]
                
                percentage_increase = [1 for _ in allocations]
                for i, df in enumerate(self.portfolio_data[n]):  # Use self.portfolio_data[n]
                    
                    percentage_increase[i] = (df.loc[date].values[0] / df.loc[period_date_zero].values[0])
                    current_investments[i] = quota_invested[i] * percentage_increase[i]
                    investment_values_over_time[etf_names[i]].append(current_investments[i])
                
                total_investment_over_time.append(sum(current_investments))  # Append total investment value for the date
            
            # Append the investment values and total investments of the current portfolio to the overall lists
            self.investment_values.append({name: pd.Series(data=investment_values_over_time[name], index=dates) for name in etf_names})
            self.total_investments.append(pd.Series(data=total_investment_over_time, index=dates))

    def calculate_investment_values_no_rebalance(self):
        dates = self.portfolio_data[0][0].index[:-1]
        
        for n, (portfolio_files, allocations, etf_names) in enumerate(self.portfolios):
            quota_invested = [self.initial_budget * allocation for allocation in allocations]
            investment_values_no_rebalance = {name: [] for name in etf_names}
            total_investment_no_rebalance_over_time = []  # List to store total investment value over time without rebalancing
            
            for date in dates:
                current_investments = quota_invested.copy()
                for i, df in enumerate(self.portfolio_data[n]):  # Use self.portfolio_data[n]
                    percentage_increase = (df.loc[date].values[0] / df.loc[dates[0]].values[0])
                    current_investments[i] = quota_invested[i] * percentage_increase
                    investment_values_no_rebalance[etf_names[i]].append(current_investments[i])
                
                total_investment_no_rebalance_over_time.append(sum(current_investments))  # Append total investment value for the date
            
            # Append the investment values and total investments without rebalancing of the current portfolio to the overall lists
            self.investment_values_no_rebalance.append({name: pd.Series(data=investment_values_no_rebalance[name], index=dates) for name in etf_names})
            self.total_investments_no_rebalance.append(pd.Series(data=total_investment_no_rebalance_over_time, index=dates))

    def calculate_percentage_increase_no_rebalance(self):
        dates = self.portfolio_data[0][0].index[:-1]
        
        for n, (portfolio_files, allocations, etf_names) in enumerate(self.portfolios):
            percentage_increase_no_rebalance = {name: [] for name in etf_names}
            
            for date in dates:
                for i, df in enumerate(self.portfolio_data[n]):  # Use self.portfolio_data[n]
                    percentage_increase = (df.loc[date].values[0] / df.loc[dates[0]].values[0])
                    percentage_increase_no_rebalance[etf_names[i]].append(percentage_increase)
            
            # Append the percentage increases without rebalancing of the current portfolio to the overall list
            self.percentage_increase_no_rebalance.append({name: pd.Series(data=percentage_increase_no_rebalance[name], index=dates) for name in etf_names})

    def plot_results(self):
        plt.figure(figsize=(14, 7))
        for i, total_investment_df in enumerate(self.total_investments):
            plt.plot(total_investment_df.index, total_investment_df, label=f'Portfolio {i + 1}')
        
        plt.title('Investment Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Investment Value ($)')
        plt.legend()
        plt.grid(True)
        plt.show()
        
    def plot_individual_investments(self):
        plt.figure(figsize=(14, 7))
        for portfolio_investments, (_, _, etf_names) in zip(self.investment_values, self.portfolios):
            for name in etf_names:
                plt.plot(portfolio_investments[name].index, portfolio_investments[name], label=name)
        
        plt.title('Percentage Revenue Over Time')
        plt.xlabel('Date')
        plt.ylabel('Percentage Revenue')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_no_rebalance_vs_comparison(self):
        plt.figure(figsize=(14, 7))
        for i, total_investment_no_rebalance_df in enumerate(self.total_investments_no_rebalance):
            plt.plot(total_investment_no_rebalance_df.index, total_investment_no_rebalance_df, label=f'Total Portfolio Investment (No Rebalance) for Portfolio {i + 1}')
        
        plt.title('Investment Value Over Time (No Rebalance)')
        plt.xlabel('Date')
        plt.ylabel('Investment Value ($)')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_percentage_increase_no_rebalance(self):
        plt.figure(figsize=(14, 7))
        for i, percentage_increase_no_rebalance in enumerate(self.percentage_increase_no_rebalance):
            for name, series in percentage_increase_no_rebalance.items():
                plt.plot(series.index, series, label=f'{name} (Portfolio {i + 1})')
        
        plt.title('Percentage Increase Over Time (No Rebalance)')
        plt.xlabel('Date')
        plt.ylabel('Percentage Increase')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_selected_etfs_percentage_increase(self, etf_names):
        plt.figure(figsize=(14, 7))
        for etf_name in etf_names:
            for percentage_increase_no_rebalance in self.percentage_increase_no_rebalance:
                if etf_name in percentage_increase_no_rebalance:
                    series = percentage_increase_no_rebalance[etf_name]
                    plt.plot(series.index, series, label=etf_name)
        
        plt.title('Selected ETFs Percentage Increase Over Time (No Rebalance)')
        plt.xlabel('Date')
        plt.ylabel('Percentage Increase')
        plt.legend()
        plt.grid(True)
        plt.show()

    def get_attributes(self):
        return self.__dict__

# Usage
path = "/home/simone/Finance/Botto/csvperetf/data/"
portfolios = [
    (['ITPS.SW.csv', 'IBGX.AS.csv', 'US10.PA.csv', 'IBCI.AS.csv', 'IBGL.AS.csv', 'SGLD.MI.csv','ICOM.L.csv', 'SPPW.DE.csv'], [0.1, 0.15, 0.1, 0.1, 0.1, 0.075, 0.075, 0.3], [
        'iShares $ TIPS UCITS ETF USD',
        'iShares Euro Government Bond 3-5 Year UCITS',
        'Lyxor US Treasury 10+Y (DR) UCITS',
        'IShares Euro Inflation Linked Government Bond UCITS',
        'iShares Euro Government Bond 15-30yr UCITS',
        'Invesco Physical Gold A',
        'Lyxor Commodities Refinitiv/CoreCommodity CRB TR UCITS',
        'SPDR MSCI World UCITS ETF'
    ]),
    (['SGLD.MI.csv','SPPW.DE.csv'], [0.4,0.6], [
        'Invesco Physical Gold A',
        'SPDR MSCI World UCITS ETF'
    ]),
    (['VBK.csv', 'VBR.csv', 'VUG.csv', 'VTV.csv', 'SGLD.MI.csv'], [0.05, 0.1, 0.7, 0.1, 0.05], [
        'Vanguard Small-Cap Growth Index Fund',
        'Vanguard Small-Cap Value Index Fund',
        'Vanguard Growth Index Fund',
        'Vanguard Value Index Fund',
        'Invesco Physical Gold'
    ]),
    (['VOO.csv'], [1], [
        'Vanguard S&P 500'
    ])
]
initial_budget = 10000  # Total budget for portfolio

simulator = ETFPortfolioSimulator(path, portfolios, initial_budget)
simulator.load_data(start_date='2020-01-01', end_date='2024-05-20')
simulator.calculate_investment_values()
simulator.calculate_investment_values_no_rebalance()
simulator.calculate_percentage_increase_no_rebalance()
simulator.plot_results()

# Plot individual ETF investment values
simulator.plot_individual_investments()

# Plot no rebalance vs comparison
simulator.plot_no_rebalance_vs_comparison()

# Plot percentage increase without rebalancing
simulator.plot_percentage_increase_no_rebalance()

# Plot selected ETFs percentage increase

