import streamlit as st

st.set_page_config(page_title="Greek Offset Calculator", layout="wide")

# ========== Session Initialization ==========
if "held_trades" not in st.session_state:
    st.session_state.held_trades = []

if "add_option_held_index" in st.session_state:
    i = st.session_state.add_option_held_index
    st.session_state.held_trades[i]["options"].append({
        "quantity": 0,
        "premium": 0.0,
        "profit": 0.0}
    )
    del st.session_state.add_option_held_index

if "sold_trades" not in st.session_state:
    st.session_state.sold_trades = []

if "add_option_sold_index" in st.session_state:
    i = st.session_state.add_option_sold_index
    st.session_state.sold_trades[i]["options"].append({
        "quantity": 0,
        "premium": 0.0,
        "profit": 0.0}
    )
    del st.session_state.add_option_sold_index

if "future_trade" not in st.session_state:
    st.session_state.future_trade = []

if "add_option_future_index" in st.session_state:
    i = st.session_state.add_option_future_index
    st.session_state.future_trade[i]["options"].append({
        "quantity": 0,
        "premium": 0.0,
        "profit": 0.0}
    )
    del st.session_state.add_option_future_index

# Initialize deletion trackers
if "held_to_delete" not in st.session_state:
    st.session_state.held_to_delete = None
if "held_option_to_delete" not in st.session_state:
    st.session_state.held_option_to_delete = {}
if "sold_to_delete" not in st.session_state:
    st.session_state.sold_to_delete = None
if "sold_option_to_delete" not in st.session_state:
    st.session_state.sold_option_to_delete = {}
if "future_to_delete" not in st.session_state:
    st.session_state.future_to_delete = None
if "future_option_to_delete" not in st.session_state:
    st.session_state.future_option_to_delete = {}


def add_held_trade():
    st.session_state.held_trades.append({"quantity": 0, "avg_price": 0.0, "total_cost": 0.0, "options": []})


def add_sold_trade():
    st.session_state.sold_trades.append(
        {"quantity": 0, "avg_price": 0.0, "sold_price": 0.0, "profit": 0.0, "options": []})


def add_future_trade():
    st.session_state.future_trade.append(
        {"quantity": 0, "avg_price": 0.0, "total_cost": 0.0, "sold_price": 0.0, "profit": 0.0, "options": []})


# Apply deletions
if st.session_state.held_to_delete is not None:
    st.session_state.held_trades.pop(st.session_state.held_to_delete)
    st.session_state.held_to_delete = None

for i, option_indices in st.session_state.held_option_to_delete.items():
    for j in sorted(option_indices, reverse=True):
        if i < len(st.session_state.held_trades) and j < len(st.session_state.held_trades[i]["options"]):
            st.session_state.held_trades[i]["options"].pop(j)
st.session_state.held_option_to_delete = {}

if st.session_state.sold_to_delete is not None:
    st.session_state.sold_trades.pop(st.session_state.sold_to_delete)
    st.session_state.sold_to_delete = None

for i, option_indices in st.session_state.sold_option_to_delete.items():
    for j in sorted(option_indices, reverse=True):
        if i < len(st.session_state.sold_trades) and j < len(st.session_state.sold_trades[i]["options"]):
            st.session_state.sold_trades[i]["options"].pop(j)
st.session_state.sold_option_to_delete = {}

if st.session_state.future_to_delete is not None:
    st.session_state.future_trade.pop(st.session_state.future_to_delete)
    st.session_state.future_to_delete = None

for i, option_indices in st.session_state.future_option_to_delete.items():
    for j in sorted(option_indices, reverse=True):
        if i < len(st.session_state.future_trade) and j < len(st.session_state.future_trade[i]["options"]):
            st.session_state.future_trade[i]["options"].pop(j)
st.session_state.future_option_to_delete = {}

# ========== UI ==========
st.title("📈 Greek Offset Calculator")

# ===== held Section =====
st.header("📌 Enter The Trades That You Are Currently Holding")
if st.button("➕ Add Trade to Held Section"):
    add_held_trade()

