from strategy import generate_signal 


def run_backtest(df, max_hold_candles=10, max_backtest_candles=700):
    """
    Fast backtest for Signal Hawk Commodities Bot.
    """

    trades = []

    if df is None or df.empty:
        return empty_result()

    if len(df) > max_backtest_candles:
        df = df.tail(max_backtest_candles).copy()

    if len(df) < 220:
        return empty_result()

    start_index = 200

    for i in range(start_index, len(df) - max_hold_candles - 1):
        history = df.iloc[:i + 1].copy()

        result = generate_signal(history)

        if len(result) == 6:
            signal, confidence, stop_loss, take_profit, score, safety_note = result
        elif len(result) == 5:
            signal, confidence, stop_loss, take_profit, score = result
        else:
            continue

        if signal not in ["BUY", "SELL"]:
            continue

        if stop_loss is None or take_profit is None:
            continue

        entry_price = float(df["close"].iloc[i])
        exit_price = float(df["close"].iloc[i + max_hold_candles])
        exit_candle = i + max_hold_candles
        outcome = "LOSS"

        for j in range(i + 1, i + max_hold_candles + 1):
            high = float(df["high"].iloc[j])
            low = float(df["low"].iloc[j])

            if signal == "BUY":
                if low <= stop_loss:
                    exit_price = stop_loss
                    exit_candle = j
                    outcome = "LOSS"
                    break

                if high >= take_profit:
                    exit_price = take_profit
                    exit_candle = j
                    outcome = "WIN"
                    break

            elif signal == "SELL":
                if high >= stop_loss:
                    exit_price = stop_loss
                    exit_candle = j
                    outcome = "LOSS"
                    break

                if low <= take_profit:
                    exit_price = take_profit
                    exit_candle = j
                    outcome = "WIN"
                    break

        if signal == "BUY":
            points = exit_price - entry_price
        else:
            points = entry_price - exit_price

        trades.append({
            "Signal": signal,
            "Entry": round(entry_price, 5),
            "Exit": round(exit_price, 5),
            "Stop Loss": round(float(stop_loss), 5),
            "Take Profit": round(float(take_profit), 5),
            "Confidence": confidence,
            "Score": score,
            "Result": outcome,
            "Points": round(points, 5),
            "Entry Candle": i,
            "Exit Candle": exit_candle
        })

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
