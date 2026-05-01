import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from modeling.dcf import DCF
from modeling.data import get_EV_statement
from modeling.lba_engine import run_lba_analysis
from modeling.lbo import LBOEngine, simulate_lbo_monte_carlo
from ai_insights import generate_insight
# from heatmap import generate_heatmap
from monte_carlo import run_monte_carlo, get_statistics

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Financial Modelling Software",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ LOAD CSS ------------------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.title("Financial Modelling Software")
    st.caption("Institutional Standard v5.0")
    st.divider()
    
    st.subheader("Primary Parameters")
    ticker = st.text_input("Asset Ticker", "AAPL").upper()
    
    col_a, col_b = st.columns(2)
    with col_a:
        discount_rate = st.slider("WACC %", 5.0, 15.0, 8.5) / 100
    with col_b:
        growth_rate = st.slider("Growth %", 5.0, 25.0, 12.0) / 100
        
    terminal_growth = st.slider("Terminal Growth %", 1.0, 6.0, 3.0) / 100
    
    st.divider()
    st.subheader("LBO Parameters")
    entry_mult = st.slider("Entry Multiple (EV/EBITDA)", 6.0, 18.0, 10.0)
    exit_mult = st.slider("Exit Multiple (EV/EBITDA)", 6.0, 18.0, 10.0)
    leverage = st.slider("Leverage (Debt/EBITDA)", 2.0, 8.0, 4.0)
    
    st.subheader("Algo Settings")
    volatility = st.select_slider("Sim Volatility", options=[0.1, 0.2, 0.3, 0.5], value=0.2)
    iterations = st.number_input("MC Iterations", 100, 2000, 1000)
    
    run_btn = st.button("DEPLOY VALUATION ENGINE", use_container_width=True)
    
    st.divider()
    st.info("Institutional data feed active via FMP Cloud.")

