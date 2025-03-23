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
    etf_std_dev = {}         # per-year std dev
    etf_daily_returns = {}
    overall_std_dev = {}     # overall standard deviation (not per year)
    
    # Convert start and end dates to datetime and ensure they are timezone-naive
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date) if end_date else None
    
    for file, etf_name in etfs:
        df = pd.read_csv(path + file, parse_dates=['Date'], index_col='Date', usecols=['Date', 'Close'])
        df.index = pd.to_datetime(df.index, utc=True)
        df.index = pd.to_datetime(df.index.date)  # remove time and keep only date
        
        # Filter dataframe based on date range
        if end_date:
            df = df[(df.index >= start_date) & (df.index <= end_date)]
        else:
            df = df[df.index >= start_date]
        
        df.rename(columns={'Close': etf_name}, inplace=True)
        df['pct_revenue'] = (df[etf_name] / df[etf_name].iloc[0] - 1) * 100
        etf_prices[etf_name] = df[etf_name]
        etf_revenue[etf_name] = df['pct_revenue']
        
        # Compute annualized percentage revenue for each year
        df['Year'] = df.index.year
        annualized_revenue_per_year = df.groupby('Year', group_keys=False).apply(
            lambda x: (x[etf_name].iloc[-1] / x[etf_name].iloc[0] - 1) * 100
        )
        etf_annualized_revenue[etf_name] = annualized_revenue_per_year
        
        # Compute standard deviation of daily returns for each year
        df['daily_return'] = df[etf_name].pct_change() * 100
        std_dev_per_year = df.groupby('Year')['daily_return'].std()
        etf_std_dev[etf_name] = std_dev_per_year
        
        # Compute overall standard deviation (for entire period)
        overall_std_dev[etf_name] = df['daily_return'].std()
        
        # Store daily returns for correlation calculations
        etf_daily_returns[etf_name] = df['daily_return']

    # Visualization: ETF Prices & Revenue
    fig_prices = go.Figure()
    fig_revenue = go.Figure()
    
    for etf_label, series in etf_prices.items():
        fig_prices.add_trace(go.Scatter(x=series.index, y=series, mode='lines', name=etf_label))
    
    for etf_label, series in etf_revenue.items():
        fig_revenue.add_trace(go.Scatter(x=series.index, y=series, mode='lines', name=etf_label))
    
    fig_prices.update_layout(title='ETF Prices Over Time', xaxis_title='Date', yaxis_title='Price')
    fig_revenue.update_layout(title='ETF Percentage Revenue Over Time', xaxis_title='Date', yaxis_title='Percentage Revenue')
    
    fig_prices.show()
    fig_revenue.show()
    
    # Prepare data for the table
    years = sorted({year for revenue in etf_annualized_revenue.values() for year in revenue.index}) # Maybe the redundancy at this line is because different Etfs might have different length
    annualized_revenue_df = pd.DataFrame(index=[etf for _, etf in etfs], columns=years)
    std_dev_df = pd.DataFrame(index=[etf for _, etf in etfs], columns=years)
    
    for etf_label, annualized_revenue in etf_annualized_revenue.items():
        annualized_revenue_df.loc[etf_label, annualized_revenue.index] = annualized_revenue.values
    
    for etf_label, std_dev in etf_std_dev.items():
        std_dev_df.loc[etf_label, std_dev.index] = std_dev.values

    # Calculate the average annualized revenue for each ETF
    annualized_revenue_df['Average'] = annualized_revenue_df.mean(axis=1)
    
    # Compute overall cross-correlation (over full period) with the reference ETFs
    reference_etfs = ['SPDR MSCI World UCITS ETF', 'Vanguard S&P 500']
    cross_correlation_overall = pd.DataFrame(index=[etf for _, etf in etfs], columns=reference_etfs)
    
    for etf_label, daily_returns in etf_daily_returns.items():
        for ref_etf in reference_etfs:
            if etf_label != ref_etf and ref_etf in etf_daily_returns:
                common_dates = daily_returns.dropna().index.intersection(etf_daily_returns[ref_etf].dropna().index)
                if not common_dates.empty:
                    corr_value = np.corrcoef(daily_returns.loc[common_dates],
                                             etf_daily_returns[ref_etf].loc[common_dates])[0, 1]
                    cross_correlation_overall.at[etf_label, ref_etf] = corr_value
                else:
                    cross_correlation_overall.at[etf_label, ref_etf] = None
    
    # Compute per-year cross-correlation with the reference ETFs
    cross_corr_yearly = {}
    for ref_etf in reference_etfs:
        # Create a DataFrame to hold per-year correlation for this reference ETF
        corr_df = pd.DataFrame(index=[etf for _, etf in etfs], columns=years)
        for etf_label, returns in etf_daily_returns.items():
            if etf_label == ref_etf or ref_etf not in etf_daily_returns:
                continue
            for year in years:
                # Filter daily returns for the given year
                series1 = returns[returns.index.year == year]
                series2 = etf_daily_returns[ref_etf][etf_daily_returns[ref_etf].index.year == year]
                common_dates = series1.dropna().index.intersection(series2.dropna().index)
                if not common_dates.empty:
                    corr = np.corrcoef(series1.loc[common_dates], series2.loc[common_dates])[0, 1]
                else:
                    corr = None
                corr_df.at[etf_label, year] = corr
        cross_corr_yearly[ref_etf] = corr_df
    
    # Add per-year standard deviation columns to the annualized revenue DataFrame
    for year in years:
        annualized_revenue_df[f'StdDev_{year}'] = std_dev_df[year]
    
    # Add overall standard deviation column
    overall_std_series = pd.Series(overall_std_dev)
    annualized_revenue_df['StdDev_All'] = overall_std_series
    
    # Add overall cross-correlation columns (over full period)
    for ref_etf in reference_etfs:
        annualized_revenue_df[f'Correlation with {ref_etf}'] = cross_correlation_overall[ref_etf]
    
    # Add per-year cross-correlation columns
    for ref_etf in reference_etfs:
        for year in years:
            col_name = f'Corr_{year}_with_{ref_etf}'
            # Use the per-year correlation DataFrame computed above
            annualized_revenue_df[col_name] = cross_corr_yearly[ref_etf][year]
    
    # Convert DataFrame numeric values to formatted strings (percentage format)
    def format_value(x):
        if pd.notnull(x) and isinstance(x, (int, float)):
            return f"{x:.2f}%"
        return x

    annualized_revenue_df = annualized_revenue_df.applymap(format_value)
    
    return annualized_revenue_df

