import streamlit as st

st.set_page_config(page_title="Covered Call Calculator", layout="centered")

st.sidebar.title("Calculator Options")
calc_option = st.sidebar.radio("Select Calculator", ["Existing Shares", "New Shares"])

# Shared Styles
st.markdown("<h2><b>Covered Call Calculator</b></h2>", unsafe_allow_html=True)
st.markdown("---")

# ======================================================
# === Existing Shares Calculator ===
# ======================================================
if calc_option == "Existing Shares":
    st.markdown("<h4><b>Stock Data:</b></h4>", unsafe_allow_html=True)

    stock_price = st.number_input("Stock Price", value=0.00, format="%.2f")
    qty_shares = st.number_input("Number of Shares", value=0)

    total_cost = stock_price * qty_shares
    st.success(f"Total Cost: ${total_cost:.2f}")

    st.markdown("---")
    st.markdown("<h4><b>Options Data:</b></h4>", unsafe_allow_html=True)

    previous_breakeven = st.number_input("Latest Breakeven Price", value=0.00, format="%.2f")
    call_strike_price = st.number_input("Call Option Strike Price", value=0.00, format="%.2f")
    call_premium = st.number_input("Call Option Premium", value=0.00, format="%.2f")
    put_strike_price = st.number_input("Put Option Strike Price", value=0.00, format="%.2f")
    put_premium = st.number_input("Put Option Premium", value=0.00, format="%.2f")

    new_breakeven = previous_breakeven - call_premium + put_premium
    st.success(f"New Breakeven Price: ${new_breakeven:.2f}")

    st.markdown("---")
    st.markdown("<h4><b>If the call option is exercised:</b></h4>", unsafe_allow_html=True)

    roi_exer = (call_strike_price - new_breakeven) / stock_price if stock_price else 0
    st.success(f"ROI: {roi_exer * 100:.2f}%")
    st.success(f"Profit: ${roi_exer * total_cost:.2f}")

    st.markdown("---")
    st.markdown("<h4><b>If the call option is not exercised:</b></h4>", unsafe_allow_html=True)

    roi_not_exer = (call_premium - put_premium) / stock_price if stock_price else 0
    st.success(f"ROI: {roi_not_exer * 100:.2f}%")
    st.success(f"Profit: ${roi_not_exer * total_cost:.2f}")

# ======================================================
# === New Shares Calculator ===
# ======================================================
else:
    st.markdown("<h4><b>Buy Stock + Write Call Calculator</b></h4>", unsafe_allow_html=True)

    stock_price = st.number_input("Stock Purchase Price", value=0.00, format="%.2f")
    qty_shares = st.number_input("Number of Shares to Buy", value=0)
    call_strike_price = st.number_input("Call Option Strike Price", value=0.00, format="%.2f")
    call_premium = st.number_input("Call Option Premium Received", value=0.00, format="%.2f")

    total_cost = stock_price * qty_shares
    net_entry = stock_price - call_premium
    max_profit_per_share = call_strike_price - net_entry
    max_profit_total = max_profit_per_share * qty_shares

    st.success(f"Total Stock Cost: ${total_cost:.2f}")
    st.success(f"Net Entry Price: ${net_entry:.2f}")
    st.success(f"Max Profit per Share: ${max_profit_per_share:.2f}")
    st.success(f"Max Profit Total: ${max_profit_total:.2f}")
