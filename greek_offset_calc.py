import streamlit as st
import json

st.set_page_config(page_title="Greek Offset Calculator", layout="wide")

# ========== Initialize from query params ==========
def load_from_params():
    """Load data from URL query parameters"""
    params = st.query_params
    
    if "data" in params:
        try:
            data = json.loads(params["data"])
            return data
        except:
            return {"held": [], "sold": [], "future": []}
    return {"held": [], "sold": [], "future": []}

def save_to_params(data):
    """Save data to URL query parameters"""
    st.query_params["data"] = json.dumps(data)

# Initialize or load data
if "data_loaded" not in st.session_state:
    st.session_state.data = load_from_params()
    st.session_state.data_loaded = True

# ========== UI State Management ==========
def update_url():
    """Update URL with current data"""
    save_to_params(st.session_state.data)

# ========== Trade Management ==========
def add_held_trade():
    st.session_state.data["held"].append({
        "q": 0,  # quantity
        "p": 0.0,  # avg price
        "o": []  # options
    })
    update_url()

def add_sold_trade():
    st.session_state.data["sold"].append({
        "q": 0,  # quantity
        "p": 0.0,  # avg price
        "s": 0.0,  # sold price
        "o": []  # options
    })
    update_url()

def add_future_trade():
    st.session_state.data["future"] = [{
        "q": 0,  # quantity
        "p": 0.0,  # avg price
        "s": 0.0,  # sold price
        "o": []  # options
    }]
    update_url()

def remove_held_trade(index):
    st.session_state.data["held"].pop(index)
    update_url()

def remove_sold_trade(index):
    st.session_state.data["sold"].pop(index)
    update_url()

def remove_future_trade():
    st.session_state.data["future"] = []
    update_url()

def add_held_option(trade_index):
    st.session_state.data["held"][trade_index]["o"].append({
        "q": 0,  # quantity
        "p": 0.0  # premium
    })
    update_url()

def add_sold_option(trade_index):
    st.session_state.data["sold"][trade_index]["o"].append({
        "q": 0,  # quantity
        "p": 0.0  # premium
    })
    update_url()

def add_future_option():
    if st.session_state.data["future"]:
        st.session_state.data["future"][0]["o"].append({
            "q": 0,  # quantity
            "p": 0.0  # premium
        })
        update_url()

def remove_held_option(trade_index, option_index):
    st.session_state.data["held"][trade_index]["o"].pop(option_index)
    update_url()

def remove_sold_option(trade_index, option_index):
    st.session_state.data["sold"][trade_index]["o"].pop(option_index)
    update_url()

def remove_future_option(option_index):
    if st.session_state.data["future"]:
        st.session_state.data["future"][0]["o"].pop(option_index)
        update_url()

# ========== Calculation Functions ==========
def calculate_totals():
    """Calculate all totals from current data"""
    data = st.session_state.data
    
    # Held trades
    held_qty = 0
    held_cost = 0
    for trade in data["held"]:
        q = trade.get("q", 0)
        p = trade.get("p", 0)
        held_qty += q
        held_cost += q * p
    
    # Option profits
    option_profit = 0
    for trade in data["held"]:
        for opt in trade.get("o", []):
            option_profit += opt.get("q", 0) * opt.get("p", 0)
    for trade in data["sold"]:
        for opt in trade.get("o", []):
            option_profit += opt.get("q", 0) * opt.get("p", 0)
    for trade in data["future"]:
        for opt in trade.get("o", []):
            option_profit += opt.get("q", 0) * opt.get("p", 0)
    
    # Sold profits
    sold_profit = 0
    for trade in data["sold"]:
        q = trade.get("q", 0)
        p = trade.get("p", 0)  # avg price
        s = trade.get("s", 0)  # sold price
        sold_profit += q * (s - p)
    
    # Future profits
    future_profit = 0
    for trade in data["future"]:
        q = trade.get("q", 0)
        p = trade.get("p", 0)  # avg price
        s = trade.get("s", 0)  # sold price
        future_profit += q * (s - p)
    
    # Future + Held
    future_held_qty = held_qty
    future_held_cost = held_cost
    for trade in data["future"]:
        q = trade.get("q", 0)
        p = trade.get("p", 0)
        future_held_qty += q
        future_held_cost += q * p
    
    return {
        "held_qty": held_qty,
        "held_cost": held_cost,
        "option_profit": option_profit,
        "sold_profit": sold_profit,
        "future_profit": future_profit,
        "future_held_qty": future_held_qty,
        "future_held_cost": future_held_cost
    }

# ========== UI ==========
st.title("📈 Greek Offset Calculator")

# ===== Held Section =====
st.header("📌 Enter The Trades That You Are Currently Holding")

if st.button("➕ Add Trade to Held Section"):
    add_held_trade()
    st.rerun()

