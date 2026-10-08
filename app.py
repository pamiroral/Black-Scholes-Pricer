import math
import streamlit as st
from black_scholes_pricing import BlackScholes
import numpy as np
from yahoo_finance_yfinance import get_history_prices
from yahoo_finance_yfinance import historical_vol
from yahoo_finance_yfinance import annotated_heatmap, PNL_CMAP, PNL_CMAP_VAR

st.set_page_config(page_title="Black-Scholes Pricer", layout="wide")
st.title("Black-Scholes Option Pricer")

with st.expander("Model assumptions"):
    st.markdown("It should be stated that this code has the following assumptions: \n"
                "1. European options (from Black-Scholes)\n"
                "2. No dividends\n"
                "3. Constant volatility\n"
                "4. Long positions (We are buying the option to buy/sell at a set price)\n"
                "5. Per-share P&L\n"
                "6. Data retrieved from yfinance (not affiliated with Yahoo!, and hence, prone to errors and crashing related to any structural changes in Yahoo!Finance)\n")

LINKEDIN_URL = "https://www.linkedin.com/in/pamir-oral-1011a220b/"

LINKEDIN_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="#ffffff">'
    '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 '
    '2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 '
    '5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 '
    '2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 '
    '0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 '
    '22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
)

with st.sidebar:
    st.markdown(
        f'<div style="font-size:0.75rem;font-weight:700;letter-spacing:0.18em;'
        f'text-transform:uppercase;color:#0A66C2;margin-bottom:0.2rem;">Created by</div>'
        f'<div style="font-size:1.6rem;font-weight:800;line-height:1.2;margin-bottom:0.7rem;">Pamir Oral</div>'
        f'<a href="{LINKEDIN_URL}" target="_blank" rel="noopener noreferrer" '
        f'style="display:inline-flex;align-items:center;gap:0.55rem;background:#0A66C2;color:#ffffff;'
        f'padding:0.5rem 1rem;border-radius:0.5rem;text-decoration:none;font-weight:600;">'
        f'{LINKEDIN_ICON}<span>LinkedIn</span></a>',
        unsafe_allow_html=True,
    )
    st.divider()

with st.sidebar:
    st.header("Inputs")
    S = st.number_input("Current asset price", value=100.0, min_value=0.01)
    K = st.number_input("Strike price", value=105.0, min_value=0.01)
    T_day = st.number_input("Time to maturity (days)", value=50, min_value=2)
    T = T_day / 365

    sigma_input = st.checkbox("Get volatility from history")

    if not sigma_input:
        sigma_manual = st.number_input(r"Volatility ($\sigma$) (%)", value=50.0, min_value=1.0) / 100
    else:
        symbol = st.text_input("Stock symbol", value= "AAPL").strip().upper()
        if not symbol:
            st.warning("Enter a ticker symbol.")
            st.stop()

        if not symbol.replace(".", "").replace("-", "").isalnum():
            st.error("Ticker contains invalid characters.")
            st.stop()
        period = st.number_input("Historical data range (days) Max: 252", value=20, min_value=2, max_value=252)

    # sigma = st.number_input("Volatility (σ)", value=0.20, min_value=0.01)
    r = st.number_input("Risk-free interest rate (%)", value=5.0, min_value=0.0) / 100
    # calculate = st.button("Calculate")

    heatmaps = st.checkbox("Display Heatmaps")

# note your function's argument order: S, K, r, T, sigma
if not sigma_input:
    sigma = sigma_manual


else:
    try:
        prices = get_history_prices(symbol)
        sigma = historical_vol(prices, period)
    except ValueError as e:
        st.error(str(e))
        st.stop()
    except Exception:
        st.error(
            "Couldn't fetch market data right now. Uncheck 'Get volatility from history' to enter volatility manually.")
        st.stop()
    if not np.isfinite(sigma) or sigma < 0:
        st.error("Couldn't compute a valid volatility from this data.")
        st.stop()

    st.sidebar.caption(f"Latest close for {symbol}: ${prices[-1]:.2f}")

call = BlackScholes(S, K, r, T, sigma)
put = call - S + K * math.exp(-r * T)  # put-call parity

his_vol, c1, c2 = st.columns(3)
if sigma_input:
    his_vol.metric("Historical volatility", f"{sigma:.2%}")
else:
    his_vol.metric("Manual volatility", f"{sigma:.2%}")
c1.metric("Call value", f"${call:.2f}")
c2.metric("Put value", f"${put:.2f}")

