import streamlit as st
import pandas as pd
import numpy as np
import math
import uuid
import os
from datetime import datetime
# Page setup
st.set_page_config(page_title="📦 Inventory Optimization", layout="wide")
st.title("📦 Inventory Management & Optimization Tool")

with st.sidebar:
    st.header("ℹ️ Instructions")
    st.markdown("""
    - Upload a file (.csv or Excel) with product demand data.
    - Select the product identifier and demand quantity column.
    - Set lead time, costs, and service level.
    - Get inventory KPIs: EOQ, Safety Stock, and Reorder Point.
    """)

uploaded_file = st.file_uploader("📤 Upload your inventory file", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        # Load file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Convert object columns to string for arrow compatibility
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].astype(str)

        st.subheader("🔍 Data Preview")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    product_col = st.selectbox("📌 Select Product Column", df.columns)
    demand_col = st.selectbox("📈 Select Demand (Quantity) Column", df.select_dtypes(include='number').columns)

    lead_time = st.number_input("⏱️ Lead Time (days)", min_value=1, value=7)
    holding_cost = st.number_input("🏬 Holding Cost per unit", min_value=0.01, value=2.0)
    order_cost = st.number_input("🧾 Order Cost", min_value=0.01, value=50.0)
    service_level = st.slider("🎯 Service Level (%)", 50, 99, 95)

    Z = round(np.abs(np.percentile(np.random.normal(size=100000), service_level)), 2)

    summary = []

    # Filter invalid demand rows
    clean_df = df[df[demand_col] > 0].dropna(subset=[demand_col, product_col])

    with st.spinner("⏳ Analyzing inventory data..."):
        for prod, group in clean_df.groupby(product_col):
            try:
                demands = group[demand_col].dropna()
                avg_demand = demands.mean()
                std_dev = demands.std()
                total_demand = demands.sum()

                if np.isnan(avg_demand) or np.isnan(std_dev) or np.isnan(total_demand):
                    continue

                safety_stock = round(Z * std_dev * math.sqrt(lead_time)) if std_dev > 0 else 0
                reorder_point = round((avg_demand * lead_time) + safety_stock)
                eoq = round(math.sqrt((2 * total_demand * order_cost) / holding_cost)) if holding_cost > 0 else 0

                summary.append({
                    "Product": prod,
                    "Avg Demand": round(avg_demand, 2),
                    "Std Dev": round(std_dev, 2),
                    "Total Demand": round(total_demand),
                    "Safety Stock": safety_stock,
                    "Reorder Point": reorder_point,
                    "EOQ": eoq
                })

            except Exception:
                continue


        safety_stock = round(Z * std_dev * math.sqrt(lead_time)) if std_dev > 0 else 0
        reorder_point = round((avg_demand * lead_time) + safety_stock)
        eoq = round(math.sqrt((2 * total_demand * order_cost) / holding_cost)) if holding_cost > 0 else 0

        summary.append({
            "Product": prod,
            "Avg Demand": round(avg_demand, 2),
            "Std Dev": round(std_dev, 2),
            "Total Demand": round(total_demand),
            "Safety Stock": safety_stock,
            "Reorder Point": reorder_point,
            "EOQ": eoq
        })


    if summary:
        result_df = pd.DataFrame(summary)
        st.success("✅ Analysis complete. Recommendations below:")
        st.subheader("📊 Inventory Recommendations")
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode()
        st.download_button("⬇️ Download Results", csv, file_name="inventory_optimization.csv")
    else:
        st.info("No valid product data to display.")
else:
    st.info("Upload a CSV or Excel file to get started.")

INVENTORY_DIR = os.path.join(os.path.dirname(__file__), "saved_files", "inventory")
os.makedirs(INVENTORY_DIR, exist_ok=True)

# Save results button
if result_df is not None and not result_df.empty:
    if st.button("💾 Save This Inventory Report"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = st.session_state.get("session_id", str(uuid.uuid4()))
        filename = f"{session_id}_inventory_{timestamp}.csv"
        filepath = os.path.join(INVENTORY_DIR, filename)
        result_df.to_csv(filepath, index=False)
        st.success("✅ Report saved!")