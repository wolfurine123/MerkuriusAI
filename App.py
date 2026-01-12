import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# --- CONFIG & THEME ---
st.set_page_config(page_title="Merkurius AI", layout="centered")

# CSS för Neon-looken
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Courier New', monospace; }
    header {visibility: hidden;} footer {visibility: hidden;}
    
    /* Neongrön Cirkel för Total Score */
    .total-score-circle {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border: 3px solid #39FF14;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #39FF14;
        font-weight: bold;
        font-size: 20px;
        box-shadow: 0 0 15px #39FF14;
        z-index: 1000;
        background: black;
    }

    /* Sektions-badge */
    .section-score {
        float: right;
        color: #39FF14;
        border: 1px solid #39FF14;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
    }

    .neon-logo {
        color: #fff; text-shadow: 0 0 10px #39FF14; font-size: 22px;
        font-weight: bold; margin-bottom: 10px;
    }

    /* Input fält */
    input[type="text"] {
        background-color: #111 !important;
        color: #39FF14 !important;
        border: 1px solid #333 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="neon-logo">☿ MERKURIUS AI</div>', unsafe_allow_html=True)

ticker_input = st.text_input("TICKER", value="VOLV-B", label_visibility="collapsed").upper()
ticker = ticker_input if "." in ticker_input else f"{ticker_input}.ST"

if st.button("RUN SCAN"):
    try:
        with st.spinner("SCANNING..."):
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo")
            info = stock.info
            
            if df.empty:
                st.error("Ingen data hittades.")
            else:
                # Hårdkodade poäng för demo (Gratis-versionen)
                total_score = "8.2" 
                scores = {"ECON": "7/10", "MOAT": "9/10", "TECH": "6/10"}

                st.markdown(f'<div class="total-score-circle">{total_score}</div>', unsafe_allow_html=True)

                tab1, tab2, tab3 = st.tabs(["TEKNIK", "EKONOMI", "MOAT"])

                with tab1:
                    st.markdown(f"TEKNISK ANALYS <span class='section-score'>{scores['TECH']}</span>", unsafe_allow_html=True)
                    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                    increasing_line_color='#39FF14', decreasing_line_color='#FF0055')])
                    fig.update_layout(template="plotly_dark", height=250, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    st.markdown(f"EKONOMISK HÄLSA <span class='section-score'>{scores['ECON']}</span>", unsafe_allow_html=True)
                    st.write(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")
                    st.write(f"Debt/Equity: {info.get('debtToEquity', 'N/A')}")

                with tab3:
                    st.markdown(f"MOAT <span class='section-score'>{scores['MOAT']}</span>", unsafe_allow_html=True)
                    st.write(info.get("longBusinessSummary", "")[:300] + "...")
    except Exception as e:
        st.error(f"Error: {e}")
