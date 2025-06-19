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
            color: #000000;
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

# ----------- Logo -----------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=400)
except FileNotFoundError:
    st.warning("⚠️ 'logo.png' not found. Please make sure it's in the same folder.")

# ----------- Title & Input -----------
st.markdown("<h2>🛠️ Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)
st.markdown("#### Enter Mobile Number or Invoice Number:")
user_input = st.text_input("")

# ----------- Load Data -----------
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1MitHqD5SZfm-yAUsrc8jkki7zD9zFlH1JXhHTKjfAhs/export?format=csv&gid=2031108065"
    return pd.read_csv(url)

df = load_data()

# ----------- Convert Google Drive URL to Direct Image ID -----------
def convert_drive_url_to_direct(cell_value):
    if pd.isna(cell_value):
        return None

    first_url = str(cell_value).split()[0]
    patterns = [
        r"id=([a-zA-Z0-9_-]{10,})",
        r"/d/([a-zA-Z0-9_-]{10,})"
    ]

    for pattern in patterns:
        match = re.search(pattern, first_url)
        if match:
            return match.group(1)

    return None

# ----------- Search Logic -----------
if st.button("Search"):
    if user_input.strip() == "":
        st.warning("Please enter a mobile number or invoice number.")
    else:
        try:
            # Adjust column indices
            phone_col = df.columns[19]       # T
            invoice_col = df.columns[1]      # B
            name_col = df.columns[2]         # C
            address_col = df.columns[20]     # U
            d365_col = df.columns[12]        # M
            markup_col = df.columns[14]      # O
            date_col = df.columns[15]        # P
            info_col = df.columns[28]        # AC
            part_img_col = df.columns[29]    # AD
            problem_img_col = df.columns[30] # AE
            supervisor_col = df.columns[33]  # AH

            result = df[
                (df[phone_col].astype(str) == user_input) |
                (df[invoice_col].astype(str) == user_input)
            ]

            if not result.empty:
                for _, row in result.iterrows():
                    st.markdown(f"""
<div class='result-box'>
<b>Name:</b> {row[name_col]}<br>
<b>Mobile Number:</b> {row[phone_col]}<br>
<b>Invoice Number:</b> {row[invoice_col]}<br>
<b>Address:</b> {row[address_col]}<br>
<b>D365 Update:</b> {row[d365_col]}<br>
<b>Service Type:</b> {row[markup_col]}<br>
<b>Scheduled Date:</b> {row[date_col]}<br>
<b>Extra Info:</b> {row[info_col]}<br>
<b>Shift Supervisor:</b> {row[supervisor_col]}
</div>
                    """, unsafe_allow_html=True)

                    # ----------- Picture of Part (link only)
                    part_img_id = convert_drive_url_to_direct(row[part_img_col])
                    if part_img_id:
                        st.markdown("📸 **Picture of Part**")
                        st.markdown(f"[🔗 Open Image](https://drive.google.com/file/d/{part_img_id}/view)", unsafe_allow_html=True)

                    # ----------- Picture of Problem (link only)
                    problem_img_id = convert_drive_url_to_direct(row[problem_img_col])
                    if problem_img_id:
                        st.markdown("⚠️ **Picture of Problem**")
                        st.markdown(f"[🔗 Open Image](https://drive.google.com/file/d/{problem_img_id}/view)", unsafe_allow_html=True)

            else:
                st.error("No matching record found.")
        except Exception as e:
            st.error(f"⚠️ Error reading data: {e}")

# ----------- Footer -----------
st.caption("© Hamad M. Al Rugaib & Sons Trading Co. – Powered by Streamlit")
