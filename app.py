import streamlit as st 
import plotly.graph_objects as go
import pandas as pd

from analysis import analyse_market


st.set_page_config(
    page_title="Signal Hawk Commodities Bot",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Signal Hawk Commodities Bot")
st.caption("Gold, Platinum and Oil signal bot — BUY / SELL / WAIT")

markets = {
    "Gold": "GC=F",
    "Platinum": "PL=F",
    "WTI Crude Oil": "CL=F",
    "Brent Crude Oil": "BZ=F",
}

market_name = st.selectbox(
    "Market",
    list(markets.keys())
)

market = markets[market_name]

timeframe = st.selectbox(
    "Timeframe",
    [
        "15 Minutes",
        "1 Hour",
        "4 Hours",
    ]
)

st.write(f"Selected market: **{market_name} ({market})**")
st.write(f"Selected timeframe: **{timeframe}**")

analyse_button = st.button("Analyse Market")

if analyse_button:
    with st.spinner("Analysing market..."):
        result = analyse_market(market, timeframe)

    if "error" in result:
        st.error(result["error"])

    else:
        signal = result["Signal"]
        safety_note = result.get("SafetyNote", "")

        st.subheader("Final Signal")

        if signal == "BUY":
            st.success("🟢 BUY")
        elif signal == "SELL":
            st.error("🔴 SELL")
        else:
            st.warning("🟡 WAIT")

        st.info(safety_note)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Confidence", f"{result['Confidence']}%")

        with col2:
            st.metric("Score", result["Score"])

        with col3:
            st.metric("Current Price", result["Price"])

        st.subheader("Trade Levels")

        col4, col5 = st.columns(2)

        with col4:
            st.metric("Stop Loss", result["StopLoss"])

        with col5:
            st.metric("Take Profit", result["TakeProfit"])

        st.subheader("Indicators")

        col6, col7, col8, col9 = st.columns(4)

        with col6:
            st.metric("EMA20", result["EMA20"])
            st.metric("EMA50", result["EMA50"])

        with col7:
            st.metric("EMA200", result["EMA200"])
            st.metric("RSI", result["RSI"])

        with col8:
            st.metric("MACD", result["MACD"])
            st.metric("ADX", result["ADX"])

        with col9:
            st.metric("ATR", result["ATR"])

        backtest = result["Backtest"]

        st.subheader("Backtest Results")

        col10, col11, col12, col13 = st.columns(4)

        with col10:
            st.metric("Total Trades", backtest["Total Trades"])

        with col11:
            st.metric("Win Rate", f"{backtest['Win Rate']}%")

        with col12:
            st.metric("Wins", backtest["Wins"])

        with col13:
            st.metric("Losses", backtest["Losses"])

        st.metric("Average Points", backtest["Average Points"])

        with st.expander("Recent Backtest Trades"):
            trades = backtest.get("Trades", [])

            if trades:
                st.dataframe(pd.DataFrame(trades), use_container_width=True)
            else:
                st.write("No recent trades.")

        st.subheader("Live Market Chart")

        df = result["Data"].tail(150)

        fig = go.Figure()

        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Price"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA20"],
                mode="lines",
                name="EMA20"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA50"],
                mode="lines",
                name="EMA50"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA200"],
                mode="lines",
                name="EMA200"
            )
        )

        fig.update_layout(
            height=600,
            xaxis_rangeslider_visible=False,
            title=f"{market_name} - {timeframe}"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.warning(
            "This bot gives signals only. It is not financial advice and should not be used for automatic trading."
        )
