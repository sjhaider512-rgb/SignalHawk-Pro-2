def generate_signal(df): 
    last = df.iloc[-1]

    price = float(last["close"])
    ema20 = float(last["EMA20"])
    ema50 = float(last["EMA50"])
    ema200 = float(last["EMA200"])
    rsi = float(last["RSI"])
    macd = float(last["MACD"])
    adx = float(last["ADX"])
    atr = float(last["ATR"])

    score = 0
    trend = "WAIT"

    # Strong trend filter
    bullish = price > ema20 and ema20 > ema50 and ema50 > ema200
    bearish = price < ema20 and ema20 < ema50 and ema50 < ema200

    if bullish:
        trend = "BUY"
        score += 40
    elif bearish:
        trend = "SELL"
        score -= 40

    # RSI filter
    if bullish:
        if 50 <= rsi <= 60:
            score += 25
        elif 60 < rsi <= 70:
            score += 15
        else:
            score -= 10

    elif bearish:
        if 40 <= rsi <= 50:
            score -= 25
        elif 30 <= rsi < 40:
            score -= 15
        else:
            score += 10

    # MACD confirmation
    if bullish:
        if macd > 0:
            score += 20
        else:
            score -= 15

    elif bearish:
        if macd < 0:
            score -= 20
        else:
            score += 15

    # ADX trend strength
    if bullish:
        if adx >= 30:
            score += 20
        elif adx >= 25:
            score += 10
        else:
            score -= 20

    elif bearish:
        if adx >= 30:
            score -= 20
        elif adx >= 25:
            score -= 10
        else:
            score += 20

    # Final signal
    if trend == "BUY" and score >= 75 and adx >= 25 and macd > 0 and 50 <= rsi <= 70:
        signal = "BUY"
    elif trend == "SELL" and score <= -75 and adx >= 25 and macd < 0 and 30 <= rsi <= 50:
        signal = "SELL"
    else:
        signal = "WAIT"

    confidence = min(abs(score), 100)

    if signal != "WAIT":
        confidence = min(confidence + 5, 100)
    else:
        confidence = min(confidence, 60)

    stop_loss = None
    take_profit = None

    # ATR-based trade levels
    if signal == "BUY":
        stop_loss = round(price - (atr * 1.5), 5)
        take_profit = round(price + (atr * 2), 5)

    elif signal == "SELL":
        stop_loss = round(price + (atr * 1.5), 5)
        take_profit = round(price - (atr * 2), 5)

    return signal, confidence, stop_loss, take_profit, score