# ------------------ DASHBOARD HEADER ------------------
if not run_btn and "initialized" not in st.session_state:
    st.markdown("""
    <div style="text-align: center; padding: 120px 20px; background: #161B22; border-radius: 40px; margin-bottom: 60px; border: 1px solid #30363D; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
        <h1 style="font-size: 80px; margin-bottom: 24px; color: #00D4FF; letter-spacing: -0.04em; line-height: 1.1;">Financial <span style="color: #00D4FF;">Modelling Software</span></h1>
        <p style="font-size: 24px; color: #00D4FF; max-width: 900px; margin: 0 auto; line-height: 1.6; font-weight: 500;">
            Advanced DCF & LBO modeling, stochastic Monte Carlo distributions, and cognitive LBA simulations. 
            Engineered for high-conviction institutional decision making.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card"><h3>LBO Returns Engine</h3><p>Leveraged buyout modeling with debt paydown and IRR/MOIC analysis.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>Stochastic Risk</h3><p>Monte Carlo modeling for P10/P90 tail-risk assessment.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><h3>Synthesis Engine</h3><p>Automated synthesis of financial statements and valuation drivers.</p></div>', unsafe_allow_html=True)
    
    st.stop()

# ------------------ EXECUTION ------------------
if run_btn:
    st.session_state.initialized = True
    
    with st.spinner("INITIATING MULTI-AGENT ALGORITHMIC SCAN..."):
        # Data Fetch
        ev_data = get_EV_statement(ticker)
        ev_item = ev_data[0] if isinstance(ev_data, (list, tuple)) else ev_data
        
        # Mocking some data for LBO if not available in real fetch
        ebitda_mock = 5e10 
        revenue_mock = 2e11
        
        # DCF Run
        result = DCF(ticker, ev_item, None, None, None, discount_rate, 10, growth_rate, 0.05, terminal_growth)
        
        # LBO Run
        lbo_engine = LBOEngine(entry_multiple=entry_mult, exit_multiple=exit_mult, leverage_ratio=leverage)
        lbo_result = lbo_engine.run_lbo(ebitda_mock, revenue_mock, growth_rate, margin=0.25)
        
        # Safe Extraction
        if isinstance(result, dict):
            ev_val = result.get("ev") or result.get("enterprise_value") or 0
            equity_val = result.get("equity") or result.get("equity_value") or 0
            price_val = result.get("price") or result.get("share_price") or 0
        else:
            try: ev_val, equity_val, price_val = result
            except: ev_val, equity_val, price_val = 0, 0, 0
            
        # LBA Algo Run (Cognitive Model)
        upside = ((price_val - 150) / 150) * 100 
        lba_result = run_lba_analysis(upside, volatility)
        
        # UI Header
        st.subheader(f"Dashboard: {ticker} Intelligence Report")
        
        # Metrics Row
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Intrinsic Value", f"${price_val:,.2f}", f"{upside:+.1f}%")
        with m_col2:
            st.metric("LBO IRR", f"{lbo_result['irr']:.1f}%", f"{lbo_result['moic']:.2f}x MOIC")
        with m_col3:
            st.metric("LBA Conviction", f"{lba_result['confidence']:.1f}%", lba_result['winner'])
        with m_col4:
            st.metric("Decision Latency", f"{lba_result['mean_latency']:.2f}ms")
            
        st.divider()
        
        # TABS
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Decision Matrix", "LBO Analysis", "Risk Simulation", "Financial Archeology", "Synthesis"])
        
        with tab1:
            col_l, col_r = st.columns([2, 1])
            with col_l:
                st.subheader("LBA Evidence Accumulation Path")
                fig_lba = go.Figure()
                for i in range(min(5, len(lba_result['paths']['bull']))):
                    fig_lba.add_trace(go.Scatter(y=lba_result['paths']['bull'][i], mode='lines', name=f'Bull {i+1}', line=dict(color='#00D4FF', width=1, dash='dot')))
                    fig_lba.add_trace(go.Scatter(y=lba_result['paths']['bear'][i], mode='lines', name=f'Bear {i+1}', line=dict(color='#DC2626', width=1, dash='dot')))
                
                fig_lba.add_hline(y=150, line_dash="dash", line_color="#00D4FF", annotation_text="Decision Threshold")
                fig_lba.update_layout(height=450, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_lba, use_container_width=True)
            
            with col_r:
                st.markdown(f"""
                <div class="card">
                    <h3 style="color: #00D4FF !important;">Algo Decision: <span style="color: {'#059669' if lba_result['winner'] == 'BULL' else '#DC2626'}">{lba_result['winner']}</span></h3>
                    <p>The LBA Engine has detected a <b>{lba_result['confidence']:.1f}%</b> probability of value accumulation hitting the {'upper' if lba_result['winner'] == 'BULL' else 'lower'} threshold.</p>
                    <hr style="border-color: #F1F5F9;">
                    <p style="font-size: 14px; color: #00D4FF; font-weight: 600;">Stochastic Noise: {volatility}</p>
                    <p style="font-size: 14px; color: #00D4FF; font-weight: 600;">Accumulator Drift: {upside/10:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # st.subheader("Sensitivity Grid")
                # fig_heat = generate_heatmap(ticker)
                # st.pyplot(fig_heat)

        with tab2:
            st.subheader("LBO Capital Structure & Returns")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="card"><h4>Equity IRR</h4><h2 style="color: #00D4FF; font-weight: 800;">{lbo_result["irr"]:.2f}%</h2></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="card"><h4>MOIC</h4><h2 style="color: #00D4FF; font-weight: 800;">{lbo_result["moic"]:.2f}x</h2></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="card"><h4>Exit Equity</h4><h2 style="color: #00D4FF; font-weight: 800;">${lbo_result["exit_equity"]/1e9:.1f}B</h2></div>', unsafe_allow_html=True)
            
            col_l, col_r = st.columns(2)
            with col_l:
                st.subheader("Debt Paydown Schedule")
                debt_df = pd.DataFrame({"Year": range(len(lbo_result['debt_path'])), "Debt Balance": lbo_result['debt_path']})
                fig_debt = px.area(debt_df, x="Year", y="Debt Balance", color_discrete_sequence=['#DC2626'])
                fig_debt.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_debt, use_container_width=True)
                
            with col_r:
                st.subheader("EBITDA Growth Path")
                ebitda_df = pd.DataFrame({"Year": range(1, len(lbo_result['ebitda_path']) + 1), "EBITDA": lbo_result['ebitda_path']})
                fig_ebitda = px.line(ebitda_df, x="Year", y="EBITDA", markers=True, color_discrete_sequence=['#00D4FF'])
                fig_ebitda.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_ebitda, use_container_width=True)

        with tab3:
            st.subheader("Monte Carlo Value Distribution (DCF)")
            vals = run_monte_carlo(ticker, iterations, growth_rate, volatility)
            stats = get_statistics(vals)
            
            fig_hist = px.histogram(vals, nbins=50, color_discrete_sequence=['#00D4FF'], marginal="box")
            fig_hist.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_hist, use_container_width=True)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Median EV", f"${stats['median']/1e9:.2f}B")
            c2.metric("P10 Tail Risk", f"${stats['p10']/1e9:.2f}B")
            c3.metric("P90 Ceiling", f"${stats['p90']/1e9:.2f}B")
            c4.metric("Value at Risk (95%)", f"${stats['var_95']/1e9:.2f}B")
            
            st.divider()
            st.subheader("LBO Return Distribution")
            lbo_mc = simulate_lbo_monte_carlo(ebitda_mock, revenue_mock, growth_rate, volatility, iterations)
            fig_lbo_mc = px.histogram(lbo_mc['irrs'], nbins=50, color_discrete_sequence=['#059669'], title="IRR Distribution (%)")
            fig_lbo_mc.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_lbo_mc, use_container_width=True)

        with tab4:
            st.subheader("Intrinsic Value vs Market Price")
            dates = ["2023-Q1", "2023-Q2", "2023-Q3", "2023-Q4", "2024-Q1"]
            prices = [145, 155, 165, 180, 190]
            intrinsic = [155, 160, 175, 175, price_val]
            
            fig_market = go.Figure()
            fig_market.add_trace(go.Scatter(x=dates, y=prices, name="Market Price", line=dict(color='#94A3B8', width=2)))
            fig_market.add_trace(go.Scatter(x=dates, y=intrinsic, name="Intrinsic Value", line=dict(color='#00D4FF', width=4)))
            fig_market.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_market, use_container_width=True)

        with tab5:
            insight = generate_insight(result, discount_rate, growth_rate, lba_result)
            st.markdown(f'<div class="card">{insight}</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="card" style="border-left: 4px solid #00D4FF;">
                <h3>Market Commentary</h3>
                <p>The convergence of DCF upside ({upside:.1f}%) and LBO IRR ({lbo_result['irr']:.1f}%) suggests a {'robust valuation floor' if upside > -10 else 'significant overvaluation risk'}. 
                LBA conviction at {lba_result['confidence']:.1f}% indicates institutional {'accumulation' if lba_result['winner'] == 'BULL' else 'distribution'} is likely.</p>
            </div>
            """, unsafe_allow_html=True)

    st.toast("Institutional Analysis Engine Deployed.")