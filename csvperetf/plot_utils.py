# plot_utils.py
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict

def plot_total_investment(total_investments: List[pd.Series], rebalance: bool):
    """Plot total investment value over time for each portfolio."""
    title = 'Investment Value Over Time' + (' (Rebalanced)' if rebalance else ' (No Rebalance)')
    plt.figure(figsize=(14, 7))
    for i, total_investment_df in enumerate(total_investments):
        plt.plot(total_investment_df.index, total_investment_df, label=f'Portfolio {i + 1}')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Investment Value ($)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_individual_investments(investment_values: List[Dict[str, pd.Series]], portfolios: List[tuple]):
    """Plot individual ETF investments over time for each portfolio."""
    plt.figure(figsize=(14, 7))
    for portfolio_investments, (_, _, etf_names) in zip(investment_values, portfolios):
        for name in etf_names:
            plt.plot(portfolio_investments[name].index, portfolio_investments[name], label=name)
    plt.title('Individual ETF Investment Over Time')
    plt.xlabel('Date')
    plt.ylabel('Investment Value')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_selected_etfs_percentage_increase(percentage_increase_no_rebalance: List[Dict[str, pd.Series]], etf_names: List[str]):
    """Plot percentage increase for selected ETFs over time (no rebalance)."""
    plt.figure(figsize=(14, 7))
    for etf_name in etf_names:
        for pct_increase_no_rebalance in percentage_increase_no_rebalance:
            if etf_name in pct_increase_no_rebalance:
                series = pct_increase_no_rebalance[etf_name]
                plt.plot(series.index, series, label=etf_name)
    plt.title('Selected ETFs Percentage Increase Over Time (No Rebalance)')
    plt.xlabel('Date')
    plt.ylabel('Percentage Increase')
    plt.legend()
    plt.grid(True)
    plt.show()
