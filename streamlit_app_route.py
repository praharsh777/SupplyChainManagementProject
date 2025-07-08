import streamlit as st
import pandas as pd
import numpy as np
import os
import uuid
import math
import folium
from streamlit_folium import st_folium
from scipy.spatial import distance_matrix

# App settings
st.set_page_config(page_title="🚚 Route Optimization", layout="wide")
st.title("🚚 Route Optimization Tool")

# Directory for saving route files
SAVE_DIR = os.path.join(os.path.dirname(__file__), "saved_files", "routes")
os.makedirs(SAVE_DIR, exist_ok=True)

# Session ID
session_id = st.session_state.get("session_id", str(uuid.uuid4()))
st.session_state["session_id"] = session_id

# Sidebar instructions
with st.sidebar:
    st.header("🚣️ Instructions")
    st.markdown("""
    1. Upload a CSV/XLSX with `Location`, `Latitude`, and `Longitude` columns.
    2. Select a depot (starting location).
    3. The tool calculates the shortest route using TSP.
    4. Visualize and download the optimized path.
    """)

# Deduplicate column names safely
def deduplicate_columns(cols):
    seen = {}
    result = []
    for col in cols:
        if col not in seen:
            seen[col] = 0
            result.append(col)
        else:
            seen[col] += 1
            result.append(f"{col}_{seen[col]}")
    return result

# File upload
uploaded_file = st.file_uploader("📄 Upload Location Data", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = deduplicate_columns(df.columns)  # Fix duplicate columns

        st.subheader("🔍 Location Data Preview")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    # Column selection
    loc_col = st.selectbox("📌 Location Name Column", df.columns)
    lat_col = st.selectbox("🚽 Latitude Column", df.select_dtypes(include='number').columns)
    lon_col = st.selectbox("🚽 Longitude Column", df.select_dtypes(include='number').columns)

    if df[loc_col].duplicated().any():
        st.warning("⚠️ Duplicate location names found. Consider making them unique.")

    depot = st.selectbox("🏠 Select Starting Depot", df[loc_col].unique())

    # Coordinates and distance matrix
    coords = df[[lat_col, lon_col]].values
    labels = df[loc_col].values
    dist_matrix = distance_matrix(coords, coords)

    # Solve TSP (naive nearest-neighbor)
    def solve_tsp_nn(dist_matrix, start_index=0):
        N = len(dist_matrix)
        visited = [False] * N
        path = [start_index]
        visited[start_index] = True

        for _ in range(N - 1):
            last = path[-1]
            next_city = np.argmin([dist_matrix[last][j] if not visited[j] else np.inf for j in range(N)])
            path.append(next_city)
            visited[next_city] = True

        return path + [start_index]  # return to start

    depot_idx = df[df[loc_col] == depot].index[0]
    route_indices = solve_tsp_nn(dist_matrix, start_index=depot_idx)

    # Output route
    ordered_df = df.iloc[route_indices].reset_index(drop=True)
    total_distance = sum(
        dist_matrix[route_indices[i]][route_indices[i + 1]] for i in range(len(route_indices) - 1)
    )

    st.subheader("📋 Optimized Route")
    ordered_df["Stop"] = list(range(1, len(ordered_df) + 1))
    st.dataframe(ordered_df[[loc_col, "Stop", lat_col, lon_col]])

    st.markdown(f"📍 **Total Distance**: `{round(total_distance, 2)} units`")

    # 🖘️ Map display
    st.subheader("🖘️ Route Map")
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=6)
    for i in range(len(ordered_df)):
        row = ordered_df.iloc[i]
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=f"{row['Stop']}: {row[loc_col]}",
            tooltip=row[loc_col],
            icon=folium.Icon(color="blue" if i == 0 else "green")
        ).add_to(m)

    coords_route = ordered_df[[lat_col, lon_col]].values.tolist()
    folium.PolyLine(coords_route, color="red", weight=2.5, opacity=0.8).add_to(m)
    st_folium(m, width=700, height=500)

    # Save and download
    csv_data = ordered_df.to_csv(index=False).encode()
    st.download_button("⬇️ Download Route as CSV", csv_data, file_name="optimized_route.csv")

    if st.button("📍 Save Route to Dashboard"):
        filename_csv = f"{session_id}_route.csv"
        save_path_csv = os.path.join(SAVE_DIR, filename_csv)
        ordered_df.to_csv(save_path_csv, index=False)

        filename_map = f"{session_id}_route_map.html"
        save_path_map = os.path.join(SAVE_DIR, filename_map)
        m.save(save_path_map)

        st.success("✅ Route and map saved to dashboard!")

else:
    st.info("Upload a dataset to begin route optimization.")
