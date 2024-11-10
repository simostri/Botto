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

def allocate_monthly_addition(portfolio_data: List[List[pd.DataFrame]], current_investments: List[float], etf_names: List[str], date, portfolio_index: int, monthly_increase: float):
    """Allocate additional monthly investment to the ETF with the lowest performance."""
    performance = []
    for i, df in enumerate(portfolio_data[portfolio_index]):
        initial_value = df.iloc[0].values[0]
        current_value = df.loc[date].values[0]
        performance.append((current_value / initial_value) - 1)
    
    lowest_performance_index = performance.index(min(performance))
    current_investments[lowest_performance_index] += monthly_increase
    print(f"Added ${monthly_increase} to {etf_names[lowest_performance_index]} for date {date}")
