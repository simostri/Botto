import streamlit as st
import logging
import json
import pandas as pd
from pathlib import Path
from analysis.data_loader import load_etfs_from_json
from analysis.core_analysis import plot_etf_prices_and_revenue
from download_etf_data import download_etf_data
from analysis.plotting import plot_technical_indicators

# Silence Streamlit warning logs
streamlit_loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict if name.startswith("streamlit")]
for logger in streamlit_loggers:
    logger.setLevel(logging.ERROR)

# --- Page Config ---
st.set_page_config(
    page_title="ETF Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load ETF Metadata ---
@st.cache_data
def load_etf_metadata(json_path):
    with open(json_path, "r") as f:
        return json.load(f)

ETF_JSON = "etfs.json"
DATA_PATH = "./data/"
etf_data = load_etf_metadata(ETF_JSON)
all_etf_names = [etf["name"] for etf in etf_data]
file_map = {etf["name"]: etf["file"] for etf in etf_data}

# --- Sidebar Filters ---
regions = sorted(set(etf["region"] for etf in etf_data))
sectors = sorted(set(etf["sector"] for etf in etf_data))

st.sidebar.header("Settings")
st.sidebar.subheader("Filters")
selected_region = st.sidebar.selectbox("Region", ["All"] + regions)
selected_sector = st.sidebar.selectbox("Sector", ["All"] + sectors)

filtered_etfs = [
    etf for etf in etf_data
    if (selected_region == "All" or etf["region"] == selected_region)
    and (selected_sector == "All" or etf["sector"] == selected_sector)
]
filtered_etf_names = [etf["name"] for etf in filtered_etfs]

# --- ETF Selector ---
selected_etfs = st.sidebar.multiselect(
    label="Select ETFs to Analyze",
    options=filtered_etf_names,
    default=filtered_etf_names[:5]
)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2025-01-01"))

st.sidebar.subheader("Plots")
show_prices = st.sidebar.checkbox("Show Price Chart", value=True)
show_revenue = st.sidebar.checkbox("Show % Revenue Chart", value=True)
show_heatmap = st.sidebar.checkbox("Show Annual Return Heatmap", value=True)
show_volatility = st.sidebar.checkbox("Show Rolling Volatility", value=True)

# --- Technical Analysis Settings ---
st.sidebar.header("Technical Analysis")
show_technicals = st.sidebar.checkbox("Show Technical Analysis Section", value=False)
if show_technicals:
    selected_ta_etf = st.sidebar.selectbox("Select ETF for Technical View", all_etf_names)
    show_bollinger = st.sidebar.checkbox("Bollinger Bands", value=True)
    show_sma = st.sidebar.checkbox("Simple Moving Average (SMA)", value=False)
    show_ema = st.sidebar.checkbox("Exponential Moving Average (EMA)", value=False)
    show_rsi = st.sidebar.checkbox("RSI", value=False)
    show_macd = st.sidebar.checkbox("MACD", value=False)

# --- ETF Downloader ---
name_to_ticker = {etf["name"]: etf["file"].replace(".csv", "") for etf in etf_data}
all_names = list(name_to_ticker.keys())

st.sidebar.subheader("Download ETF Data")
selected_to_download = st.sidebar.selectbox("Choose ETF to Download", all_names)
if st.sidebar.button("Download Selected ETF"):
    st.info(f"Downloading data for {selected_to_download}...")
    download_etf_data({"etfs": [{"ticker": name_to_ticker[selected_to_download], "name": selected_to_download}]})
    st.success("Download complete!")

# --- Run Analysis ---
if selected_etfs:
    selected_files = [(file_map[name], name) for name in selected_etfs]
    with st.spinner("Processing data..."):
        df = plot_etf_prices_and_revenue(
            path=DATA_PATH,
            etfs=selected_files,
            start_date=start_date,
            end_date=end_date,
            show_prices=show_prices,
            show_revenue=show_revenue,
            show_heatmap=show_heatmap,
            show_volatility=show_volatility,
            render_inline=True
        )

    st.success("Analysis Complete")

    # --- Add Metadata Columns ---
    meta_map = {etf["name"]: etf for etf in etf_data}
    df["Type"] = df.index.map(lambda name: meta_map.get(name, {}).get("type", ""))
    df["Region"] = df.index.map(lambda name: meta_map.get(name, {}).get("region", ""))
    df["Sector"] = df.index.map(lambda name: meta_map.get(name, {}).get("sector", ""))

    # --- Show Final Table with Column Selector ---
    st.subheader("Summary Table")
    all_columns = df.columns.tolist()
    default_columns = ["Average", "Type", "Region", "Sector"] if "Average" in df.columns else all_columns[:5]
    selected_columns = st.multiselect(
        "Select columns to display:",
        options=all_columns,
        default=default_columns
    )
    st.dataframe(df[selected_columns], use_container_width=True)

else:
    st.warning("Please select at least one ETF to analyze.")

# --- Technical Analysis Visualization ---
# --- Technical Analysis Visualization ---
if show_technicals and selected_ta_etf in file_map:
    ta_file = Path(DATA_PATH) / file_map[selected_ta_etf]
    df_price = pd.read_csv(ta_file, parse_dates=["Date"], index_col="Date")
    df_price.index = pd.to_datetime(df_price.index, utc=True).normalize()
    price = df_price["Close"]

    plots = plot_technical_indicators(
        price,
        show_bollinger,
        show_sma,
        show_ema,
        show_rsi,
        show_macd,
        selected_ta_etf
    )

    plot_technical_indicators(
    price,
    show_bollinger,
    show_sma,
    show_ema,
    show_rsi,
    show_macd,
    selected_ta_etf,
    render_inline=True
)
