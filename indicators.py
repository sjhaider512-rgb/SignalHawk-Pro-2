import ta 


def ema(close, period):
    """
    Exponential Moving Average
    """
    return ta.trend.EMAIndicator(
        close=close,
        window=period
    ).ema_indicator()


def rsi(close):
    """
    Relative Strength Index
    """
    return ta.momentum.RSIIndicator(
        close=close,
        window=14
    ).rsi()


def macd(close):
    """
    Moving Average Convergence Divergence
    """
    indicator = ta.trend.MACD(close=close)

    return indicator.macd()


def adx(df):
    """
    Average Directional Index
    """

    indicator = ta.trend.ADXIndicator(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=14
    )

    return indicator.adx()


def atr(df):
    """
    Average True Range
    """

    indicator = ta.volatility.AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=14
    )

    return indicator.average_true_range()
