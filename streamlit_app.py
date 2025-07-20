# streamlit_app.py

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

@st.cache_data
def load_data():
    return pd.read_excel("your_excel_file.xlsx")

# UI
st.image("logo.png", width=200)
st.title("🛠️ Maintenance Tracker - Rugaib")

mobile_or_invoice = st.text_input("Enter Mobile Number or Invoice Number:")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

start_datetime = st.datetime_input("🗓️ Start Timestamp Filter (Optional):", value=None)
end_datetime = st.datetime_input("🗓️ End Timestamp Filter (Optional):", value=None)

if st.button("Search"):
    df = load_data()

    # Ensure 'Timestamp' column is in datetime format
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

    # Filters
    if mobile_or_invoice:
        df = df[df['Invoice Number'].astype(str).str.contains(mobile_or_invoice, na=False) |
                df['رقم الجوال'].astype(str).str.contains(mobile_or_invoice, na=False)]

    if start_datetime:
        df = df[df['Timestamp'] >= pd.to_datetime(start_datetime)]
    if end_datetime:
        df = df[df['Timestamp'] <= pd.to_datetime(end_datetime)]

    if df.empty:
        st.warning("No matching records found.")
    else:
        st.success(f"{len(df)} records found.")
        st.dataframe(df)

        # Summary
        st.subheader("📊 Summary")

        summary = df.groupby("MarkupCode").size().reset_index(name="Total")
        total_all = summary["Total"].sum()

        st.table(pd.concat([summary, pd.DataFrame([["Total", total_all]], columns=summary.columns)]))

        # Region Summary if Region column exists
        if "Region" in df.columns:
            st.subheader("📍 Region Summary")
            st.table(df["Region"].value_counts().reset_index().rename(columns={'index': 'Region', 'Region': 'Count'}))
else:
    st.info("Please enter mobile/invoice or apply timestamp filter.")
