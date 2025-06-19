import streamlit as st
import pandas as pd
from PIL import Image
import re

st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

# ----------- CSS Styling -----------
st.markdown("""
    <style>
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
            padding: 10px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-bottom: 10px;
        }
        .logo-container {
            display: flex;
            justify-content: center;
            margin-top: -40px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ----------- Logo -----------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=250)
except FileNotFoundError:
    st.warning("⚠️ 'logo.png' not found. Please make sure it's in the same folder.")

# ----------- Title -----------
st.markdown("<h2 style='text-align:center;'>🛠️ Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)

# ----------- Input Section -----------
user_input = st.text_input("🔎 Enter Mobile Number or Invoice Number:")

# ----------- Refresh Button -----------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.success("✅ Data refreshed. Please click Search again.")

# ----------- Google Drive Link Cleaner -----------
def convert_drive_url_to_direct(cell_value):
    if pd.isna(cell_value):
        return None
    first_url = str(cell_value).split()[0]
    patterns = [r"id=([a-zA-Z0-9_-]{10,})", r"/d/([a-zA-Z0-9_-]{10,})"]
    for pattern in patterns:
        match = re.search(pattern, first_url)
        if match:
            return match.group(1)
    return None

# ----------- Load Data Without Cache -----------
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1MitHqD5SZfm-yAUsrc8jkki7zD9zFlH1JXhHTKjfAhs/export?format=csv&gid=2031108065"
    return pd.read_csv(url, header=0)

# ----------- Search Button -----------
if st.button("Search"):
    if user_input.strip() == "":
        st.warning("Please enter a mobile number or invoice number.")
    else:
        try:
            with st.spinner("🔄 Loading data..."):
                df = load_data()

            # Column mappings by name
            phone_col = "Phone Number | رقم الجوال"
            invoice_col = "Invoice Number | رقم الفاتورة"
            name_col = "Pt Name | اسم العميل الأول"
            address_col = "Address | العنوان"
            d365_col = "D365 تحديث"
            d365_so_col = "D365"
            markup_col = "MarkupCode"
            date_col = "Scheduled"
            date_request_col = "Date | التاريخ"
            info_col = "Info"
            part_img_col = "Picture of Part"
            problem_img_col = "Picture of Problem"
            supervisor_col = "shift supervisor"

            # Optional service type filter
            unique_services = df[markup_col].dropna().unique()
            selected_service = st.selectbox("📂 Filter by Service Type (Optional):", ["All"] + list(unique_services))

            # Filtered results
            result = df[
                df[phone_col].astype(str).str.contains(user_input, case=False, na=False) |
                df[invoice_col].astype(str).str.contains(user_input, case=False, na=False) |
                df[d365_so_col].astype(str).str.contains(user_input, case=False, na=False)
            ]

            if selected_service != "All":
                result = result[result[markup_col] == selected_service]

            if not result.empty:
                st.success(f"✅ {len(result)} record(s) found.")
                for _, row in result.iterrows():
                    with st.expander(f"🔍 Result for Invoice: {row[invoice_col]}"):
                        request_date = pd.to_datetime(row[date_request_col], errors='coerce')
                        request_date_str = request_date.strftime('%d/%m/%Y') if not pd.isna(request_date) else 'N/A'

                        st.markdown(f"""
<div class='result-box'>
<b>👤 Name:<
