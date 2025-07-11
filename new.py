import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# --- CONFIG ---
st.set_page_config(page_title="🌱 NGO Food Dashboard", layout="wide")

# --- SET DEFAULT PAGE ---
if "active_page" not in st.session_state:
    st.session_state.active_page = "home"

# --- STYLING ---
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #009688;
        color: white;
        border-radius: 10px;
        padding: 0.5em 1.5em;
        font-weight: bold;
        margin-bottom: 0.3em;
    }
    div.stDownloadButton > button {
        background-color: #00796B;
        color: white;
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #004D40;
    }
    </style>
""", unsafe_allow_html=True)

# --- FILE PATHS ---
inventory_file = 'data/inventory.csv'
waste_log_file = 'data/waste_log.csv'

def init_data_files():
    if not os.path.exists(inventory_file):
        pd.DataFrame(columns=['Item', 'Quantity', 'Date Received', 'Expiry Date']).to_csv(inventory_file, index=False)
    if not os.path.exists(waste_log_file):
        pd.DataFrame(columns=['Item', 'Quantity Wasted', 'Reason', 'Waste Date']).to_csv(waste_log_file, index=False)

def load_inventory():
    return pd.read_csv(inventory_file)

def load_waste_log():
    return pd.read_csv(waste_log_file)

def save_inventory(df):
    df.to_csv(inventory_file, index=False)

def save_waste_log(df):
    df.to_csv(waste_log_file, index=False)

init_data_files()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🔍 Navigation")
if st.sidebar.button("🏠 Home", key="home_btn"):
    st.session_state.active_page = "home"
if st.sidebar.button("📦 Inventory", key="view_inv"):
    st.session_state.active_page = "inventory"
if st.sidebar.button("➕ Add Inventory", key="add_inv"):
    st.session_state.active_page = "add"
if st.sidebar.button("♻️ Log Waste", key="log_waste"):
    st.session_state.active_page = "waste"
if st.sidebar.button("📊 Waste Analytics", key="analytics"):
    st.session_state.active_page = "analytics"
if st.sidebar.button("🔐 Admin Panel", key="admin"):
    st.session_state.active_page = "admin"

# --- ACTIVE PAGE LOGIC ---
if st.session_state.active_page == "home":
    st.markdown("# 🏠 Welcome to NGO Dashboard")
    st.markdown("### Helping reduce food waste, one item at a time.")
    st.markdown("---")
    inv_df = load_inventory()
    waste_df = load_waste_log()

    st.metric("📦 Inventory Items", len(inv_df))
    st.metric("♻️ Waste Records", len(waste_df))

    if not waste_df.empty:
        top_item = waste_df.groupby('Item')['Quantity Wasted'].sum().sort_values(ascending=False).idxmax()
        top_qty = waste_df.groupby('Item')['Quantity Wasted'].sum().max()
        st.info(f"🥲 Most Wasted: {top_item} ({int(top_qty)} units)")

    st.image("https://cdn-icons-png.flaticon.com/512/765/765412.png", width=120)

elif st.session_state.active_page == "inventory":
    st.header("📦 Current Inventory")
    st.dataframe(load_inventory())

elif st.session_state.active_page == "add":
    st.header("➕ Add New Inventory")
    item = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=1)
    expiry_date = st.date_input("Expiry Date")

    if st.button("Add Item", key="btn_add_item"):
        new_row = pd.DataFrame([[item, quantity, datetime.today().strftime('%Y-%m-%d'), expiry_date]],
                               columns=['Item', 'Quantity', 'Date Received', 'Expiry Date'])
        df = load_inventory()
        df = pd.concat([df, new_row], ignore_index=True)
        save_inventory(df)
        st.success("✅ Item added to inventory.")

elif st.session_state.active_page == "waste":
    st.header("♻️ Log Food Waste")
    items = load_inventory()['Item'].unique()

    if len(items) == 0:
        st.info("Inventory empty.")
    else:
        item = st.selectbox("Select Item", items)
        qty = st.number_input("Quantity Wasted", min_value=1)
        reason = st.text_area("Reason for Waste")

        if st.button("Log Waste", key="btn_log_waste"):
            df = load_waste_log()
            new_row = pd.DataFrame([[item, qty, reason, datetime.today().strftime('%Y-%m-%d')]],
                                   columns=['Item', 'Quantity Wasted', 'Reason', 'Waste Date'])
            df = pd.concat([df, new_row], ignore_index=True)
            save_waste_log(df)
            st.success("✅ Waste logged.")

    st.subheader("🗑️ Delete Waste Entry")
    df = load_waste_log()
    if not df.empty:
        i = st.selectbox("Entry to Delete", df.index,
                         format_func=lambda x: f"{x} - {df.loc[x, 'Item']} ({df.loc[x, 'Waste Date']})")
        st.write(df.loc[[i]])
        if st.button("Delete Waste Entry", key="btn_del_waste"):
            df = df.drop(index=i)
            save_waste_log(df)
            st.success("🧹 Deleted successfully.")
    else:
        st.info("No waste logs to delete.")

elif st.session_state.active_page == "analytics":
    st.header("📊 Waste Analytics")
    df = load_waste_log()
    if df.empty:
        st.info("No records.")
    else:
        chart_data = waste_df.groupby('Item')['Quantity Wasted'].sum()
        fig, ax = plt.subplots()
        ax.bar(chart_data.index, chart_data.values, color="#009688")
        ax.set_xlabel("Item")
        ax.set_ylabel("Total Quantity Wasted")
        ax.set_title("Waste Per Item")
        plt.xticks(rotation=45)
        st.pyplot(fig)


        with st.expander("📄 Full Waste Log"):
            st.dataframe(df)

elif st.session_state.active_page == "admin":
    st.header("🔐 Admin Panel")
    col1, col2, col3, col4 = st.columns(4)

    if col1.button("View Data", key="view_raw"):
        st.subheader("Inventory")
        st.dataframe(load_inventory())
        st.subheader("Waste Log")
        st.dataframe(load_waste_log())

    if col2.button("Delete Entry", key="admin_delete"):
        src = st.selectbox("Delete From", ["Inventory", "Waste Log"])
        if src == "Inventory":
            df = load_inventory()
            if not df.empty:
                i = st.selectbox("Index", df.index)
                st.write(df.loc[[i]])
                if st.button("Delete Inventory", key="btn_del_inv"):
                    df = df.drop(index=i)
                    save_inventory(df)
                    st.success("✅ Deleted.")
            else:
                st.info("Inventory is empty.")
        else:
            df = load_waste_log()
            if not df.empty:
                i = st.selectbox("Index", df.index)
                st.write(df.loc[[i]])
                if st.button("Delete Waste", key="btn_del_admin_waste"):
                    df = df.drop(index=i)
                    save_waste_log(df)
                    st.success("✅ Deleted.")
            else:
                st.info("Waste log is empty.")

    if col3.button("Reset All", key="admin_reset"):
        st.warning("⚠️ Deletes ALL data.")
        if st.button("Confirm Reset", key="btn_confirm_reset"):
            save_inventory(pd.DataFrame(columns=['Item', 'Quantity', 'Date Received', 'Expiry Date']))
            save_waste_log(pd.DataFrame(columns=['Item', 'Quantity Wasted', 'Reason', 'Waste Date']))
            st.success("🚫 All data cleared.")

    if col4.button("Download CSV", key="admin_download"):
        inv = load_inventory()
        waste = load_waste_log()
        st.download_button("Download Inventory", inv.to_csv(index=False).encode(), file_name="inventory.csv", mime='text/csv')
        st.download_button("Download Waste Log", waste.to_csv(index=False).encode(), file_name="waste_log.csv", mime='text/csv')
