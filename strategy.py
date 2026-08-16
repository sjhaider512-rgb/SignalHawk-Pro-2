def safe_float(value): 
    try:
        return float(value)
    except Exception:
        return None


def generate_signal(df):
    """
    Signal Hawk Commodities Bot
    Pullback strategy for Gold, Platinum and Oil.

    Returns:
    signal, confidence, stop_loss, take_profit, score, safety_note
    """

    if df is None or df.empty or len(df) < 220:
        return "WAIT", 0, None, None, 0, "WAIT: not enough market data."

    last = df.iloc[-1]
    prev = df.iloc[-2]

    price = safe_float(last["close"])
    prev_price = safe_float(prev["close"])

    ema20 = safe_float(last["EMA20"])
    ema50 = safe_float(last["EMA50"])
    ema200 = safe_float(last["EMA200"])

    prev_ema20 = safe_float(prev["EMA20"])
    prev_ema50 = safe_float(prev["EMA50"])

    rsi = safe_float(last["RSI"])
    prev_rsi = safe_float(prev["RSI"])

    macd = safe_float(last["MACD"])
    prev_macd = safe_float(prev["MACD"])

    adx = safe_float(last["ADX"])
    atr = safe_float(last["ATR"])

    values = [
        price, prev_price,
        ema20, ema50, ema200,
        prev_ema20, prev_ema50,
        rsi, prev_rsi,
        macd, prev_macd,
        adx, atr
    ]

    if any(v is None for v in values):
        return "WAIT", 0, None, None, 0, "WAIT: indicators are not ready."

    if atr <= 0:
        return "WAIT", 0, None, None, 0, "WAIT: ATR is not valid."

    score = 0
    signal = "WAIT"
    confidence = 0
    stop_loss = None
    take_profit = None
    safety_note = "WAIT: no strong safe setup."

    # Main trend
    bullish_trend = price > ema200 and ema20 > ema50
    bearish_trend = price < ema200 and ema20 < ema50

    # Pullback area
    bullish_pullback = price >= ema50 and price <= ema20 * 1.003
    bearish_pullback = price <= ema50 and price >= ema20 * 0.997

    # Momentum change
    macd_improving = macd > prev_macd
    macd_falling = macd < prev_macd

    rsi_improving = rsi > prev_rsi
    rsi_falling = rsi < prev_rsi

    # ---------------- BUY SCORE ----------------
    if bullish_trend:
        score += 35

        if bullish_pullback:
            score += 25

        if 40 <= rsi <= 58:
            score += 20

        if macd_improving:
            score += 15

        if rsi_improving:
            score += 10

        if adx >= 18:
            score += 10

    # ---------------- SELL SCORE ----------------
    elif bearish_trend:
        score -= 35

        if bearish_pullback:
            score -= 25

        if 42 <= rsi <= 60:
            score -= 20

        if macd_falling:
            score -= 15

        if rsi_falling:
            score -= 10

        if adx >= 18:
            score -= 10

    # Avoid weak trend
    if adx < 15:
        return "WAIT", 0, None, None, score, "WAIT: trend is too weak."

    # Avoid overbought BUY
    if bullish_trend and rsi > 70:
        return "WAIT", 0, None, None, score, "WAIT: RSI too high for BUY."

    # Avoid oversold SELL
    if bearish_trend and rsi < 30:
        return "WAIT", 0, None, None, score, "WAIT: RSI too low for SELL."

    # Final BUY
    if (
        bullish_trend
        and bullish_pullback
        and score >= 75
        and 40 <= rsi <= 65
        and macd_improving
        and adx >= 18
    ):
        signal = "BUY"
        confidence = min(abs(score), 95)
        stop_loss = round(price - (1.3 * atr), 5)
        take_profit = round(price + (2.0 * atr), 5)
        safety_note = "BUY: bullish pullback setup."

    # Final SELL
    elif (
        bearish_trend
        and bearish_pullback
        and score <= -75
        and 35 <= rsi <= 60
        and macd_falling
        and adx >= 18
    ):
        signal = "SELL"
        confidence = min(abs(score), 95)
        stop_loss = round(price + (1.3 * atr), 5)
        take_profit = round(price - (2.0 * atr), 5)
        safety_note = "SELL: bearish pullback setup."

    else:
        signal = "WAIT"
        confidence = 0
        stop_loss = None
        take_profit = None

    return signal, confidence, stop_loss, take_profit, score, safety_note
