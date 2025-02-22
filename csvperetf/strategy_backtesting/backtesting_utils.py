import os
import pandas as pd
from typing import List, Tuple

def calculate_budget(initial_budget: float, monthly_increase: float, months_elapsed: int) -> float:
    """Calculate the updated budget after adding monthly increases for a given period."""
    return initial_budget + (monthly_increase * months_elapsed)

def load_data(path: str, portfolios: List[Tuple[List[str], List[float], List[str]]], start_date: str = '2017-03-01', end_date: str = None) -> List[List[pd.DataFrame]]:
    """Load and prepare ETF data for each portfolio."""
    portfolio_data = []
    for portfolio_files, _, etf_names in portfolios:
        portfolio_df_list = []
        for file, etf_name in zip(portfolio_files, etf_names):
            full_path = os.path.join(path, file)
            df = pd.read_csv(full_path, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
            df = df.loc[start_date:end_date] if end_date else df.loc[start_date:]
            df.rename(columns={'Close': etf_name}, inplace=True)
            df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0]) - 1
            portfolio_df_list.append(df)
        portfolio_data.append(portfolio_df_list)
    return portfolio_data

def initialize_data(path: str, portfolios: List[Tuple[List[str], List[float], List[str]]], start_date: str = '2017-03-01', end_date: str = None) -> List[List[pd.DataFrame]]:
    """Initialize portfolio data by loading it with the load_data utility function."""
    return load_data(path, portfolios, start_date, end_date)

def allocate_monthly_addition(current_investments: List[float], etf_names: List[str], percentage_increases: List[float], monthly_increase: float) -> List[float]:
    """Allocate additional investment to the ETF that increased the least over the past month."""
    
    # Identify the ETF with the smallest percentage increase
    lowest_performance_index = percentage_increases.index(min(percentage_increases))
    
    # Allocate extra funds to that ETF
    current_investments[lowest_performance_index] += monthly_increase
    print(current_investments[lowest_performance_index])
    
    return current_investments
