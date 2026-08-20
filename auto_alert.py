from analysis import analyse_market
from telegram_alert import send_telegram_alert


MARKETS = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Platinum": "PL=F",
}


def check_market(market_name, pair):
    print(f"Checking {market_name}...")

    results = {}

    for timeframe in ["15 Minutes", "1 Hour", "4 Hours"]:
        result = analyse_market(pair, timeframe)

        if "error" in result:
            print(f"{market_name} {timeframe} error: {result['error']}")
            return

        results[timeframe] = result

    r15 = results["15 Minutes"]
    r1h = results["1 Hour"]
    r4h = results["4 Hours"]

    s15 = r15.get("Signal", "WAIT")
    s1h = r1h.get("Signal", "WAIT")
    s4h = r4h.get("Signal", "WAIT")

    c15 = int(r15.get("Confidence", 0))
    c1h = int(r1h.get("Confidence", 0))
    c4h = int(r4h.get("Confidence", 0))

    final_confidence = min(c15, c1h, c4h)
    current_price = r4h.get("Price", "-")
    stop_loss = r4h.get("StopLoss", "-")
    take_profit = r4h.get("TakeProfit", "-")

    print(f"{market_name}: 15m={s15}, 1h={s1h}, 4h={s4h}")

    if s15 == "BUY" and s1h == "BUY" and s4h == "BUY":
        message = f"""
🚨 <b>Signal Hawk Commodities Alert</b>

Market: <b>{market_name}</b>
Signal: <b>STRONG BUY</b>

15m: {s15} ({c15}%)
1h: {s1h} ({c1h}%)
4h: {s4h} ({c4h}%)

Final Confidence: {final_confidence}%
Current Price: {current_price}
Stop Loss: {stop_loss}
Take Profit: {take_profit}

Platform: BullionVault
Mode: Test / paper trading first
"""

        sent, response = send_telegram_alert(message)

        if sent:
            print(f"Telegram STRONG BUY alert sent for {market_name}")
        else:
            print(f"Telegram failed for {market_name}: {response}")

    else:
        print(f"No STRONG BUY for {market_name}")


def main():
    for market_name, pair in MARKETS.items():
        check_market(market_name, pair)


if __name__ == "__main__":
    main()
