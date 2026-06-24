import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------
st.set_page_config(
    page_title="My Stock Tracker",
    page_icon="📈",
    layout="wide"
)

# Auto refresh every 30 seconds
st_autorefresh(interval=30000, key="refresh")

st.title("📈 Real-Time Favourite Stock Tracker")

st.markdown(
    """
Track your favourite stocks in real time.
Examples:

- AAPL (Apple)
- MSFT (Microsoft)
- NVDA (Nvidia)
- DBSDF (DBS OTC)
- D05.SI (DBS Singapore)
- O39.SI (OCBC)
- U11.SI (UOB)
    """
)

# ---------------------------------------
# SIDEBAR
# ---------------------------------------
st.sidebar.header("Favourite Stocks")

default_stocks = [
    "D05.SI",
    "O39.SI",
    "U11.SI",
    "AAPL",
    "MSFT",
    "NVDA"
]

stock_input = st.sidebar.text_area(
    "Enter stock symbols (one per line)",
    value="\n".join(default_stocks),
    height=200
)

tickers = [
    ticker.strip().upper()
    for ticker in stock_input.splitlines()
    if ticker.strip()
]

# ---------------------------------------
# GET STOCK DATA
# ---------------------------------------
@st.cache_data(ttl=30)
def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)

    info = ticker.info

    hist = ticker.history(period="1mo", interval="1d")

    return info, hist

# ---------------------------------------
# SUMMARY TABLE
# ---------------------------------------
summary_rows = []

for ticker in tickers:

    try:
        info, hist = get_stock_data(ticker)

        current_price = info.get("currentPrice")

        previous_close = info.get("previousClose")

        volume = info.get("volume")

        if current_price and previous_close:
            change_pct = (
                (current_price - previous_close)
                / previous_close
            ) * 100
        else:
            change_pct = None

        summary_rows.append(
            {
                "Ticker": ticker,
                "Price": current_price,
                "Change %": round(change_pct, 2)
                if change_pct is not None
                else None,
                "Volume": volume,
            }
        )

    except Exception:
        pass

st.subheader("Market Overview")

if summary_rows:

    df = pd.DataFrame(summary_rows)

    st.dataframe(
        df,
        use_container_width=True
    )

# ---------------------------------------
# CHARTS
# ---------------------------------------
st.subheader("Stock Charts")

for ticker in tickers:

    try:
        info, hist = get_stock_data(ticker)

        st.markdown(f"## {ticker}")

        col1, col2, col3 = st.columns(3)

        price = info.get("currentPrice")

        previous_close = info.get("previousClose")

        market_cap = info.get("marketCap")

        if price and previous_close:
            pct = (
                (price - previous_close)
                / previous_close
            ) * 100
        else:
            pct = 0

        col1.metric(
            "Current Price",
            f"{price}"
        )

        col2.metric(
            "Daily Change",
            f"{pct:.2f}%"
        )

        col3.metric(
            "Market Cap",
            f"{market_cap:,}"
            if market_cap
            else "N/A"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["Close"],
                mode="lines",
                name=ticker
            )
        )

        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:
        st.error(
            f"Unable to load {ticker}: {e}"
        )
