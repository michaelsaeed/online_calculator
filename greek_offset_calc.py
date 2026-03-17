import streamlit as st

st.set_page_config(page_title="Greek Offset Calculator", layout="wide")

# ========== Session Initialization ==========
if "held_trades" not in st.session_state:
    st.session_state.held_trades = []

if "sold_trades" not in st.session_state:
    st.session_state.sold_trades = []

if "future_trade" not in st.session_state:
    st.session_state.future_trade = []

# Initialize deletion trackers if they don't exist
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


# Callback functions for held trades
def update_held_quantity(i):
    st.session_state.held_trades[i]["quantity"] = st.session_state[f"hold_qty_{i}"]
    st.session_state.held_trades[i]["total_cost"] = st.session_state.held_trades[i]["quantity"] * st.session_state.held_trades[i]["avg_price"]

def update_held_avg_price(i):
    st.session_state.held_trades[i]["avg_price"] = st.session_state[f"hold_avg_{i}"]
    st.session_state.held_trades[i]["total_cost"] = st.session_state.held_trades[i]["quantity"] * st.session_state.held_trades[i]["avg_price"]

def update_held_option_qty(i, j):
    st.session_state.held_trades[i]["options"][j]["quantity"] = st.session_state[f"hold_option_qty_{i}_{j}"]
    st.session_state.held_trades[i]["options"][j]["profit"] = st.session_state.held_trades[i]["options"][j]["quantity"] * st.session_state.held_trades[i]["options"][j]["premium"]

def update_held_option_premium(i, j):
    st.session_state.held_trades[i]["options"][j]["premium"] = st.session_state[f"hold_option_premium_{i}_{j}"]
    st.session_state.held_trades[i]["options"][j]["profit"] = st.session_state.held_trades[i]["options"][j]["quantity"] * st.session_state.held_trades[i]["options"][j]["premium"]

# Callback functions for sold trades
def update_sold_quantity(i):
    st.session_state.sold_trades[i]["quantity"] = st.session_state[f"sold_qty_{i}"]
    st.session_state.sold_trades[i]["profit"] = st.session_state.sold_trades[i]["quantity"] * (st.session_state.sold_trades[i]["sold_price"] - st.session_state.sold_trades[i]["avg_price"])

def update_sold_avg_price(i):
    st.session_state.sold_trades[i]["avg_price"] = st.session_state[f"sold_avg_{i}"]
    st.session_state.sold_trades[i]["profit"] = st.session_state.sold_trades[i]["quantity"] * (st.session_state.sold_trades[i]["sold_price"] - st.session_state.sold_trades[i]["avg_price"])

def update_sold_price(i):
    st.session_state.sold_trades[i]["sold_price"] = st.session_state[f"sold_price_{i}"]
    st.session_state.sold_trades[i]["profit"] = st.session_state.sold_trades[i]["quantity"] * (st.session_state.sold_trades[i]["sold_price"] - st.session_state.sold_trades[i]["avg_price"])

def update_sold_option_qty(i, j):
    st.session_state.sold_trades[i]["options"][j]["quantity"] = st.session_state[f"sold_option_qty_{i}_{j}"]
    st.session_state.sold_trades[i]["options"][j]["profit"] = st.session_state.sold_trades[i]["options"][j]["quantity"] * st.session_state.sold_trades[i]["options"][j]["premium"]

def update_sold_option_premium(i, j):
    st.session_state.sold_trades[i]["options"][j]["premium"] = st.session_state[f"sold_option_premium_{i}_{j}"]
    st.session_state.sold_trades[i]["options"][j]["profit"] = st.session_state.sold_trades[i]["options"][j]["quantity"] * st.session_state.sold_trades[i]["options"][j]["premium"]

# Callback functions for future trades
def update_future_quantity(i):
    st.session_state.future_trade[i]["quantity"] = st.session_state[f"future_qty"]
    st.session_state.future_trade[i]["total_cost"] = st.session_state.future_trade[i]["quantity"] * st.session_state.future_trade[i]["avg_price"]
    st.session_state.future_trade[i]["profit"] = st.session_state.future_trade[i]["quantity"] * (st.session_state.future_trade[i]["sold_price"] - st.session_state.future_trade[i]["avg_price"])

def update_future_avg_price(i):
    st.session_state.future_trade[i]["avg_price"] = st.session_state[f"future_avg"]
    st.session_state.future_trade[i]["total_cost"] = st.session_state.future_trade[i]["quantity"] * st.session_state.future_trade[i]["avg_price"]
    st.session_state.future_trade[i]["profit"] = st.session_state.future_trade[i]["quantity"] * (st.session_state.future_trade[i]["sold_price"] - st.session_state.future_trade[i]["avg_price"])

