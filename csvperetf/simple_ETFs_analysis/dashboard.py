# dashboard.py

import streamlit as st
import pandas as pd
from analysis.data_loader import load_etfs_from_json
from analysis.core_analysis import plot_etf_prices_and_revenue

# --- Page Config ---
st.set_page_config(
    page_title="ETF Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load ETF Metadata ---
ETF_JSON = "etfs.json"
DATA_PATH = "./data/"
all_etfs = load_etfs_from_json(ETF_JSON)
all_etf_names = [name for _, name in all_etfs]
file_map = {name: file for file, name in all_etfs}

# --- Sidebar Controls ---
st.sidebar.header("Settings")
selected_etfs = st.sidebar.multiselect(
    label="Select ETFs to Analyze",
    options=all_etf_names,
    default=all_etf_names[:5]
)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2025-01-01"))

st.sidebar.subheader("Plots")
show_prices = st.sidebar.checkbox("Show Price Chart", value=True)
show_revenue = st.sidebar.checkbox("Show % Revenue Chart", value=True)
show_heatmap = st.sidebar.checkbox("Show Annual Return Heatmap", value=True)
show_volatility = st.sidebar.checkbox("Show Rolling Volatility", value=True)

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

    # --- Show Final Table ---
    st.subheader("Summary Table")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("Please select at least one ETF to analyze.")
