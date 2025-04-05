# analysis/plotting.py

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict
import pandas as pd
from technicals import *


try:
    import streamlit as st
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

def plot_time_series(data_dict: Dict[str, pd.Series], title: str, yaxis_title: str, render_inline: bool = False):
    fig = go.Figure()
    for label, series in data_dict.items():
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series,
            mode='lines',
            name=label,
            hovertemplate=f"{label}<br>Date: %{{x}}<br>{yaxis_title}: %{{y:.2f}}<extra></extra>"
        ))
    fig.update_layout(
        title={'text': title, 'x': 0.5, 'font': {'size': 24}},
        xaxis_title='Date',
        yaxis_title=yaxis_title,
        template='plotly_white',
        hovermode='x unified'
    )
    if render_inline and ST_AVAILABLE:
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()

def plot_annual_return_heatmap(df: pd.DataFrame, title="Annualized Returns (%)", render_inline: bool = False):
    years = [str(col) for col in df.columns if str(col).isdigit()]
    heat_df = df[years].astype(float)

    fig = px.imshow(
        heat_df,
        labels=dict(x="Year", y="ETF", color="Return (%)"),
        x=years,
        y=heat_df.index,
        color_continuous_scale='Viridis',
        aspect="auto",
        title=title
    )
    fig.update_layout(title_x=0.5)

    if render_inline and ST_AVAILABLE:
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()

def plot_rolling_volatility(etf_returns: Dict[str, pd.Series], window: int = 30, render_inline: bool = False):
    fig = go.Figure()
    for name, series in etf_returns.items():
        rolling_std = series.rolling(window=window).std()
        fig.add_trace(go.Scatter(
            x=rolling_std.index,
            y=rolling_std,
            name=name,
            text=[name] * len(rolling_std),
            hovertemplate="%{text}<br>Date: %{x}<br>Volatility: %{y:.2f}%<extra></extra>"
        ))
    fig.update_layout(
        title=f"{window}-Day Rolling Volatility",
        xaxis_title='Date',
        yaxis_title='Volatility (%)',
        template='plotly_white',
        hovermode='x unified'
    )

    if render_inline and ST_AVAILABLE:
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()

def plot_technical_indicators(price, show_bollinger, show_sma, show_ema, show_rsi, show_macd, etf_name):
    plots = {}

    price = price.dropna()

    if len(price) < 30:
        print(f"[SKIP] Not enough data to compute technical indicators for: {etf_name}")
        return plots

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price.index, y=price, name="Close", line=dict(color="black")))

    if show_bollinger:
        sma, upper, lower = calculate_bollinger_bands(price)
        fig.add_trace(go.Scatter(x=sma.index, y=sma, name="SMA", line=dict(dash="dot", color="blue")))
        fig.add_trace(go.Scatter(x=upper.index, y=upper, name="Upper Band", line=dict(color="green")))
        fig.add_trace(go.Scatter(x=lower.index, y=lower, name="Lower Band", line=dict(color="red")))

    if show_sma:
        sma = calculate_sma(price)
        fig.add_trace(go.Scatter(x=sma.index, y=sma, name="SMA", line=dict(dash="dot", color="blue")))

    if show_ema:
        ema = calculate_ema(price)
        fig.add_trace(go.Scatter(x=ema.index, y=ema, name="EMA", line=dict(dash="dot", color="orange")))

    fig.update_layout(title=f"{etf_name} - Price with Indicators", xaxis_title="Date", yaxis_title="Price")
    plots["Price with Indicators"] = fig

    if show_rsi:
        rsi = calculate_rsi(price)
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=rsi.index, y=rsi, name="RSI", line=dict(color="purple")))
        fig_rsi.update_layout(title=f"{etf_name} - RSI", xaxis_title="Date", yaxis_title="RSI")
        plots["RSI"] = fig_rsi

    if show_macd:
        macd, signal, hist = calculate_macd(price)
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=macd.index, y=macd, name="MACD", line=dict(color="blue")))
        fig_macd.add_trace(go.Scatter(x=signal.index, y=signal, name="Signal", line=dict(color="orange")))
        fig_macd.add_trace(go.Bar(x=hist.index, y=hist, name="Histogram"))
        fig_macd.update_layout(title=f"{etf_name} - MACD", xaxis_title="Date", yaxis_title="MACD")
        plots["MACD"] = fig_macd

    return plots