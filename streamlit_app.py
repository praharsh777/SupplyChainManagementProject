import uuid
import streamlit as st
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import os
import re
# ✅ MUST BE FIRST Streamlit command
st.set_page_config(page_title="Demand Forecasting with Prophet", layout="wide")

# 🆔 Create/get session_id
# Get session_id from URL if provided (Streamlit 1.32+ syntax)
params = st.query_params
incoming_session_id = params.get("session_id")

if incoming_session_id:
    session_id = incoming_session_id
else:
    session_id = st.session_state.get("session_id", str(uuid.uuid4()))

st.session_state["session_id"] = session_id


# 🌐 Go Back Button
st.markdown(
    """
    <a href="http://localhost:3000/home" target="_self">
        <button style="padding: 0.5rem 1rem; background-color: #007bff; color: white; border: none; border-radius: 4px;">
            ⬅️ Go Back to Dashboard
        </button>
    </a>
    """,
    unsafe_allow_html=True
)

# 📁 Directory to save image files
SAVE_DIR = os.path.join(os.path.dirname(__file__), "saved_files", "images")
os.makedirs(SAVE_DIR, exist_ok=True)

st.title("📈 Demand Forecasting Dashboard (Prophet)")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    date_col = st.selectbox("Select the Date column", df.columns)
    numeric_col = st.selectbox("Select the Numeric (Target) column", df.select_dtypes(include='number').columns)
    group_col = st.selectbox("Optional: Group by column (e.g., Product, Region)", ["None"] + list(df.columns))
    forecast_years = st.slider("Forecast Duration (Years)", 1, 10, 3)
    future_periods = forecast_years * 12

    try:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df[numeric_col] = pd.to_numeric(df[numeric_col], errors='coerce')
    except Exception as e:
        st.error(f"Error converting columns: {e}")
        st.stop()

    df.dropna(subset=[date_col, numeric_col], inplace=True)
    forecasts = {}

    # 🎨 Multi-plot selection
    chart_types = st.multiselect(
        "Choose one or more plot types to display:",
        ["Line Chart", "Bar Chart", "Area Chart", "Scatter Plot"],
        default=["Line Chart"]
    )

    def forecast_grouped(dataframe):
        df_local = dataframe.rename(columns={date_col: 'ds', numeric_col: 'y'})
        model = Prophet()
        model.fit(df_local)
        future = model.make_future_dataframe(periods=future_periods, freq='MS')
        forecast = model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

    def plot_forecast_matplotlib(forecast_df, name, title, chart_types):
        cols = st.columns(2)  # Two columns per row
        for i, chart_type in enumerate(chart_types):
            fig, ax = plt.subplots(figsize=(6, 3))  # Compact plot size

            # Plot selection
            if chart_type == "Line Chart":
                ax.plot(forecast_df['ds'], forecast_df['yhat'], label='Forecast')
            elif chart_type == "Bar Chart":
                ax.bar(forecast_df['ds'], forecast_df['yhat'], label='Forecast', width=20)
            elif chart_type == "Area Chart":
                ax.plot(forecast_df['ds'], forecast_df['yhat'], label='Forecast')
                ax.fill_between(forecast_df['ds'], forecast_df['yhat_lower'], forecast_df['yhat_upper'], alpha=0.3)
            elif chart_type == "Scatter Plot":
                ax.scatter(forecast_df['ds'], forecast_df['yhat'], label='Forecast')

            ax.set_title(f"{chart_type} - {title}", fontsize=10)
            ax.set_xlabel("Date")
            ax.set_ylabel("Forecasted Value")
            ax.tick_params(labelsize=7)
            ax.legend(fontsize=8)

            # Render in alternating columns
            col = cols[i % 2]
            with col:
                st.pyplot(fig)
                safe_name = re.sub(r'\W+', '_', name)
                if st.button(f"💾 Save - {chart_type} ({name})", key=f"{name}_{chart_type}"):
                    filename = os.path.join(SAVE_DIR, f"{session_id}_{safe_name}_{chart_type.replace(' ', '_')}.png")
                    fig.savefig(filename)
                    st.success("✅ Saved")


    # 👥 Grouped forecast
    if group_col != "None":
        st.subheader(f"Forecasts by {group_col}")
        for name, group in df.groupby(group_col):
            st.markdown(f"### {name}")
            forecast_df = forecast_grouped(group)
            plot_forecast_matplotlib(forecast_df, name, f"Forecast for {name}", chart_types)
            forecasts[name] = forecast_df
    else:
        st.subheader("Forecast Result")
        forecast_df = forecast_grouped(df)
        plot_forecast_matplotlib(forecast_df, "overall", "Overall Forecast", chart_types)
        forecasts['overall'] = forecast_df

    # 📥 Download CSV
    st.subheader("📥 Download Forecasts")
    for name, forecast_df in forecasts.items():
        csv = forecast_df.to_csv(index=False).encode()
        st.download_button(
            label=f"Download Forecast - {name}.csv",
            data=csv,
            file_name=f"forecast_{name}.csv",
            mime='text/csv'
        )
