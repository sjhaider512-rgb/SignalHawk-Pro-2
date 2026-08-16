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

    # Trend score
    if price > ema20:
        score += 20
    else:
        score -= 20

    if ema20 > ema50:
        score += 20
    else:
        score -= 20

    if ema50 > ema200:
        score += 20
    else:
        score -= 20

    # RSI score
    if rsi > 55:
        score += 15
    elif rsi < 45:
        score -= 15

    # MACD score
    if macd > 0:
        score += 20
    else:
        score -= 20

    # ADX strength
    if adx >= 20:
        if score > 0:
            score += 15
        elif score < 0:
            score -= 15

    # TEST MODE signal rules
    if score >= 40:
        signal = "BUY"
    elif score <= -40:
        signal = "SELL"
    else:
        signal = "WAIT"

    confidence = min(abs(score), 95)

    stop_loss = None
    take_profit = None

    if signal == "BUY":
        stop_loss = round(price - (1.5 * atr), 5)
        take_profit = round(price + (2.0 * atr), 5)

    elif signal == "SELL":
        stop_loss = round(price + (1.5 * atr), 5)
        take_profit = round(price - (2.0 * atr), 5)

    return signal, confidence, stop_loss, take_profit, score