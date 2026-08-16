import yfinance as yf 
import pandas as pd

from indicators import ema, rsi, macd, adx, atr
from strategy import generate_signal
from backtest import run_backtest


def analyse_market(pair, timeframe):
    interval_map = {
        "15 Minutes": "15m",
        "1 Hour": "1h",
        "4 Hours": "1h",
    }

    interval = interval_map.get(timeframe, "1h")

    if interval == "15m":
        period = "60d"
    elif interval == "1h":
        period = "730d"
    else:
        period = "730d"

    df = yf.download(
        pair,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=False,
    )

    if df is None or df.empty:
        return {"error": "No data returned from Yahoo Finance."}

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )

    required_columns = ["open", "high", "low", "close"]

    for col in required_columns:
        if col not in df.columns:
            return {"error": f"Missing column: {col}"}

    df = df[required_columns].copy()
    df = df.dropna()

    if df.empty:
        return {"error": "No clean candle data available."}

    if timeframe == "4 Hours":
        df = df.resample("4h").agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
            }
        )
        df = df.dropna()

    if df.empty or len(df) < 220:
        return {"error": "Not enough candles to calculate indicators."}

    df["EMA20"] = ema(df["close"], 20)
    df["EMA50"] = ema(df["close"], 50)
    df["EMA200"] = ema(df["close"], 200)
    df["RSI"] = rsi(df["close"], 14)
    df["MACD"] = macd(df["close"])
    df["ADX"] = adx(df, 14)
    df["ATR"] = atr(df, 14)

    df = df.dropna()

    if df.empty or len(df) < 220:
        return {"error": "Not enough clean indicator data."}

    signal_result = generate_signal(df)

    if len(signal_result) == 6:
        signal, confidence, stop_loss, take_profit, score, safety_note = signal_result
    else:
        signal, confidence, stop_loss, take_profit, score = signal_result
        safety_note = "Signal checked."

    backtest = run_backtest(df)

    total_trades = backtest.get("Total Trades", 0)
    win_rate = backtest.get("Win Rate", 0)
    average_points = backtest.get("Average Points", 0)

    if signal in ["BUY", "SELL"]:
        if total_trades < 5:
            signal = "WAIT"
            confidence = 0
            stop_loss = None
            take_profit = None
            safety_note = "WAIT: not enough backtest trades."

        elif win_rate < 45:
            signal = "WAIT"
            confidence = 0
            stop_loss = None
            take_profit = None
            safety_note = "WAIT: backtest result is weak."

        elif average_points <= 0:
            signal = "WAIT"
            confidence = 0
            stop_loss = None
            take_profit = None
            safety_note = "WAIT: average backtest points are weak."

    if signal == "WAIT":
        stop_loss = None
        take_profit = None

    return {
        "Signal": signal,
        "Confidence": confidence,
        "Score": score,
        "Price": round(float(df["close"].iloc[-1]), 5),
        "EMA20": round(float(df["EMA20"].iloc[-1]), 5),
        "EMA50": round(float(df["EMA50"].iloc[-1]), 5),
        "EMA200": round(float(df["EMA200"].iloc[-1]), 5),
        "RSI": round(float(df["RSI"].iloc[-1]), 2),
        "MACD": round(float(df["MACD"].iloc[-1]), 5),
        "ADX": round(float(df["ADX"].iloc[-1]), 2),
        "ATR": round(float(df["ATR"].iloc[-1]), 5),
        "StopLoss": stop_loss,
        "TakeProfit": take_profit,
        "Backtest": backtest,
        "SafetyNote": safety_note,
        "Data": df,
    }
