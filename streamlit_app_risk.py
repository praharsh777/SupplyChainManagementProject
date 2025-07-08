import streamlit as st
import pandas as pd
import numpy as np
import os
import uuid
import matplotlib.pyplot as plt
import seaborn as sns

# Page setup
st.set_page_config(page_title="⚠️ Risk Analysis", layout="wide")
st.title("⚠️ Supply Chain Risk Analysis Tool")

# Directory setup
BASE_DIR = os.path.join(os.path.dirname(__file__), "saved_files", "risk")
IMG_DIR = os.path.join(BASE_DIR, "images")
CSV_DIR = os.path.join(BASE_DIR, "csvs")
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

# Session ID from query params
if "session_id" not in st.session_state:
    query_params = st.query_params
    st.session_state["session_id"] = query_params.get("session_id", [str(uuid.uuid4())])[0]
session_id = st.session_state["session_id"]

# Sidebar
with st.sidebar:
    st.header("🧠 How to Use")
    st.markdown("""
    1. Upload a CSV or Excel file with supplier and risk KPI data.
    2. Adjust column selections as needed.
    3. View results and visualizations.
    4. Click 'Save' buttons to store results in dashboard.
    """)

# Deduplicate column names
def deduplicate_columns(columns):
    seen = {}
    new_cols = []
    for col in columns:
        if col not in seen:
            seen[col] = 0
            new_cols.append(col)
        else:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
    return new_cols

# File upload
uploaded_file = st.file_uploader("📄 Upload your supplier risk data", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        df.columns = deduplicate_columns(df.columns)
        st.subheader("📄 Data Preview")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    # Column selections
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    text_cols = df.select_dtypes(include='object').columns.tolist()

    if len(numeric_cols) < 4 or len(text_cols) == 0:
        st.warning("Please upload data with at least one text and four numeric columns.")
        st.stop()

    supplier_col = st.selectbox("🏠 Supplier Column", text_cols, index=0)
    lead_time_col = st.selectbox("⏱️ Lead Time Column", numeric_cols, index=0)
    on_time_col = st.selectbox("🚞 On-Time Delivery Column", numeric_cols, index=1)
    defect_col = st.selectbox("🛠️ Defect Rate Column", numeric_cols, index=2)
    demand_var_col = st.selectbox("📊 Demand Variability Column", numeric_cols, index=3)

    # Risk calculation
    results = []
    for supplier, group in df.groupby(supplier_col):
        lead_var = group[lead_time_col].std()
        on_time = group[on_time_col].mean()
        defects = group[defect_col].mean()
        demand_var = group[demand_var_col].std()
        risk_score = (lead_var + demand_var + defects - on_time) / 4

        suggestions = []
        if on_time < 85: suggestions.append("📍 Improve on-time delivery")
        if defects > 5: suggestions.append("📍 Address quality issues")
        if lead_var > 2: suggestions.append("📍 Reduce lead time variance")
        if risk_score > 5: suggestions.append("📍 Consider alternate supplier")

        results.append({
            "Supplier": supplier,
            "Avg On-Time Delivery": round(on_time, 2),
            "Lead Time Variability": round(lead_var, 2),
            "Defect Rate (%)": round(defects, 2),
            "Demand Variability": round(demand_var, 2),
            "Risk Score": round(risk_score, 2),
            "Recommendations": " | ".join(suggestions)
        })

    result_df = pd.DataFrame(results).sort_values(by="Risk Score", ascending=False)

    st.subheader("📉 Risk Summary")
    st.dataframe(result_df)

    # Save CSV (on click only)
    csv_path = os.path.join(CSV_DIR, f"{session_id}_risk_report.csv")
    result_df.to_csv(csv_path, index=False)

    with open(csv_path, "rb") as f:
        st.download_button("⬇️ Download Risk Report as CSV", f, file_name="supply_risk_report.csv")

    if st.button("📥 Save Risk Report to Dashboard"):
        st.success("✅ Risk CSV saved to dashboard!")

    # ───── Visualization Cards ─────
    st.subheader("📊 Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📌 Risk Score by Supplier")
        fig1, ax1 = plt.subplots()
        sns.barplot(x="Risk Score", y="Supplier", data=result_df, ax=ax1, palette="Reds_r")
        ax1.set_title("Risk Score by Supplier")
        st.pyplot(fig1)
        if st.button("💾 Save Risk Score Plot"):
            fig1_path = os.path.join(IMG_DIR, f"{session_id}_risk_score.png")
            fig1.savefig(fig1_path, bbox_inches='tight')
            st.success("✅ Risk Score Plot saved!")
            with open(fig1_path, "rb") as f:
                st.download_button("⬇️ Download Plot", f, file_name="risk_score_plot.png")

    with col2:
        st.markdown("### 📌 On-Time Delivery vs Defect Rate")
        fig2, ax2 = plt.subplots()
        sns.scatterplot(data=result_df, x="Avg On-Time Delivery", y="Defect Rate (%)", hue="Supplier", ax=ax2)
        ax2.set_title("On-Time Delivery vs Defect Rate")
        st.pyplot(fig2)
        if st.button("💾 Save Scatter Plot"):
            fig2_path = os.path.join(IMG_DIR, f"{session_id}_on_time_vs_defects.png")
            fig2.savefig(fig2_path, bbox_inches='tight')
            st.success("✅ Scatter Plot saved!")
            with open(fig2_path, "rb") as f:
                st.download_button("⬇️ Download Plot", f, file_name="on_time_vs_defects.png")

else:
    st.info("Upload a CSV or XLSX file to start your risk analysis.")
