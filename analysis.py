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
        "4 Hours": "1h",
        "1 Day": "1d",
    }

    interval = interval_map.get(timeframe, "1h")

    if interval == "1m":
        period = "7d"
    elif interval in ["5m", "15m"]:
        period = "60d"
    elif interval == "1h":
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
        return {"error": "No data returned."}

    # Fix multi-index columns if yfinance returns them
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Make column names simple lowercase
    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume"
    })

    needed_columns = ["open", "high", "low", "close"]

    for col in needed_columns:
        if col not in df.columns:
            return {"error": f"Missing column: {col}"}

    df = df[needed_columns].copy()

    # Convert 1-hour candles into 4-hour candles
    if timeframe == "4 Hours":
        df = df.resample("4H").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last"
        })

    df = df.dropna()

    if len(df) < 220:
        return {"error": "Not enough candles to calculate indicators."}

    # Indicators
    df["EMA20"] = ema(df["close"], 20)
    df["EMA50"] = ema(df["close"], 50)
    df["EMA200"] = ema(df["close"], 200)
    df["RSI"] = rsi(df["close"])
    df["MACD"] = macd(df["close"])
    df["ADX"] = adx(df)
    df["ATR"] = atr(df)

    df = df.dropna()

    if df.empty or len(df) < 220:
        return {"error": "Not enough candles to calculate indicators."}

    # Generate signal safely
    signal_result = generate_signal(df)

    if signal_result is None:
        signal = "WAIT"
        confidence = 60
        stop_loss = None
        take_profit = None
        score = 0
    elif len(signal_result) == 5:
        signal, confidence, stop_loss, take_profit, score = signal_result
    else:
        signal, confidence, stop_loss, take_profit = signal_result
        score = 0

    # Run faster backtest
    backtest = run_backtest(df)

    safety_note = "Signal passed basic checks."

    total_trades = backtest.get("Total Trades", 0)
    win_rate = backtest.get("Win Rate", 0)
    average_points = backtest.get("Average Points", 0)
    current_rsi = float(df["RSI"].iloc[-1])

    # Safety filter 1: not enough backtest trades
    if total_trades < 50:
        signal = "WAIT"
        confidence = min(confidence, 60)
        safety_note = "WAIT: not enough backtest trades."

    # Safety filter 2: poor backtest result
    elif win_rate < 45 or average_points <= 0:
        signal = "WAIT"
        confidence = min(confidence, 60)
        safety_note = "WAIT: backtest result is weak."

    # Safety filter 3: avoid BUY when RSI is too high
    elif signal == "BUY" and current_rsi >= 70:
        signal = "WAIT"
        confidence = min(confidence, 60)
        safety_note = "WAIT: RSI is too high for BUY."

    # Safety filter 4: avoid SELL when RSI is too low
    elif signal == "SELL" and current_rsi <= 30:
        signal = "WAIT"
        confidence = min(confidence, 60)
        safety_note = "WAIT: RSI is too low for SELL."

    elif signal in ["BUY", "SELL"]:
        safety_note = "Signal passed safety checks."

    else:
        signal = "WAIT"
        confidence = min(confidence, 60)
        safety_note = "No valid trade setup."

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
