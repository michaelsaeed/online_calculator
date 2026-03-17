import streamlit as st
import pandas as pd
import io
import json

st.set_page_config(page_title="Greek Offset Calculator", layout="wide")

# ========== Session Initialization ==========
if "held_trades" not in st.session_state:
    st.session_state.held_trades = []

if "add_option_held_index" in st.session_state:
    i = st.session_state.add_option_held_index
    st.session_state.held_trades[i]["options"].append({
        "quantity": st.session_state.held_trades[i]["quantity"],
        "premium": 0.0,
        "profit": 0.0}
    )
    del st.session_state.add_option_held_index

if "sold_trades" not in st.session_state:
    st.session_state.sold_trades = []

if "add_option_sold_index" in st.session_state:
    i = st.session_state.add_option_sold_index
    st.session_state.sold_trades[i]["options"].append({
        "quantity": st.session_state.sold_trades[i]["quantity"],
        "premium": 0.0,
        "profit": 0.0}
    )
    del st.session_state.add_option_sold_index

if "future_trades" not in st.session_state:
    st.session_state.future_trades = []

if "add_option_future_index" in st.session_state:
    i = st.session_state.add_option_future_index
    st.session_state.future_trades[i]["options"].append({
        "quantity": 0,
        "premium": 0.0,
        "profit": 0.0
    })
    del st.session_state.add_option_future_index

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
    st.session_state.future_trades.append({
        "quantity": 0,
        "avg_price": 0.0,
        "total_cost": 0.0,
        "sold_price": 0.0,
        "profit": 0.0,
        "options": []
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
    st.session_state.future_trades.pop(st.session_state.future_to_delete)
    st.session_state.future_to_delete = None


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
    trade["quantity"] = cols[0].number_input(f"Quantity {i + 1}", value=trade["quantity"], key=f"hold_qty_{i}")
    trade["avg_price"] = cols[1].number_input(f"AVG Price {i + 1}", value=trade["avg_price"], key=f"hold_avg_{i}")

    # Auto-calculate Total Cost
    trade["total_cost"] = trade["quantity"] * trade["avg_price"]
    st.session_state[f"hold_cost_{i}"] = trade["total_cost"]
    cols[2].number_input(f"Total Cost {i + 1}", key=f"hold_cost_{i}", disabled=True)

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        option["quantity"] = trade["quantity"]
        st.session_state[f"hold_option_qty_{i}_{j}"] = option["quantity"]
        pcols[0].number_input(f"Option {j + 1} Qty (Held {i + 1})", key=f"hold_option_qty_{i}_{j}", disabled=True, step=1, format="%d")
        option["premium"] = pcols[1].number_input(f"Premium {j + 1} (Held {i + 1})", value=option["premium"], key=f"hold_option_premium_{i}_{j}")

        # Auto-calculate Option Profit
        option["profit"] = option["quantity"] * option["premium"]
        st.session_state[f"hold_option_profit_{i}_{j}"] = option["profit"]
        pcols[2].number_input(f"Profit {j + 1} (Held {i + 1})", key=f"hold_option_profit_{i}_{j}", disabled=True)

        if pcols[3].button("➖", key=f"remove_hold_option_{i}_{j}"):
            if i not in st.session_state.held_option_to_delete:
                st.session_state.held_option_to_delete[i] = []
            st.session_state.held_option_to_delete[i].append(j)
            st.rerun()

    if st.button(f"➕ Add Option to Held Trade {i + 1}", key=f"add_hold_option_{i}"):
        st.session_state.add_option_held_index = i
        st.rerun()

    st.markdown("---")

st.markdown("---")  # adds a horizontal line

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
    trade["quantity"] = cols[0].number_input(f"Quantity {i + 1} (Sold)", value=trade["quantity"], key=f"sold_qty_{i}")
    trade["avg_price"] = cols[1].number_input(f"AVG Price {i + 1} (Sold)", value=trade["avg_price"],
                                              key=f"sold_avg_{i}")
    trade["sold_price"] = cols[2].number_input(f"Strike Price {i + 1}", value=trade["sold_price"], key=f"sold_price_{i}")

    # Auto-calculate Profit
    trade["profit"] = trade["quantity"] * (trade["sold_price"] - trade["avg_price"])
    st.session_state[f"sold_profit_{i}"] = trade["profit"]
    cols[3].number_input(f"Profit {i + 1}", key=f"sold_profit_{i}", disabled=True)

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)
        option["quantity"] = trade["quantity"]
        st.session_state[f"sold_option_qty_{i}_{j}"] = option["quantity"]
        pcols[0].number_input(f"Option {j + 1} Qty (Sold {i + 1})", key=f"sold_option_qty_{i}_{j}", disabled=True, step=1, format="%d")
        option["premium"] = pcols[1].number_input(f"Premium {j + 1} (Sold {i + 1})", value=option["premium"], key=f"sold_option_premium_{i}_{j}")

        # Auto-calculate Option Profit
        option["profit"] = option["quantity"] * option["premium"]
        st.session_state[f"sold_option_profit_{i}_{j}"] = option["profit"]
        pcols[2].number_input(f"Profit {j + 1} (Sold {i + 1})", key=f"sold_option_profit_{i}_{j}", disabled=True)

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


# ===== Future Section =====
st.header("📌 Enter The Future Trades You Would Like To Place")

# Add Trade button (now allows multiple trades)
if st.button("➕ Add Trade to Future Section"):
    add_future_trade()
    st.rerun()

for i, trade in enumerate(st.session_state.future_trades):

    if st.button(f"➖ Remove Future Trade {i + 1}", key=f"remove_future_trade_{i}"):
        st.session_state.future_to_delete = i
        st.rerun()

    cols = st.columns(5)
    trade["quantity"] = cols[0].number_input(f"Quantity {i + 1}", value=trade["quantity"], key=f"future_qty_{i}")
    trade["avg_price"] = cols[1].number_input(f"Stock Price {i + 1}", value=trade["avg_price"], key=f"future_avg_{i}")

    # Auto-calculate Total Cost
    trade["total_cost"] = trade["quantity"] * trade["avg_price"]
    st.session_state[f"future_cost_{i}"] = trade["total_cost"]
    cols[2].number_input(f"Total Cost {i + 1}", key=f"future_cost_{i}", disabled=True)

    trade["sold_price"] = cols[3].number_input(f"Strike Price {i + 1}", value=trade["sold_price"], key=f"future_sold_price_{i}")

    # Auto-calculate Profit
    trade["profit"] = trade["quantity"] * (trade["sold_price"] - trade["avg_price"])
    st.session_state[f"future_sold_profit_{i}"] = trade["profit"]
    cols[4].number_input(f"Profit {i + 1}", key=f"future_sold_profit_{i}", disabled=True)

    st.markdown("**Options Trades**")
    for j, option in enumerate(trade["options"]):
        pcols = st.columns(4)

        # Option quantity syncs with stock quantity, uneditable
        option["quantity"] = trade["quantity"]
        pcols[0].number_input(f"Option {j + 1} Qty (Future {i + 1})", value=option["quantity"], key=f"future_option_qty_{i}_{j}", disabled=True, step=1, format="%d")

        option["premium"] = pcols[1].number_input(f"Premium {j + 1} (Future {i + 1})", value=option["premium"], key=f"future_option_premium_{i}_{j}")

        # Auto-calculate Option Profit
        option["profit"] = option["quantity"] * option["premium"]
        st.session_state[f"future_option_profit_{i}_{j}"] = option["profit"]
        pcols[2].number_input(f"Profit {j + 1} (Future {i + 1})", key=f"future_option_profit_{i}_{j}", disabled=True)

        if pcols[3].button("➖", key=f"remove_future_option_{i}_{j}"):
            if i not in st.session_state.future_option_to_delete:
                st.session_state.future_option_to_delete[i] = []
            st.session_state.future_option_to_delete[i].append(j)
            st.rerun()

    # Add Option button
    if st.button(f"➕ Add Option to Future Trade {i + 1}", key=f"add_future_option_{i}"):
        st.session_state.add_option_future_index = i
        st.rerun()

    st.markdown("---")

st.markdown("---")  # adds a horizontal line


col1, col2 = st.columns(2)

# ===== Left Column =====
with col1:

    # ===== Trades Summary If Future Trade is Exercised =====
    st.header("📊 Trades Summary If Future Trade Is Exercised")

    # Calculate totals
    total_quantity_exer = sum(trade["quantity"] for trade in st.session_state.held_trades)
    total_cost_exer = sum(trade["total_cost"] for trade in st.session_state.held_trades)

    total_option_profit = sum(
        option["profit"]
        for trade in st.session_state.held_trades + st.session_state.sold_trades + st.session_state.future_trades
        for option in trade["options"]
    )

    total_sold_profit = sum(trade["profit"] for trade in st.session_state.sold_trades)
    total_future_sold_profit = sum(trade["profit"] for trade in st.session_state.future_trades)
    total_profit = total_option_profit + total_sold_profit + total_future_sold_profit

    # Avoid division by zero
    if total_quantity_exer > 0:
        breakeven_price = (total_cost_exer - total_profit) / total_quantity_exer
    else:
        breakeven_price = 0.0

    # Display
    st.markdown(f"**Total Quantity of Shares:** {total_quantity_exer}")
    st.markdown(f"**Total Cost:** ${total_cost_exer:,.2f}")
    st.markdown(f"**Total Profit:** ${total_profit:,.2f}")
    st.success(f"**Breakeven Price:** ${breakeven_price:,.2f}")

    st.markdown("---")  # adds a horizontal line

    # ===== Selling the Shares If Future Trade Is Exercised =====
    st.header("📉 Selling the Shares If Future Trade Is Exercised")
    st.markdown("<h4>Note: In case of making a change in the above trades, re-enter the Selling Price for updated calculations.</h4>", unsafe_allow_html=True)

    selling_price_exer = st.number_input("**Selling Price**", min_value=0.0, step=0.01, key="selling_price_exer")

    current_value_exer = total_quantity_exer * selling_price_exer
    adjusted_cost_exer = total_cost_exer - total_profit
    net_profit_loss_exer = current_value_exer - adjusted_cost_exer
    profit_loss_pct_exer = (net_profit_loss_exer / adjusted_cost_exer * 100) if adjusted_cost_exer != 0 else 0.0

    # Display
    st.markdown(f"**Current Shares Value:** ${current_value_exer:,.2f}")
    st.markdown(f"**Adjusted Cost:** ${adjusted_cost_exer:,.2f}")
    st.success(f"**Net Profit/Loss:** ${net_profit_loss_exer:,.2f}")
    st.success(f"**Profit/Loss Percentage:** {profit_loss_pct_exer:.2f}%")


# ===== Right Column =====
with col2:

    # ===== Trades Summary If Future Trade is Not Exercised =====
    st.header("📊 Trades Summary If Future Trade Is NOT Exercised")

    # Calculate totals
    total_quantity_not_exer = sum(trade["quantity"] for trade in st.session_state.held_trades + st.session_state.future_trades)
    total_cost_not_exer = sum(trade["total_cost"] for trade in st.session_state.held_trades + st.session_state.future_trades)

    total_option_profit = sum(
        option["profit"]
        for trade in st.session_state.held_trades + st.session_state.sold_trades + st.session_state.future_trades
        for option in trade["options"]
    )

    total_sold_profit = sum(trade["profit"] for trade in st.session_state.sold_trades)
    total_profit = total_option_profit + total_sold_profit

    # Avoid division by zero
    if total_quantity_not_exer > 0:
        breakeven_price = (total_cost_not_exer - total_profit) / total_quantity_not_exer
    else:
        breakeven_price = 0.0

    # Display
    st.markdown(f"**Total Quantity of Shares:** {total_quantity_not_exer}")
    st.markdown(f"**Total Cost:** ${total_cost_not_exer:,.2f}")
    st.markdown(f"**Total Profit:** ${total_profit:,.2f}")
    st.success(f"**Breakeven Price:** ${breakeven_price:,.2f}")

    st.markdown("---")  # adds a horizontal line

    # ===== Selling the Shares If Future Trade Is Exercised =====
    st.header("📉 Selling the Shares If Future Trade Is NOT Exercised")
    st.markdown("<h4>Note: In case of making a change in the above trades, re-enter the Selling Price for updated calculations.</h4>", unsafe_allow_html=True)

    selling_price_not_exer = st.number_input("**Selling Price**", min_value=0.0, step=0.01, key="selling_price_not_exer")

    current_value_not_exer = total_quantity_not_exer * selling_price_not_exer
    adjusted_cost_not_exer = total_cost_not_exer - total_profit
    net_profit_loss_not_exer = current_value_not_exer - adjusted_cost_not_exer
    profit_loss_pct_not_exer = (net_profit_loss_not_exer / adjusted_cost_not_exer * 100) if adjusted_cost_not_exer != 0 else 0.0

    # Display
    st.markdown(f"**Current Shares Value:** ${current_value_not_exer:,.2f}")
    st.markdown(f"**Adjusted Cost:** ${adjusted_cost_not_exer:,.2f}")
    st.success(f"**Net Profit/Loss:** ${net_profit_loss_not_exer:,.2f}")
    st.success(f"**Profit/Loss Percentage:** {profit_loss_pct_not_exer:.2f}%")

st.markdown("---")  # adds a horizontal line


st.header("💾 Save or Export Your Trades")

# ---------- 1️⃣ Download Trades JSON for Later Editing ----------
trades_data = {
    "held_trades": st.session_state.held_trades,
    "sold_trades": st.session_state.sold_trades,
    "future_trades": st.session_state.future_trades
}

json_bytes = io.BytesIO()
json_bytes.write(json.dumps(trades_data, indent=4).encode("utf-8"))
json_bytes.seek(0)

st.download_button(
    label="Download Trades JSON (Reload Later)",
    data=json_bytes,
    file_name="my_trades.json",
    mime="application/json"
)

# ---------- 2️⃣ Load Saved JSON Trades ----------
uploaded_file = st.file_uploader("📂 Upload Saved Trades JSON", type=["json"])

# Track load state
if "load_triggered" not in st.session_state:
    st.session_state.load_triggered = False

if uploaded_file is not None and not st.session_state.load_triggered:
    try:
        saved_trades = json.load(uploaded_file)

        # Only update if data is different
        if (saved_trades.get("held_trades", []) != st.session_state.held_trades or
                saved_trades.get("sold_trades", []) != st.session_state.sold_trades or
                saved_trades.get("future_trades", []) != st.session_state.future_trades):
            st.session_state.held_trades = saved_trades.get("held_trades", [])
            st.session_state.sold_trades = saved_trades.get("sold_trades", [])
            st.session_state.future_trades = saved_trades.get("future_trades", [])
            st.session_state.load_triggered = True
            st.success("✅ Trades restored successfully!")
            st.rerun()

    except Exception as e:
        st.error(f"Failed to load trades: {e}")

# Reset trigger when file is removed
if uploaded_file is None:
    st.session_state.load_triggered = False

st.markdown("---")  # adds a horizontal line

# ===== Download Trades Excel =====
st.header("💾 Download Trades Spreadsheet")

# Combine all trades into one DataFrame
all_trades = []

for trade_list, trade_type in [
    (st.session_state.held_trades, "Held"),
    (st.session_state.sold_trades, "Sold"),
    (st.session_state.future_trades, "Future")
]:
    for i, trade in enumerate(trade_list):
        base = {
            "Trade Type": trade_type,
            "Trade #": i + 1,
            "Quantity": trade["quantity"],
            "Stock Price": trade.get("avg_price", 0.0),
            "Sold Price": trade.get("sold_price", 0.0),
            "Total Cost": trade.get("total_cost", 0.0),
            "Profit": trade.get("profit", 0.0)
        }
        # Add options if any
        if trade["options"]:
            for j, option in enumerate(trade["options"]):
                row = base.copy()
                row.update({
                    "Option #": j + 1,
                    "Option Quantity": option["quantity"],
                    "Option Premium": option["premium"],
                    "Option Profit": option["profit"]
                })
                all_trades.append(row)
        else:
            row = base.copy()
            row.update({
                "Option #": "",
                "Option Quantity": "",
                "Option Premium": "",
                "Option Profit": ""
            })
            all_trades.append(row)

df = pd.DataFrame(all_trades)

# Create Excel in-memory
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name="Trades")
    worksheet = writer.sheets["Trades"]
    workbook = writer.book

    # Format: Left-aligned + full border for all cells
    full_border_format = workbook.add_format({"align": "left", "valign": "vcenter", "border": 1})

    # Adjust column widths and apply formats
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, max_len)  # set width first

        for row_num, value in enumerate(df[col], start=1):  # +1 for header
            worksheet.write(row_num, i, value, full_border_format)

    # Format header row
    header_format = workbook.add_format({"bold": True, "align": "left", "valign": "vcenter", "border": 1})
    for i, col in enumerate(df.columns):
        worksheet.write(0, i, col, header_format)

excel_data = excel_buffer.getvalue()

# Single download button
st.download_button(
    label="📥 Download Trades Spreadsheet",
    data=excel_data,
    file_name="trades_export.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

