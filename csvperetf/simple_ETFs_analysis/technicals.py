import pandas as pd
import numpy as np
import warnings

# Suppress rolling/statistical warnings due to short data windows
warnings.filterwarnings("ignore", category=RuntimeWarning)

def calculate_bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0):
    series = series.dropna()
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper_band = sma + (num_std * std)
    lower_band = sma - (num_std * std)
    return sma, upper_band, lower_band

def calculate_sma(series: pd.Series, window: int = 20):
    return series.dropna().rolling(window=window).mean()

def calculate_ema(series: pd.Series, span: int = 20):
    return series.dropna().ewm(span=span, adjust=False).mean()

def calculate_rsi(series: pd.Series, window: int = 14):
    series = series.dropna()
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain, index=series.index).rolling(window=window).mean()
    avg_loss = pd.Series(loss, index=series.index).rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return pd.Series(rsi, index=series.index)

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    series = series.dropna()
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram
