import numpy as np
import pandas as pd

INITIAL_CAPITAL = 100_000.0
PERIODS_PER_YEAR = 252


def backtest(df, signal, initial_capital=INITIAL_CAPITAL):
    open_ = df["open"].values
    close = df["close"].values
    index = df.index
    sig = signal.reindex(index).fillna(0.0).values

    cash = initial_capital
    shares = 0.0
    position = 0
    entry_price = np.nan

    values = np.empty(len(index))
    trades = []

    for i in range(len(index)):
        px_open = open_[i]

        if sig[i] > 0 and position == 0:
            shares = cash / px_open
            cash = 0.0
            position = 1
            entry_price = px_open
            trades.append({"date": index[i], "side": "BUY", "price": px_open,
                           "shares": shares})

        elif sig[i] < 0 and position == 1:
            cash = shares * px_open
            pnl = (px_open - entry_price) * shares
            ret = px_open / entry_price - 1.0
            trades.append({"date": index[i], "side": "SELL", "price": px_open,
                           "shares": shares, "pnl": pnl, "return": ret})
            shares = 0.0
            position = 0
            entry_price = np.nan

        values[i] = cash + shares * close[i]

    portfolio = pd.Series(values, index=index, name="portfolio")
    return portfolio, trades


def _win_rate(trades):
    closed = [t["return"] for t in trades if t["side"] == "SELL"]
    if not closed:
        return np.nan
    wins = sum(1 for r in closed if r > 0)
    return wins / len(closed)


def performance_metrics(portfolio, trades=None, periods_per_year=PERIODS_PER_YEAR,
                        risk_free=0.0):
    ret = portfolio.pct_change().dropna()
    total_return = portfolio.iloc[-1] / portfolio.iloc[0] - 1.0

    years = len(portfolio) / periods_per_year
    cagr = (portfolio.iloc[-1] / portfolio.iloc[0]) ** (1.0 / years) - 1.0 if years > 0 else np.nan

    vol = ret.std(ddof=0) * np.sqrt(periods_per_year)

    excess = ret - risk_free / periods_per_year
    ann_excess = excess.mean() * periods_per_year
    sharpe = ann_excess / vol if vol > 0 else np.nan

    downside = ret[ret < 0].std(ddof=0) * np.sqrt(periods_per_year)
    sortino = ann_excess / downside if downside > 0 else np.nan

    cummax = portfolio.cummax()
    drawdown = portfolio / cummax - 1.0
    max_drawdown = drawdown.min()

    return {
        "Total Return": total_return,
        "CAGR": cagr,
        "Volatility": vol,
        "Sharpe": sharpe,
        "Sortino": sortino,
        "Max Drawdown": max_drawdown,
        "Win Rate": _win_rate(trades) if trades is not None else np.nan,
    }


def metrics_table(results):
    rows = {}
    for name, (portfolio, trades) in results.items():
        m = performance_metrics(portfolio, trades)
        rows[name] = m
    table = pd.DataFrame(rows).T
    return table[
        ["Total Return", "CAGR", "Volatility", "Sharpe", "Sortino",
         "Max Drawdown", "Win Rate"]
    ]
