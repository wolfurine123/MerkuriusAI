import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from PIL import Image
import pandas as pd
import numpy as np
from datetime import datetime

# --- 1. CONFIG ---
try:
    img = Image.open("icon.png")
    st.set_page_config(page_title="Merkurius AI", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="Merkurius AI", layout="centered")

# --- 2. DEMO DATA GENERATOR ---
def get_demo_data():
    dates = pd.date_range(end=datetime.now(), periods=104, freq='W')
    base = np.linspace(100, 210, 104) + np.random.normal(0, 10, 104)
    df = pd.DataFrame({
        'Open': base * 0.99, 'High': base * 1.03, 'Low': base * 0.96, 'Close': base
    }, index=dates)
    info = {
        'currentPrice': round(base[-1], 2), 'currency': 'USD', 'trailingPE': 22.0,
        'marketCap': 150000000000, 'longBusinessSummary': "DEMO: Yahoo är blockerat. Visar systemets analyskapacitet..."
    }
    return {"info": info, "hist": df}

# --- 3. DATA FETCH ---
@st.cache_data(ttl=3600)
def get_analysis_data(ticker_symbol):
    try:
        import requests
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        stock = yf.Ticker(ticker_symbol, session=session)
        hist = stock.history(period="2y", interval="1wk")
        if hist.empty: return None
        return {"info": stock.info, "hist": hist}
    except:
        return None

# --- 4. DESIGN (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Helvetica Neue', sans-serif; }
    header {visibility: hidden;} footer {visibility: hidden;}
    .total-score-circle {
        position: fixed; top: 20px; right: 20px; width: 65px; height: 65px;
        border: 2px solid #39FF14; border-radius: 50%; display: flex;
        align-items: center; justify-content: center; color: #39FF14;
        font-weight: bold; font-size: 22px; box-shadow: 0 0 15px #39FF14;
        z-index: 1000; background: black;
    }
    .neon-text { color: #fff; text-shadow: 0 0 10px #39FF14; font-size: 28px; font-weight: 800; margin-left: 15px; }
    .status-box { padding: 15px; border-radius: 5px; border: 1px solid #333; margin-bottom: 10px; background: #111; }
    .indicator-on { color: #39FF14; font-weight: bold; }
    .indicator-off { color: #FF0055; font-weight: bold; }
    .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .section-badge { background: #39FF14; color: black; padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: bold; }
    .stButton > button { background: transparent; color: #39FF14; border: 1px solid #39FF14; width: 100%; height: 50px; font-weight: bold; }
    .stButton > button:hover { background: #39FF14; color: black; box-shadow: 0 0 20px #39FF14; }
</style>
""", unsafe_allow_html=True)

# --- 5. HEADER ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try: st.image("icon.png", width=65)
    except: st.write("☿")
with col_title:
    st.markdown('<div class="neon-text">MERKURIUS AI</div>', unsafe_allow_html=True)

# --- 6. INPUT ---
col_tick, col_curr = st.columns([3, 1])
with col_tick:
    ticker_input = st.text_input("SYMBOL", value="VOLV-B").upper()
    ticker = ticker_input if "." in ticker_input else f"{ticker_input}.ST"
with col_curr:
    currency = st.selectbox("VALUTA", ["SEK", "USD", "EUR", "NOK", "CAD"])

if st.button("EXECUTE AUTOMATED SCAN"):
    data = get_analysis_data(ticker)
    is_demo = False
    if data is None:
        st.warning("⚠️ Demo-mode aktiverat (Yahoo Limit).")
        data = get_demo_data()
        is_demo = True
    
    info, df = data["info"], data["hist"]
    
    # --- AI SCORING LOGIK ---
    # 1. Teknik-poäng (baserat på Weekly Golden Cross & Momentum)
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    has_gc = df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1]
    has_mom = df['Close'].iloc[-1] > df['Close'].tail(4).mean()
    
    tech_score = 4.0
    if has_gc: tech_score += 3.0
    if has_mom: tech_score += 3.0
    
    # 2. Ekonomi-poäng (baserat på P/E)
    pe = info.get('trailingPE', 20)
    econ_score = 9.0 if pe < 15 else (7.0 if pe < 25 else 5.0)
    
    # 3. Moat-poäng (Simulerat baserat på Market Cap)
    mcap = info.get('marketCap', 0)
    moat_score = 9.5 if mcap > 100 * 10**9 else 7.5
    
    # TOTAL SCORE (Genomsnitt)
    total_score = round((tech_score + econ_score + moat_score) / 3, 1)
    st.markdown(f'<div class="total-score-circle">{total_score}</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 CHART", "⚡ AI SIGNAL", "📉 EKONOMI", "📝 SUMMERING"])

    with tab1:
        st.markdown(f'<div class="section-header">MARKET TREND <span class="section-badge">{tech_score}/10</span></div>', unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#39FF14', decreasing_line_color='#FF0055', name="Weekly")])
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='cyan', width=1), name='SMA 50'))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='orange', width=1), name='SMA 200'))
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.write("#### AUTOMATED SIGNALS")
        st.markdown(f'<div class="status-box">Golden Cross (Weekly): <span class="{"indicator-on" if has_gc else "indicator-off"}">{"ACTIVE" if has_gc else "INACTIVE"}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="status-box">Price Momentum: <span class="{"indicator-on" if has_mom else "indicator-off"}">{"POSITIVE" if has_mom else "NEGATIVE"}</span></div>', unsafe_allow_html=True)

    with tab3:
        st.markdown(f'<div class="section-header">FINANCIALS <span class="section-badge">{econ_score}/10</span></div>', unsafe_allow_html=True)
        st.metric(f"Pris ({currency})", f"{info.get('currentPrice')} {currency}")
        st.write(f"**P/E Ratio:** {pe}")

    with tab4:
        st.markdown(f'<div class="section-header">SUMMARY & MOAT <span class="section-badge">{moat_score}/10</span></div>', unsafe_allow_html=True)
        st.write(info.get('longBusinessSummary', 'Ingen info.'))

st.markdown("<br><p style='text-align:center; color:#444; font-size:10px;'>MERKURIUS AI v2.0 | COMPOSITE SCORING ENGINE</p>", unsafe_allow_html=True)
