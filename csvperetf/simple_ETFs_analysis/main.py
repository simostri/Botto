from pathlib import Path
from analysis.data_loader import load_etfs_from_json
from analysis.core_analysis import plot_etf_prices_and_revenue

def main(show_plots=True,
         show_prices=True,
         show_revenue=True,
         show_heatmap= True,
         show_volatility = True):
    json_file = 'etfs.json'
    data_path = './data/'

    if not Path(json_file).exists():
        raise FileNotFoundError(f"ETF list file not found: {json_file}")
    if not Path(data_path).exists():
        raise FileNotFoundError(f"Data path not found: {data_path}")

    etfs = load_etfs_from_json(json_file)
    df = plot_etf_prices_and_revenue(
        data_path,
        etfs,
        start_date='2018-03-01',
        end_date='2025-02-01',
        show_prices=show_prices,
        show_revenue=show_revenue,
        show_heatmap=show_heatmap,
        show_volatility=show_volatility
    )

    print(df)
    return df

if __name__ == "__main__":
    # Run with plots ON when executed directly
    df = main(show_plots=False,
             show_prices=False,
             show_revenue=False,
             show_heatmap= False,
             show_volatility = False)
