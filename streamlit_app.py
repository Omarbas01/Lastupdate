import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import re

st.set_page_config(page_title="📊 Dashboard - Maintenance Tracker", layout="wide")

# ---------- Load Data ----------
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1MitHqD5SZfm-yAUsrc8jkki7zD9zFlH1JXhHTKjfAhs/export?format=csv&gid=2031108065"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # Remove any extra spaces from column names
    return df

# ---------- Main Dashboard ----------
st.title("📊 Maintenance Dashboard - Al Rugaib")

with st.spinner("Loading data..."):
    df = load_data()

# ---------- Column Definitions ----------
try:
    status_col = df.columns[12]      # M - D365 Update
    region_col = df.columns[20]      # U - Address
    service_col = df.columns[14]     # O - Service Type
    date_col = df.columns[15]        # P - Scheduled Date

    # Preprocess
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])

    # KPI Section
    total_requests = len(df)
    total_regions = df[region_col].nunique()
    total_services = df[service_col].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Requests", total_requests)
    col2.metric("📍 Unique Regions", total_regions)
    col3.metric("🛠️ Service Types", total_services)

    st.markdown("---")

    # ---------- Graphs ----------
    colA, colB = st.columns(2)

    with colA:
        st.subheader("🗂️ Requests by Status (D365 Update)")
        fig_status = px.pie(df, names=status_col, title="Status Distribution", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_status, use_container_width=True)

    with colB:
        st.subheader("📍 Requests by Region")
        fig_region = px.bar(df[region_col].value_counts().reset_index(), 
                            x='index', y=region_col, 
                            labels={'index': 'Region', region_col: 'Request Count'},
                            color='index', 
                            color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_region, use_container_width=True)

    st.markdown("---")
    st.subheader("📅 Scheduled Requests Over Time")
    date_data = df[date_col].dt.date.value_counts().sort_index()
    date_df = pd.DataFrame({"Date": date_data.index, "Count": date_data.values})
    fig_timeline = px.line(date_df, x="Date", y="Count", markers=True, title="Scheduled Request Trend")
    st.plotly_chart(fig_timeline, use_container_width=True)

except Exception as e:
    st.error(f"Error loading dashboard: {e}")

# ---------- Footer ----------
st.caption("Made with ❤️ for Hamad M. Al Rugaib & Sons - Powered by Streamlit")