for i, trade in enumerate(st.session_state.held_trades):
    st.subheader(f"Held Stock Trade {i + 1}")
    if st.button(f"➖ Remove Trade {i + 1}", key=f"remove_held_trade_{i}"):
        st.session_state.held_to_delete = i
        st.rerun()

    cols = st.columns(3)
    trade["quantity"] = cols[0].number_input(f"Quantity {i + 1}", value=trade["quantity"], key=f"hold_qty_{i}")
    trade["avg_price"] = cols[1].number_input(f"AVG Price {i + 1}", value=trade["avg_price"], key=f"hold_avg_{i}")
    trade["total_cost"] = trade["quantity"] * trade["avg_price"]
    cols[2].number_input(f"Total Cost {i + 1}", value=trade["total_cost"], key=f"hold_cost_{i}", disabled=True)

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        option["quantity"] = pcols[0].number_input(f"Option {j + 1} Qty (Held {i + 1})", value=option["quantity"],
                                                   key=f"hold_option_qty_{i}_{j}")
        option["premium"] = pcols[1].number_input(f"Premium {j + 1} (Held {i + 1})", value=option["premium"],
                                                  key=f"hold_option_premium_{i}_{j}")
        option["profit"] = option["quantity"] * option["premium"]
        pcols[2].number_input(f"Profit {j + 1} (Held {i + 1})", value=option["profit"],
                              key=f"hold_option_profit_{i}_{j}", disabled=True)
        if pcols[3].button("➖", key=f"remove_hold_option_{i}_{j}"):
            if i not in st.session_state.held_option_to_delete:
                st.session_state.held_option_to_delete[i] = []
            st.session_state.held_option_to_delete[i].append(j)
            st.rerun()

    if st.button(f"➕ Add Option to Held Trade {i + 1}", key=f"add_hold_option_{i}"):
        st.session_state.add_option_held_index = i
        st.rerun()
    st.markdown("---")

# ===== Sold Section =====
st.header("📌 Enter The Trades That Were Exercised")
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
    trade["sold_price"] = cols[2].number_input(f"Strike Price {i + 1}", value=trade["sold_price"],
                                               key=f"sold_price_{i}")
    trade["profit"] = trade["quantity"] * (trade["sold_price"] - trade["avg_price"])
    cols[3].number_input(f"Profit {i + 1}", value=trade["profit"], key=f"sold_profit_{i}", disabled=True)

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        option["quantity"] = pcols[0].number_input(f"Option {j + 1} Qty (Sold {i + 1})", value=option["quantity"],
                                                   key=f"sold_option_qty_{i}_{j}")
        option["premium"] = pcols[1].number_input(f"Premium {j + 1} (Sold {i + 1})", value=option["premium"],
                                                  key=f"sold_option_premium_{i}_{j}")
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

# ===== Future Section =====
st.header("📌 Enter The Future Trade You Would Like To Place")
if len(st.session_state.future_trade) == 0:
    if st.button("➕ Add Trade to Future Section"):
        add_future_trade()
        st.rerun()

for i, trade in enumerate(st.session_state.future_trade):
    if st.button(f"➖ Remove Trade", key=f"remove_future_trade"):
        st.session_state.future_to_delete = i
        st.rerun()

    cols = st.columns(5)
    trade["quantity"] = cols[0].number_input(f"Quantity", value=trade["quantity"], key=f"future_qty")
    trade["avg_price"] = cols[1].number_input(f"AVG Price", value=trade["avg_price"], key=f"future_avg")
    trade["total_cost"] = trade["quantity"] * trade["avg_price"]
    cols[2].number_input(f"Total Cost", value=trade["total_cost"], key=f"future_cost", disabled=True)
    trade["sold_price"] = cols[3].number_input(f"Strike Price", value=trade["sold_price"], key=f"future_sold_price")
    trade["profit"] = trade["quantity"] * (trade["sold_price"] - trade["avg_price"])
    cols[4].number_input(f"Profit", value=trade["profit"], key=f"future_sold_profit", disabled=True)

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        option["quantity"] = pcols[0].number_input(f"Option Qty", value=option["quantity"],
                                                   key=f"future_option_qty_{j}")
        option["premium"] = pcols[1].number_input(f"Premium", value=option["premium"], key=f"future_option_premium_{j}")
        option["profit"] = option["quantity"] * option["premium"]
        pcols[2].number_input(f"Profit", value=option["profit"], key=f"future_option_profit_{j}", disabled=True)
        if pcols[3].button("➖", key=f"remove_future_option_{j}"):
            if i not in st.session_state.future_option_to_delete:
                st.session_state.future_option_to_delete[i] = []
            st.session_state.future_option_to_delete[i].append(j)
            st.rerun()

    if len(trade["options"]) == 0:
        if st.button(f"➕ Add Option to Future Trade", key=f"add_future_option"):
            st.session_state.add_option_future_index = i
            st.rerun()
    st.markdown("---")

st.markdown("---")

# ==================== CORRECTED CALCULATION BLOCK ====================
# We sum directly from session_state widget keys to avoid Render latency issues.
col1, col2 = st.columns(2)

