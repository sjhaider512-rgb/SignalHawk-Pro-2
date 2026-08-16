from strategy import generate_signal


def empty_result():
    return {
        "Total Trades": 0,
        "BUY Trades": 0,
        "SELL Trades": 0,
        "Wins": 0,
        "Losses": 0,
        "Win Rate": 0,
        "Average Points": 0,
        "Trades": []
    }


def run_backtest(df, max_hold_candles=12, max_backtest_candles=700):
    """
    Improved backtest:
    - Only tests real BUY/SELL signals
    - Uses stop loss and take profit properly
    - Checks candle high/low after entry
    - Avoids double-counting overlapping trades
    """

    if df is None or df.empty:
        return empty_result()

    if len(df) > max_backtest_candles:
        df = df.tail(max_backtest_candles).copy()

    if len(df) < 220:
        return empty_result()

    trades = []
    i = 220

    while i < len(df) - max_hold_candles - 1:
        history = df.iloc[:i + 1].copy()
        result = generate_signal(history)

        if len(result) == 6:
            signal, confidence, stop_loss, take_profit, score, safety_note = result
        else:
            i += 1
            continue

        if signal not in ["BUY", "SELL"]:
            i += 1
            continue

        if stop_loss is None or take_profit is None:
            i += 1
            continue

        entry_price = float(df["close"].iloc[i])
        stop_loss = float(stop_loss)
        take_profit = float(take_profit)

        outcome = "LOSS"
        exit_price = float(df["close"].iloc[i + max_hold_candles])
        exit_candle = i + max_hold_candles

        for j in range(i + 1, i + max_hold_candles + 1):
            high = float(df["high"].iloc[j])
            low = float(df["low"].iloc[j])

            if signal == "BUY":
                if low <= stop_loss:
                    exit_price = stop_loss
                    outcome = "LOSS"
                    exit_candle = j
                    break

                if high >= take_profit:
                    exit_price = take_profit
                    outcome = "WIN"
                    exit_candle = j
                    break

            elif signal == "SELL":
                if high >= stop_loss:
                    exit_price = stop_loss
                    outcome = "LOSS"
                    exit_candle = j
                    break

                if low <= take_profit:
                    exit_price = take_profit
                    outcome = "WIN"
                    exit_candle = j
                    break

        if signal == "BUY":
            points = exit_price - entry_price
        else:
            points = entry_price - exit_price

        trades.append({
            "Signal": signal,
            "Entry": round(entry_price, 5),
            "Exit": round(exit_price, 5),
            "Stop Loss": round(stop_loss, 5),
            "Take Profit": round(take_profit, 5),
            "Confidence": confidence,
            "Score": score,
            "Result": outcome,
            "Points": round(points, 5),
            "Entry Candle": i,
            "Exit Candle": exit_candle
        })

        # Skip forward after trade closes to avoid overlapping trades
        i = exit_candle + 1

    total_trades = len(trades)
    buy_trades = len([t for t in trades if t["Signal"] == "BUY"])
    sell_trades = len([t for t in trades if t["Signal"] == "SELL"])
    wins = len([t for t in trades if t["Result"] == "WIN"])
    losses = len([t for t in trades if t["Result"] == "LOSS"])

    if total_trades > 0:
        win_rate = round((wins / total_trades) * 100, 2)
        average_points = round(sum(t["Points"] for t in trades) / total_trades, 5)
    else:
        win_rate = 0
        average_points = 0

    return {
        "Total Trades": total_trades,
        "BUY Trades": buy_trades,
        "SELL Trades": sell_trades,
        "Wins": wins,
        "Losses": losses,
        "Win Rate": win_rate,
        "Average Points": average_points,
        "Trades": trades[-20:]
    }
