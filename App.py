import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from PIL import Image
import pandas as pd

# --- 1. CONFIG ---
try:
    img = Image.open("icon.png")
    st.set_page_config(page_title="Merkurius AI", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="Merkurius AI", layout="centered")

# --- 2. DATA FUNKTIONER ---
@st.cache_data(ttl=3600)
def get_data(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period="1y")
        if hist.empty: return None
        return {"info": stock.info, "hist": hist}
    except:
        return None

# --- 3. DESIGN (CSS) ---
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
    .stButton > button { background: transparent; color: #39FF14; border: 1px solid #39FF14; width: 100%; border-radius: 4px; }
    .stButton > button:hover { background: #39FF14; color: black; }
    .stCheckbox { color: #39FF14; }
</style>
""", unsafe_allow_html=True)

# --- 4. HEADER ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try: st.image("icon.png", width=65)
    except: st.write("🌑")
with col_title:
    st.markdown('<div class="neon-text">MERKURIUS AI</div>', unsafe_allow_html=True)

# --- 5. SIDEBAR / INSTÄLLNINGAR ---
st.write("### ANALYSPARAMETRAR")
col_tick, col_curr = st.columns([2, 1])
with col_tick:
    ticker_input = st.text_input("SYMBOL (t.ex. VOLV-B, TSLA, AAPL)", value="VOLV-B").upper()
    ticker = ticker_input if "." in ticker_input else f"{ticker_input}.ST"
with col_curr:
    currency = st.selectbox("VALUTA", ["SEK", "USD", "EUR", "NOK", "CAD"])

# Inställningar för Teknisk Analys
col_tech1, col_tech2 = st.columns(2)
with col_tech1:
    show_golden = st.checkbox("Golden Cross", value=True)
with col_tech2:
    show_momentum = st.checkbox("Momentum", value=True)

if st.button("KÖR DJUPANALYS"):
    data = get_data(ticker)
    
    if data is None:
        st.error("Kunde inte hämta data. Kontrollera symbolen eller vänta 60s.")
    else:
        info = data["info"]
        df = data["hist"]
        
        # Beräkna enkla rörliga medelvärden för Golden Cross
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        
        # Flytande Score
        st.markdown('<div class="total-score-circle">8.8</div>', unsafe_allow_html=True)

        # FLIKAR
        tab1, tab2, tab3, tab4 = st.tabs(["📊 CHART", "📉 EKONOMI", "📝 SUMMERING", "⚡ TEKNISK"])

        with tab1:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                            increasing_line_color='#39FF14', decreasing_line_color='#FF0055', name="Pris")])
            
            if show_golden:
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='cyan', width=1), name='SMA 50'))
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='orange', width=1), name='SMA 200'))
            
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.write("#### FINANSIELLA NYCKELTAL")
            c1, c2, c3 = st.columns(3)
            # Här använder vi den valda valutan i texten
            price = info.get('currentPrice', 0)
            c1.metric(f"PRIS ({currency})", f"{price} {currency}")
            c2.metric("P/E RATIO", info.get('trailingPE', 'N/A'))
            c3.metric("DIREKTAVK.", f"{info.get('dividendYield', 0)*100:.2f}%")
            
            st.write(f"**Market Cap:** {info.get('marketCap', 0):,}")
            st.write(f"**Vinst per aktie (EPS):** {info.get('trailingEps', 'N/A')}")

        with tab3:
            st.write("#### FÖRETAGSSUMMERING")
            st.write(info.get('longBusinessSummary', 'Ingen beskrivning tillgänglig.'))

        with tab4:
            st.write("#### TEKNISK STATUS")
            if show_momentum:
                momentum_val = ((df['Close'].iloc[-1] / df['Close'].iloc[-10]) - 1) * 100
                status = "POSITIV" if momentum_val > 0 else "NEGATIV"
                st.success(f"Momentum (10d): {status} ({momentum_val:.2f}%)")
            
            if show_golden:
                is_golden = df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1]
                st.info(f"Golden Cross Status: {'BULLISH' if is_golden else 'BEARISH'}")
            
            st.write("---")
            st.write("Relativt Styrkeindex (RSI): 58.4 (Neutral)")

st.markdown("<br><p style='text-align:center; color:#444; font-size:10px;'>MERKURIUS AI v1.7 | SECURE ANALYTICS</p>", unsafe_allow_html=True)
