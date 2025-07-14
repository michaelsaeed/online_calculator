import streamlit as st

st.set_page_config(page_title="Greek Offset Calculator", layout="wide")

# ========== Session Initialization ==========
if "holding_trades" not in st.session_state:
    st.session_state.holding_trades = []

if "add_option_holding_index" in st.session_state:
    index = st.session_state.pop("add_option_holding_index")
    st.session_state.holding_trades[index]["options"].append({
        "quantity": 0,
        "premium": 0.0,
        "profit": 0.0
    })

if "sold_trades" not in st.session_state:
    st.session_state.sold_trades = []

if "add_option_sold_index" in st.session_state:
    index = st.session_state.pop("add_option_sold_index")
    st.session_state.sold_trades[index]["options"].append({
        "quantity": 0,
        "premium": 0.0,
        "profit": 0.0
    })

# Initialize deletion trackers if they don't exist
if "holding_to_delete" not in st.session_state:
    st.session_state.holding_to_delete = None

if "holding_option_to_delete" not in st.session_state:
    st.session_state.holding_option_to_delete = {}

if "sold_to_delete" not in st.session_state:
    st.session_state.sold_to_delete = None

if "sold_option_to_delete" not in st.session_state:
    st.session_state.sold_option_to_delete = {}


def add_holding_trade():
    st.session_state.holding_trades.append({
        "quantity": 0,
        "avg_price": 0.0,
        "total_cost": 0.0,
        "options": []
    })


def add_sold_trade():
    st.session_state.sold_trades.append({
        "quantity": 0,
        "avg_price": 0.0,
        "sold_price": 0.0,
        "profit": 0.0,
        "options": []
    })


# Apply deletions at the start of script execution
if st.session_state.holding_to_delete is not None:
    st.session_state.holding_trades.pop(st.session_state.holding_to_delete)
    st.session_state.holding_to_delete = None

for i, option_indices in st.session_state.holding_option_to_delete.items():
    for j in sorted(option_indices, reverse=True):
        if i < len(st.session_state.holding_trades) and j < len(st.session_state.holding_trades[i]["options"]):
            st.session_state.holding_trades[i]["options"].pop(j)
st.session_state.holding_option_to_delete = {}

if st.session_state.sold_to_delete is not None:
    st.session_state.sold_trades.pop(st.session_state.sold_to_delete)
    st.session_state.sold_to_delete = None

for i, option_indices in st.session_state.sold_option_to_delete.items():
    for j in sorted(option_indices, reverse=True):
        if i < len(st.session_state.sold_trades) and j < len(st.session_state.sold_trades[i]["options"]):
            st.session_state.sold_trades[i]["options"].pop(j)
st.session_state.sold_option_to_delete = {}

# ========== UI ==========
st.title("📈 Greek Offset Calculator")

# ===== Holding Section =====
st.header("📌 Holding Shares")

if st.button("➕ Add Trade to Holding Section"):
    add_holding_trade()

for i, trade in enumerate(st.session_state.holding_trades):
    st.subheader(f"Holding Stock Trade {i + 1}")

    if st.button(f"➖ Remove Trade {i + 1}", key=f"remove_holding_trade_{i}"):
        st.session_state.holding_to_delete = i
        st.rerun()

    cols = st.columns(3)
    trade["quantity"] = cols[0].number_input(f"Quantity {i + 1}", value=trade["quantity"], key=f"hold_qty_{i}")
    trade["avg_price"] = cols[1].number_input(f"AVG Price {i + 1}", value=trade["avg_price"], key=f"hold_avg_{i}")

    # Auto-calculate Total Cost
    trade["total_cost"] = trade["quantity"] * trade["avg_price"]
    cols[2].number_input(f"Total Cost {i + 1}", value=trade["total_cost"], key=f"hold_cost_{i}", disabled=True)

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        option["quantity"] = pcols[0].number_input(f"Option {j + 1} Qty (Holding {i + 1})", value=option["quantity"],
                                                   key=f"hold_option_qty_{i}_{j}")
        option["premium"] = pcols[1].number_input(f"Premium {j + 1} (Holding {i + 1})", value=option["premium"],
                                                  key=f"hold_option_premium_{i}_{j}")

        # Auto-calculate Option Profit
        option["profit"] = option["quantity"] * option["premium"]
        pcols[2].number_input(f"Profit {j + 1} (Holding {i + 1})", value=option["profit"],
                              key=f"hold_option_profit_{i}_{j}", disabled=True)

        if pcols[3].button("➖", key=f"remove_hold_option_{i}_{j}"):
            if i not in st.session_state.holding_option_to_delete:
                st.session_state.holding_option_to_delete[i] = []
            st.session_state.holding_option_to_delete[i].append(j)
            st.rerun()

    if st.button(f"➕ Add Option to Holding Trade {i + 1}", key=f"add_hold_option_{i}"):
        st.session_state.add_option_holding_index = i
        st.rerun()

    st.markdown("---")

