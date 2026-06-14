import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration for Premium Look
st.set_page_config(page_title="Siddhant's Trading Journal", page_icon="📈", layout="wide")

# Custom CSS for Premium Telegram-like UI
st.markdown("""
<style>
    .main { background-color: #0e1621; color: #ffffff; }
    .trade-card {
        background-color: #17212b;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 6px solid #5288c1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .profit-card { border-left: 6px solid #4caf50; background-color: #1c2e24; }
    .loss-card { border-left: 6px solid #f44336; background-color: #321e1e; }
    .status-badge {
        background-color: #243141;
        color: #5288c1;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .metric-box {
        background-color: #17212b;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #243141;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Siddhant's Premium Journal")
st.caption("Your Ultimate Indian, Crypto & Forex Analytics Hub")

# Google Sheets Connection Setup
try:
    if "gsheets" in st.secrets:
        sheet_url = st.secrets["gsheets"]["public_sheet_url"]
        # Convert share link to direct CSV link
        csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv").replace("/edit", "/export?format=csv")
        df_journal = pd.read_csv(csv_url)
    else:
        df_journal = pd.DataFrame()
except Exception as e:
    df_journal = pd.DataFrame()
    st.error("Google Sheets कनेक्ट करने में समस्या आ रही है। कृपया Secrets चेक करें।")

# Sidebar Form (For Input)
st.sidebar.header("📥 Add New Trade")
with st.sidebar.form(key="trade_form", clear_on_submit=True):
    trade_date = st.date_input("Date", datetime.now())
    market_type = st.selectbox("Market Type", ["Indian Market", "Crypto", "Forex"])
    asset_name = st.text_input("Asset / Symbol", placeholder="e.g., NIFTY, BTC, EURUSD")
    trade_type = st.radio("Trade Type", ["BUY", "SELL"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        entry_price = st.number_input("Entry", min_value=0.0, format="%.4f")
        sl_price = st.number_input("Stop Loss", min_value=0.0, format="%.4f")
    with col2:
        target_price = st.number_input("Target", min_value=0.0, format="%.4f")
        exit_price = st.number_input("Exit Price", min_value=0.0, format="%.4f")
        
    qty = st.number_input("Quantity / Lots", min_value=0.0, format="%.4f")
    status = st.selectbox("Status", ["OPEN", "TARGET HIT", "SL HIT", "MANUAL EXIT"])
    notes = st.text_area("Notes / Strategy Details")
    
    submit_button = st.form_submit_button(label="🚀 Save to Sheet")

# Dashboard Metrics
if not df_journal.empty and "Date" in df_journal.columns:
    # Basic Calculations
    df_journal['Gross PnL'] = pd.to_numeric(df_journal['Gross PnL'], errors='coerce').fillna(0)
    total_trades = len(df_journal)
    net_pnl = df_journal['Gross PnL'].sum()
    
    # Premium Analytics Row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"<div class='metric-box'><p style='color:#aaa;margin:0;'>Total Trades</p><h2 style='margin:5px 0;'>{total_trades}</h2></div>", unsafe_allow_html=True)
    with m2:
        pnl_color = "#4caf50" if net_pnl >= 0 else "#f44336"
        st.markdown(f"<div class='metric-box'><p style='color:#aaa;margin:0;'>Net Profit / Loss</p><h2 style='color:{pnl_color};margin:5px 0;'>₹ {net_pnl:,.2nd}</h2></div>", unsafe_allow_html=True)
    with m3:
        closed = df_journal[df_journal["Status"] != "OPEN"]
        wins = len(closed[closed["Gross PnL"] > 0])
        win_rate = round((wins / len(closed)) * 100, 2) if len(closed) > 0 else 0
        st.markdown(f"<div class='metric-box'><p style='color:#aaa;margin:0;'>Win Rate</p><h2 style='color:#5288c1;margin:5px 0;'>{win_rate}%</h2></div>", unsafe_allow_html=True)

    st.write("---")
    st.header("📜 Live Feed (Telegram Style)")

    # Filter Box
    market_filter = st.selectbox("Filter Feed", ["All Markets", "Indian Market", "Crypto", "Forex"])
    
    # Loop through trades to display as Beautiful Cards
    for idx, row in df_journal.iloc[::-1].iterrows(): # Show latest first
        if market_filter != "All Markets" and row['Market Type'] != market_filter:
            continue
            
        pnl_val = row['Gross PnL']
        card_class = "trade-card"
        pnl_text = f"⏳ Open Trade"
        
        if row['Status'] != "OPEN":
            if pnl_val >= 0:
                card_class = "trade-card profit-card"
                pnl_text = f"🟢 Profit: +₹{pnl_val:,.2f}"
            else:
                card_class = "trade-card loss-card"
                pnl_text = f"🔴 Loss: -₹{abs(pnl_val):,.2f}"

        # HTML Card Structure
        card_html = f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <b style="font-size: 18px; color: #fff;">{row['Asset/Symbol']} ({row['Trade Type']})</b>
                <span class="status-badge">{row['Market Type']} | {row['Status']}</span>
            </div>
            <p style="margin: 5px 0; color: #b2b2b2; font-size: 13px;">📅 Date: {row['Date']}</p>
            <div style="display: flex; gap: 20px; margin: 10px 0; font-size: 14px;">
                <div><b>Entry:</b> {row['Entry Price']}</div>
                <div><b>SL:</b> {row['Stop Loss']}</div>
                <div><b>Target:</b> {row['Target Price']}</div>
                <div><b>Exit:</b> {row['Exit Price'] if row['Status'] != 'OPEN' else '-'}</div>
                <div><b>R:R:</b> {row['R:R Ratio']}</div>
            </div>
            <div style="font-size: 16px; font-weight: bold; margin-top: 5px;">{pnl_text}</div>
            {f'<div style="margin-top:8px; font-style: italic; color:#aaa; font-size:13px;">📝 {row["Notes"]}</div>' if pd.notna(row['Notes']) else ''}
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
else:
    st.info("⚠️ अपनी Google Sheet को Streamlit से जोड़ने के लिए Secrets सेट करें ताकि आपका प्रीमियम फीड चालू हो सके।")
      
