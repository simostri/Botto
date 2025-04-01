from pathlib import Path
import pandas as pd
from analysis.data_loader import load_etfs_from_json, read_etf_data
from analysis.core_analysis import plot_etf_prices_and_revenue
from analysis.plotting import plot_technical_indicators
import plotly.graph_objects as go

def main(
    show_prices=True,
    show_revenue=True,
    show_heatmap=True,
    show_volatility=True,
    show_technical=True,
    show_plot=True,
    start_date="2018-01-01",
    end_date="2025-01-01",
    etf_name_for_technicals="Vanguard S&P 500 ETF"
):
    print("[main] 🚀 Starting ETF Analysis")

    json_file = 'etfs.json'
    data_path = './data/'

    print("[main] 📂 Loading ETF metadata...")
    try:
        etfs_meta = load_etfs_from_json(json_file)
    except Exception as e:
        print(f"[main] ❌ Failed to load ETF JSON: {e}")
        return

    etfs = [(etf["file"], etf["name"]) for etf in etfs_meta]
    print(f"[main] ✅ Loaded {len(etfs)} ETFs")

    print("[main] 📈 Computing price/revenue/volatility metrics...")
    try:
        df_summary = plot_etf_prices_and_revenue(
            data_path,
            etfs,
            start_date=start_date,
            end_date=end_date,
            show_prices=show_prices,
            show_revenue=show_revenue,
            show_heatmap=show_heatmap,
            show_volatility=show_volatility,
            render_inline=show_plot
        )
        print("[main] ✅ Summary plots created")
    except Exception as e:
        print(f"[main] ❌ Error during core analysis: {e}")
        df_summary = pd.DataFrame()

    if show_technical:
        print(f"[main] 🔎 Plotting technical indicators for: {etf_name_for_technicals}")
        etf_lookup = {etf["name"]: etf["file"] for etf in etfs_meta}
        file = etf_lookup.get(etf_name_for_technicals)

        if not file:
            print(f"[main] ❌ ETF '{etf_name_for_technicals}' not found in etfs.json")
        else:
            try:
                df_price = read_etf_data(Path(data_path) / file, pd.to_datetime(start_date), pd.to_datetime(end_date))
                price = df_price["Close"]
                figs = plot_technical_indicators(
                    price,
                    show_bollinger=True,
                    show_sma=True,
                    show_ema=True,
                    show_rsi=True,
                    show_macd=True,
                    etf_name=etf_name_for_technicals,
                    render_inline=False
                )
                if show_plot and figs:
                    for name, fig in figs.items():
                        fig.show(renderer='browser')
                        filename = f"{etf_name_for_technicals}_{name.replace(' ', '_')}.html"
                        fig.write_html(filename)
                        print(f"[main] 💾 Saved: {filename}")
                print("[main] ✅ Technical indicator plots displayed")
            except Exception as e:
                print(f"[main] ❌ Failed to plot technical indicators: {e}")

    # Final test plot
    
    print("[main] 🏁 Analysis complete")
    return df_summary


if __name__ == "__main__":
    df = main(
        show_prices=True,
        show_revenue=True,
        show_heatmap=True,
        show_volatility=True,
        show_technical=True,
        show_plot=True
    )
