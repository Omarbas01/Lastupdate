
import streamlit as st
import pandas as pd

# إعداد صفحة التطبيق
st.set_page_config(page_title="Maintenance Tracker - Rugaib", page_icon="🔧", layout="centered")

# الشعار (اختياري - يمكن استبداله برابط شعار حقيقي)
st.image("https://i.imgur.com/NVqvZ4P.png", width=180)

# العنوان
st.markdown("<h2 style='text-align: center;'>🔧 Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)
st.markdown("#### Enter Mobile Number or Invoice Number:")

# إدخال المستخدم
user_input = st.text_input("", placeholder="05XXXXXXXX أو رقم الفاتورة")

# رابط Google Sheet بصيغة CSV
# ملاحظة: يجب أن يكون الشيت متاح للعرض العام
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv"

if user_input:
    try:
        df = pd.read_csv(sheet_url)
        # البحث
        result = df[
            (df["رقم الجوال"].astype(str) == user_input) |
            (df["رقم الفاتورة"].astype(str) == user_input)
        ]

        if not result.empty:
            st.success("✅ Customer Found:")
            st.write(result)
        else:
            st.warning("❗ لا يوجد تطابق لهذا الرقم.")
    except KeyError as e:
        st.error(f"⚠️ تأكد من أسماء الأعمدة في Google Sheet: {e}")
    except Exception as e:
        st.error(f"❌ حصل خطأ أثناء الاتصال أو المعالجة: {e}")
