import streamlit as st

st.title("Covered Call Calculator (New Shares)")

stock_price = st.number_input("Stock Price", value=0.00, format="%.2f")
qty_shares = st.number_input("Number of Shares", value=0)

total_cost = stock_price * qty_shares
st.write(f"**Total Cost:** ${total_cost:.2f}")

st.markdown("---")  # adds a horizontal line
# --------------------------------------------------------------------

call_strike_price = st.number_input("Call Option Strike Price", value=0.00, format="%.2f")
call_premium = st.number_input("Call Option Premium", value=0.00, format="%.2f")

put_strike_price = st.number_input("Put Option Strike Price", value=0.00, format="%.2f")
put_premium = st.number_input("Put Option Premium", value=0.00, format="%.2f")

breakeven = stock_price - call_premium + put_premium
st.write(f"**Breakeven Price:** ${breakeven:.2f}")

st.markdown("---")  # adds a horizontal line
# --------------------------------------------------------------------

if stock_price != 0:
    roi_exer = (call_strike_price - breakeven) / stock_price
else:
    roi_exer = 0  # or use None, or display a message
st.write(f"**ROI (Exer.):** {roi_exer * 100:.2f}%")

profit_exer = roi_exer * total_cost
st.write(f"**Profit (Exer.):** ${profit_exer:.2f}")

st.markdown("---")  # adds a horizontal line
# --------------------------------------------------------------------

if stock_price != 0:
    roi_not_exer = (call_premium - put_premium) / stock_price
else:
    roi_not_exer = 0  # or use None, or display a message
st.write(f"**ROI (Not Exer.):** {roi_not_exer * 100:.2f}%")

profit_not_exer = roi_not_exer * total_cost
st.write(f"**Profit (Not Exer.):** ${profit_not_exer:.2f}")