def update_future_sold_price(i):
    st.session_state.future_trade[i]["sold_price"] = st.session_state[f"future_sold_price"]
    st.session_state.future_trade[i]["profit"] = st.session_state.future_trade[i]["quantity"] * (st.session_state.future_trade[i]["sold_price"] - st.session_state.future_trade[i]["avg_price"])

def update_future_option_qty(i, j):
    st.session_state.future_trade[i]["options"][j]["quantity"] = st.session_state[f"future_option_qty_{j}"]
    st.session_state.future_trade[i]["options"][j]["profit"] = st.session_state.future_trade[i]["options"][j]["quantity"] * st.session_state.future_trade[i]["options"][j]["premium"]

def update_future_option_premium(i, j):
    st.session_state.future_trade[i]["options"][j]["premium"] = st.session_state[f"future_option_premium_{j}"]
    st.session_state.future_trade[i]["options"][j]["profit"] = st.session_state.future_trade[i]["options"][j]["quantity"] * st.session_state.future_trade[i]["options"][j]["premium"]


def add_held_trade():
    st.session_state.held_trades.append({
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

def add_future_trade():
    st.session_state.future_trade.append({
        "quantity": 0,
        "avg_price": 0.0,
        "total_cost": 0.0,
        "sold_price": 0.0,
        "profit": 0.0,
        "options": []
    })

def add_held_option(i):
    st.session_state.held_trades[i]["options"].append({
        "quantity": st.session_state.held_trades[i]["quantity"],
        "premium": 0.0,
        "profit": 0.0
    })

def add_sold_option(i):
    st.session_state.sold_trades[i]["options"].append({
        "quantity": st.session_state.sold_trades[i]["quantity"],
        "premium": 0.0,
        "profit": 0.0
    })

def add_future_option(i):
    st.session_state.future_trade[i]["options"].append({
        "quantity": st.session_state.future_trade[i]["quantity"],
        "premium": 0.0,
        "profit": 0.0
    })


# Apply deletions at the start of script execution
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
    
    cols[0].number_input(f"Quantity {i + 1}", 
                        value=trade["quantity"], 
                        key=f"hold_qty_{i}",
                        on_change=update_held_quantity,
                        args=(i,))
    
    cols[1].number_input(f"AVG Price {i + 1}", 
                        value=trade["avg_price"], 
                        key=f"hold_avg_{i}", 
                        format="%.2f",
                        on_change=update_held_avg_price,
                        args=(i,))

    cols[2].number_input(f"Total Cost {i + 1}", 
                        value=trade["total_cost"], 
                        key=f"hold_cost_{i}", 
                        disabled=True, 
                        format="%.2f")

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        
        pcols[0].number_input(f"Option {j + 1} Qty (Held {i + 1})", 
                             value=option["quantity"],
                             key=f"hold_option_qty_{i}_{j}",
                             on_change=update_held_option_qty,
                             args=(i, j))
        
        pcols[1].number_input(f"Premium {j + 1} (Held {i + 1})", 
                             value=option["premium"],
                             key=f"hold_option_premium_{i}_{j}", 
                             format="%.2f",
                             on_change=update_held_option_premium,
                             args=(i, j))
        
        pcols[2].number_input(f"Profit {j + 1} (Held {i + 1})", 
                             value=option["profit"],
                             key=f"hold_option_profit_{i}_{j}", 
                             disabled=True, 
                             format="%.2f")

        if pcols[3].button("➖", key=f"remove_hold_option_{i}_{j}"):
            if i not in st.session_state.held_option_to_delete:
                st.session_state.held_option_to_delete[i] = []
            st.session_state.held_option_to_delete[i].append(j)
            st.rerun()

    if st.button(f"➕ Add Option to Held Trade {i + 1}", key=f"add_hold_option_{i}"):
        add_held_option(i)
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
    
    cols[0].number_input(f"Quantity {i + 1} (Sold)", 
                        value=trade["quantity"], 
                        key=f"sold_qty_{i}",
                        on_change=update_sold_quantity,
                        args=(i,))
    
    cols[1].number_input(f"AVG Price {i + 1} (Sold)", 
                        value=trade["avg_price"],
                        key=f"sold_avg_{i}", 
                        format="%.2f",
                        on_change=update_sold_avg_price,
                        args=(i,))
    
    cols[2].number_input(f"Strike Price {i + 1}", 
                        value=trade["sold_price"], 
                        key=f"sold_price_{i}", 
                        format="%.2f",
                        on_change=update_sold_price,
                        args=(i,))

    cols[3].number_input(f"Profit {i + 1}", 
                        value=trade["profit"], 
                        key=f"sold_profit_{i}", 
                        disabled=True, 
                        format="%.2f")

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        
        pcols[0].number_input(f"Option {j + 1} Qty (Sold {i + 1})", 
                             value=option["quantity"],
                             key=f"sold_option_qty_{i}_{j}",
                             on_change=update_sold_option_qty,
                             args=(i, j))
        
        pcols[1].number_input(f"Premium {j + 1} (Sold {i + 1})", 
                             value=option["premium"],
                             key=f"sold_option_premium_{i}_{j}", 
                             format="%.2f",
                             on_change=update_sold_option_premium,
                             args=(i, j))

        pcols[2].number_input(f"Profit {j + 1} (Sold {i + 1})", 
                             value=option["profit"],
                             key=f"sold_option_profit_{i}_{j}", 
                             disabled=True, 
                             format="%.2f")

        if pcols[3].button("➖", key=f"remove_sold_option_{i}_{j}"):
            if i not in st.session_state.sold_option_to_delete:
                st.session_state.sold_option_to_delete[i] = []
            st.session_state.sold_option_to_delete[i].append(j)
            st.rerun()

    if st.button(f"➕ Add Option to Sold Trade {i + 1}", key=f"add_sold_option_{i}"):
        add_sold_option(i)
        st.rerun()

    st.markdown("---")

st.markdown("---")

# ===== Future Section =====
st.header("📌 Enter The Future Trade You Would Like To Place")

# Allow only ONE trade
if len(st.session_state.future_trade) == 0:
    if st.button("➕ Add Trade to Future Section"):
        add_future_trade()
        st.rerun()

for i, trade in enumerate(st.session_state.future_trade):

    if st.button(f"➖ Remove Trade", key=f"remove_future_trade"):
        st.session_state.future_to_delete = i
        st.rerun()

    cols = st.columns(5)
    
    cols[0].number_input(f"Quantity", 
                        value=trade["quantity"], 
                        key=f"future_qty",
                        on_change=update_future_quantity,
                        args=(i,))
    
    cols[1].number_input(f"AVG Price", 
                        value=trade["avg_price"], 
                        key=f"future_avg", 
                        format="%.2f",
                        on_change=update_future_avg_price,
                        args=(i,))

    cols[2].number_input(f"Total Cost", 
                        value=trade["total_cost"], 
                        key=f"future_cost", 
                        disabled=True, 
                        format="%.2f")

    cols[3].number_input(f"Strike Price", 
                        value=trade["sold_price"], 
                        key=f"future_sold_price", 
                        format="%.2f",
                        on_change=update_future_sold_price,
                        args=(i,))

    cols[4].number_input(f"Profit", 
                        value=trade["profit"], 
                        key=f"future_sold_profit", 
                        disabled=True, 
                        format="%.2f")

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        
        pcols[0].number_input(f"Option Qty", 
                             value=option["quantity"],
                             key=f"future_option_qty_{j}",
                             on_change=update_future_option_qty,
                             args=(i, j))
        
        pcols[1].number_input(f"Premium", 
                             value=option["premium"],
                             key=f"future_option_premium_{j}", 
                             format="%.2f",
                             on_change=update_future_option_premium,
                             args=(i, j))

        pcols[2].number_input(f"Profit", 
                             value=option["profit"],
                             key=f"future_option_profit_{j}", 
                             disabled=True, 
                             format="%.2f")

        if pcols[3].button("➖", key=f"remove_future_option_{j}"):
            if i not in st.session_state.future_option_to_delete:
                st.session_state.future_option_to_delete[i] = []
            st.session_state.future_option_to_delete[i].append(j)
            st.rerun()

    # Allow only ONE option
    if len(trade["options"]) == 0:
        if st.button(f"➕ Add Option to Future Trade", key=f"add_future_option"):
            add_future_option(i)
            st.rerun()

    st.markdown("---")

st.markdown("---")

col1, col2 = st.columns(2)

# ===== Left Column =====
with col1:
    st.header("📊 Trades Summary If Future Trade Is Exercised")

    # Calculate totals
    total_quantity_exer = sum(trade["quantity"] for trade in st.session_state.held_trades)
    total_cost_exer = sum(trade["total_cost"] for trade in st.session_state.held_trades)

    total_option_profit = sum(
        option["profit"]
        for trade in st.session_state.held_trades + st.session_state.sold_trades + st.session_state.future_trade
        for option in trade["options"]
    )

    total_sold_profit = sum(trade["profit"] for trade in st.session_state.sold_trades)
    total_future_sold_profit = sum(trade["profit"] for trade in st.session_state.future_trade)
    total_profit = total_option_profit + total_sold_profit + total_future_sold_profit

    # Avoid division by zero
    if total_quantity_exer > 0:
        breakeven_price = (total_cost_exer - total_profit) / total_quantity_exer
    else:
        breakeven_price = 0.0

    st.markdown(f"**Total Quantity of Shares:** {total_quantity_exer}")
    st.markdown(f"**Total Cost:** ${total_cost_exer:,.2f}")
    st.markdown(f"**Total Profit:** ${total_profit:,.2f}")
    st.success(f"**Breakeven Price:** ${breakeven_price:,.2f}")

    st.markdown("---")

    st.header("📉 Selling the Shares If Future Trade Is Exercised")
    st.markdown("<h4>Note: In case of making a change in the above trades, re-enter the Selling Price for updated calculations.</h4>", unsafe_allow_html=True)

    selling_price_exer = st.number_input("**Selling Price**", min_value=0.0, step=0.01, key="selling_price_exer", format="%.2f")

    current_value_exer = total_quantity_exer * selling_price_exer
    adjusted_cost_exer = total_cost_exer - total_profit
    net_profit_loss_exer = current_value_exer - adjusted_cost_exer
    profit_loss_pct_exer = (net_profit_loss_exer / adjusted_cost_exer * 100) if adjusted_cost_exer != 0 else 0.0

    st.markdown(f"**Current Shares Value:** ${current_value_exer:,.2f}")
    st.markdown(f"**Adjusted Cost:** ${adjusted_cost_exer:,.2f}")
    st.success(f"**Net Profit/Loss:** ${net_profit_loss_exer:,.2f}")
    st.success(f"**Profit/Loss Percentage:** {profit_loss_pct_exer:.2f}%")

# ===== Right Column =====
with col2:
    st.header("📊 Trades Summary If Future Trade Is NOT Exercised")

    # Calculate totals
    total_quantity_not_exer = sum(trade["quantity"] for trade in st.session_state.held_trades + st.session_state.future_trade)
    total_cost_not_exer = sum(trade["total_cost"] for trade in st.session_state.held_trades + st.session_state.future_trade)

    total_option_profit = sum(
        option["profit"]
        for trade in st.session_state.held_trades + st.session_state.sold_trades + st.session_state.future_trade
        for option in trade["options"]
    )

    total_sold_profit = sum(trade["profit"] for trade in st.session_state.sold_trades)
    total_profit = total_option_profit + total_sold_profit

    # Avoid division by zero
    if total_quantity_not_exer > 0:
        breakeven_price = (total_cost_not_exer - total_profit) / total_quantity_not_exer
    else:
        breakeven_price = 0.0

    st.markdown(f"**Total Quantity of Shares:** {total_quantity_not_exer}")
    st.markdown(f"**Total Cost:** ${total_cost_not_exer:,.2f}")
    st.markdown(f"**Total Profit:** ${total_profit:,.2f}")
    st.success(f"**Breakeven Price:** ${breakeven_price:,.2f}")

    st.markdown("---")

    st.header("📉 Selling the Shares If Future Trade Is NOT Exercised")
    st.markdown("<h4>Note: In case of making a change in the above trades, re-enter the Selling Price for updated calculations.</h4>", unsafe_allow_html=True)

    selling_price_not_exer = st.number_input("**Selling Price**", min_value=0.0, step=0.01, key="selling_price_not_exer", format="%.2f")

    current_value_not_exer = total_quantity_not_exer * selling_price_not_exer
    adjusted_cost_not_exer = total_cost_not_exer - total_profit
    net_profit_loss_not_exer = current_value_not_exer - adjusted_cost_not_exer
    profit_loss_pct_not_exer = (net_profit_loss_not_exer / adjusted_cost_not_exer * 100) if adjusted_cost_not_exer != 0 else 0.0

    st.markdown(f"**Current Shares Value:** ${current_value_not_exer:,.2f}")
    st.markdown(f"**Adjusted Cost:** ${adjusted_cost_not_exer:,.2f}")
    st.success(f"**Net Profit/Loss:** ${net_profit_loss_not_exer:,.2f}")
    st.success(f"**Profit/Loss Percentage:** {profit_loss_pct_not_exer:.2f}%")