graph_click = False

if heatmaps:
    with st.sidebar:
        st.divider()
        st.header("Heatmap Parameter Inputs")

        S_lower = st.number_input("Min spot price", value=90.00, min_value=0.01, key="S_lo")
        S_upper = st.number_input("Max spot price", value=150.00, min_value=0.01, key="S_hi")
        if S_lower >= S_upper:
            st.error("Min spot price must be smaller than max.")
            st.stop()

        # index=None -> nothing selected until the user picks one
        heatmap_selection = st.selectbox(
            "Variable", ["Volatility", "Risk-free Interest"],
            index=None, placeholder="Choose a variable", key="heatmap_var",
        )

        if heatmap_selection == "Volatility":
            ylabel = "Volatility"
            y_lo = st.number_input("Min volatility (%)", value=10.0, min_value=1.0, key="vol_lo")
            y_hi = st.number_input("Max volatility (%)", value=50.0, min_value=1.0, key="vol_hi")
        elif heatmap_selection == "Risk-free Interest":
            ylabel = "Risk-free Interest"
            y_lo = st.number_input("Min interest (%)", value=1.0, min_value=0.0, key="r_lo")
            y_hi = st.number_input("Max interest (%)", value=10.0, min_value=0.1, key="r_hi")

        # the button only exists once a variable has been chosen
        if heatmap_selection is not None:
            if y_lo >= y_hi:
                st.error("Min must be smaller than max.")
                st.stop()
            graph_click = st.button("Graph heatmap")
            st.text("To view the changes in the heatmap, click 'Graph heatmap' again")

        test_pricing = st.checkbox("Test P&L")

    if graph_click:

        S_lin = np.linspace(S_lower, S_upper, 10)
        y_lin = np.linspace(y_lo / 100, y_hi / 100, 10)
        calls = np.zeros((10, 10))
        puts = np.zeros((10, 10))

        for i_y, y_val in enumerate(y_lin):
            sig_h = y_val if heatmap_selection == "Volatility" else sigma
            r_h = y_val if heatmap_selection == "Risk-free Interest" else r
            for i_S, S_val in enumerate(S_lin):
                c = BlackScholes(S_val, K, r_h, T, sig_h)
                calls[i_y][i_S] = c
                puts[i_y][i_S] = c - S_val + K * math.exp(-r_h * T)

        # store the DATA, not the figures
        st.session_state.hm = {
            "calls": calls, "puts": puts,
            "S_lin": S_lin, "y_lin": y_lin, "ylabel": ylabel,
        }

    if test_pricing:
        with st.sidebar:
            call_pricing = st.number_input("Call purchase price", value=round(float(call), 2), min_value=0.00, key="call_price")
            put_pricing = st.number_input("Put purchase price", value=round(float(put), 2), min_value=0.00, key="put_price")
            color_change = st.checkbox("Change colors")


    # draw on every run, so the plots stay when other inputs change
    if "hm" in st.session_state:
        hm = st.session_state.hm

        st.header("Call and Put Heatmaps")
        col_a, col_b = st.columns(2)
        col_a.pyplot(annotated_heatmap(
            hm["calls"], "CALL", x_vals=hm["S_lin"], y_vals=hm["y_lin"],
            xlabel="Stock Price", ylabel=hm["ylabel"], cbar_label="Call Price", cmap="viridis"))
        col_b.pyplot(annotated_heatmap(
            hm["puts"], "PUT", x_vals=hm["S_lin"], y_vals=hm["y_lin"],
            xlabel="Stock Price", ylabel=hm["ylabel"], cbar_label="Put Price", cmap="viridis"))

        if test_pricing:
            cmap = PNL_CMAP_VAR if color_change else PNL_CMAP

            st.header("P&L Heatmaps")
            col_c, col_d = st.columns(2)
            col_c.pyplot(annotated_heatmap(
                hm["calls"] - call_pricing, "CALL P&L", x_vals=hm["S_lin"], y_vals=hm["y_lin"],
                xlabel="Stock Price", ylabel=hm["ylabel"], cbar_label="P&L", cmap=cmap, center=0))
            col_d.pyplot(annotated_heatmap(
                hm["puts"] - put_pricing, "PUT P&L", x_vals=hm["S_lin"], y_vals=hm["y_lin"],
                xlabel="Stock Price", ylabel=hm["ylabel"], cbar_label="P&L", cmap=cmap, center=0))






