import numpy as np
import pandas as pd


def SMA(data, window=20):
    return data["close"].rolling(window=window).mean()


def EMA(data, window=20):
    return data["close"].ewm(span=window, adjust=False).mean()


def MACD(data, fast=12, slow=26, signal=9):
    macd_line = (
        data["close"].ewm(span=fast, adjust=False).mean()
        - data["close"].ewm(span=slow, adjust=False).mean()
    )
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def RSI(data):
    delta = data["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()

    RS = avg_gain / avg_loss
    RSI = 100 - (100 / (1 + RS))
    return RSI


def Stochastic_Oscillator(data, k_window=14, d_window=3):
    low_min = data["low"].rolling(window=k_window).min()
    high_max = data["high"].rolling(window=k_window).max()

    percent_k = 100 * (data["close"] - low_min) / (high_max - low_min)
    percent_d = percent_k.rolling(window=d_window).mean()
    return percent_k, percent_d


def Williams(data, window=14):
    high_max = data["high"].rolling(window=window).max()
    low_min = data["low"].rolling(window=window).min()

    return -100 * (high_max - data["close"]) / (high_max - low_min)


def Bollinger_Bands(data, window=20, num_std=2):
    middle = data["close"].rolling(window=window).mean()
    std = data["close"].rolling(window=window).std()

    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def ATR(data, window=14):
    high_low = data["high"] - data["low"]
    high_close = (data["high"] - data["close"].shift()).abs()
    low_close = (data["low"] - data["close"].shift()).abs()

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / window, adjust=False).mean()


def OBV(data):
    direction = np.sign(data["close"].diff()).fillna(0)
    return (direction * data["volume"]).cumsum()


def Chaikin_Money_Flow(data, window=20):
    high_low = data["high"] - data["low"]
    mf_multiplier = (
        (data["close"] - data["low"]) - (data["high"] - data["close"])
    ) / high_low
    mf_multiplier = mf_multiplier.fillna(0)
    mf_volume = mf_multiplier * data["volume"]

    return (
        mf_volume.rolling(window=window).sum()
        / data["volume"].rolling(window=window).sum()
    )
