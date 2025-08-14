
import json
import time
from typing import List
import pandas as pd
import streamlit as st

from tracker.api import top_market_coins, simple_price
from tracker.alert import AlertRule, send_email
from tracker.config import settings
from tracker.utils import fmt_currency, safe_get

st.set_page_config(page_title="Crypto Price Tracker", page_icon="📈")

# --- SIDEBAR ---
st.sidebar.title("⚙️ Settings")
vs = st.sidebar.selectbox("Quote currency", ["usd", "inr", "eur"], index=0)
refresh = st.sidebar.slider("Auto-refresh (seconds)", 15, 180, settings.refresh_sec, step=15)
st.sidebar.caption("CoinGecko has free rate-limits. Keep refresh sensible.")

st.sidebar.divider()
st.sidebar.write("📧 Email Alerts (optional). Configure .env or Streamlit secrets.")
if settings.smtp_user:
    st.sidebar.success(f"Email sender: {settings.smtp_user}")
else:
    st.sidebar.info("Email not configured (optional).")

# Keep state
if "rules" not in st.session_state:
    st.session_state.rules: List[AlertRule] = []

# --- HEADER ---
st.title("📈 Crypto Price Tracker & Alerts")
st.caption("Top coins by market cap. Set alert rules and get in-app toasts (and optional email).")

# Fetch coin markets
with st.spinner("Fetching market data…"):
    try:
        coins = top_market_coins(vs=vs, per_page=settings.top_n)
    except Exception as e:
        st.error(f"Failed to fetch markets: {e}")
        coins = []

if coins:
    df = pd.DataFrame([{
        "id": c["id"],
        "symbol": c["symbol"].upper(),
        "name": c["name"],
        "price": c.get("current_price"),
        "24h %": c.get("price_change_percentage_24h"),
        "mcap": c.get("market_cap"),
        "vol": c.get("total_volume"),
    } for c in coins])

    st.dataframe(df.set_index("symbol"), use_container_width=True)

# --- ALERT BUILDER ---
st.subheader("🔔 Create Alert")
col1, col2 = st.columns([2,1])
with col1:
    coin_options = {f'{c["name"]} ({c["symbol"].upper()})': c["id"] for c in coins}
    choice = st.selectbox("Select coin", list(coin_options.keys())) if coins else None
with col2:
    op = st.selectbox("Condition", [">=", "<="], index=0)

threshold = st.number_input(f"Threshold price ({vs.upper()})", min_value=0.0, value=0.0, step=0.1, format="%.4f")
email_flag = st.checkbox("Also send email (optional)")

if st.button("➕ Add Alert") and choice:
    coin_id = coin_options[choice]
    coin_symbol = choice.split("(")[-1].replace(")", "").lower()
    rule = AlertRule(coin_id=coin_id, coin_symbol=coin_symbol, op=op, threshold=threshold, vs=vs, email=email_flag)
    st.session_state.rules.append(rule)
    st.success(f"Added alert: {coin_symbol} {op} {threshold} {vs.upper()}")

# Show active rules
if st.session_state.rules:
    st.subheader("📜 Active Alerts")
    rules_df = pd.DataFrame([r.__dict__ for r in st.session_state.rules])
    st.dataframe(rules_df, use_container_width=True)

# --- POLLING LOOP (single tick per page refresh) ---
st.divider()
st.subheader("⏱️ Live Monitor")
st.write(f"Auto-refresh every **{refresh}s**. Leave the page open.")

# Only poll when we have rules
if st.session_state.rules:
    ids = list({r.coin_id for r in st.session_state.rules})
    try:
        prices = simple_price(ids, vs=vs)
    except Exception as e:
        st.error(f"Failed to fetch prices: {e}")
        prices = {}

    for r in st.session_state.rules:
        price = safe_get(prices, r.coin_id, vs, default=None)
        if price is None:
            continue
        if r.triggered(price):
            msg = f"{r.coin_symbol.upper()} {r.op} {fmt_currency(r.threshold, symbol='$' if vs=='usd' else '')} — current: {fmt_currency(price, symbol='$' if vs=='usd' else '')}"
            st.toast(f"🔔 Alert hit: {msg}", icon="🔔")
            if r.email:
                err = send_email(subject=f"Crypto Alert: {r.coin_symbol.upper()} {r.op} {r.threshold} {vs.upper()}",
                                 body=f"Rule: {r.coin_symbol.upper()} {r.op} {r.threshold} {vs.upper()}\nCurrent price: {price} {vs.upper()}")
                if err:
                    st.warning(f"Email failed: {err}")
                else:
                    st.info("Email sent ✅")

# Auto refresh hint (Streamlit refresh handled by user interactions/slider)
st.caption("Tip: Adjust refresh from sidebar. Keep tab open for alerts.")
