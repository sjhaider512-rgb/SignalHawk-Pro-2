import streamlit as st 
import plotly.graph_objects as go

from analysis import analyse_market


st.set_page_config(
    page_title="Signal Hawk Pro",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Signal Hawk Pro")

market = st.selectbox(
    "Market",
    [
        "GC=F",
                
    ]
)

timeframe = st.selectbox(
    "Timeframe",
    [
        "1 Minute",
        "5 Minutes",
        "15 Minutes",
        "1 Hour",
        "4 Hours",
        "1 Day",
    ],
    index=3
)

if st.button("Analyse Market"):
    with st.spinner("Analysing..."):
        result = analyse_market(market, timeframe)

    if result is None:
        st.error("No data returned.")
        st.stop()

    if "error" in result:
        st.error(result["error"])
        st.stop()

    signal = result.get("Signal", "WAIT")

    if signal == "BUY":
        st.success(f"Signal: {signal}")
    elif signal == "SELL":
        st.error(f"Signal: {signal}")
    else:
        st.warning(f"Signal: {signal}")

    safety_note = result.get("SafetyNote", "")
    if safety_note:
        if signal == "WAIT":
            st.warning(safety_note)
        else:
            st.info(safety_note)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Confidence", f"{result.get('Confidence', 0)} %")

    with col2:
        st.metric("Score", result.get("Score", "N/A"))

    with col3:
        st.metric("Current Price", result.get("Price", "N/A"))

    st.subheader("Indicators")

    st.write(f"EMA20 : {result.get('EMA20')}")
    st.write(f"EMA50 : {result.get('EMA50')}")
    st.write(f"EMA200 : {result.get('EMA200')}")
    st.write(f"RSI : {result.get('RSI')}")
    st.write(f"MACD : {result.get('MACD')}")
    st.write(f"ADX : {result.get('ADX')}")
    st.write(f"ATR : {result.get('ATR')}")

    st.subheader("Trade Levels")

    st.write(f"Stop Loss : {result.get('StopLoss')}")
    st.write(f"Take Profit : {result.get('TakeProfit')}")

    st.subheader("Backtest Results")

    backtest = result.get("Backtest", {})

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        st.metric("Total Trades", backtest.get("Total Trades", 0))

    with b2:
        st.metric("Win Rate", f"{backtest.get('Win Rate', 0)} %")

    with b3:
        st.metric("Wins", backtest.get("Wins", 0))

    with b4:
        st.metric("Losses", backtest.get("Losses", 0))

    st.metric("Average Points", backtest.get("Average Points", 0))

    with st.expander("Recent Backtest Trades"):
        st.write(backtest.get("Trades", []))

    df = result.get("Data")

    if df is not None and not df.empty:
        st.subheader("📊 Live Market Chart")

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
            height=700,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, width="stretch")
