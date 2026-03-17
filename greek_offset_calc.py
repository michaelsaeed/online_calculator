import streamlit as st

st.set_page_config(page_title="Greek Offset Calculator", layout="wide")

# ========== Session Initialization - MINIMAL ==========
if "held_trades" not in st.session_state:
    st.session_state.held_trades = []

if "sold_trades" not in st.session_state:
    st.session_state.sold_trades = []

if "future_trade" not in st.session_state:
    st.session_state.future_trade = []

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
    st.session_state.held_trades.append({
        "quantity": 0,
        "avg_price": 0.0,
        "options": []
    })


def add_sold_trade():
    st.session_state.sold_trades.append({
        "quantity": 0,
        "avg_price": 0.0,
        "sold_price": 0.0,
        "options": []
    })


def add_future_trade():
    st.session_state.future_trade.append({
        "quantity": 0,
        "avg_price": 0.0,
        "sold_price": 0.0,
        "options": []
    })


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
    st.rerun()

for i, trade in enumerate(st.session_state.held_trades):
    st.subheader(f"Held Stock Trade {i + 1}")

    if st.button(f"➖ Remove Trade {i + 1}", key=f"remove_held_trade_{i}"):
        st.session_state.held_to_delete = i
        st.rerun()

    cols = st.columns(3)

    # Store values directly in session state with unique keys
    quantity_key = f"hold_qty_{i}"
    price_key = f"hold_avg_{i}"

    # Get current values from trade or use defaults
    current_qty = trade.get("quantity", 0)
    current_price = trade.get("avg_price", 0.0)

    # Input fields
    new_qty = cols[0].number_input(f"Quantity {i + 1}", value=current_qty, key=quantity_key)
    new_price = cols[1].number_input(f"AVG Price {i + 1}", value=current_price, key=price_key, format="%.2f")

    # Update trade dictionary with new values
    trade["quantity"] = new_qty
    trade["avg_price"] = new_price

    # Calculate and display total cost
    total_cost = new_qty * new_price
    cols[2].number_input(f"Total Cost {i + 1}", value=total_cost, key=f"hold_cost_{i}", disabled=True, format="%.2f")

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade.get("options", [])):
        pcols = st.columns(4)

        opt_qty_key = f"hold_option_qty_{i}_{j}"
        opt_prem_key = f"hold_option_premium_{i}_{j}"

        current_opt_qty = option.get("quantity", 0)
        current_opt_prem = option.get("premium", 0.0)

        new_opt_qty = pcols[0].number_input(f"Option {j + 1} Qty", value=current_opt_qty, key=opt_qty_key)
        new_opt_prem = pcols[1].number_input(f"Premium {j + 1}", value=current_opt_prem, key=opt_prem_key,
                                             format="%.2f")

        # Update option dictionary
        option["quantity"] = new_opt_qty
        option["premium"] = new_opt_prem

        # Calculate and display option profit
        opt_profit = new_opt_qty * new_opt_prem
        pcols[2].number_input(f"Profit {j + 1}", value=opt_profit, key=f"hold_option_profit_{i}_{j}", disabled=True,
                              format="%.2f")

        if pcols[3].button("➖", key=f"remove_hold_option_{i}_{j}"):
            if i not in st.session_state.held_option_to_delete:
                st.session_state.held_option_to_delete[i] = []
            st.session_state.held_option_to_delete[i].append(j)
            st.rerun()

    if st.button(f"➕ Add Option to Held Trade {i + 1}", key=f"add_hold_option_{i}"):
        if "options" not in trade:
            trade["options"] = []
        trade["options"].append({"quantity": 0, "premium": 0.0})
        st.rerun()

    st.markdown("---")

st.markdown("---")

# ===== Sold Section =====
st.header("📌 Enter The Trades That Were Exercised")

if st.button("➕ Add Trade to Sold Section"):
    add_sold_trade()
    st.rerun()

