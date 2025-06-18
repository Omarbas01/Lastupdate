import streamlit as st
from fpdf import FPDF
import os

# إعداد واجهة الصفحة
st.set_page_config(page_title="متابعة الصيانة - الرقيب", layout="centered")

# تنسيق CSS بسيط لتوحيد الخط والألوان
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
    </style>
""", unsafe_allow_html=True)

# عرض الشعار
st.image("logo.png", width=300)

# عنوان التطبيق
st.markdown("<h2 style='text-align: center;'>🔍 نظام متابعة الصيانة - الرقيب</h2>", unsafe_allow_html=True)
st.markdown("#### الرجاء إدخال رقم الجوال أو رقم الفاتورة:")

# مدخل المستخدم
user_input = st.text_input("", max_chars=15)

# بيانات وهمية للاختبار – يمكنك ربطها بقاعدة بيانات لاحقاً
def fetch_maintenance_data(input_value):
    # مثال ثابت حسب الصورة التي أرسلتها
    return {
        "الاسم": "سلمان",
        "رقم الجوال": "0501762520",
        "رقم الفاتورة": "SO000697361",
        "العنوان": "الاحساء، الغسانية",
        "تحديث D365": "لا يوجد"
    }

# إنشاء PDF من البيانات
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    font_path = "fonts/NotoNaskhArabic-Regular.ttf"
    if not os.path.exists(font_path):
        st.error("خط Noto Naskh Arabic غير موجود في مجلد fonts/")
        return None

    pdf.add_font('Arabic', '', font_path, uni=True)
    pdf.set_font('Arabic', '', 14)

    pdf.cell(0, 10, txt="شركة حمد محمد الرقيب وأولاده التجارية", ln=True, align='R')
    pdf.cell(0, 10, txt="متابعة حالة الصيانة", ln=True, align='R')
    pdf.ln(10)

    for key, value in data.items():
        pdf.cell(0, 10, txt=f"{key}: {value}", ln=True, align='R')

    pdf.output("maintenance_report.pdf")
    return "maintenance_report.pdf"

# عند الضغط على زر البحث
if st.button("🔍 بحث"):
    if not user_input:
        st.warning("يرجى إدخال رقم الجوال أو رقم الفاتورة.")
    else:
        result = fetch_maintenance_data(user_input)
        st.markdown("---")
        for k, v in result.items():
            st.markdown(f"**{k}**: {v}")

        # زر تحميل PDF
        pdf_path = generate_pdf(result)
        if pdf_path:
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 تحميل تقرير PDF",
                    data=f,
                    file_name="maintenance_report.pdf",
                    mime="application/pdf"
                )
