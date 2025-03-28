# analysis/plotting.py

import plotly.express as px
import plotly.graph_objects as go
from typing import Dict
import pandas as pd

def plot_time_series(data_dict: Dict[str, pd.Series], title: str, yaxis_title: str, render_inline: bool = False):
    import plotly.graph_objects as go
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

    if render_inline:
        import streamlit as st
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()



def plot_annual_return_heatmap(df: pd.DataFrame, title="Annualized Returns (%)", render_inline: bool = False):
    import plotly.express as px
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

    if render_inline:
        import streamlit as st
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()



def plot_rolling_volatility(etf_returns: Dict[str, pd.Series], window: int = 30, render_inline: bool = False):
    import plotly.graph_objects as go
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

    if render_inline:
        import streamlit as st
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig.show()

