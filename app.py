import streamlit as st 
from analysis import analyse_market
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Signal Hawk Pro",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Signal Hawk Pro")

market = st.selectbox( 
    "Market",
    [
        "XAUUSD", # Gold
        "XAGUSD", # Silver
        "XPTUSD", # Platinum
        "XPDUSD", # Palladium
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
        "1 Day"
    ]
)

if st.button("Analyse Market"):

   with st.spinner("Analysing..."): 

    symbol_map = {
        "XAUUSD": "GC=F",
        "XAGUSD": "SI=F",
        "XPTUSD": "PL=F",
        "XPDUSD": "PA=F"
    }

    market = symbol_map.get(market, market)

    result = analyse_market(market, timeframe)

    if result is None:
        st.error("No data returned.")
        st.stop()

    if "error" in result:
        st.error(result["error"])
        st.stop()

    st.success(f"Signal: {result['Signal']}")

    col1, col2, col3 = st.columns(3) 

    with col1:
        st.metric("Confidence", f"{result['Confidence']} %")

    with col2:
        st.metric("Score", result.get("Score", "N/A"))

    with col3:
        st.metric("Current Price", result["Price"])

    st.subheader("Indicators")

    st.write(f"EMA20 : {result['EMA20']}")
    st.write(f"EMA50 : {result['EMA50']}")
    st.write(f"EMA200 : {result['EMA200']}")
    st.write(f"RSI : {result['RSI']}")
    st.write(f"MACD : {result['MACD']}")
    st.write(f"ADX : {result['ADX']}")
    st.write(f"ATR : {result['ATR']}")

    st.subheader("Trade Levels")

    st.write(f"Stop Loss : {result['StopLoss']}")
    st.write(f"Take Profit : {result['TakeProfit']}")

    df = result["Data"].copy()

    # Rename back for Plotly
    df["Open"] = df["open"]
    df["High"] = df["high"]
    df["Low"] = df["low"]
    df["Close"] = df["close"]

    st.subheader("📊 Live Market Chart")

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.60, 0.20, 0.20]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["EMA20"],
            name="EMA20"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["EMA50"],
            name="EMA50"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["EMA200"],
            name="EMA200"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["RSI"],
            name="RSI"
        ),
        row=2,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["MACD"],
            name="MACD"
        ),
        row=3,
        col=1
    )

    fig.update_layout(
        height=900,
        template="plotly_dark",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)
