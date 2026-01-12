import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from PIL import Image
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 1. CONFIG ---
try:
    img = Image.open("icon.png")
    st.set_page_config(page_title="Merkurius AI", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="Merkurius AI", layout="centered")

# --- 2. DEMO DATA GENERATOR ---
def get_demo_data():
    # Skapar 104 veckor (2 år) av låtsasdata
    dates = pd.date_range(end=datetime.now(), periods=104, freq='W')
    # Skapar en trendande graf
    base = np.linspace(100, 200, 104) + np.random.normal(0, 15, 104)
    df = pd.DataFrame({
        'Open': base * 0.98,
        'High': base * 1.05,
        'Low': base * 0.95,
        'Close': base
    }, index=dates)
    
    info = {
        'currentPrice': round(base[-1], 2),
        'currency': 'USD',
        'trailingPE': 24.5,
        'marketCap': 150000000000,
        'longBusinessSummary': "DEMO MODE: Merkurius AI kunde inte hämta realtidsdata just nu. Detta är en visualisering av hur systemet identifierar långsiktiga trender, Golden Cross och momentum på weekly time frame."
    }
    return {"info": info, "hist": df}

# --- 3. REAL DATA FETCH ---
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
    .indicator-on { color: #39FF14; font-weight: bold; text-shadow: 0 0 5px #39FF14; }
    .indicator-off { color: #FF0055; font-weight: bold; }
    .stButton > button { background: transparent; color: #39FF14; border: 1px solid #39FF14; width: 100%; height: 50px; font-weight: bold; }
    .stButton > button:hover { background: #39FF14; color: black; box-shadow: 0 0 20px #39FF14; }
</style>
""", unsafe_allow_html=True)

# --- 5. HEADER ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try: st.image("icon.png", width=65)
    except: st.write("🌑")
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
        st.warning("⚠️ Yahoo Connection Lost. Entering DEMO MODE...")
        data = get_demo_data()
        is_demo = True
    
    info = data["info"]
    df = data["hist"]
    
    # --- AUTOMATISK AI ANALYS ---
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    
    # Golden Cross: SMA50 > SMA200
    has_golden_cross = df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1]
    
    # Momentum: Pris över 4-veckors medelvärde
    current_price = df['Close'].iloc[-1]
    has_momentum = current_price > df['Close'].tail(4).mean()
    
    # Score-beräkning
    final_score = 4.0
    if has_golden_cross: final_score += 3.0
    if has_momentum: final_score += 3.0
    if is_demo: final_score = "DEMO"

    # UI: Score
    st.markdown(f'<div class="total-score-circle">{final_score}</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 CHART", "⚡ AI SIGNAL", "📉 EKONOMI", "📝 SUMMERING"])

    with tab1:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#39FF14', decreasing_line_color='#FF0055', name="Weekly")])
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='cyan', width=1.5), name='SMA 50'))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='orange', width=1.5), name='SMA 200'))
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.write("#### AUTOMATED TECHNICAL SIGNALS (WEEKLY)")
        
        # Golden Cross UI
        gc_status = "ACTIVE" if has_golden_cross else "INACTIVE"
        gc_class = "indicator-on" if has_golden_cross else "indicator-off"
        st.markdown(f'<div class="status-box">Golden Cross: <span class="{gc_class}">{gc_status}</span></div>', unsafe_allow_html=True)
        
        # Momentum UI
        mom_status = "POSITIVE" if has_momentum else "NEGATIVE"
        mom_class = "indicator-on" if has_momentum else "indicator-off"
        st.markdown(f'<div class="status-box">Price Momentum: <span class="{mom_class}">{mom_status}</span></div>', unsafe_allow_html=True)

    with tab3:
        c1, c2 = st.columns(2)
        c1.metric(f"Pris ({currency})", f"{info.get('currentPrice')} {currency}")
        c2.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
        st.write(f"**Market Cap:** {info.get('marketCap', 0):,} {currency}")

    with tab4:
        st.write(info.get('longBusinessSummary', 'Ingen info tillgänglig.'))

st.markdown("<br><p style='text-align:center; color:#444; font-size:10px;'>MERKURIUS AI v1.9 | AUTONOMOUS ANALYSIS ENGINE</p>", unsafe_allow_html=True)