# Usage example
path = "/home/simone/Finance/Botto/csvperetf/data/"
etfs = [
    ('VOO.csv', 'Vanguard S&P 500 ETF'),
    ('VTI.csv', 'Vanguard Total Stock Market ETF'),
    ('SPY.csv', 'SPDR S&P 500 ETF Trust'),
    ('QQQ.csv', 'Invesco QQQ Trust'),
    ('ARKK.csv', 'ARK Innovation ETF'),
    ('VUG.csv', 'Vanguard Growth ETF'),
    ('VTV.csv', 'Vanguard Value ETF'),
    ('VBK.csv', 'Vanguard Small-Cap Growth ETF'),
    ('VBR.csv', 'Vanguard Small-Cap Value ETF'),
    ('VT.csv', 'Vanguard Total World Stock ETF'),
    ('DIA.csv', 'SPDR Dow Jones Industrial Average ETF Trust'),
    ('IWM.csv', 'iShares Russell 2000 ETF'),
    ('IVV.csv', 'iShares Core S&P 500 ETF'),
    ('XLF.csv', 'Financial Select Sector SPDR Fund'),
    ('XLK.csv', 'Technology Select Sector SPDR Fund'),
    ('XLV.csv', 'Health Care Select Sector SPDR Fund'),
    ('XLY.csv', 'Consumer Discretionary Select Sector SPDR Fund'),
    ('XLI.csv', 'Industrial Select Sector SPDR Fund'),
    ('XLE.csv', 'Energy Select Sector SPDR Fund'),
    ('XLC.csv', 'Communication Services Select Sector SPDR Fund'),
    ('XLU.csv', 'Utilities Select Sector SPDR Fund'),
    ('XLP.csv', 'Consumer Staples Select Sector SPDR Fund'),
    ('XLB.csv', 'Materials Select Sector SPDR Fund'),
    ('XLRE.csv', 'Real Estate Select Sector SPDR Fund'),
    ('ITPS.SW.csv', 'iShares $ TIPS UCITS ETF USD'),
    ('IBGX.AS.csv', 'iShares Euro Government Bond 3-5 Year UCITS'),
    ('US10.PA.csv', 'Lyxor US Treasury 10+Y (DR) UCITS'),
    ('IBCI.AS.csv', 'IShares Euro Inflation Linked Government Bond UCITS'),
    ('IBGL.AS.csv', 'iShares Euro Government Bond 15-30yr UCITS'),
    ('SGLD.MI.csv', 'Invesco Physical Gold A'),
    ('ICOM.L.csv', 'Lyxor Commodities Refinitiv/CoreCommodity CRB TR UCITS'),
    ('SPPW.DE.csv', 'SPDR MSCI World UCITS ETF'),
    ('VBK.csv', 'Vanguard Small-Cap Growth Index Fund'),
    ('VBR.csv', 'Vanguard Small-Cap Value Index Fund'),
    ('VUG.csv', 'Vanguard Growth Index Fund'),
    ('VTV.csv', 'Vanguard Value Index Fund'),
    ('VOO.csv', 'Vanguard S&P 500')
]

annualized_revenue_df = plot_etf_prices_and_revenue(path, etfs, start_date='2018-03-01', end_date='2025-02-01')
print(annualized_revenue_df)
