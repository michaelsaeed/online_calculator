import streamlit as st

st.title("Covered Call Calculator (New Shares)")

st.markdown("---")  # adds a horizontal line
# --------------------------------------------------------------------

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
