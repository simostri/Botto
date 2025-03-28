
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
import json
import logging
from typing import Optional, Tuple, List, Dict

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set default renderer
pio.renderers.default = 'browser'

def load_etfs_from_json(json_file: str) -> List[Tuple[str, str]]:
    with open(json_file, 'r') as f:
        return [(item['file'], item['name']) for item in json.load(f)]

def read_etf_data(filepath: Path, start_date: pd.Timestamp, end_date: Optional[pd.Timestamp]) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=['Date'], usecols=['Date', 'Close'], index_col='Date')
    df.index = pd.to_datetime(df.index, utc=True)
    df.index = pd.to_datetime(df.index.date)  # normalize to date only
    df = df.loc[start_date:end_date] if end_date else df.loc[start_date:]
    return df

def calculate_revenue_and_returns(df: pd.DataFrame, etf_name: str) -> pd.DataFrame:
    df.rename(columns={'Close': etf_name}, inplace=True)
    df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0] - 1) * 100
    df['Year'] = df.index.year
    df['daily_return'] = df[etf_name].pct_change() * 100
    return df

def plot_time_series(data_dict: Dict[str, pd.Series], title: str, yaxis_title: str):
    fig = go.Figure()
    for label, series in data_dict.items():
        fig.add_trace(go.Scatter(x=series.index, y=series, mode='lines', name=label))
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title=yaxis_title)
    fig.show()

def plot_etf_prices_and_revenue(path: str, etfs: List[Tuple[str, str]],
                                 start_date: str = '2017-03-01', end_date: Optional[str] = None,
                                 show_plots: bool = True) -> pd.DataFrame:
    path = Path(path)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date) if end_date else None

    etf_prices, etf_revenue, etf_annualized_revenue = {}, {}, {}
    etf_std_dev, etf_daily_returns, overall_std_dev = {}, {}, {}

    for file, name in etfs:
        df = read_etf_data(path / file, start_date, end_date)
        df = calculate_revenue_and_returns(df, name)

        etf_prices[name] = df[name]
        etf_revenue[name] = df['pct_revenue']
        etf_annualized_revenue[name] = df.groupby('Year')[name].apply(
            lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100
        )
        etf_std_dev[name] = df.groupby('Year')['daily_return'].std()
        overall_std_dev[name] = df['daily_return'].std()
        etf_daily_returns[name] = df['daily_return']

    if show_plots:
        plot_time_series(etf_prices, 'ETF Prices Over Time', 'Price')
        plot_time_series(etf_revenue, 'ETF Percentage Revenue Over Time', 'Percentage Revenue')

    all_years = sorted({yr for v in etf_annualized_revenue.values() for yr in v.index})
    index_labels = [name for _, name in etfs]

    annual_df = pd.DataFrame(index=index_labels, columns=all_years)
    std_df = pd.DataFrame(index=index_labels, columns=all_years)

    for name in index_labels:
        annual_df.loc[name, etf_annualized_revenue[name].index] = etf_annualized_revenue[name].values
        std_df.loc[name, etf_std_dev[name].index] = etf_std_dev[name].values

    annual_df['Average'] = annual_df.astype(float).mean(axis=1)
    overall_std_series = pd.Series(overall_std_dev)
    annual_df['StdDev_All'] = overall_std_series

    reference_etfs = ['SPDR MSCI World UCITS ETF', 'Vanguard S&P 500']
    corr_df = pd.DataFrame(index=index_labels, columns=reference_etfs)

    for name in index_labels:
        for ref in reference_etfs:
            if name != ref and ref in etf_daily_returns:
                common_dates = etf_daily_returns[name].dropna().index.intersection(
                    etf_daily_returns[ref].dropna().index
                )
                if not common_dates.empty:
                    corr = np.corrcoef(etf_daily_returns[name].loc[common_dates],
                                       etf_daily_returns[ref].loc[common_dates])[0, 1]
                    corr_df.loc[name, ref] = corr

    for ref in reference_etfs:
        annual_df[f'Correlation with {ref}'] = corr_df[ref]

    for ref in reference_etfs:
        yearly_corr = pd.DataFrame(index=index_labels, columns=all_years)
        for name in index_labels:
            if name == ref or ref not in etf_daily_returns:
                continue
            for yr in all_years:
                s1 = etf_daily_returns[name][etf_daily_returns[name].index.year == yr]
                s2 = etf_daily_returns[ref][etf_daily_returns[ref].index.year == yr]
                common = s1.dropna().index.intersection(s2.dropna().index)
                yearly_corr.loc[name, yr] = np.corrcoef(s1.loc[common], s2.loc[common])[0, 1] if not common.empty else None
        for yr in all_years:
            annual_df[f'Corr_{yr}_with_{ref}'] = yearly_corr[yr]

    for yr in all_years:
        annual_df[f'StdDev_{yr}'] = std_df[yr]

    def fmt(x):
        return f"{x:.2f}%" if pd.notnull(x) and isinstance(x, (int, float)) else x

    return annual_df.applymap(fmt)

def main():
    json_file = 'etfs.json'
    data_path = 'C:/Users/sistri/OneDrive/Degiro/Botto/csvperetf/data/'

    if not Path(json_file).exists():
        raise FileNotFoundError(f"ETF list file not found: {json_file}")
    if not Path(data_path).exists():
        raise FileNotFoundError(f"Data path not found: {data_path}")

    etfs = load_etfs_from_json(json_file)
    df = plot_etf_prices_and_revenue(data_path, etfs, start_date='2018-03-01', end_date='2025-02-01', show_plots=True)
    print(df)

if __name__ == "__main__":
    main()
