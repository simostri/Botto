import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

# Set default renderer to 'browser' for Spyder or other non-Jupyter environments
pio.renderers.default = 'browser'

def plot_etf_prices_and_revenue(path, etfs, start_date='2017-03-01', end_date=None):
    etf_prices = {}
    etf_revenue = {}
    etf_annualized_revenue = {}
    etf_std_dev = {}
    etf_daily_returns = {}

    # Convert start and end dates to datetime and ensure they are timezone-naive
    start_date = pd.to_datetime(start_date).tz_localize(None)
    end_date = pd.to_datetime(end_date).tz_localize(None) if end_date else None

    for file, etf_name in etfs:
        df = pd.read_csv(path + file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
        
        # Ensure df.index is a DatetimeIndex and make it timezone-naive
        if isinstance(df.index, pd.DatetimeIndex):
            df.index = df.index.tz_localize(None)
        
        # Filter dataframe based on date range
        df = df[(df.index >= start_date) & (df.index <= end_date)] if end_date else df[df.index >= start_date]
        
        df.rename(columns={'Close': etf_name}, inplace=True)
        df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0] - 1) * 100
        etf_prices[etf_name] = df[etf_name]
        etf_revenue[etf_name] = df['pct_revenue']
        
        # Compute annualized percentage revenue for each year using correct Pandas syntax
        df['Year'] = df.index.year
        annualized_revenue_per_year = df.groupby('Year', group_keys=False).apply(
            lambda x: (x[etf_name].iloc[-1] / x[etf_name].iloc[0] - 1) * 100
        )
        etf_annualized_revenue[etf_name] = annualized_revenue_per_year
        
        # Compute standard deviation of daily returns for each year
        df['daily_return'] = df[etf_name].pct_change() * 100
        std_dev_per_year = df.groupby('Year')['daily_return'].std()
        etf_std_dev[etf_name] = std_dev_per_year
        
        # Store daily returns for correlation calculation
        etf_daily_returns[etf_name] = df['daily_return']

    # Visualization: ETF Prices & Revenue
    fig_prices = go.Figure()
    fig_revenue = go.Figure()
    
    for etf_label, df in etf_prices.items():
        fig_prices.add_trace(go.Scatter(x=df.index, y=df, mode='lines', name=etf_label))
    
    for etf_label, df in etf_revenue.items():
        fig_revenue.add_trace(go.Scatter(x=df.index, y=df, mode='lines', name=etf_label))
    
    fig_prices.update_layout(title='ETF Prices Over Time', xaxis_title='Date', yaxis_title='Price')
    fig_revenue.update_layout(title='ETF Percentage Revenue Over Time', xaxis_title='Date', yaxis_title='Percentage Revenue')
    
    fig_prices.show()
    fig_revenue.show()
    
    # DataFrame for annualized revenue and statistics
    years = sorted(set(year for df in etf_annualized_revenue.values() for year in df.index))
    annualized_revenue_df = pd.DataFrame(index=[etf for _, etf in etfs], columns=years)
    std_dev_df = pd.DataFrame(index=[etf for _, etf in etfs], columns=years)
    
    for etf_label, annualized_revenue in etf_annualized_revenue.items():
        annualized_revenue_df.loc[etf_label, annualized_revenue.index] = annualized_revenue.values
    
    for etf_label, std_dev in etf_std_dev.items():
        std_dev_df.loc[etf_label, std_dev.index] = std_dev.values
    
    annualized_revenue_df['Average'] = annualized_revenue_df.mean(axis=1)
    
    # Convert DataFrame values to percentage format
    annualized_revenue_df = annualized_revenue_df.applymap(lambda x: f"{x:.2f}%" if pd.notnull(x) and isinstance(x, (int, float)) else x)
    
    return annualized_revenue_df

# Usage
path = "/home/simone/Finance/Botto/csvperetf/data/"
etfs = [
    ('IUST.DE.csv', 'SPDR Bloomberg Barclays US TIPS UCITS ETF'),
    ('IBGX.SW.csv', 'Invesco Euro Government Bond 3-5 Year'),
    ('US10.PA.csv', 'Lyxor US Treasury 10+Y (DR) UCITS'),
    ('IBCI.L.csv', 'Lyxor Euro Government Inflation Linked Bond (DR)'),
    ('IBGL.L.csv', 'iShares Euro Government Bond 15-30yr UCITS'),
    ('SGLD.MI.csv', 'Invesco Physical Gold A'),
    ('ICOM.L.csv', 'Lyxor Commodities Refinitiv/CoreCommodity CRB TR UCITS'),
    ('SPPW.DE.csv', 'SPDR MSCI World UCITS ETF'),
    ('VBK.csv', 'Vanguard Small-Cap Growth Index Fund'),
    ('VBR.csv', 'Vanguard Small-Cap Value Index Fund'),
    ('VUG.csv', 'Vanguard Growth Index Fund'),
    ('VTV.csv', 'Vanguard Value Index Fund'),
    ('VOO.csv', 'Vanguard S&P 500'),
    ('SMH.csv', 'Vaneck Semiconductors UCITS ETF')
]

annualized_revenue_df = plot_etf_prices_and_revenue(path, etfs, start_date='2018-03-01', end_date='2024-05-20')
print(annualized_revenue_df)