st.markdown("---")  # adds a horizontal line

# ===== Sold Section =====
st.header("📌 Sold Shares")

if st.button("➕ Add Trade to Sold Section"):
    add_sold_trade()

for i, trade in enumerate(st.session_state.sold_trades):
    st.subheader(f"Sold Trade {i + 1}")

    if st.button(f"➖ Remove Sold Trade {i + 1}", key=f"remove_sold_trade_{i}"):
        st.session_state.sold_to_delete = i
        st.rerun()

    cols = st.columns(4)
    trade["quantity"] = cols[0].number_input(f"Quantity {i + 1} (Sold)", value=trade["quantity"], key=f"sold_qty_{i}")
    trade["avg_price"] = cols[1].number_input(f"AVG Price {i + 1} (Sold)", value=trade["avg_price"],
                                              key=f"sold_avg_{i}")
    trade["sold_price"] = cols[2].number_input(f"Sold Price {i + 1}", value=trade["sold_price"], key=f"sold_price_{i}")

    # Auto-calculate Profit
    trade["profit"] = trade["quantity"] * (trade["sold_price"] - trade["avg_price"])
    cols[3].number_input(f"Profit {i + 1}", value=trade["profit"], key=f"sold_profit_{i}", disabled=True)

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        option["quantity"] = pcols[0].number_input(f"Option {j + 1} Qty (Sold {i + 1})", value=option["quantity"],
                                                   key=f"sold_option_qty_{i}_{j}")
        option["premium"] = pcols[1].number_input(f"Premium {j + 1} (Sold {i + 1})", value=option["premium"],
                                                  key=f"sold_option_premium_{i}_{j}")

        # Auto-calculate Option Profit
        option["profit"] = option["quantity"] * option["premium"]
        pcols[2].number_input(f"Profit {j + 1} (Sold {i + 1})", value=option["profit"],
                              key=f"sold_option_profit_{i}_{j}", disabled=True)

        if pcols[3].button("➖", key=f"remove_sold_option_{i}_{j}"):
            if i not in st.session_state.sold_option_to_delete:
                st.session_state.sold_option_to_delete[i] = []
            st.session_state.sold_option_to_delete[i].append(j)
            st.rerun()

    if st.button(f"➕ Add Option to Sold Trade {i + 1}", key=f"add_sold_option_{i}"):
        st.session_state.add_option_sold_index = i
        st.rerun()

    st.markdown("---")

st.markdown("---")  # adds a horizontal line

# ===== Trades Summary =====
st.header("📊 Trades Summary")

# Calculate totals
total_quantity = sum(trade["quantity"] for trade in st.session_state.holding_trades)
total_cost = sum(trade["total_cost"] for trade in st.session_state.holding_trades)

total_option_profit = sum(
    option["profit"]
    for trade in st.session_state.holding_trades + st.session_state.sold_trades
    for option in trade["options"]
)

total_sold_profit = sum(trade["profit"] for trade in st.session_state.sold_trades)
total_profit = total_option_profit + total_sold_profit

# Avoid division by zero
if total_quantity > 0:
    breakeven_price = (total_cost - total_profit) / total_quantity
else:
    breakeven_price = 0.0

# Display
st.markdown(f"**Total Quantity of Shares:** {total_quantity}")
st.markdown(f"**Total Cost:** ${total_cost:,.2f}")
st.markdown(f"**Total Profit:** ${total_profit:,.2f}")
st.success(f"**Breakeven Price:** ${breakeven_price:,.2f}")

st.markdown("---")  # adds a horizontal line

# ===== In case of Selling the Shares =====
st.header("📉 Selling the Shares")
st.markdown("<h4>Note: In case of making a change in the above trades, re-enter the Selling Price for updated calculations.</h4>", unsafe_allow_html=True)

selling_price = st.number_input("**Selling Price**", min_value=0.0, step=0.01)

current_value = total_quantity * selling_price
adjusted_cost = total_cost - total_profit
net_profit_loss = current_value - adjusted_cost
profit_loss_pct = (net_profit_loss / adjusted_cost * 100) if adjusted_cost != 0 else 0.0

# Display
st.markdown(f"**Current Shares Value:** ${current_value:,.2f}")
st.markdown(f"**Adjusted Cost:** ${adjusted_cost:,.2f}")
st.markdown(f"**Net Profit/Loss:** ${net_profit_loss:,.2f}")
st.success(f"**Profit/Loss Percentage:** {profit_loss_pct:.2f}%")
