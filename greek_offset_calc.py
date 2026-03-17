import streamlit as st
import json

st.set_page_config(page_title="Greek Offset Calculator", layout="wide")

# ========== Initialize with simple session state only ==========
if "data" not in st.session_state:
    st.session_state.data = {
        "held": [],
        "sold": [], 
        "future": []
    }

# ========== Helper Functions ==========
def save_state():
    """Just trigger a rerun to refresh the UI"""
    st.rerun()

# ========== UI ==========
st.title("📈 Greek Offset Calculator")

# ===== Held Section =====
st.header("📌 Enter The Trades That You Are Currently Holding")

if st.button("➕ Add Trade to Held Section"):
    st.session_state.data["held"].append({"q": 0, "p": 0.0, "o": []})
    save_state()

for i, trade in enumerate(st.session_state.data["held"]):
    with st.expander(f"Held Stock Trade {i + 1}", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        # Simple number inputs - direct session state updates
        trade["q"] = col1.number_input("Quantity", value=trade["q"], key=f"h_q_{i}")
        trade["p"] = col2.number_input("Avg Price", value=trade["p"], key=f"h_p_{i}", format="%.2f")
        
        total_cost = trade["q"] * trade["p"]
        col3.number_input("Total Cost", value=total_cost, key=f"h_c_{i}", disabled=True, format="%.2f")
        
        if st.button("🗑️ Remove", key=f"rem_h_{i}"):
            st.session_state.data["held"].pop(i)
            save_state()
            st.rerun()
        
        # Options
        st.markdown("**Options**")
        for j, opt in enumerate(trade["o"]):
            ocol1, ocol2, ocol3 = st.columns(3)
            opt["q"] = ocol1.number_input(f"Qty", value=opt["q"], key=f"h_oq_{i}_{j}")
            opt["p"] = ocol2.number_input(f"Premium", value=opt["p"], key=f"h_op_{i}_{j}", format="%.2f")
            opt_profit = opt["q"] * opt["p"]
            ocol3.number_input("Profit", value=opt_profit, key=f"h_oprof_{i}_{j}", disabled=True, format="%.2f")
            
            if st.button("🗑️", key=f"rem_ho_{i}_{j}"):
                trade["o"].pop(j)
                save_state()
                st.rerun()
        
        if st.button("➕ Add Option", key=f"add_ho_{i}"):
            trade["o"].append({"q": 0, "p": 0.0})
            save_state()
            st.rerun()

# [Similar simplified sections for Sold and Future trades...]

# ===== Results =====
st.header("📊 Summary")
if st.session_state.data["held"]:
    total_qty = sum(t["q"] for t in st.session_state.data["held"])
    total_cost = sum(t["q"] * t["p"] for t in st.session_state.data["held"])
    
    st.metric("Total Quantity", total_qty)
    st.metric("Total Cost", f"${total_cost:,.2f}")
