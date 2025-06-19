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
    st.markdown("""
        <div class='logo-container'>
            <img src='data:image/png;base64,{}' width='250'>
        </div>
    """.format(Image.open("logo.png").convert("RGB").tobytes().hex()), unsafe_allow_html=True)
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
    return pd.read_csv(url)

# ----------- Search Button -----------
if st.button("Search"):
    if user_input.strip() == "":
        st.warning("Please enter a mobile number or invoice number.")
    else:
        try:
            with st.spinner("🔄 Loading data..."):
                df = load_data()

            # Column mappings
            phone_col = df.columns[19]
            invoice_col = df.columns[1]
            name_col = df.columns[2]
            address_col = df.columns[20]
            d365_col = df.columns[12]
            markup_col = df.columns[14]
            date_col = df.columns[15]
            date_request_col = df.columns[10]
date_request_col = df.columns[10]  # Assuming 'Date| التاريخ' is column 10
            info_col = df.columns[28]
            part_img_col = df.columns[29]
            problem_img_col = df.columns[30]
            supervisor_col = df.columns[33]

            # Optional service type filter
            unique_services = df[markup_col].dropna().unique()
            selected_service = st.selectbox("📂 Filter by Service Type (Optional):", ["All"] + list(unique_services))

            # Filtered results
            result = df[
                df[phone_col].astype(str).str.contains(user_input, case=False, na=False) |
                df[invoice_col].astype(str).str.contains(user_input, case=False, na=False)
            ]

            if selected_service != "All":
                result = result[result[markup_col] == selected_service]

            if not result.empty:
                st.success(f"✅ {len(result)} record(s) found.")
                for _, row in result.iterrows():
                    with st.expander(f"🔍 Result for Invoice: {row[invoice_col]}"):
                        st.markdown(f"""
<div class='result-box'>
<b>👤 Name:</b> {row[name_col]}<br>
<b>📱 Mobile:</b> {row[phone_col]}<br>
<b>🧾 Invoice:</b> {row[invoice_col]}<br>
<b>📍 Address:</b> {row[address_col]}<br>
<b>🔄 D365 Update:</b> {row[d365_col]}<br>
<b>🛠️ Service Type:</b> {row[markup_col]}<br>
<b>📅 Scheduled:</b> {row[date_col]}<br>
<b>🗓️ Request Date:</b> {row[date_request_col]}<br>
<b>📝 Info:</b> {row[info_col]}<br>
<b>👨‍🔧 Supervisor:</b> {row[supervisor_col]}
</div>
                        """, unsafe_allow_html=True)

                        # Part Image
                        part_img_id = convert_drive_url_to_direct(row[part_img_col])
                        if part_img_id:
                            st.markdown("📸 **Picture of Part:**")
                            st.markdown(f"[🔗 Open Image](https://drive.google.com/file/d/{part_img_id}/view)")

                        # Problem Image
                        problem_img_id = convert_drive_url_to_direct(row[problem_img_col])
                        if problem_img_id:
                            st.markdown("⚠️ **Picture of Problem:**")
                            st.markdown(f"[🔗 Open Image](https://drive.google.com/file/d/{problem_img_id}/view)")
            else:
                st.error("❌ No matching record found.")

        except Exception as e:
            st.error(f"⚠️ Error: {e}")

# ----------- Footer -----------
st.caption("© Hamad M. Al Rugaib & Sons Trading Co. – Powered by Streamlit")
