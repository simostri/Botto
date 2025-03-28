# analysis/metrics.py

import pandas as pd
import numpy as np

def calculate_revenue_and_returns(df: pd.DataFrame, etf_name: str) -> pd.DataFrame:
    df.rename(columns={'Close': etf_name}, inplace=True)
    df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0] - 1) * 100
    df['Year'] = df.index.year
    df['daily_return'] = df[etf_name].pct_change() * 100
    return df

# ----------------------------
# 🔍 ADVANCED METRICS BELOW
# ----------------------------

def calculate_cagr(series: pd.Series) -> float:
    if series.empty:
        return np.nan
    start_value = series.iloc[0]
    end_value = series.iloc[-1]
    n_years = (series.index[-1] - series.index[0]).days / 365.25
    return ((end_value / start_value) ** (1 / n_years) - 1) * 100 if start_value > 0 else np.nan

def calculate_max_drawdown(series: pd.Series) -> float:
    cumulative_max = series.cummax()
    drawdown = (series - cumulative_max) / cumulative_max
    return drawdown.min() * 100  # return as negative %

def calculate_sharpe_ratio(daily_returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    excess_returns = daily_returns / 100 - risk_free_rate / 252
    mean = excess_returns.mean()
    std = excess_returns.std()
    return (mean / std) * np.sqrt(252) if std > 0 else np.nan

def calculate_rolling_beta(target: pd.Series, benchmark: pd.Series, window: int = 30) -> pd.Series:
    return target.rolling(window).cov(benchmark) / benchmark.rolling(window).var()
