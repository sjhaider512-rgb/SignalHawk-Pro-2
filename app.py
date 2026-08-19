import streamlit as st 
import plotly.graph_objects as go

from analysis import analyse_market
from telegram_alert import send_telegram_alert


st.set_page_config(
    page_title="Signal Hawk Commodities Bot",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Signal Hawk Commodities Bot")
st.write("Gold and Platinum signal bot — BUY / SELL / WAIT")

market_options = {
    "Gold": "GC=F",
    "Platinum": "PL=F",
}

market_name = st.selectbox(
    "Market",
    list(market_options.keys()),
)

mode = st.selectbox(
    "Signal Mode",
    [
        "Strong Signal: 15m + 1h + 4h",
        "Single Timeframe",
    ],
)

if mode == "Single Timeframe":
    timeframe = st.selectbox(
        "Timeframe",
        [
            "15 Minutes",
            "1 Hour",
            "4 Hours",
            "1 Day",
        ],
    )
else:
    timeframe = "Strong Signal: 15m + 1h + 4h"

pair = market_options[market_name]

st.write(f"Selected market: **{market_name} ({pair})**")
st.write(f"Selected mode: **{mode}**")


def show_chart(result, title):
    df = result.get("Data")

    if df is None or df.empty:
        return

    chart_df = df.tail(150)

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["open"],
            high=chart_df["high"],
            low=chart_df["low"],
            close=chart_df["close"],
            name="Price",
        )
    )

    if "EMA20" in chart_df.columns:
        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["EMA20"],
                name="EMA20",
                mode="lines",
            )
        )

    if "EMA50" in chart_df.columns:
        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["EMA50"],
                name="EMA50",
                mode="lines",
            )
        )

    if "EMA200" in chart_df.columns:
        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["EMA200"],
                name="EMA200",
                mode="lines",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Price",
        height=600,
        xaxis_rangeslider_visible=False,
    )

    st.plotly_chart(fig, use_container_width=True)


def display_single_result(result):
    signal = result.get("Signal", "WAIT")
    confidence = result.get("Confidence", 0)
    score = result.get("Score", 0)
    price = result.get("Price", "-")
    safety_note = result.get("SafetyNote", "")

    st.subheader("Final Signal")

    if signal == "BUY":
        st.success("🟢 BUY")
    elif signal == "SELL":
        st.error("🔴 SELL")
    else:
        st.warning("🟡 WAIT")

    if safety_note:
        st.info(safety_note)

    col1, col2, col3 = st.columns(3)
    col1.metric("Confidence", f"{confidence}%")
    col2.metric("Score", score)
    col3.metric("Current Price", price)

    st.subheader("Trade Levels")

    col1, col2 = st.columns(2)
    col1.metric("Stop Loss", result.get("StopLoss") or "—")
    col2.metric("Take Profit", result.get("TakeProfit") or "—")

    st.subheader("Indicators")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("EMA20", result.get("EMA20", "-"))
    col1.metric("EMA50", result.get("EMA50", "-"))

    col2.metric("EMA200", result.get("EMA200", "-"))
    col2.metric("RSI", result.get("RSI", "-"))

    col3.metric("MACD", result.get("MACD", "-"))
    col3.metric("ADX", result.get("ADX", "-"))

    col4.metric("ATR", result.get("ATR", "-"))

    st.subheader("Backtest Results")

    backtest = result.get("Backtest", {})

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Trades", backtest.get("Total Trades", 0))
    col2.metric("Win Rate", f"{backtest.get('Win Rate', 0)}%")
    col3.metric("Wins", backtest.get("Wins", 0))
    col4.metric("Losses", backtest.get("Losses", 0))

    st.metric("Average Points", backtest.get("Average Points", 0))

    with st.expander("Recent Backtest Trades"):
        st.write(backtest.get("Trades", []))


