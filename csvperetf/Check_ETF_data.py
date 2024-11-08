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

    for file, etf_name in etfs:
        df = pd.read_csv(path + file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
        if end_date:
            df = df[(df.index >= start_date) & (df.index <= end_date)]
        else:
            df = df[df.index >= start_date]
        df.rename(columns={'Close': etf_name}, inplace=True)
        df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0] - 1) * 100  # Calculate pct_revenue as percentage
        etf_prices[etf_name] = df[etf_name]
        etf_revenue[etf_name] = df['pct_revenue']
        
        # Compute annualized percentage revenue for each year
        df['Year'] = df.index.year
        annualized_revenue_per_year = df.groupby('Year').apply(
            lambda x: (x[etf_name].iloc[-1] / x[etf_name].iloc[0] - 1) * 100
        )
        etf_annualized_revenue[etf_name] = annualized_revenue_per_year
        
        # Compute standard deviation of daily returns for each year
        df['daily_return'] = df[etf_name].pct_change() * 100
        std_dev_per_year = df.groupby('Year')['daily_return'].std()
        etf_std_dev[etf_name] = std_dev_per_year
        
        # Store daily returns for correlation calculation
        etf_daily_returns[etf_name] = df['daily_return']

    fig_prices = go.Figure()
    fig_revenue = go.Figure()
    
    for etf_label, df in etf_prices.items():
        fig_prices.add_trace(go.Scatter(x=df.index, y=df, mode='lines', name=etf_label))
    
    for etf_label, df in etf_revenue.items():
        fig_revenue.add_trace(go.Scatter(x=df.index, y=df, mode='lines', name=etf_label))
    
    fig_prices.update_layout(
        title='ETF Prices Over Time',
        xaxis_title='Date',
        yaxis_title='Price',
        legend_title='ETF',
        hovermode='x unified'
    )
    
    fig_revenue.update_layout(
        title='ETF Percentage Revenue Over Time',
        xaxis_title='Date',
        yaxis_title='Percentage Revenue',
        legend_title='ETF',
        hovermode='x unified'
    )
    
    fig_prices.show()
    fig_revenue.show()
    
    # Prepare data for the table
    years = sorted(set(year for df in etf_annualized_revenue.values() for year in df.index))
    annualized_revenue_df = pd.DataFrame(index=[etf for _, etf in etfs], columns=years)
    std_dev_df = pd.DataFrame(index=[etf for _, etf in etfs], columns=years)
    
    for etf_label, annualized_revenue in etf_annualized_revenue.items():
        for year in years:
            annualized_revenue_df.at[etf_label, year] = annualized_revenue.get(year, None)
    
    for etf_label, std_dev in etf_std_dev.items():
        for year in years:
            std_dev_df.at[etf_label, year] = std_dev.get(year, None)
    
    # Calculate the average annualized revenue for each ETF
    average_annualized_revenue = annualized_revenue_df.mean(axis=1)
    annualized_revenue_df['Average'] = average_annualized_revenue
    
    # Compute normalized cross-correlation with SPDR MSCI World UCITS ETF and Vanguard S&P 500
    reference_etfs = ['SPDR MSCI World UCITS ETF', 'Vanguard S&P 500']
    cross_correlation_df = pd.DataFrame(index=[etf for _, etf in etfs], columns=reference_etfs)
    
    for etf_label, daily_returns in etf_daily_returns.items():
        for ref_etf in reference_etfs:
            if etf_label != ref_etf:
                common_dates = daily_returns.dropna().index.intersection(etf_daily_returns[ref_etf].dropna().index)
                cross_correlation = np.corrcoef(daily_returns[common_dates], etf_daily_returns[ref_etf][common_dates])[0, 1]
                cross_correlation_df.at[etf_label, ref_etf] = cross_correlation
    
    # Add standard deviation columns to the annualized_revenue_df
    for year in years:
        annualized_revenue_df[f'StdDev_{year}'] = std_dev_df[year]
    
    # Add cross-correlation columns to the annualized_revenue_df
    for ref_etf in reference_etfs:
        annualized_revenue_df[f'Correlation with {ref_etf}'] = cross_correlation_df[ref_etf]
    
    # Convert DataFrame values to percentage format for the annualized revenue
    annualized_revenue_df = annualized_revenue_df.applymap(lambda x: f"{x:.2f}%" if pd.notnull(x) and isinstance(x, (int, float)) else x)
    
    # Convert the DataFrame to a NumPy array
    annualized_revenue_array = annualized_revenue_df.replace('%', '', regex=True).astype(float).values
    
    return annualized_revenue_df, annualized_revenue_array

# Usage
path = "/home/simone/Finance/Botto/csvperetf/"
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

annualized_revenue_df, annualized_revenue_array = plot_etf_prices_and_revenue(path, etfs, start_date='2018-03-01', end_date='2024-05-20')
print(annualized_revenue_df)
print(annualized_revenue_array)

# You can now visualize the `annualized_revenue_df` DataFrame and `annualized_revenue_array` NumPy array in Spyder's variable explorer
