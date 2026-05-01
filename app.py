import streamlit as st
import plotly.express as px
from modeling.dcf import DCF
from modeling.data import get_EV_statement
from ai_insights import generate_insight
from heatmap import generate_heatmap
from monte_carlo import run_monte_carlo, get_statistics

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="DCF Valuation System", layout="wide")

# ------------------ CUSTOM CSS ------------------
def load_css():
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0E1117, #1A1F2B);
    }

    .block-container {
        padding-top: 2rem;
    }

    h1, h2, h3 {
        color: #00D4FF;
    }

    .stButton>button {
        background: linear-gradient(90deg, #00D4FF, #007CF0);
        color: white;
        border-radius: 12px;
        height: 3em;
        font-weight: bold;
        border: none;
        width: 100%;
    }

    .card {
        background: #1A1F2B;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ------------------ HEADER ------------------
st.title("AI Financial Intelligence Platform")
st.caption("Valuation • Risk Modeling • AI Insights")
st.divider()

# ------------------ SIDEBAR ------------------
st.sidebar.header("Input Parameters")

ticker = st.sidebar.text_input("Ticker", "AAPL")
discount_rate = st.sidebar.slider("Discount Rate", 0.05, 0.15, 0.08)
growth_rate = st.sidebar.slider("Growth Rate", 0.05, 0.20, 0.10)
terminal_growth = st.sidebar.slider("Terminal Growth", 0.01, 0.06, 0.05)

run = st.sidebar.button("Run Analysis")

# ------------------ MAIN ------------------
if run:

    with st.spinner("Running AI Financial Analysis..."):

        ev_data = get_EV_statement(ticker)
        ev = ev_data[0] if isinstance(ev_data, (list, tuple)) else ev_data

        result = DCF(
            ticker,
            ev,
            None, None, None,
            discount_rate,
            10,
            growth_rate,
            0.05,
            terminal_growth
        )

        # ------------------ SAFE METRIC EXTRACTION ------------------
        if isinstance(result, dict):
            ev_val = result.get("ev") or result.get("enterprise_value") or 0
            equity_val = result.get("equity") or result.get("equity_value") or 0
            price_val = result.get("price") or result.get("share_price") or 0
        else:
            try:
                ev_val, equity_val, price_val = result
            except:
                ev_val, equity_val, price_val = 0, 0, 0

        # ------------------ KPI METRICS ------------------
        st.subheader("Key Metrics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Enterprise Value", f"{ev_val:.2E}")

        with col2:
            st.metric("Equity Value", f"{equity_val:.2E}")

        with col3:
            st.metric("Per Share Value", f"{price_val:.2f}")

        st.divider()

        # ------------------ TABS ------------------
        tab1, tab2, tab3 = st.tabs(["Valuation", "Simulation", "Insights"])

        # ------------------ TAB 1 ------------------
        with tab1:
            st.markdown(f"""
            <div class="card">
            <h3>Valuation Output</h3>
            <p>{result}</p>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("Sensitivity Analysis")
            fig = generate_heatmap(ticker)
            st.pyplot(fig)

        # ------------------ TAB 2 ------------------
        with tab2:
            vals = run_monte_carlo(ticker, 300)
            stats = get_statistics(vals)

            st.subheader(" Monte Carlo Distribution")

            fig2 = px.histogram(vals, nbins=50)
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown(f"""
            <div class="card">
            <h3>Simulation Stats</h3>
            <p>P10: {stats.get('p10', 0):.2E}</p>
            <p>P90: {stats.get('p90', 0):.2E}</p>
            </div>
            """, unsafe_allow_html=True)

        # ------------------ TAB 3 ------------------
        with tab3:
            insight = generate_insight(result, discount_rate, growth_rate)

            st.markdown(f"""
            <div class="card">
            <h3>Insight</h3>
            <p>{insight}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
            <h3> Simulation Insight</h3>
            <p>
            High probability valuation range: 
            {stats.get('p10', 0):.2E} to {stats.get('p90', 0):.2E}.
            <br><br>
            Indicates sensitivity to growth and discount assumptions.
            </p>
            </div>
            """, unsafe_allow_html=True)