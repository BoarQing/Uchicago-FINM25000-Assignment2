def bar_to_df(data):
    df = data.df
    symbol = df.index.get_level_values("symbol")[0]
    df = df.droplevel("symbol")
    df = df.tz_convert("America/New_York")

    return symbol, df