for i, trade in enumerate(st.session_state.sold_trades):
    st.subheader(f"Sold Trade {i + 1}")

    if st.button(f"➖ Remove Sold Trade {i + 1}", key=f"remove_sold_trade_{i}"):
        st.session_state.sold_to_delete = i
        st.rerun()

    cols = st.columns(4)

    qty_key = f"sold_qty_{i}"
    avg_key = f"sold_avg_{i}"
    strike_key = f"sold_price_{i}"

    current_qty = trade.get("quantity", 0)
    current_avg = trade.get("avg_price", 0.0)
    current_strike = trade.get("sold_price", 0.0)

    new_qty = cols[0].number_input(f"Quantity {i + 1}", value=current_qty, key=qty_key)
    new_avg = cols[1].number_input(f"AVG Price {i + 1}", value=current_avg, key=avg_key, format="%.2f")
    new_strike = cols[2].number_input(f"Strike Price {i + 1}", value=current_strike, key=strike_key, format="%.2f")

    trade["quantity"] = new_qty
    trade["avg_price"] = new_avg
    trade["sold_price"] = new_strike

    # Calculate and display profit
    profit = new_qty * (new_strike - new_avg)
    cols[3].number_input(f"Profit {i + 1}", value=profit, key=f"sold_profit_{i}", disabled=True, format="%.2f")

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade.get("options", [])):
        pcols = st.columns(4)

        opt_qty_key = f"sold_option_qty_{i}_{j}"
        opt_prem_key = f"sold_option_premium_{i}_{j}"

        current_opt_qty = option.get("quantity", 0)
        current_opt_prem = option.get("premium", 0.0)

        new_opt_qty = pcols[0].number_input(f"Option {j + 1} Qty", value=current_opt_qty, key=opt_qty_key)
        new_opt_prem = pcols[1].number_input(f"Premium {j + 1}", value=current_opt_prem, key=opt_prem_key,
                                             format="%.2f")

        option["quantity"] = new_opt_qty
        option["premium"] = new_opt_prem

        opt_profit = new_opt_qty * new_opt_prem
        pcols[2].number_input(f"Profit {j + 1}", value=opt_profit, key=f"sold_option_profit_{i}_{j}", disabled=True,
                              format="%.2f")

        if pcols[3].button("➖", key=f"remove_sold_option_{i}_{j}"):
            if i not in st.session_state.sold_option_to_delete:
                st.session_state.sold_option_to_delete[i] = []
            st.session_state.sold_option_to_delete[i].append(j)
            st.rerun()

    if st.button(f"➕ Add Option to Sold Trade {i + 1}", key=f"add_sold_option_{i}"):
        if "options" not in trade:
            trade["options"] = []
        trade["options"].append({"quantity": 0, "premium": 0.0})
        st.rerun()

    st.markdown("---")

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

    qty_key = "future_qty"
    avg_key = "future_avg"
    strike_key = "future_sold_price"

    current_qty = trade.get("quantity", 0)
    current_avg = trade.get("avg_price", 0.0)
    current_strike = trade.get("sold_price", 0.0)

    new_qty = cols[0].number_input("Quantity", value=current_qty, key=qty_key)
    new_avg = cols[1].number_input("AVG Price", value=current_avg, key=avg_key, format="%.2f")

    trade["quantity"] = new_qty
    trade["avg_price"] = new_avg

    total_cost = new_qty * new_avg
    cols[2].number_input("Total Cost", value=total_cost, key="future_cost", disabled=True, format="%.2f")

    new_strike = cols[3].number_input("Strike Price", value=current_strike, key=strike_key, format="%.2f")
    trade["sold_price"] = new_strike

    profit = new_qty * (new_strike - new_avg)
    cols[4].number_input("Profit", value=profit, key="future_sold_profit", disabled=True, format="%.2f")

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade.get("options", [])):
        pcols = st.columns(4)

        opt_qty_key = f"future_option_qty_{j}"
        opt_prem_key = f"future_option_premium_{j}"

        current_opt_qty = option.get("quantity", 0)
        current_opt_prem = option.get("premium", 0.0)

        new_opt_qty = pcols[0].number_input("Option Qty", value=current_opt_qty, key=opt_qty_key)
        new_opt_prem = pcols[1].number_input("Premium", value=current_opt_prem, key=opt_prem_key, format="%.2f")

        option["quantity"] = new_opt_qty
        option["premium"] = new_opt_prem

        opt_profit = new_opt_qty * new_opt_prem
        pcols[2].number_input("Profit", value=opt_profit, key=f"future_option_profit_{j}", disabled=True, format="%.2f")

        if pcols[3].button("➖", key=f"remove_future_option_{j}"):
            if i not in st.session_state.future_option_to_delete:
                st.session_state.future_option_to_delete[i] = []
            st.session_state.future_option_to_delete[i].append(j)
            st.rerun()

    if len(trade.get("options", [])) == 0:
        if st.button("➕ Add Option to Future Trade", key="add_future_option"):
            if "options" not in trade:
                trade["options"] = []
            trade["options"].append({"quantity": 0, "premium": 0.0})
            st.rerun()

    st.markdown("---")

st.markdown("---")


