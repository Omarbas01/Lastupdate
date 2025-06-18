import streamlit as st
import pandas as pd
from PIL import Image
import re

st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

# ----------- CSS Styling -----------
st.markdown("""
    <style>
        body {
            background-color: #f9f9f9;
            font-family: 'Segoe UI', sans-serif;
            color: #333;
        }
        .stButton > button {
            background-color: #000000;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 8px;
        }
        .result-box {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-top: 20px;
        }
        h2 {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# ----------- Logo Centered -----------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=400)
except FileNotFoundError:
    st.warning("⚠️ 'logo.png' not found. Please make sure it's in the same folder.")

# ----------- Title & Input -----------
st.markdown("<h2>🛠️ Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)
st.markdown("#### Enter Mobile Number or Invoice Number:")
user_input = st.text_input("")

# ----------- Load Data from Google Sheet -----------
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1MitHqD5SZfm-yAUsrc8jkki7zD9zFlH1JXhHTKjfAhs/export?format=csv&gid=2031108065"
    return pd.read_csv(url)

df = load_data()

# ----------- Convert Drive Link to Direct Image URL -----------
def convert_drive_url_to_direct(link):
    if pd.isna(link):
        return None

    # Handle id=XXXX or /d/XXXX/
    patterns = [
        r"id=([a-zA-Z0-9_-]+)",
        r"/d/([a-zA-Z0-9_-]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?id={file_id}"

    return None

# ----------- Search Logic -----------
if st.button("Search"):
    if user_input.strip() == "":
        st.warning("Please enter a mobile number or invoice number.")
    else:
        try:
            # Column mappings
            phone_col = df.columns[19]      # T
            invoice_col = df.columns[1]     # B
