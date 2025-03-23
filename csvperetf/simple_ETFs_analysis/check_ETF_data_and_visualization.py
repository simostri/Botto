#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 12:21:57 2025

@author: simone
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import pdb


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
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        for portfolio_files, _, etf_names in self.portfolios:
            portfolio_df_list = []
            for file, etf_name in zip(portfolio_files, etf_names):
                df = pd.read_csv(self.path + file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
                df.index = pd.to_datetime(df.index,utc = True)
                df.index = pd.to_datetime(df.index.date)  # remove time and keep only date
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
    
        # Generate rebalance schedule every 6 months from start date
        start = dates[0]
        end = dates[-1]
        rebalance_schedule = pd.date_range(start=start, end=end, freq='6MS')
    
        # Only use rebalance dates that exist in our dataset
        self.rebalance_dates = dates[dates.isin(rebalance_schedule)]
    
        for n, (_, allocations, etf_names) in enumerate(self.portfolios):
            #print('n is equal to ', n)
            quota_invested = [self.initial_budget * allocation for allocation in allocations]
            current_investments = quota_invested.copy()
            investment_values_over_time = {name: [] for name in etf_names}
            total_investment_over_time = []
            date_old = [dates[0] for name in etf_names]
            period_date_zero_old = [dates[0] for name in etf_names]  
            period_date_zero = dates[0]  # First rebalance reference point
            
            for date in dates:
                if date in self.rebalance_dates:
                    period_date_zero = date
                    total_value = sum(current_investments)
                    quota_invested = [total_value * allocation for allocation in allocations]
                percentage_increase = [1 for _ in allocations]
                for i, df in enumerate(self.portfolio_data[n]):
                    #print('df is equal to ',df.columns[0])
                    #print('date is ',date)
                    #print('i is equal to ',i)
                    #print('date old is ',date_old[i])
                    #if pd.to_datetime(date) == pd.Timestamp('2021-07-29 00:00:00') and n == 2:
                    #    pdb.set_trace()
                    if date in df.index and period_date_zero in df.index:
                        date_old[i] = date
                        percentage_increase[i] = df.loc[date].values[0] / df.loc[period_date_zero].values[0]                    
                        
                    elif date> df.index[0] and date_old[i]>df.index[0] and period_date_zero in df.index:
                        percentage_increase[i] = df.loc[date_old[i]].values[0] / df.loc[period_date_zero].values[0]                    
                        
                    elif date> df.index[0] and date_old[i]>df.index[0] and period_date_zero >= df.index[0]:
                        period_date_zero_old[i] = date_old[i]
                        percentage_increase[i] = df.loc[date_old[i]].values[0] / df.loc[period_date_zero_old[i]].values[0]                    
                        
                    current_investments[i] = quota_invested[i] * percentage_increase[i]
                    investment_values_over_time[etf_names[i]].append(current_investments[i])
    
                total_investment_over_time.append(sum(current_investments))
    
            self.investment_values.append({name: pd.Series(data=investment_values_over_time[name], index=dates) for name in etf_names})
            self.total_investments.append(pd.Series(data=total_investment_over_time, index=dates))

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
                print(' ')
                print(name)
                print(' ')
                print(portfolio_investments[name])
                print(' ')
                
                plt.plot(portfolio_investments[name].index, portfolio_investments[name], label=name)
        
        plt.title('Percentage Revenue Over Time (to fix - not a percentage)')
        plt.xlabel('Date')
        plt.ylabel('Percentage Revenue')
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
simulator.load_data(start_date='2017-01-01', end_date='2025-02-20')
simulator.calculate_investment_values()
simulator.plot_results()

# Plot individual ETF investment values
simulator.plot_individual_investments()