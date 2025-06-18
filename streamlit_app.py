import streamlit as st
import pandas as pd
from PIL import Image

# إعداد الصفحة
st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

# ----------- تنسيق CSS -----------
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

# ----------- شعار الشركة (بشكل صحيح) -----------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=400)
except FileNotFoundError:
    st.warning("⚠️ 'logo.png' not found. Please make sure it's in the same folder as this app.")

# ----------- عنوان وحقول الإدخال -----------
st.markdown("<h2>🛠️ Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)
st.markdown("#### Enter Mobile Number or Invoice Number:")
user_input = st.text_input("")

# ----------- تحميل البيانات من Google Sheet -----------
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1MitHqD5SZfm-yAUsrc8jkki7zD9zFlH1JXhHTKjfAhs/export?format=csv&gid=2031108065"
    return pd.read_csv(url)

df = load_data()

# ----------- عملية البحث -----------
if st.button("Search"):
    if user_input.strip() == "":
        st.warning("Please enter a mobile number or invoice number.")
    else:
        try:
            # تأكد من الأعمدة الصحيحة حسب الجدول
            phone_col = df.columns[19]   # T
            invoice_col = df.columns[1]  # B
            name_col = df.columns[2]     # C
            address_col = df.columns[20] # U
            d365_col = df.columns[12]    # M

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
<b>D365 Update:</b> {row[d365_col]}
</div>
                    """, unsafe_allow_html=True)
            else:
                st.error("No matching record found.")
        except Exception as e:
            st.error(f"⚠️ Error reading data: {e}")

# ----------- التذييل -----------
st.caption("© Hamad M. Al Rugaib & Sons Trading Co. – Powered by Streamlit")
