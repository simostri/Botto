# analysis/core_analysis.py

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional

from .data_loader import read_etf_data
from .metrics import (
    calculate_revenue_and_returns,
    calculate_cagr,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_rolling_beta,
)
from .plotting import (
    plot_time_series,
    plot_annual_return_heatmap,
    plot_rolling_volatility,
)

def compute_etf_metrics(path: Path, etfs: List[Tuple[str, str]], start_date, end_date):
    print("[core_analysis] 🔄 Starting ETF metric computation...")
    etf_prices, etf_revenue = {}, {}
    etf_annualized_revenue, etf_std_dev = {}, {}
    etf_daily_returns, overall_std_dev = {}, {}

    for file, name in etfs:
        try:
            print(f"[core_analysis] 📄 Processing {name} ({file})...")
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
        except Exception as e:
            print(f"[core_analysis] ❌ Failed to process {name}: {e}")

    return etf_prices, etf_revenue, etf_annualized_revenue, etf_std_dev, overall_std_dev, etf_daily_returns

def compute_correlations(index_labels, etf_daily_returns, reference_etfs):
    print("[core_analysis] 📊 Computing overall correlations...")
    corr_df = pd.DataFrame(index=index_labels, columns=reference_etfs)
    for name in index_labels:
        for ref in reference_etfs:
            if name != ref and ref in etf_daily_returns:
                common_dates = etf_daily_returns[name].dropna().index.intersection(
                    etf_daily_returns[ref].dropna().index
                )
                if not common_dates.empty:
                    corr = np.corrcoef(
                        etf_daily_returns[name].loc[common_dates],
                        etf_daily_returns[ref].loc[common_dates]
                    )[0, 1]
                    corr_df.loc[name, ref] = corr
    return corr_df

def compute_yearly_correlations(index_labels, etf_daily_returns, reference_etfs, all_years):
    print("[core_analysis] 📊 Computing yearly correlations...")
    yearly_corr_dfs = {}
    for ref in reference_etfs:
        yearly_corr = pd.DataFrame(index=index_labels, columns=all_years)
        for name in index_labels:
            if name == ref or ref not in etf_daily_returns:
                continue
            for yr in all_years:
                s1 = etf_daily_returns[name][etf_daily_returns[name].index.year == int(yr)]
                s2 = etf_daily_returns[ref][etf_daily_returns[ref].index.year == int(yr)]
                common = s1.dropna().index.intersection(s2.dropna().index)
                yearly_corr.loc[name, yr] = (
                    np.corrcoef(s1.loc[common], s2.loc[common])[0, 1] if not common.empty else None
                )
        yearly_corr_dfs[ref] = yearly_corr
    return yearly_corr_dfs

def compute_advanced_metrics(index_labels, etf_prices, etf_daily_returns, benchmark):
    print("[core_analysis] 📈 Computing advanced metrics (CAGR, Drawdown, Sharpe, Beta)...")
    metrics = {
        "CAGR": [],
        "MaxDrawdown": [],
        "SharpeRatio": [],
        f"Beta_vs_{benchmark}": []
    }

    for name in index_labels:
        try:
            metrics["CAGR"].append(calculate_cagr(etf_prices[name]))
            metrics["MaxDrawdown"].append(calculate_max_drawdown(etf_prices[name]))
            metrics["SharpeRatio"].append(calculate_sharpe_ratio(etf_daily_returns[name]))

            if name == benchmark or benchmark not in etf_daily_returns:
                metrics[f"Beta_vs_{benchmark}"].append(None)
            else:
                beta_series = calculate_rolling_beta(etf_daily_returns[name], etf_daily_returns[benchmark])
                metrics[f"Beta_vs_{benchmark}"].append(beta_series.mean())
        except Exception as e:
            print(f"[core_analysis] ❌ Error computing metrics for {name}: {e}")

    return metrics

def build_summary_dataframe(index_labels, all_years, etf_annualized_revenue, etf_std_dev, overall_std_dev, corr_df, yearly_corr_dfs, adv_metrics):
    print("[core_analysis] 📋 Building summary dataframe...")
    annual_df = pd.DataFrame(index=index_labels, columns=all_years)
    std_df = pd.DataFrame(index=index_labels, columns=all_years)

    for name in index_labels:
        for year, value in etf_annualized_revenue[name].items():
            annual_df.loc[name, str(year)] = value
        for year, std in etf_std_dev[name].items():
            std_df.loc[name, str(year)] = std

    annual_df['Average'] = annual_df.astype(float).mean(axis=1)
    annual_df['StdDev_All'] = pd.Series(overall_std_dev)

    for ref, corr_vals in corr_df.items():
        annual_df[f'Correlation with {ref}'] = corr_vals

    for ref, yearly_corr in yearly_corr_dfs.items():
        for yr in all_years:
            annual_df[f'Corr_{yr}_with_{ref}'] = yearly_corr[yr]

    for yr in all_years:
        annual_df[f'StdDev_{yr}'] = std_df[yr]

    for metric, values in adv_metrics.items():
        annual_df[metric] = values

    return annual_df

def plot_etf_prices_and_revenue(
    path: str,
    etfs: List[Tuple[str, str]],
    start_date: str = '2017-03-01',
    end_date: Optional[str] = None,
    show_prices: bool = True,
    show_revenue: bool = True,
    show_heatmap: bool = True,
    show_volatility: bool = True,
    render_inline: bool = False
) -> pd.DataFrame:

    print("[core_analysis] 🚀 Starting full ETF visual analysis...")

    path = Path(path)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date) if end_date else None

    etf_prices, etf_revenue, etf_annualized_revenue, etf_std_dev, overall_std_dev, etf_daily_returns = compute_etf_metrics(
        path, etfs, start_date, end_date
    )

    all_years = sorted({str(yr) for v in etf_annualized_revenue.values() for yr in v.index})
    index_labels = [name for _, name in etfs]

    corr_df = compute_correlations(index_labels, etf_daily_returns, reference_etfs=['SPDR MSCI World UCITS ETF', 'Vanguard S&P 500 ETF'])
    yearly_corr_dfs = compute_yearly_correlations(index_labels, etf_daily_returns, ['SPDR MSCI World UCITS ETF', 'Vanguard S&P 500 ETF'], all_years)
    adv_metrics = compute_advanced_metrics(index_labels, etf_prices, etf_daily_returns, benchmark="Vanguard S&P 500 ETF")

    annual_df = build_summary_dataframe(
        index_labels,
        all_years,
        etf_annualized_revenue,
        etf_std_dev,
        overall_std_dev,
        corr_df,
        yearly_corr_dfs,
        adv_metrics
    )

    def fmt(x):
        return f"{x:.2f}%" if pd.notnull(x) and isinstance(x, (int, float)) else x

    if show_prices:
        print("[core_analysis] 📊 Plotting ETF prices...")
        plot_time_series(etf_prices, 'ETF Prices Over Time', 'Price', render_inline=render_inline)

    if show_revenue:
        print("[core_analysis] 📊 Plotting ETF returns...")
        plot_time_series(etf_revenue, 'ETF Percentage Revenue Over Time', 'Percentage Revenue', render_inline=render_inline)

    if show_heatmap:
        print("[core_analysis] 🗺️ Plotting annual return heatmap...")
        plot_annual_return_heatmap(annual_df, render_inline=render_inline)

    if show_volatility:
        print("[core_analysis] 📉 Plotting volatility...")
        plot_rolling_volatility(etf_daily_returns, render_inline=render_inline)

    print("[core_analysis] ✅ ETF visual analysis complete.")
    return annual_df.applymap(fmt)
