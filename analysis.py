from backtest import run_backtest 
import yfinance as yf
import pandas as pd

from indicators import ema, rsi, macd, adx, atr
from strategy import generate_signal


def analyse_market(pair, timeframe):
    interval_map = {
        "1 Minute": "1m",
        "5 Minutes": "5m",
        "15 Minutes": "15m",
        "1 Hour": "1h",
        "4 Hours": "4h",
        "1 Day": "1d"
    }

    interval = interval_map.get(timeframe, "1h")

    if interval == "1m":
        period = "7d"
    elif interval in ["5m", "15m"]:
        period = "60d"
    elif interval in ["1h", "4h"]:
        period = "730d"
    else:
        period = "2y"

    df = yf.download(
        pair,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=False
    )

    if df is None or df.empty:
        return {"error": "No market data returned."}

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })

    required_columns = ["open", "high", "low", "close"]

    for col in required_columns:
        if col not in df.columns:
            return {"error": f"Missing required column: {col}"}

    df["EMA20"] = ema(df["close"], 20)
    df["EMA50"] = ema(df["close"], 50)
    df["EMA200"] = ema(df["close"], 200)

    df["RSI"] = rsi(df["close"])
    df["MACD"] = macd(df["close"])
    df["ADX"] = adx(df)
    df["ATR"] = atr(df)

    df = df.dropna()

    if df.empty:
        return {"error": "Not enough candles to calculate indicators."}

    signal_result = generate_signal(df)

    if signal_result is None:
        signal = "WAIT"
        confidence = 60
        stop_loss = None
        take_profit = None
        score = None
    elif len(signal_result) == 5:
        signal, confidence, stop_loss, take_profit, score = signal_result
    else:
        signal, confidence, stop_loss, take_profit = signal_result
        score = None

    backtest = run_backtest(df)

    safety_note = None

    backtest_win_rate = backtest.get("Win Rate", 0)
    backtest_total_trades = backtest.get("Total Trades", 0)

    if backtest_total_trades >= 30 and backtest_win_rate < 50:
        signal = "WAIT"
        confidence = min(confidence, 60)
        safety_note = "Backtest win rate is low, so signal changed to WAIT for safety."

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
        "Data": df
    }
