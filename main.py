import os
import argparse
from datetime import datetime, timezone
from data_connector import Account
from utils import bar_to_df
from strategy import *
from visualization import *
from backtest import backtest, metrics_table


def get_account():
    key = os.getenv("alpaca_key")
    secret = os.getenv("alpaca_secret")
    return Account(key, secret)


def utc_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def parse_args():
    parser = argparse.ArgumentParser(description="Download historical stock data")

    parser.add_argument(
        "--symbol",
        default="AAPL",
        help="Stock ticker (default: AAPL)",
    )
    parser.add_argument(
        "--start",
        type=utc_date,
        default=datetime(2015, 1, 1, tzinfo=timezone.utc),
        help="Start date (YYYY-MM-DD). Default: 2015-01-01",
    )

    parser.add_argument(
        "--end",
        type=utc_date,
        default=datetime(2025, 1, 1, tzinfo=timezone.utc),
        help="End date (YYYY-MM-DD). Default: 2025-01-01",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    account = get_account()
    data = account.download_history(args.symbol, args.start, args.end)
    symbol, df = bar_to_df(data)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    strategies = [strategy_1(df), strategy_2(df), strategy_3(df)]

    results = {"Buy & Hold": backtest(df, baseline(df))}
    equity = {"Buy & Hold": results["Buy & Hold"][0]}

    for i, (name, panels, signal) in enumerate(strategies, start=1):
        price_chart(
            df,
            symbol=f"{symbol} - {name}",
            overlays=panels["overlays"],
            subplots=panels["subplots"],
            signal=signal,
            filename=f"strategy_{i}_price.svg",
        )
        portfolio, trades = backtest(df, signal)
        results[name] = (portfolio, trades)
        equity[name] = portfolio

    equity_curve(equity, symbol=symbol, filename="equity.svg")
    drawdown_chart(equity, symbol=symbol, filename="drawdown.svg")

    table = metrics_table(results)
    pct_cols = ["Total Return", "CAGR", "Volatility", "Max Drawdown", "Win Rate"]
    display = table.copy()
    for c in pct_cols:
        display[c] = (display[c] * 100).map("{:.2f}%".format)
    for c in ["Sharpe", "Sortino"]:
        display[c] = display[c].map("{:.2f}".format)
    print(f"\nPerformance Summary ({symbol})")
    print(display.to_string())


if __name__ == "__main__":
    main()
