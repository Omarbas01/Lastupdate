import streamlit as st
from fpdf import FPDF
import os

# إعداد صفحة Streamlit
st.set_page_config(page_title="مولد PDF بالعربية", layout="centered")

st.title("📄 توليد ملف PDF باللغة العربية")

# مدخلات المستخدم
name = st.text_input("الاسم:")
address = st.text_input("العنوان:")

# دالة إنشاء PDF
def generate_pdf(name, address):
    pdf = FPDF()
    pdf.add_page()

    # التأكد من وجود الخط
    font_path = "fonts/NotoNaskhArabic-Regular.ttf"
    if not os.path.exists(font_path):
        st.error("❌ خط Noto Naskh Arabic غير موجود في المجلد fonts/")
        return None

    pdf.add_font('Arabic', '', font_path, uni=True)
    pdf.set_font('Arabic', '', 14)

    # كتابة المحتوى
    pdf.cell(0, 10, txt=f"الاسم: {name}", ln=True, align='R')
    pdf.cell(0, 10, txt=f"العنوان: {address}", ln=True, align='R')

    # حفظ الملف
    output_path = "output.pdf"
    pdf.output(output_path)
    return output_path

# زر توليد PDF
if st.button("📥 إنشاء وتحميل PDF"):
    if not name or not address:
        st.warning("يرجى إدخال الاسم والعنوان أولاً.")
    else:
        file_path = generate_pdf(name, address)
        if file_path:
            with open(file_path, "rb") as f:
                st.download_button(
                    label="📄 تحميل PDF",
                    data=f,
                    file_name="output.pdf",
                    mime="application/pdf"
                )