for i, trade in enumerate(st.session_state.data["held"]):
    st.subheader(f"Held Stock Trade {i + 1}")

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    # Quantity
    q_key = f"h_q_{i}"
    new_q = col1.number_input("Quantity", value=trade.get("q", 0), key=q_key)
    if new_q != trade.get("q", 0):
        trade["q"] = new_q
        update_url()
    
    # Avg Price
    p_key = f"h_p_{i}"
    new_p = col2.number_input("Avg Price", value=trade.get("p", 0.0), key=p_key, format="%.2f")
    if new_p != trade.get("p", 0.0):
        trade["p"] = new_p
        update_url()
    
    # Total Cost (calculated)
    total_cost = trade.get("q", 0) * trade.get("p", 0)
    col3.number_input("Total Cost", value=total_cost, key=f"h_c_{i}", disabled=True, format="%.2f")
    
    # Remove button
    if col4.button("🗑️", key=f"rem_h_{i}"):
        remove_held_trade(i)
        st.rerun()

    # Options
    st.markdown("**Options Trades**")
    for j, opt in enumerate(trade.get("o", [])):
        ocol1, ocol2, ocol3, ocol4 = st.columns([2, 2, 2, 1])
        
        # Option quantity
        oq_key = f"h_oq_{i}_{j}"
        new_oq = ocol1.number_input(f"Opt {j+1} Qty", value=opt.get("q", 0), key=oq_key)
        if new_oq != opt.get("q", 0):
            opt["q"] = new_oq
            update_url()
        
        # Option premium
        op_key = f"h_op_{i}_{j}"
        new_op = ocol2.number_input(f"Premium", value=opt.get("p", 0.0), key=op_key, format="%.2f")
        if new_op != opt.get("p", 0.0):
            opt["p"] = new_op
            update_url()
        
        # Option profit (calculated)
        opt_profit = opt.get("q", 0) * opt.get("p", 0)
        ocol3.number_input("Profit", value=opt_profit, key=f"h_oprof_{i}_{j}", disabled=True, format="%.2f")
        
        # Remove option button
        if ocol4.button("🗑️", key=f"rem_ho_{i}_{j}"):
            remove_held_option(i, j)
            st.rerun()
    
    if st.button(f"➕ Add Option", key=f"add_ho_{i}"):
        add_held_option(i)
        st.rerun()
    
    st.markdown("---")

st.markdown("---")

# ===== Sold Section =====
st.header("📌 Enter The Trades That Were Exercised")

if st.button("➕ Add Trade to Sold Section"):
    add_sold_trade()
    st.rerun()

for i, trade in enumerate(st.session_state.data["sold"]):
    st.subheader(f"Sold Trade {i + 1}")

    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
    
    # Quantity
    q_key = f"s_q_{i}"
    new_q = col1.number_input("Quantity", value=trade.get("q", 0), key=q_key)
    if new_q != trade.get("q", 0):
        trade["q"] = new_q
        update_url()
    
    # Avg Price
    p_key = f"s_p_{i}"
    new_p = col2.number_input("Avg Price", value=trade.get("p", 0.0), key=p_key, format="%.2f")
    if new_p != trade.get("p", 0.0):
        trade["p"] = new_p
        update_url()
    
    # Strike Price
    s_key = f"s_s_{i}"
    new_s = col3.number_input("Strike", value=trade.get("s", 0.0), key=s_key, format="%.2f")
    if new_s != trade.get("s", 0.0):
        trade["s"] = new_s
        update_url()
    
    # Profit (calculated)
    profit = trade.get("q", 0) * (trade.get("s", 0) - trade.get("p", 0))
    col4.number_input("Profit", value=profit, key=f"s_prof_{i}", disabled=True, format="%.2f")
    
    # Remove button
    if col5.button("🗑️", key=f"rem_s_{i}"):
        remove_sold_trade(i)
        st.rerun()

    # Options
    st.markdown("**Options Trades**")
    for j, opt in enumerate(trade.get("o", [])):
        ocol1, ocol2, ocol3, ocol4 = st.columns([2, 2, 2, 1])
        
        oq_key = f"s_oq_{i}_{j}"
        new_oq = ocol1.number_input(f"Opt {j+1} Qty", value=opt.get("q", 0), key=oq_key)
        if new_oq != opt.get("q", 0):
            opt["q"] = new_oq
            update_url()
        
        op_key = f"s_op_{i}_{j}"
        new_op = ocol2.number_input(f"Premium", value=opt.get("p", 0.0), key=op_key, format="%.2f")
        if new_op != opt.get("p", 0.0):
            opt["p"] = new_op
            update_url()
        
        opt_profit = opt.get("q", 0) * opt.get("p", 0)
        ocol3.number_input("Profit", value=opt_profit, key=f"s_oprof_{i}_{j}", disabled=True, format="%.2f")
        
        if ocol4.button("🗑️", key=f"rem_so_{i}_{j}"):
            remove_sold_option(i, j)
            st.rerun()
    
    if st.button(f"➕ Add Option", key=f"add_so_{i}"):
        add_sold_option(i)
        st.rerun()
    
    st.markdown("---")

st.markdown("---")

# ===== Future Section =====
st.header("📌 Enter The Future Trade You Would Like To Place")

if len(st.session_state.data["future"]) == 0:
    if st.button("➕ Add Trade to Future Section"):
        add_future_trade()
        st.rerun()

