import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from PIL import Image
import datetime

# --- 1. CONFIG & FAVICON ---
# Sätter ikonen i webbläsarfliken (favicon)
try:
    img = Image.open("icon.png")
    st.set_page_config(page_title="Merkurius AI", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="Merkurius AI", layout="centered")

# --- 2. OPTIMERAD CACHING (Sparar i 1 timme för att slippa Rate Limit) ---
@st.cache_data(ttl=3600)
def get_market_data(ticker_symbol):
    try:
        stock_obj = yf.Ticker(ticker_symbol)
        # Hämtar historik och info
        hist = stock_obj.history(period="6mo")
        if hist.empty:
            return None
        return {
            "info": stock_obj.info,
            "history": hist
        }
    except Exception:
        return None

# --- 3. PREMIUM DARK THEME CSS ---
st.markdown("""
<style>
    /* Grunddesign */
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Helvetica Neue', sans-serif; }
    header {visibility: hidden;} footer {visibility: hidden;}
    
    /* Flytande Total Score Cirkel */
    .total-score-circle {
        position: fixed; top: 20px; right: 20px; width: 65px; height: 65px;
        border: 2px solid #39FF14; border-radius: 50%; display: flex;
        align-items: center; justify-content: center; color: #39FF14;
        font-weight: bold; font-size: 22px; box-shadow: 0 0 15px rgba(57, 255, 20, 0.4);
        z-index: 1000; background: rgba(0,0,0,0.8);
    }
    
    /* Sektionspoäng (Piller) */
    .section-score {
        float: right; color: #39FF14; border: 1px solid #39FF14;
        padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;
    }
    
    /* Header & Logo */
    .header-container { display: flex; align-items: center; margin-bottom: 25px; }
    .neon-text {
        color: #fff; text-shadow: 0 0 10px #39FF14; font-size: 28px;
        font-weight: 800; letter-spacing: 1px; margin-left: 15px;
    }
    
    /* Anpassade knappar */
    .stButton > button {
        background-color: transparent; color: #39FF14; border: 1px solid #39FF14;
        border-radius: 4px; padding: 10px; width: 100%; transition: 0.4s;
        text-transform: uppercase; font-weight: bold; letter-spacing: 1px;
    }
    .stButton > button:hover { background-color: #39FF14; color: #000; box-shadow: 0 0 20px #39FF14; }
    
    /* Input-fält */
    .stTextInput > div > div > input {
        background-color: #111; border: 1px solid #333; color: #39FF14;
        font-size: 18px; text-align: center; border-radius: 4px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111; border-radius: 4px 4px 0 0; padding: 10px 20px; color: #888;
    }
    .stTabs [aria-selected="true"] { background-color: #222; color: #39FF14 !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. APP LAYOUT ---
with st.container():
    col_img, col_txt = st.columns([1, 4])
    with col_img:
        try:
            st.image("icon.png", width=65)
        except:
            st.write("🌍")
    with col_txt:
        st.markdown('<div class="neon-text">MERKURIUS AI</div>', unsafe_allow_html=True)

# Sökruta
ticker_input = st.text_input("SYMBOL", value="VOLV-B", label_visibility="collapsed").upper()
ticker = ticker_input if "." in ticker_input else f"{ticker_input}.ST"

if st.button("INITIATE DEEP SCAN"):
    data = get_market_data(ticker)
    
    if data is None:
        st.error("⚠️ SYSTEM ERROR: Too many requests or invalid ticker. Wait 60s.")
    else:
        info = data["info"]
        df = data["history"]
        
        # Simulerad AI-analys baserad på data
        pe = info.get('trailingPE', 20)
        score = 9.2 if pe < 15 else (7.5 if pe < 25 else 5.2)
        
        # Visa den runda totalpoängen
        st.markdown(f'<div class="total-score-circle">{score}</div>', unsafe_allow_html=True)

        # Huvudinnehåll
        tab1, tab2, tab3 = st.tabs(["📊 CHART", "📉 METRICS", "🤖 AI INSIGHT"])

        with tab1:
            st.markdown(f"MARKET MOMENTUM <span class='section-score'>TECH 8/10</span>", unsafe_allow_html=True)
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                increasing_line_color='#39FF14', decreasing_line_color='#FF0055'
            )])
            fig.update_layout(
                template="plotly_dark", height=350, 
                margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown(f"FINANCIAL DATA <span class='section-score'>ECON 7/10</span>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("P/E", f"{info.get('trailingPE', 'N/A')}")
            m2.metric("DIVIDEND", f"{info.get('dividendYield', 0)*100:.1f}%")
            m3.metric("MCAP", f"{info.get('marketCap', 0)//10**9}B")
            
            st.write(f"**Business Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Current Price:** {info.get('currentPrice', 'N/A')} {info.get('currency', '')}")

        with tab3:
            st.markdown(f"AI STRATEGY ANALYSIS <span class='section-score'>MOAT 9/10</span>", unsafe_allow_html=True)
            summary = info.get("longBusinessSummary", "No analysis available.")
            st.write(f"**AI Summary:** {summary[:450]}...")
            st.info("💡 Merkurius Tip: Analysis suggests strong resistance at current levels.")

# Footer
st.markdown("<br><hr><p style='font-size:10px; color:#444; text-align:center;'>MERKURIUS QUANTUM ENGINE v1.5 | ENCRYPTED CONNECTION</p>", unsafe_allow_html=True)
