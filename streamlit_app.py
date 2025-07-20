import streamlit as st
import pandas as pd
from PIL import Image
import re
import io

st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

# ----------- CSS Styling -----------
st.markdown("""
    <style>
        .stButton > button {
            background-color: #000;
            color: #fff;
            font-weight: 600;
            padding: 10px 24px;
            border-radius: 8px;
            border: none;
        }
        input[type="text"] {
            border: 2px solid #ccc;
            padding: 10px;
            border-radius: 6px;
            width: 100%;
        }
        .result-box {
            background-color: #f9f9f9;
            color: #000;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin-bottom: 12px;
            font-size: 15px;
        }
        .stTextInput>div>div>input {
            border: 2px solid #ccc;
            border-radius: 6px;
            padding: 10px;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# ----------- Logo -----------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=350)
except FileNotFoundError:
    st.warning("⚠️ 'logo.png' not found. Please make sure it's in the same folder.")

# ----------- Title -----------
st.markdown("<h2 style='text-align:center; font-family:sans-serif;'>🛠️ Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)

# ----------- Input Section -----------
user_input = st.text_input(" Enter Mobile Number or Invoice Number:")

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

# ----------- Detect Mobile Column -----------
def detect_mobile_column(df):
    target_keywords = ["Phone Number | رقم الجوال ", "جوال", "رقم", "phone"]
    for col in df.columns:
        clean_col = col.strip().lower().replace("|", " ").replace("  ", " ")
        if any(keyword in clean_col for keyword in target_keywords):
            return col
    for col in df.columns:
        sample = df[col].astype(str).str.strip().dropna().head(100)
        matches = sample[sample.str.match(r"^05[0-9]{8}$")]
        if len(matches) > 3:
            return col
    return None

# ----------- Detect Invoice Column -----------
def detect_invoice_column(df):
    for col in df.columns:
        sample = df[col].astype(str).str.strip().dropna().head(100)
        if sample.str.match(r"SO[0-9]{9}").any():
            return col
    return df.columns[1]

# ----------- Load Data Without Cache -----------
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1ZZOFElk1ZOKSzRuVE_d_Et46JR-How-qo5xwij8NXho/export?format=csv&gid=1295915446"
    return pd.read_csv(url, encoding="utf-8")

# ----------- Search Button -----------
if st.button("Search"):
    if user_input.strip() == "":
        st.warning("Please enter a mobile number or invoice number.")
    else:
        try:
            with st.spinner("🛠️ Loading data..."):
                df = load_data()

            invoice_col = detect_invoice_column(df)
            phone_col = detect_mobile_column(df)

            if not phone_col:
                st.error("❌ Could not detect mobile number column. Please check the sheet.")
                st.stop()

            name_col = "First Name " if "الاسم الأول" in df.columns else df.columns[4]
            address_col = "Address | العنوان" if "العنوان" in df.columns else df.columns[18]
            d365_col = "D365" if "D365" in df.columns else df.columns[10]
            markup_col = "MarkupCode" if "MarkupCode" in df.columns else df.columns[14]
            date_col = "Date" if "Scheduled" in df.columns else df.columns[14]
            info_col = "التقييم" if "Info" in df.columns else df.columns[2]
            part_img_col = "Picture of Part" if "Part Image" in df.columns else df.columns[26]
            problem_img_col = "Problem Image" if "Problem Image" in df.columns else df.columns[27]
            supervisor_col = "Supervisor" if "Supervisor" in df.columns else None

            unique_services = df[markup_col].dropna().unique()
            selected_service = st.selectbox("📂 Filter by Service Type (Optional):", ["All"] + list(unique_services))

            query = user_input.strip().lower()
            result = df[
                df[phone_col].astype(str).str.strip().str.lower().str.contains(query, na=False) |
                df[invoice_col].astype(str).str.strip().str.lower().str.contains(query, na=False)
            ]

            if selected_service != "All":
                result = result[result[markup_col] == selected_service]

            if not result.empty:
                st.success(f"✅ {len(result)} record(s) found.")
                for _, row in result.iterrows():
                    with st.expander(f" Result for Invoice: {row[invoice_col]}"):
                        st.markdown(f"""
<div class='result-box'>
<b> Name:</b> {row.get(name_col, 'N/A')}<br>
<b> Mobile:</b> {row.get(phone_col, 'N/A')}<br>
<b> Invoice:</b> {row.get(invoice_col, 'N/A')}<br>
<b> Address:</b> {row.get(address_col, 'N/A')}<br>
<b> D365 Update:</b> {row.get(d365_col, 'N/A')}<br>
<b> Service Type:</b> {row.get(markup_col, 'N/A')}<br>
<b> Scheduled:</b> {row.get(date_col, 'N/A')}<br>
<b> Info:</b> {row.get(info_col, 'N/A') if info_col else 'N/A'}<br>
<b> Supervisor:</b> {row.get(supervisor_col, 'N/A') if supervisor_col else 'N/A'}
</div>
                        """, unsafe_allow_html=True)

                        if part_img_col:
                            part_img_id = convert_drive_url_to_direct(row.get(part_img_col))
                            if part_img_id:
                                st.markdown("📸 **Picture of Part:**")
                                st.markdown(f"[🔗 Open Image](https://drive.google.com/file/d/{part_img_id}/view)")

                        if problem_img_col:
                            problem_img_id = convert_drive_url_to_direct(row.get(problem_img_col))
                            if problem_img_id:
                                st.markdown("⚠️ **Picture of Problem:**")
                                st.markdown(f"[🔗 Open Image](https://drive.google.com/file/d/{problem_img_id}/view)")

                # ----------- Export Button -----------
                st.markdown("---")
                st.markdown("### 📁 Download Report")
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    result.to_excel(writer, index=False, encoding="utf-8")
                st.download_button(
                    label="📄 Download Report as Excel",
                    data=output.getvalue(),
                    file_name="maintenance_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("❌ No matching record found.")

        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# ----------- Footer -----------
st.caption("© Hamad M. Al Rugaib & Sons Trading Co. – Maintenance Department")
