from technical_indicator import *


def action_to_signal(buy_data, sell_data):
    signal = pd.Series(0.0, index=buy_data.index)

    state = 0

    for i in range(len(buy_data) - 1):
        if state == 0 and buy_data.iloc[i]:
            signal.iloc[i] = 1.0
            state = 1

        elif state == 1 and sell_data.iloc[i]:
            signal.iloc[i] = -1.0
            state = 0
    # we use close price, we can only buy next open
    signal = signal.shift(1, fill_value=0.0)
    return signal


def strategy_1(data):
    macd_line, signal_line, _ = MACD(data)
    buy_data = macd_line > signal_line
    sell_data = macd_line < signal_line

    panels = {
        "overlays": {},
        "subplots": {"MACD": {"MACD": macd_line, "Signal": signal_line}},
    }
    return "Trend Following (MACD)", panels, action_to_signal(buy_data, sell_data)


def strategy_2(data):
    rsi = RSI(data)
    upper, middle, lower = Bollinger_Bands(data)
    buy_data = (rsi < 30) & (data["close"] < lower)
    sell_data = (rsi > 70) & (data["close"] > upper)

    panels = {
        "overlays": {"BB Upper": upper, "BB Middle": middle, "BB Lower": lower},
        "subplots": {"RSI": {"RSI": rsi}},
    }
    return "Mean Reversion (RSI+BB)", panels, action_to_signal(buy_data, sell_data)


def strategy_3(data):
    ema20 = EMA(data, window=20)
    ema50 = EMA(data, window=50)
    atr = ATR(data)
    obv = OBV(data)

    obv_ma = obv.ewm(span=20, adjust=False).mean()
    atr_ma = atr.rolling(20).mean()

    buy_data = (ema20 > ema50) & (atr > atr_ma) & (obv > obv_ma)

    sell_data = (ema20 < ema50) | (obv < obv_ma) | (atr < atr_ma)

    panels = {
        "overlays": {"EMA20": ema20, "EMA50": ema50},
        "subplots": {
            "ATR": {"ATR": atr, "ATR MA": atr_ma},
            "OBV": {"OBV": obv, "OBV MA": obv_ma},
        },
    }
    return "Custom (EMA+ATR+OBV)", panels, action_to_signal(buy_data, sell_data)


def baseline(data):
    signal = pd.Series(0.0, index=data.index)
    signal.iloc[0] = 1.0

    return signal
