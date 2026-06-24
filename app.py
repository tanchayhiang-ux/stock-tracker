import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(
    page_title="SGX Stock Tracker",
    page_icon="📈",
    layout="wide"
)

st.title("📈 My SGX Stock Tracker")

# SGX Stocks
stocks = {
    "D05.SI": "DBS Group",
    "O39.SI": "OCBC Bank",
    "U11.SI": "UOB Bank",
    "BN4.SI": "Keppel Ltd",
    "9CI.SI": "CapitaLand Investment",
    "C38U.SI": "CapitaLand Integrated Commercial Trust",
    "G07.SI": "Great Eastern Holdings",
    "U10.SI": "UOB Kay Hian",
    "Z74.SI": "Singtel"
}

st.sidebar.header("Settings")

selected = st.sidebar.multiselect(
    "Select Stocks",
    options=list(stocks.keys()),
    default=list(stocks.keys())
)

if st.button("🔄 Refresh Prices"):
    st.rerun()

rows = []

for ticker in selected:
    try:
        stock = yf.Ticker(ticker)

        info = stock.info

        current_price = info.get("currentPrice")
        previous_close = info.get("previousClose")

        if current_price and previous_close:
            change = current_price - previous_close
            change_pct = (change / previous_close) * 100
        else:
            change = None
            change_pct = None

        rows.append({
            "Symbol": ticker,
            "Company": stocks[ticker],
            "Price (S$)": current_price,
            "Previous Close": previous_close,
            "Change": round(change, 3) if change else None,
            "Change %": round(change_pct, 2) if change_pct else None
        })

    except:
        pass

df = pd.DataFrame(rows)

st.subheader("Live Stock Prices")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("Price Charts")

for ticker in selected:

    st.markdown(
        f"### {stocks[ticker]} ({ticker})"
    )

    try:
        hist = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False
        )

        if not hist.empty:
            st.line_chart(hist["Close"])

    except:
        st.error(f"Unable to load {ticker}")