# ===== Helper function to calculate totals =====
def calculate_totals():
    """Calculate all totals from current session state"""

    # Held trades totals
    held_qty = sum(trade.get("quantity", 0) for trade in st.session_state.held_trades)
    held_cost = sum(trade.get("quantity", 0) * trade.get("avg_price", 0) for trade in st.session_state.held_trades)

    # Option profits from all sections
    option_profit = 0
    for trade in st.session_state.held_trades:
        for option in trade.get("options", []):
            option_profit += option.get("quantity", 0) * option.get("premium", 0)

    for trade in st.session_state.sold_trades:
        for option in trade.get("options", []):
            option_profit += option.get("quantity", 0) * option.get("premium", 0)

    for trade in st.session_state.future_trade:
        for option in trade.get("options", []):
            option_profit += option.get("quantity", 0) * option.get("premium", 0)

    # Sold trades profit
    sold_profit = 0
    for trade in st.session_state.sold_trades:
        qty = trade.get("quantity", 0)
        sold_profit += qty * (trade.get("sold_price", 0) - trade.get("avg_price", 0))

    # Future trade profit
    future_profit = 0
    for trade in st.session_state.future_trade:
        qty = trade.get("quantity", 0)
        future_profit += qty * (trade.get("sold_price", 0) - trade.get("avg_price", 0))

    # Future + Held qty and cost
    future_held_qty = held_qty
    future_held_cost = held_cost
    for trade in st.session_state.future_trade:
        future_held_qty += trade.get("quantity", 0)
        future_held_cost += trade.get("quantity", 0) * trade.get("avg_price", 0)

    return {
        "held_qty": held_qty,
        "held_cost": held_cost,
        "option_profit": option_profit,
        "sold_profit": sold_profit,
        "future_profit": future_profit,
        "future_held_qty": future_held_qty,
        "future_held_cost": future_held_cost
    }


# Get current totals
totals = calculate_totals()

col1, col2 = st.columns(2)

# ===== Left Column =====
with col1:
    st.header("📊 Trades Summary If Future Trade Is Exercised")

    total_profit_exer = totals["option_profit"] + totals["sold_profit"] + totals["future_profit"]

    st.markdown(f"**Total Quantity of Shares:** {totals['held_qty']}")
    st.markdown(f"**Total Cost:** ${totals['held_cost']:,.2f}")
    st.markdown(f"**Total Profit:** ${total_profit_exer:,.2f}")

    if totals['held_qty'] > 0:
        breakeven = (totals['held_cost'] - total_profit_exer) / totals['held_qty']
        st.success(f"**Breakeven Price:** ${breakeven:,.2f}")
    else:
        st.success(f"**Breakeven Price:** $0.00")

    st.markdown("---")

    st.header("📉 Selling the Shares If Future Trade Is Exercised")
    st.markdown(
        "<h4>Note: In case of making a change in the above trades, re-enter the Selling Price for updated calculations.</h4>",
        unsafe_allow_html=True)

    selling_price_exer = st.number_input("**Selling Price**", min_value=0.0, step=0.01, key="selling_price_exer",
                                         format="%.2f")

    current_value = totals['held_qty'] * selling_price_exer
    adjusted_cost = totals['held_cost'] - total_profit_exer
    net_pl = current_value - adjusted_cost
    pl_pct = (net_pl / adjusted_cost * 100) if adjusted_cost != 0 else 0.0

    st.markdown(f"**Current Shares Value:** ${current_value:,.2f}")
    st.markdown(f"**Adjusted Cost:** ${adjusted_cost:,.2f}")
    st.success(f"**Net Profit/Loss:** ${net_pl:,.2f}")
    st.success(f"**Profit/Loss Percentage:** {pl_pct:.2f}%")

# ===== Right Column =====
with col2:
    st.header("📊 Trades Summary If Future Trade Is NOT Exercised")

    total_profit_not_exer = totals["option_profit"] + totals["sold_profit"]

    st.markdown(f"**Total Quantity of Shares:** {totals['future_held_qty']}")
    st.markdown(f"**Total Cost:** ${totals['future_held_cost']:,.2f}")
    st.markdown(f"**Total Profit:** ${total_profit_not_exer:,.2f}")

    if totals['future_held_qty'] > 0:
        breakeven = (totals['future_held_cost'] - total_profit_not_exer) / totals['future_held_qty']
        st.success(f"**Breakeven Price:** ${breakeven:,.2f}")
    else:
        st.success(f"**Breakeven Price:** $0.00")

    st.markdown("---")

    st.header("📉 Selling the Shares If Future Trade Is NOT Exercised")
    st.markdown(
        "<h4>Note: In case of making a change in the above trades, re-enter the Selling Price for updated calculations.</h4>",
        unsafe_allow_html=True)

    selling_price_not_exer = st.number_input("**Selling Price**", min_value=0.0, step=0.01,
                                             key="selling_price_not_exer", format="%.2f")

    current_value = totals['future_held_qty'] * selling_price_not_exer
    adjusted_cost = totals['future_held_cost'] - total_profit_not_exer
    net_pl = current_value - adjusted_cost
    pl_pct = (net_pl / adjusted_cost * 100) if adjusted_cost != 0 else 0.0

    st.markdown(f"**Current Shares Value:** ${current_value:,.2f}")
    st.markdown(f"**Adjusted Cost:** ${adjusted_cost:,.2f}")
    st.success(f"**Net Profit/Loss:** ${net_pl:,.2f}")
    st.success(f"**Profit/Loss Percentage:** {pl_pct:.2f}%")
