from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit


class Account:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.hist = StockHistoricalDataClient(api_key=self.key, secret_key=self.secret)

    def download_history(self, symbol, start, end):
        request = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame(1, TimeFrameUnit.Day),
            start=start,
            end=end,
            adjustment=Adjustment.ALL,
        )

        return self.hist.get_stock_bars(request)
