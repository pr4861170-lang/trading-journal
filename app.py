import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# Mobile friendly storage path
DATA_FILE = "my_trading_journal.csv"

st.set_page_config(page_title="Mobile Trading Journal", page_icon="📈", layout="wide")

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "Date", "Market Type", "Asset/Symbol", "Trade Type", 
        "Entry Price", "Stop Loss", "Target Price", "Exit Price", 
        "Quantity", "R:R Ratio", "Gross PnL", "Status", "Notes"
    ])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.title("📈 Mobile Trading Journal")
st.caption("Indian Market, Crypto & Forex")

st.sidebar.header("📥 Log New Trade")
with st.sidebar.form(key="trade_form", clear_on_submit=True):
    trade_date = st.date_input("Date", datetime.now())
    market_type = st.selectbox("Market Type", ["Indian Market", "Crypto", "Forex"])
    asset_name = st.text_input("Asset / Symbol", placeholder="e.g., NIFTY, BTC, EURUSD")
    trade_type = st.radio("Trade Type", ["BUY", "SELL"], horizontal=True)
    
    entry_price = st.number_input("Entry Price", min_value=0.0, format="%.4f")
    sl_price = st.number_input("Stop Loss (SL)", min_value=0.0, format="%.4f")
    target_price = st.number_input("Target Price", min_value=0.0, format="%.4f")
    exit_price = st.number_input("Exit Price", min_value=0.0, format="%.4f")
    qty = st.number_input("Quantity / Lots", min_value=0.0, format="%.4f")
    
    status = st.selectbox("Status", ["OPEN", "TARGET HIT", "SL HIT", "MANUAL EXIT"])
    notes = st.text_area("Notes")
    submit_button = st.form_submit_button(label="🚀 Save Trade")

if submit_button:
    if asset_name and entry_price > 0 and qty > 0:
        risk = abs(entry_price - sl_price)
        reward = abs(target_price - entry_price)
        rr_ratio = round(reward / risk, 2) if risk > 0 else 0.0
        
        if status == "OPEN":
            pnl = 0.0
        else:
            pnl = (exit_price - entry_price) * qty if trade_type == "BUY" else (entry_price - exit_price) * qty
        
        new_trade = {
            "Date": trade_date.strftime("%Y-%m-%d"), "Market Type": market_type,
            "Asset/Symbol": asset_name.upper(), "Trade Type": trade_type,
            "Entry Price": entry_price, "Stop Loss": sl_price, "Target Price": target_price,
            "Exit Price": exit_price, "Quantity": qty, "R:R Ratio": rr_ratio,
            "Gross PnL": round(pnl, 2), "Status": status, "Notes": notes
        }
        current_df = load_data()
        current_df = pd.concat([current_df, pd.DataFrame([new_trade])], ignore_index=True)
        save_data(current_df)
        st.sidebar.success("Trade Saved! 🎉")
    else:
        st.sidebar.error("Fill Symbol, Entry, and Qty.")

df_journal = load_data()
if not df_journal.empty:
    st.header("📊 Performance")
    col1, col2 = st.columns(2)
    col1.metric("Total Trades", len(df_journal))
    col2.metric("Total PnL", f"₹/{round(df_journal['Gross PnL'].sum(), 2)}")
    
    st.write("---")
    st.header("📜 History")
    market_filter = st.selectbox("Filter", ["All", "Indian Market", "Crypto", "Forex"])
    filtered_df = df_journal if market_filter == "All" else df_journal[df_journal["Market Type"] == market_filter]
    st.dataframe(filtered_df.sort_index(ascending=False), use_container_width=True)
    
    if st.button("⚠️ Clear Data"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.rerun()
else:
    st.info("Journal is empty. Use sidebar to add trades!")
