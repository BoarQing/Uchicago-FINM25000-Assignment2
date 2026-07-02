import os

import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

GREEN = "#26a69a"
RED = "#ef5350"
LINE_COLORS = ["#2962ff", "#ff6d00", "#aa00ff", "#00c853", "#d500f9", "#00b8d4"]

CHART_DIR = "charts"


def _x(index):
    return index.tz_convert(None).to_pydatetime()


def _save(fig, filename):
    os.makedirs(CHART_DIR, exist_ok=True)
    path = os.path.join(CHART_DIR, filename)
    fig.write_image(path, scale=3)
    return path


def price_chart(df, symbol="", overlays=None, subplots=None, signal=None,
                filename="price.svg"):
    overlays = overlays or {}
    subplots = subplots or {}

    x = _x(df.index)
    n_sub = len(subplots)
    rows = 2 + n_sub

    row_heights = [0.5, 0.15] + [0.35 / n_sub] * n_sub if n_sub else [0.75, 0.25]

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        row_heights=row_heights,
        vertical_spacing=0.03,
    )

    fig.add_trace(
        go.Candlestick(
            x=x,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="OHLC",
            increasing_line_color=GREEN,
            decreasing_line_color=RED,
        ),
        row=1,
        col=1,
    )

    for i, (label, series) in enumerate(overlays.items()):
        fig.add_trace(
            go.Scatter(
                x=x,
                y=series.values,
                mode="lines",
                name=label,
                line=dict(width=1.3, color=LINE_COLORS[i % len(LINE_COLORS)]),
            ),
            row=1,
            col=1,
        )

    if signal is not None:
        offset = 0.03
        buys = signal[signal > 0].index
        sells = signal[signal < 0].index
        fig.add_trace(
            go.Scatter(
                x=_x(buys),
                y=(df.loc[buys, "low"] * (1 - offset)).values,
                mode="markers",
                name="Buy",
                marker=dict(symbol="triangle-up", size=7, color=GREEN,
                            line=dict(width=0.5, color="white")),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=_x(sells),
                y=(df.loc[sells, "high"] * (1 + offset)).values,
                mode="markers",
                name="Sell",
                marker=dict(symbol="triangle-down", size=7, color=RED,
                            line=dict(width=0.5, color="white")),
            ),
            row=1,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=df["volume"],
            mode="lines",
            name="Volume",
            line=dict(width=0.5, color="#5c6bc0"),
            fill="tozeroy",
            fillcolor="rgba(92,107,192,0.35)",
        ),
        row=2,
        col=1,
    )
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    for r, (title, lines) in enumerate(subplots.items(), start=3):
        for i, (label, series) in enumerate(lines.items()):
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=series.values,
                    mode="lines",
                    name=label,
                    line=dict(width=1.3, color=LINE_COLORS[i % len(LINE_COLORS)]),
                ),
                row=r,
                col=1,
            )
        fig.update_yaxes(title_text=title, row=r, col=1)

    fig.update_layout(
        title=f"{symbol} Price & Signals",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=350 + 220 * (rows - 1),
        width=1400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return _save(fig, filename)


def equity_curve(equity, symbol="", filename="equity.svg"):
    fig = go.Figure()
    for i, (name, series) in enumerate(equity.items()):
        fig.add_trace(
            go.Scatter(
                x=_x(series.index),
                y=series.values,
                mode="lines",
                name=name,
                line=dict(width=1.8, color=LINE_COLORS[i % len(LINE_COLORS)]),
            )
        )
    fig.update_layout(
        title=f"{symbol} Equity Curve Comparison".strip(),
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        template="plotly_white",
        height=650,
        width=1400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return _save(fig, filename)


def drawdown_chart(equity, symbol="", filename="drawdown.svg"):
    fig = go.Figure()
    for i, (name, series) in enumerate(equity.items()):
        dd = (series / series.cummax() - 1.0) * 100
        fig.add_trace(
            go.Scatter(
                x=_x(dd.index),
                y=dd.values,
                mode="lines",
                name=name,
                line=dict(width=1.5, color=LINE_COLORS[i % len(LINE_COLORS)]),
            )
        )
    fig.update_layout(
        title=f"{symbol} Drawdown Comparison".strip(),
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_white",
        height=650,
        width=1400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return _save(fig, filename)
