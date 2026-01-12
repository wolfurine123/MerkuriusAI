import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from PIL import Image
import pandas as pd
import numpy as np

# --- 1. CONFIG ---
try:
    img = Image.open("icon.png")
    st.set_page_config(page_title="Merkurius AI", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="Merkurius AI", layout="centered")

# --- 2. DEMO DATA GENERATOR (Om Yahoo sviker) ---
def get_demo_data():
    dates = pd.date_range(start="2023-01-01", periods=180)
    df = pd.DataFrame({
        'Open': np.random.uniform(100, 150, 180),
        'High': np.random.uniform(150, 200, 180),
        'Low': np.random.uniform(50, 100, 180),
        'Close': np.random.uniform(100, 150, 180)
    }, index=dates)
    info = {
        'currentPrice': 142.5, 'currency': 'USD', 'trailingPE': 18.4,
        'marketCap': 2500000000, 'longBusinessSummary': "DEMO MODE: Yahoo Finance is currently rate-limiting requests. This is a preview of how Merkurius AI analyzes and visualizes market moats and financial health once the data stream is active."
    }
    return {"info": info, "history": df}

@st.cache_data(ttl=3600)
def get_market_data(ticker_symbol):
    try:
        stock_obj = yf.Ticker(ticker_symbol)
        hist = stock_obj.history(period="6mo")
        if hist.empty: return None
        return {"info": stock_obj.info, "history": hist}
    except:
        return None

# --- 3. DESIGN (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Helvetica Neue', sans-serif; }
    .total-score-circle {
        position: fixed; top: 20px; right: 20px; width: 65px; height: 65px;
        border: 2px solid #39FF14; border-radius: 50%; display: flex;
        align-items: center; justify-content: center; color: #39FF14;
        font-weight: bold; font-size: 22px; box-shadow: 0 0 15px #39FF14;
        z-index: 1000; background: black;
    }
    .neon-text { color: #fff; text-shadow: 0 0 10px #39FF14; font-size: 28px; font-weight: 800; }
    .stButton > button { background: transparent; color: #39FF14; border: 1px solid #39FF14; width: 100%; }
    .stButton > button:hover { background: #39FF14; color: black; }
</style>
""", unsafe_allow_html=True)

# --- 4. UI ---
col1, col2 = st.columns([1, 4])
with col1:
    try: st.image("icon.png", width=65)
    except: st.write("☿")
with col2:
    st.markdown('<div class="neon-text">MERKURIUS AI</div>', unsafe_allow_html=True)

ticker_input = st.text_input("SYMBOL", value="VOLV-B").upper()
ticker = ticker_input if "." in ticker_input else f"{ticker_input}.ST"

if st.button("RUN SCAN"):
    data = get_market_data(ticker)
    is_demo = False
    
    if data is None:
        st.warning("Yahoo Rate Limit active. Entering DEMO MODE to show functionality...")
        data = get_demo_data()
        is_demo = True
    
    info = data["info"]
    df = data["history"]
    
    st.markdown(f'<div class="total-score-circle">{"8.5" if not is_demo else "DEMO"}</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 CHART", "📉 METRICS", "🤖 ANALYSIS"])
    
    with tab1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#39FF14', decreasing_line_color='#FF0055')])
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        st.metric("PRICE", f"{info.get('currentPrice')} {info.get('currency')}")
        st.write(f"**P/E:** {info.get('trailingPE')}")
    with tab3:
        st.write(info.get('longBusinessSummary')[:500] + "...")
