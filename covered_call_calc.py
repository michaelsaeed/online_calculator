import streamlit as st

# Set page configuration
st.set_page_config(page_title="Covered Call Calculator", layout="centered")

# Initialize session state for reset functionality
if 'calc_option' not in st.session_state:
    st.session_state.calc_option = "Existing Shares"
    st.session_state.reset_inputs = True

st.sidebar.title("Calculator Options")
calc_option = st.sidebar.radio(
    "Select Calculator", 
    ["Existing Shares", "New Shares"],
    key='calc_option',
    on_change=lambda: st.session_state.update({'reset_inputs': True})
)

# Reset inputs when calculator type changes
if st.session_state.reset_inputs:
    st.session_state.clear()  # Clear all inputs
    st.session_state.calc_option = calc_option  # Restore the calculator option
    st.session_state.reset_inputs = False  # Reset the flag
    st.rerun()  # Rerun the app to reflect cleared inputs

# Shared Styles
st.markdown("<h2><b>Covered Call Calculator</b></h2>", unsafe_allow_html=True)
st.markdown("---")

# ======================================================
# === Existing Shares Calculator ===
# ======================================================
if calc_option == "Existing Shares":
    st.markdown("<h3><b>Existing Shares</b></h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h4><b>Stock Data:</b></h4>", unsafe_allow_html=True)

    stock_price = st.number_input("Stock Price", value=0.00, format="%.2f")
    qty_shares = st.number_input("Number of Shares", value=0)
    
    total_cost = stock_price * qty_shares
    #st.write(f"**Total Cost:** ${total_cost:.2f}")
    st.success(f"Total Cost: ${total_cost:.2f}")  # Green box
    
    st.markdown("---")  # adds a horizontal line
    # --------------------------------------------------------------------
    
    st.markdown("<h4><b>Options Data:</b></h4>", unsafe_allow_html=True)
    
    previous_breakeven = st.number_input("Latest Breakeven Price", value=0.00, format="%.2f")
    
    call_strike_price = st.number_input("Call Option Strike Price", value=0.00, format="%.2f")
    call_premium = st.number_input("Call Option Premium", value=0.00, format="%.2f")
    
    put_strike_price = st.number_input("Put Option Strike Price", value=0.00, format="%.2f")
    put_premium = st.number_input("Put Option Premium", value=0.00, format="%.2f")
    
    new_breakeven = previous_breakeven - call_premium + put_premium
    #st.write(f"**New Breakeven Price:** ${new_breakeven:.2f}")
    st.success(f"New Breakeven Price: ${new_breakeven:.2f}")  # Green box
    
    st.markdown("---")  # adds a horizontal line
    # --------------------------------------------------------------------
    
    st.markdown("<h4><b>In case the call option is exercised:</b></h4>", unsafe_allow_html=True)
    st.markdown("<h4><b>Note: Below profit calculations include all previous trades.</b></h4>", unsafe_allow_html=True)
    
    if stock_price != 0:
        roi_exer = (call_strike_price - new_breakeven) / stock_price
    else:
        roi_exer = 0  # or use None, or display a message
    #st.write(f"**Return On Investment:** {roi_exer * 100:.2f}%")
    st.success(f"ROI: {roi_exer * 100:.2f}%")  # Green box
    
    profit_exer = roi_exer * total_cost
    #st.write(f"**Profit:** ${profit_exer:.2f}")
    st.success(f"Profit: ${profit_exer:.2f}")  # Green box
    
    st.markdown("---")  # adds a horizontal line
    # --------------------------------------------------------------------
    
    st.markdown("<h4><b>In case the call option is not exercised:</b></h4>", unsafe_allow_html=True)
    
    if stock_price != 0:
        roi_not_exer = (call_premium - put_premium) / stock_price
    else:
        roi_not_exer = 0  # or use None, or display a message
    #st.write(f"**Return On Investment:** {roi_not_exer * 100:.2f}%")
    st.success(f"ROI: {roi_not_exer * 100:.2f}%")  # Green box
    
    profit_not_exer = roi_not_exer * total_cost
    #st.write(f"**Profit:** ${profit_not_exer:.2f}")
    st.success(f"Profit: ${profit_not_exer:.2f}")  # Green box

# ======================================================
# === New Shares Calculator ===
# ======================================================
else:
    st.markdown("<h3><b>New Shares</b></h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h4><b>Stock Data:</b></h4>", unsafe_allow_html=True)

    stock_price = st.number_input("Stock Price", value=0.00, format="%.2f")
    qty_shares = st.number_input("Number of Shares", value=0)
    
    total_cost = stock_price * qty_shares
    #st.write(f"**Total Cost:** ${total_cost:.2f}")
    st.success(f"Total Cost: ${total_cost:.2f}")  # Green box
    
    st.markdown("---")  # adds a horizontal line
    # --------------------------------------------------------------------
    
    st.markdown("<h4><b>Options Data:</b></h4>", unsafe_allow_html=True)
    
    call_strike_price = st.number_input("Call Option Strike Price", value=0.00, format="%.2f")
    call_premium = st.number_input("Call Option Premium", value=0.00, format="%.2f")
    
    put_strike_price = st.number_input("Put Option Strike Price", value=0.00, format="%.2f")
    put_premium = st.number_input("Put Option Premium", value=0.00, format="%.2f")
    
    breakeven = stock_price - call_premium + put_premium
    #st.write(f"**Breakeven Price:** ${breakeven:.2f}")
    st.success(f"Breakeven Price: ${breakeven:.2f}")  # Green box
    
    st.markdown("---")  # adds a horizontal line
    # --------------------------------------------------------------------
    
    st.markdown("<h4><b>In case the call option is exercised:</b></h4>", unsafe_allow_html=True)
    
    if stock_price != 0:
        roi_exer = (call_strike_price - breakeven) / stock_price
    else:
        roi_exer = 0  # or use None, or display a message
    #st.write(f"**ROI (Exer.):** {roi_exer * 100:.2f}%")
    st.success(f"ROI: {roi_exer * 100:.2f}%")  # Green box
    
    profit_exer = roi_exer * total_cost
    #st.write(f"**Profit (Exer.):** ${profit_exer:.2f}")
    st.success(f"Profit: ${profit_exer:.2f}")  # Green box
    
    st.markdown("---")  # adds a horizontal line
    # --------------------------------------------------------------------
    
    st.markdown("<h4><b>In case the call option is not exercised:</b></h4>", unsafe_allow_html=True)
    
    if stock_price != 0:
        roi_not_exer = (call_premium - put_premium) / stock_price
    else:
        roi_not_exer = 0  # or use None, or display a message
    #st.write(f"**Return On Investment:** {roi_not_exer * 100:.2f}%")
    st.success(f"ROI: {roi_not_exer * 100:.2f}%")  # Green box
    
    profit_not_exer = roi_not_exer * total_cost
    #st.write(f"**Profit:** ${profit_not_exer:.2f}")
    st.success(f"Profit: ${profit_not_exer:.2f}")  # Green box