def display_strong_result(results):
    r15 = results["15 Minutes"]
    r1h = results["1 Hour"]
    r4h = results["4 Hours"]

    signals = [
        r15.get("Signal", "WAIT"),
        r1h.get("Signal", "WAIT"),
        r4h.get("Signal", "WAIT"),
    ]

    confidences = [
        int(r15.get("Confidence", 0)),
        int(r1h.get("Confidence", 0)),
        int(r4h.get("Confidence", 0)),
    ]

    scores = [
        int(r15.get("Score", 0)),
        int(r1h.get("Score", 0)),
        int(r4h.get("Score", 0)),
    ]

    strong_signal = "WAIT"
    note = "No full agreement between 15m, 1h and 4h."

    if signals == ["BUY", "BUY", "BUY"]:
        strong_signal = "STRONG BUY"
        note = "15m + 1h + 4h all show BUY."
    elif signals == ["SELL", "SELL", "SELL"]:
        strong_signal = "STRONG SELL"
        note = "15m + 1h + 4h all show SELL."

    final_confidence = min(confidences)
    final_score = sum(scores)

    main_result = r4h

    st.subheader("Final Strong Signal")

    if strong_signal == "STRONG BUY":
        st.success("🟢 STRONG BUY")
    elif strong_signal == "STRONG SELL":
        st.error("🔴 STRONG SELL")
    else:
        st.warning("🟡 WAIT / MIXED")

    st.info(note)
    st.warning("TEST MODE: use this for demo or paper testing only.")

    if strong_signal in ["STRONG BUY", "STRONG SELL"]:
        telegram_message = f"""
🚨 Signal Hawk Commodities Alert

Market: {market_name}
Signal: {strong_signal}
Confidence: {final_confidence}%
Current Price: {main_result.get("Price", "-")}
Stop Loss: {main_result.get("StopLoss", "-")}
Take Profit: {main_result.get("TakeProfit", "-")}

15m: {r15.get("Signal", "WAIT")}
1h: {r1h.get("Signal", "WAIT")}
4h: {r4h.get("Signal", "WAIT")}

Mode: Test / paper trading only
"""

        if st.button("Send Telegram Alert"):
            sent, message = send_telegram_alert(telegram_message)

            if sent:
                st.success("Telegram alert sent.")
            else:
                st.error(f"Telegram alert failed: {message}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Final Confidence", f"{final_confidence}%")
    col2.metric("Combined Score", final_score)
    col3.metric("Current Price", main_result.get("Price", "-"))

    st.subheader("Timeframe Confirmation")

    col1, col2, col3 = st.columns(3)

    col1.metric("15 Minutes", r15.get("Signal", "WAIT"), f"{r15.get('Confidence', 0)}%")
    col2.metric("1 Hour", r1h.get("Signal", "WAIT"), f"{r1h.get('Confidence', 0)}%")
    col3.metric("4 Hours", r4h.get("Signal", "WAIT"), f"{r4h.get('Confidence', 0)}%")

    st.subheader("Trade Levels")

    col1, col2 = st.columns(2)

    if strong_signal in ["STRONG BUY", "STRONG SELL"]:
        col1.metric("Stop Loss", main_result.get("StopLoss") or "—")
        col2.metric("Take Profit", main_result.get("TakeProfit") or "—")
    else:
        col1.metric("Stop Loss", "—")
        col2.metric("Take Profit", "—")

    st.subheader("Indicators from 4H")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("EMA20", main_result.get("EMA20", "-"))
    col1.metric("EMA50", main_result.get("EMA50", "-"))

    col2.metric("EMA200", main_result.get("EMA200", "-"))
    col2.metric("RSI", main_result.get("RSI", "-"))

    col3.metric("MACD", main_result.get("MACD", "-"))
    col3.metric("ADX", main_result.get("ADX", "-"))

    col4.metric("ATR", main_result.get("ATR", "-"))

    st.subheader("Backtest Results from 4H")

    backtest = main_result.get("Backtest", {})

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Trades", backtest.get("Total Trades", 0))
    col2.metric("Win Rate", f"{backtest.get('Win Rate', 0)}%")
    col3.metric("Wins", backtest.get("Wins", 0))
    col4.metric("Losses", backtest.get("Losses", 0))

    st.metric("Average Points", backtest.get("Average Points", 0))

    with st.expander("Recent Backtest Trades"):
        st.write(backtest.get("Trades", []))

    st.subheader("Live Market Chart")
    show_chart(main_result, f"{market_name} - 4 Hours")


if st.button("Analyse Market"):
    with st.spinner("Analysing market..."):

        if mode == "Strong Signal: 15m + 1h + 4h":
            results = {}

            for tf in ["15 Minutes", "1 Hour", "4 Hours"]:
                result = analyse_market(pair, tf)

                if "error" in result:
                    st.error(f"{tf}: {result['error']}")
                    st.stop()

                results[tf] = result

            display_strong_result(results)

        else:
            result = analyse_market(pair, timeframe)

            if "error" in result:
                st.error(result["error"])
                st.stop()

            display_single_result(result)

            st.subheader("Live Market Chart")
            show_chart(result, f"{market_name} - {timeframe}")

st.warning(
    "This bot gives signals only. It is not financial advice and should not be used for automatic trading."
)
