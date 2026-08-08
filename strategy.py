def generate_signal(df): 
    """
    Generate trading signal from latest candle
    """

    last = df.iloc[-1]

    score = 0

    # EMA Trend 
    bullish = last["EMA20"] > last["EMA50"] > last["EMA200"]
    bearish = last["EMA20"] < last["EMA50"] < last["EMA200"]

    trend = "WAIT" 

    if bullish:
        trend = "BUY"
    elif bearish:
        trend = "SELL"

    if bullish:
        score += 35
    elif bearish:
        score -= 35

    # RSI 
    if bullish and 50 <= last["RSI"] <= 60: 
        score += 20
    elif bullish and 60 < last["RSI"] <= 70:
        score += 10
    elif bullish and last["RSI"] > 70:
        score -= 10
    elif bearish and 30 <= last["RSI"] <= 50:
        score -= 20

    # MACD 
    if bullish and last["MACD"] > 0: 
        score += 20
    elif bearish and last["MACD"] < 0:
        score -= 20

    # ADX Strength 
    if last["ADX"] > 40: 
        score += 20
    elif last["ADX"] > 30:
        score += 15
    elif last["ADX"] > 25:
        score += 10
    elif last["ADX"] > 20:
        score += 5
    else:
        score -= 10

   # Signal
    if trend == "BUY" and score >= 70:
        signal = "BUY"
    elif trend == "SELL" and score <= -70:
        signal = "SELL"
    else:
        signal = "WAIT"


    confidence = min(abs(score), 100) 

    if trend == signal:
        confidence = min(confidence + 5, 100)

    atr = last["ATR"]
    price = last["close"]

    stop_loss = None
    take_profit = None

    if signal == "BUY":
        stop_loss = round(price - (atr * 2), 5)
        take_profit = round(price + (atr * 4), 5)

    elif signal == "SELL":
        stop_loss = round(price + (atr * 2), 5)
        take_profit = round(price - (atr * 4), 5)

    return signal, confidence, stop_loss, take_profit, score
