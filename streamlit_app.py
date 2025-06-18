import streamlit as st
import os

# إعداد صفحة Streamlit
st.set_page_config(page_title="متابعة الصيانة - الرقيب", layout="centered")

# تنسيق ألوان وخط متناسق مع الشعار
st.markdown("""
    <style>
        body {
            direction: rtl;
            font-family: 'Segoe UI', sans-serif;
            color: #222;
            background-color: #f9f9f9;
        }
        .stButton > button {
            background-color: #cc0000;
            color: white;
            font-weight: bold;
        }
        input {
            text-align: right;
        }
    </style>
""", unsafe_allow_html=True)

# عرض شعار الشركة
st.image("logo.png", width=300)

# عنوان التطبيق
st.markdown("<h2 style='text-align: center;'>🔍 نظام متابعة الصيانة - الرقيب</h2>", unsafe_allow_html=True)
st.markdown("#### الرجاء إدخال رقم الجوال أو رقم الفاتورة:")

# حقل الإدخال
user_input = st.text_input("", max_chars=15)

# دالة استرجاع البيانات (مثال ثابت)
def fetch_maintenance_data(input_value):
    return {
        "الاسم": "سلمان",
        "رقم الجوال": "0501762520",
        "رقم الفاتورة": "SO000697361",
        "العنوان": "الاحساء، الغسانية",
        "تحديث D365": "لا يوجد"
    }

# عند الضغط على زر البحث
if st.button("🔍 بحث"):
    if not user_input:
        st.warning("يرجى إدخال رقم الجوال أو الفاتورة.")
    else:
        result = fetch_maintenance_data(user_input)
        st.markdown("---")
        for k, v in result.items():
            st.markdown(f"**{k}**: {v}")
