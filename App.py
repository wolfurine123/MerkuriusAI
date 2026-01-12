import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from PIL import Image
import requests
import time

# --- 1. CONFIG & FAVICON ---
try:
    img = Image.open("icon.png")
    st.set_page_config(page_title="Merkurius AI", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="Merkurius AI", layout="centered")

# --- 2. AVANCERAD DATA-HÄMTNING (User-Agent Skydd) ---
@st.cache_data(ttl=3600)
def get_market_data(ticker_symbol):
    # Skapar en session som ser ut som en vanlig webbläsare
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        stock_obj = yf.Ticker(ticker_symbol, session=session)
        # Vi försöker hämta historik först
        hist = stock_obj.history(period="6mo")
        
        if hist.empty:
            # Om Yahoo spärrar oss, väntar vi 2 sekunder och provar en sista gång
            time.sleep(2)
            hist = stock_obj.history(period="6mo")
            if hist.empty: return None
            
        return {
            "info": stock_obj.info,
            "history": hist
        }
    except Exception:
        return None

# --- 3. PREMIUM DESIGN (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Helvetica Neue', sans-serif; }
    header {visibility: hidden;} footer {visibility: hidden;}
    
    .total-score-circle {
        position: fixed; top: 20px; right: 20px; width: 65px; height: 65px;
        border: 2px solid #39FF14; border-radius: 50%; display: flex;
        align-items: center; justify-content: center; color: #39FF14;
        font-weight: bold; font-size: 22px; box-shadow: 0 0 15px rgba(57, 255, 20, 0.4);
        z-index: 1000; background: rgba(0,0,0,0.9);
    }
    
    .section-score {
        float: right; color: #39FF14; border: 1px solid #39FF14;
        padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;
    }
    
    .neon-text {
        color: #fff; text-shadow: 0 0 10px #39FF14; font-size: 28px;
        font-weight: 800; letter-spacing: 1px; margin-left: 15px;
    }
    
    .stButton > button {
        background-color: transparent; color: #39FF14; border: 1px solid #39FF14;
        border-radius: 4px; padding: 10px; width: 100%; transition: 0.4s;
        text-transform: uppercase; font-weight: bold;
    }
    .stButton > button:hover { background-color: #39FF14; color: #000; box-shadow: 0 0 20px #39FF14; }
    
    .stTextInput > div > div > input {
        background-color: #111; border: 1px solid #333; color: #39FF14;
        font-size: 18px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. LAYOUT ---
with st.container():
    col_img, col_txt = st.columns([1, 4])
    with col_img:
        try:
            st.image("icon.png", width=65)
        except:
            st.write("☿")
    with col_txt:
        st.markdown('<div class="neon-text">MERKURIUS AI</div>', unsafe_allow_html=True)

ticker_input = st.text_input("SYMBOL", value="VOLV-B", label_visibility="collapsed").upper()
ticker = ticker_input if "." in ticker_input else f"{ticker_input}.ST"

if st.button("INITIATE SECURE SCAN"):
    with st.spinner("BYPASSING FIREWALLS..."):
        data = get_market_data(ticker)
    
    if data is None:
        st.error("⚠️ ACCESS DENIED: Yahoo Finance is blocking the request. Try again in 60s or check the Ticker.")
    else:
        info = data["info"]
        df = data["history"]
        
        # Simulerad AI-score
        score = 8.5
        st.markdown(f'<div class="total-score-circle">{score}</div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📊 CHART", "📉 METRICS", "🤖 ANALYSIS"])

        with tab1:
            st.markdown(f"MARKET DATA <span class='section-score'>TECH 8/10</span>", unsafe_allow_html=True)
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                increasing_line_color='#39FF14', decreasing_line_color='#FF0055'
            )])
            fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown(f"FINANCIALS <span class='section-score'>ECON 7/10</span>", unsafe_allow_html=True)
            st.metric("CURRENT PRICE", f"{info.get('currentPrice', 'N/A')} {info.get('currency', '')}")
            st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
            st.write(f"**Market Cap:** {info.get('marketCap', 0)//10**6} Million")

        with tab3:
            st.markdown(f"AI INSIGHT <span class='section-score'>MOAT 9/10</span>", unsafe_allow_html=True)
            st.write(info.get("longBusinessSummary", "No analysis available.")[:500] + "...")

st.markdown("<br><hr><p style='font-size:10px; color:#444; text-align:center;'>PROPRIETARY ENGINE v1.6 | SECURE SESSION ACTIVE</p>", unsafe_allow_html=True)
