import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from PIL import Image
import os

# --- 1. CONFIG & FAVICON ---
# Detta sätter ikonen i webbläsarfliken
try:
    img = Image.open("icon.png")
    st.set_page_config(page_title="Merkurius AI", page_icon=img, layout="centered")
except:
    st.set_page_config(page_title="Merkurius AI", layout="centered")

# --- 2. CACHING FUNKTION (Motverkar "Too Many Requests") ---
@st.cache_data(ttl=600)
def get_cached_data(ticker_symbol):
    stock_obj = yf.Ticker(ticker_symbol)
    return {
        "info": stock_obj.info,
        "history": stock_obj.history(period="6mo")
    }

# --- 3. CUSTOM CSS (Design) ---
st.markdown("""
<style>
    /* Bakgrund och typsnitt */
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Courier New', monospace; }
    header {visibility: hidden;} footer {visibility: hidden;}
    
    /* Den stora runda poängmätaren uppe till höger */
    .total-score-circle {
        position: fixed; top: 20px; right: 20px; width: 65px; height: 65px;
        border: 3px solid #39FF14; border-radius: 50%; display: flex;
        align-items: center; justify-content: center; color: #39FF14;
        font-weight: bold; font-size: 22px; box-shadow: 0 0 15px #39FF14;
        z-index: 1000; background: black;
    }
    
    /* Poängbubblor för sektioner */
    .section-score {
        float: right; color: #39FF14; border: 1px solid #39FF14;
        padding: 2px 8px; border-radius: 10px; font-size: 12px;
    }
    
    /* Logga och rubrik */
    .logo-container { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    .neon-logo-text {
        color: #fff; text-shadow: 0 0 10px #39FF14; font-size: 26px;
        font-weight: bold; letter-spacing: 2px;
    }
    
    /* Knappar */
    .stButton > button {
        background-color: #000; color: #39FF14; border: 1px solid #39FF14;
        box-shadow: 0 0 8px #39FF14; width: 100%; transition: 0.3s;
    }
    .stButton > button:hover { background-color: #39FF14; color: black; }
    
    /* Input-fält */
    .stTextInput > div > div > input {
        background-color: #111; border: 1px solid #333; color: #39FF14; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. APPENS HEADLINE MED IKON ---
col1, col2 = st.columns([1, 5])
with col1:
    try:
        st.image("icon.png", width=60)
    except:
        st.write("☿") # Fallback om bild saknas
with col2:
    st.markdown('<div class="neon-logo-text">MERKURIUS AI</div>', unsafe_allow_html=True)

# --- 5. INPUT & LOGIK ---
ticker_input = st.text_input("TICKER", value="VOLV-B", label_visibility="collapsed").upper()
ticker = ticker_input if "." in ticker_input else f"{ticker_input}.ST"

if st.button("RUN DEEP SCAN"):
    try:
        with st.spinner("BROWSING GLOBAL DATA..."):
            data = get_cached_data(ticker)
            info = data["info"]
            df = data["history"]
            
            if df.empty:
                st.error("STOCK NOT FOUND.")
            else:
                # Exempelpoäng (Här kan du bygga in riktig logik senare)
                total_score = "8.7" 
                scores = {"ECON": "8/10", "MOAT": "9/10", "TECH": "7/10"}

                # Visa den flytande cirkeln
                st.markdown(f'<div class="total-score-circle">{total_score}</div>', unsafe_allow_html=True)

                # Tabs för olika vyer
                tab1, tab2, tab3 = st.tabs(["CHART", "FINANCE", "ANALYSIS"])

                with tab1:
                    st.markdown(f"TECHNICAL ANALYSIS <span class='section-score'>{scores['TECH']}</span>", unsafe_allow_html=True)
                    fig = go.Figure(data=[go.Candlestick(
                        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        increasing_line_color='#39FF14', decreasing_line_color='#FF0055'
                    )])
                    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    st.markdown(f"FINANCIAL HEALTH <span class='section-score'>{scores['ECON']}</span>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    c1.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
                    c2.metric("Forward P/E", info.get('forwardPE', 'N/A'))
                    st.write(f"**Market Cap:** {info.get('marketCap', 'N/A'):,}")

                with tab3:
                    st.markdown(f"BUSINESS MOAT <span class='section-score'>{scores['MOAT']}</span>", unsafe_allow_html=True)
                    st.write(info.get("longBusinessSummary", "No summary available.")[:500] + "...")

    except Exception as e:
        if "Too Many Requests" in str(e):
            st.warning("SYSTEM OVERLOAD: Yahoo Rate Limit. Wait 60s.")
        else:
            st.error(f"ERROR: {e}")

st.markdown("<br><br><p style='font-size:10px; color:#444; text-align:center;'>QUANTUM ANALYSIS ENGINE v1.4 | © MERKURIUS</p>", unsafe_allow_html=True)
