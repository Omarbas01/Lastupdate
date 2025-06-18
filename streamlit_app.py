import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

# Custom styling for layout and buttons
st.markdown("""
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f5f5f5;
            color: #222;
        }
        .stButton > button {
            background-color: #000000;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 8px;
        }
        .result-box {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin-top: 20px;
            direction: rtl;
        }
        h2 {
            text-align: center;
            margin-top: -20px;
        }
    </style>
""", unsafe_allow_html=True)

# Show company logo
st.markdown(
    """
    <div style='text-align: center;'>
        <img src='logo.png' width='400'>
    </div>
    """,
    unsafe_allow_html=True
)

# Page title and input
st.markdown("## 🔧 Maintenance Tracker - Rugaib", unsafe_allow_html=True)
st.markdown("#### Enter Mobile Number or Invoice Number:")

user_input = st.text_input("")

# Load data from Google Sheets
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1MitHqD5SZfm-yAUsrc8jkki7zD9zFlH1JXhHTKjfAhs/export?format=csv&gid=2031108065"
    return pd.read_csv(url)

df = load_data()

# Search action
if st.button("Search"):
    if user_input.strip() == "":
        st.warning("Please enter a mobile number or invoice number.")
    else:
        try:
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
<b>الاسم:</b> {row[name_col]}<br>
<b>رقم الجوال:</b> {row[phone_col]}<br>
<b>رقم الفاتورة:</b> {row[invoice_col]}<br>
<b>العنوان:</b> {row[address_col]}<br>
<b>تحديث D365:</b> {row[d365_col]}
</div>
                    """, unsafe_allow_html=True)
            else:
                st.error("لم يتم العثور على نتائج مطابقة.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة البيانات: {e}")

# Footer
st.caption("© Hamad M. Al Rugaib & Sons Trading Co. – Powered by Streamlit")
