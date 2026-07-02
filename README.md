# Technical Trading Strategies & Backtesting Engine

FINM 25000 – Assignment 2. Downloads historical daily price data from Alpaca,
computes technical indicators, runs three trading strategies through a reusable
long-only backtesting engine, and produces performance metrics and charts.

## What it does

Given a stock ticker, the program:

1. **Downloads** 10 years of daily OHLCV data from the Alpaca Historical Market
   Data API (split- and dividend-adjusted).
2. **Computes technical indicators** (`technical_indicator.py`):
   SMA, EMA, MACD, RSI, Stochastic Oscillator, Williams %R, Bollinger Bands,
   ATR, OBV, and Chaikin Money Flow.
3. **Runs three strategies** (`strategy.py`):
   - **Strategy 1 – Trend Following:** long when MACD is above its signal line,
     exit when it crosses below.
   - **Strategy 2 – Mean Reversion:** long when RSI < 30 *and* price is below the
     lower Bollinger Band; exit when RSI > 70 *and* price is above the upper band.
   - **Strategy 3 – Custom:** combines trend (EMA20/EMA50), volatility (ATR vs its
     moving average), and volume (OBV vs its moving average).
4. **Backtests** each strategy plus a Buy & Hold baseline (`backtest.py`):
   - Initial capital: $100,000
   - Long-only, no leverage, no short selling
   - All-in / all-out; signals are executed at the **next day's open** price
5. **Reports performance** — Total Return, CAGR, Volatility, Sharpe, Sortino,
   Maximum Drawdown, and Win Rate — printed as a comparison table.
6. **Generates charts** (`visualization.py`) as SVG files in `charts/`:
   - `strategy_{1,2,3}_price.svg` — candlesticks, volume, the indicators each
     strategy uses, and buy/sell markers
   - `equity.svg` — equity curves for Buy & Hold vs. the three strategies
   - `drawdown.svg` — drawdown comparison across all strategies

## Usage

```bash
python main.py --symbol AAPL --start 2015-01-01 --end 2025-01-01
```

Arguments (all optional):

| Argument | Default | Description |
|----------|---------|-------------|
| `--symbol` | `AAPL` | Stock ticker (e.g. AAPL, MSFT, SPY, QQQ, NVDA) |
| `--start` | `2015-01-01` | Start date (YYYY-MM-DD) |
| `--end` | `2025-01-01` | End date (YYYY-MM-DD) |

Running the command prints a performance summary to the console and writes the
five SVG charts to the `charts/` directory.