with col1:
    st.header("📊 Trades Summary If Future Trade Is Exercised")

    # Accessing widget keys directly via st.session_state.get()
    q_held = sum(st.session_state.get(f"hold_qty_{i}", 0) for i in range(len(st.session_state.held_trades)))
    c_held = sum(st.session_state.get(f"hold_qty_{i}", 0) * st.session_state.get(f"hold_avg_{i}", 0.0) for i in
                 range(len(st.session_state.held_trades)))

    # Sum all option profits from Held, Sold, and Future sections
    opt_prof = sum(
        st.session_state.get(f"hold_option_qty_{i}_{j}", 0) * st.session_state.get(f"hold_option_premium_{i}_{j}", 0.0)
        for i, t in enumerate(st.session_state.held_trades) for j in range(len(t["options"])))
    opt_prof += sum(
        st.session_state.get(f"sold_option_qty_{i}_{j}", 0) * st.session_state.get(f"sold_option_premium_{i}_{j}", 0.0)
        for i, t in enumerate(st.session_state.sold_trades) for j in range(len(t["options"])))
    opt_prof += sum(
        st.session_state.get(f"future_option_qty_{j}", 0) * st.session_state.get(f"future_option_premium_{j}", 0.0) for
        t in st.session_state.future_trade for j in range(len(t["options"])))

    sold_stock_prof = sum(st.session_state.get(f"sold_qty_{i}", 0) * (
                st.session_state.get(f"sold_price_{i}", 0.0) - st.session_state.get(f"sold_avg_{i}", 0.0)) for i in
                          range(len(st.session_state.sold_trades)))
    future_stock_prof = sum(st.session_state.get(f"future_qty", 0) * (
                st.session_state.get(f"future_sold_price", 0.0) - st.session_state.get(f"future_avg", 0.0)) for _ in
                            st.session_state.future_trade)

    total_prof_exer = opt_prof + sold_stock_prof + future_stock_prof
    be_price_exer = (c_held - total_prof_exer) / q_held if q_held > 0 else 0.0

    st.markdown(f"**Total Quantity of Shares:** {q_held}")
    st.markdown(f"**Total Cost:** ${c_held:,.2f}")
    st.markdown(f"**Total Profit:** ${total_prof_exer:,.2f}")
    st.success(f"**Breakeven Price:** ${be_price_exer:,.2f}")

    st.markdown("---")
    st.header("📉 Selling the Shares If Future Trade Is Exercised")
    sell_price_exer = st.number_input("**Selling Price**", min_value=0.0, step=0.01, key="selling_price_exer")
    curr_val_exer = q_held * sell_price_exer
    adj_cost_exer = c_held - total_prof_exer
    net_pl_exer = curr_val_exer - adj_cost_exer
    pl_pct_exer = (net_pl_exer / adj_cost_exer * 100) if adj_cost_exer != 0 else 0.0
    st.markdown(f"**Current Shares Value:** ${curr_val_exer:,.2f}")
    st.markdown(f"**Adjusted Cost:** ${adj_cost_exer:,.2f}")
    st.success(f"**Net Profit/Loss:** ${net_pl_exer:,.2f}")
    st.success(f"**Profit/Loss Percentage:** {pl_pct_exer:.2f}%")

with col2:
    st.header("📊 Trades Summary If Future Trade Is NOT Exercised")
    q_not = q_held + sum(st.session_state.get(f"future_qty", 0) for _ in st.session_state.future_trade)
    c_not = c_held + sum(st.session_state.get(f"future_qty", 0) * st.session_state.get(f"future_avg", 0.0) for _ in
                         st.session_state.future_trade)

    total_prof_not = opt_prof + sold_stock_prof
    be_price_not = (c_not - total_prof_not) / q_not if q_not > 0 else 0.0

    st.markdown(f"**Total Quantity of Shares:** {q_not}")
    st.markdown(f"**Total Cost:** ${c_not:,.2f}")
    st.markdown(f"**Total Profit:** ${total_prof_not:,.2f}")
    st.success(f"**Breakeven Price:** ${be_price_not:,.2f}")

    st.markdown("---")
    st.header("📉 Selling the Shares If Future Trade Is NOT Exercised")
    sell_price_not = st.number_input("**Selling Price**", min_value=0.0, step=0.01, key="selling_price_not_exer")
    curr_val_not = q_not * sell_price_not
    adj_cost_not = c_not - total_prof_not
    net_pl_not = curr_val_not - adj_cost_not
    pl_pct_not = (net_pl_not / adj_cost_not * 100) if adj_cost_not != 0 else 0.0
    st.markdown(f"**Current Shares Value:** ${curr_val_not:,.2f}")
    st.markdown(f"**Adjusted Cost:** ${adj_cost_not:,.2f}")
    st.success(f"**Net Profit/Loss:** ${net_pl_not:,.2f}")
    st.success(f"**Profit/Loss Percentage:** {pl_pct_not:.2f}%")
