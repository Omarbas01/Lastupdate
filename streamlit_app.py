
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

st.title("🔍 Maintenance Tracker - Rugaib")
st.markdown("Enter mobile number or invoice number:")

user_input = st.text_input("")

@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1MitHqD5SZfm-yAUsrc8jkki7zD9zFlH1JXhHTKjfAhs/export?format=csv&gid=2031108065"
    return pd.read_csv(url)

df = load_data()

if st.button("Search"):
    if user_input.strip() == "":
        st.warning("Please enter a mobile number or invoice number.")
    else:
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
                st.markdown("""
**الاسم:** {}  
**رقم الجوال:** {}  
**رقم الفاتورة:** {}  
**العنوان:** {}  
**تحديث D365:** {}
                """.format(
                    row[name_col],
                    row[phone_col],
                    row[invoice_col],
                    row[address_col],
                    row[d365_col]
                ))
        else:
            st.error("لم يتم العثور على نتائج مطابقة.")

st.caption("© Hamad M. Al Rugaib & Sons Trading Co. – Powered by Streamlit")
