import streamlit as st
import pandas as pd

# UI setup
st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")
st.image("logo.png", width=300)
st.markdown("<h2 style='text-align: center;'>🔧 Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)

# Load data from Excel
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("your_data.xlsx")  # replace with actual filename
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

df = load_data()

# Input
user_input = st.text_input("Enter Mobile Number or Invoice Number:")

# Search
if st.button("Search"):
    if df.empty:
        st.warning("No data available.")
    elif "Mobile Number" not in df.columns:
        st.error("Column 'Mobile Number' not found in Excel file.")
    else:
        results = df[df["Mobile Number"].astype(str) == user_input]
        if not results.empty:
            for idx, row in results.iterrows():
                for col in df.columns:
                    st.markdown(f"**{col}**: {row[col]}")
        else:
            st.warning("No matching record found.")