for i, trade in enumerate(st.session_state.data["future"]):
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
    
    # Quantity
    q_key = "f_q"
    new_q = col1.number_input("Quantity", value=trade.get("q", 0), key=q_key)
    if new_q != trade.get("q", 0):
        trade["q"] = new_q
        update_url()
    
    # Avg Price
    p_key = "f_p"
    new_p = col2.number_input("Avg Price", value=trade.get("p", 0.0), key=p_key, format="%.2f")
    if new_p != trade.get("p", 0.0):
        trade["p"] = new_p
        update_url()
    
    # Total Cost (calculated)
    total_cost = trade.get("q", 0) * trade.get("p", 0)
    col3.number_input("Total Cost", value=total_cost, key="f_c", disabled=True, format="%.2f")
    
    # Strike Price
    s_key = "f_s"
    new_s = col4.number_input("Strike", value=trade.get("s", 0.0), key=s_key, format="%.2f")
    if new_s != trade.get("s", 0.0):
        trade["s"] = new_s
        update_url()
    
    # Profit (calculated)
    profit = trade.get("q", 0) * (trade.get("s", 0) - trade.get("p", 0))
    col5.number_input("Profit", value=profit, key="f_prof", disabled=True, format="%.2f")
    
    # Remove button
    if col6.button("🗑️", key="rem_f"):
        remove_future_trade()
        st.rerun()

    # Options
    st.markdown("**Options Trades**")
    for j, opt in enumerate(trade.get("o", [])):
        ocol1, ocol2, ocol3, ocol4 = st.columns([2, 2, 2, 1])
        
        oq_key = f"f_oq_{j}"
        new_oq = ocol1.number_input(f"Opt {j+1} Qty", value=opt.get("q", 0), key=oq_key)
        if new_oq != opt.get("q", 0):
            opt["q"] = new_oq
            update_url()
        
        op_key = f"f_op_{j}"
        new_op = ocol2.number_input(f"Premium", value=opt.get("p", 0.0), key=op_key, format="%.2f")
        if new_op != opt.get("p", 0.0):
            opt["p"] = new_op
            update_url()
        
        opt_profit = opt.get("q", 0) * opt.get("p", 0)
        ocol3.number_input("Profit", value=opt_profit, key=f"f_oprof_{j}", disabled=True, format="%.2f")
        
        if ocol4.button("🗑️", key=f"rem_fo_{j}"):
            remove_future_option(j)
            st.rerun()
    
    if len(trade.get("o", [])) == 0:
        if st.button("➕ Add Option", key="add_fo"):
            add_future_option()
            st.rerun()
    
    st.markdown("---")

st.markdown("---")

# ===== Results =====
totals = calculate_totals()

col1, col2 = st.columns(2)

with col1:
    st.header("📊 If Future Trade Is Exercised")
    
    total_profit = totals["option_profit"] + totals["sold_profit"] + totals["future_profit"]
    
    st.metric("Total Quantity", f"{totals['held_qty']}")
    st.metric("Total Cost", f"${totals['held_cost']:,.2f}")
    st.metric("Total Profit", f"${total_profit:,.2f}")
    
    if totals['held_qty'] > 0:
        breakeven = (totals['held_cost'] - total_profit) / totals['held_qty']
        st.success(f"**Breakeven:** ${breakeven:,.2f}")
    
    st.markdown("---")
    st.header("📉 Sell Shares")
    
    sell_price = st.number_input("Selling Price", min_value=0.0, step=0.01, key="sell_exer", format="%.2f")
    
    current_value = totals['held_qty'] * sell_price
    adjusted_cost = totals['held_cost'] - total_profit
    net_pl = current_value - adjusted_cost
    
    st.metric("Current Value", f"${current_value:,.2f}")
    st.metric("Adjusted Cost", f"${adjusted_cost:,.2f}")
    st.metric("Net P/L", f"${net_pl:,.2f}")

with col2:
    st.header("📊 If Future Trade Is NOT Exercised")
    
    total_profit = totals["option_profit"] + totals["sold_profit"]
    
    st.metric("Total Quantity", f"{totals['future_held_qty']}")
    st.metric("Total Cost", f"${totals['future_held_cost']:,.2f}")
    st.metric("Total Profit", f"${total_profit:,.2f}")
    
    if totals['future_held_qty'] > 0:
        breakeven = (totals['future_held_cost'] - total_profit) / totals['future_held_qty']
        st.success(f"**Breakeven:** ${breakeven:,.2f}")
    
    st.markdown("---")
    st.header("📉 Sell Shares")
    
    sell_price = st.number_input("Selling Price", min_value=0.0, step=0.01, key="sell_not_exer", format="%.2f")
    
    current_value = totals['future_held_qty'] * sell_price
    adjusted_cost = totals['future_held_cost'] - total_profit
    net_pl = current_value - adjusted_cost
    
    st.metric("Current Value", f"${current_value:,.2f}")
    st.metric("Adjusted Cost", f"${adjusted_cost:,.2f}")
    st.metric("Net P/L", f"${net_pl:,.2f}")
