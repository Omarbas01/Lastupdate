import streamlit as st
import pandas as pd
import datetime
import io
import re
from PIL import Image

st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

# -------- CSS Styling --------
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
    </style>
""", unsafe_allow_html=True)

# -------- Logo --------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=400)
except FileNotFoundError:
    st.warning("⚠️ 'logo.png' not found. Please make sure it's in the same folder.")

st.markdown("<h2 style='text-align:center;'>🛠️ Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)

user_input = st.text_input(" Enter Mobile Number or Invoice Number:")

# -------- Data Refresh Button --------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.success("✅ Data refreshed. Please click Search again.")

# -------- Utilities --------
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

def detect_mobile_column(df):
    keywords = ["جوال", "phone", "رقم"]
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            return col
    for col in df.columns:
        sample = df[col].astype(str).str.strip().dropna().head(100)
        matches = sample[sample.str.match(r"^05[0-9]{8}$")]
        if len(matches) > 3:
            return col
    return None

def detect_invoice_column(df):
    for col in df.columns:
        sample = df[col].astype(str).str.strip().dropna().head(100)
        if sample.str.match(r"SO[0-9]{9}").any():
            return col
    return df.columns[1]

def load_data():
    url = "https://docs.google.com/spreadsheets/d/1ZZOFElk1ZOKSzRuVE_d_Et46JR-How-qo5xwij8NXho/export?format=csv&gid=1295915446"
    return pd.read_csv(url)

# -------- Search Button --------
if st.button("Search"):
    if user_input.strip() == "" and "start_date" not in st.session_state:
        st.warning("Please enter mobile/invoice or apply timestamp filter.")
    else:
        try:
            with st.spinner("🛠️ Loading data..."):
                df = load_data()

            invoice_col = detect_invoice_column(df)
            phone_col = detect_mobile_column(df)

            name_col = "First Name" if "First Name" in df.columns else df.columns[2]
            address_col = "Address" if "Address" in df.columns else df.columns[18]
            markup_col = "MarkupCode" if "MarkupCode" in df.columns else df.columns[14]
            d365_col = "D365" if "D365" in df.columns else df.columns[10]
            info_col = "Info" if "Info" in df.columns else df.columns[2]
            date_col = "Timestamp" if "Timestamp" in df.columns else df.columns[0]
            supervisor_col = "Supervisor" if "Supervisor" in df.columns else None
            region_col = "Region" if "Region" in df.columns else df.columns[15]

            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

            # Filter Controls
            unique_services = df[markup_col].dropna().unique()
            selected_service = st.selectbox("📂 Filter by Service Type (Optional):", ["All"] + list(unique_services))

            start_date = st.date_input("📅 Start Timestamp Filter:", value=datetime.date(2024, 1, 1))
            end_date = st.date_input("📅 End Timestamp Filter:", value=datetime.date.today())

            filtered_df = df[
                (df[date_col].dt.date >= start_date) &
                (df[date_col].dt.date <= end_date)
            ]

            if user_input.strip():
                query = user_input.strip().lower()
                filtered_df = filtered_df[
                    filtered_df[phone_col].astype(str).str.lower().str.contains(query, na=False) |
                    filtered_df[invoice_col].astype(str).str.lower().str.contains(query, na=False)
                ]

            if selected_service != "All":
                filtered_df = filtered_df[filtered_df[markup_col] == selected_service]

            if not filtered_df.empty:
                st.success(f"✅ {len(filtered_df)} record(s) found.")

                for _, row in filtered_df.iterrows():
                    with st.expander(f"Result for Invoice: {row[invoice_col]}"):
                        st.markdown(f"""
<div class='result-box'>
<b>Name:</b> {row.get(name_col, 'N/A')}<br>
<b>Mobile:</b> {row.get(phone_col, 'N/A')}<br>
<b>Invoice:</b> {row.get(invoice_col, 'N/A')}<br>
<b>Address:</b> {row.get(address_col, 'N/A')}<br>
<b>D365:</b> {row.get(d365_col, 'N/A')}<br>
<b>Service Type:</b> {row.get(markup_col, 'N/A')}<br>
<b>Scheduled:</b> {row.get(date_col, 'N/A')}<br>
<b>Info:</b> {row.get(info_col, 'N/A')}<br>
<b>Supervisor:</b> {row.get(supervisor_col, 'N/A')}
</div>
""", unsafe_allow_html=True)

                        # Images
                        part_img_id = convert_drive_url_to_direct(row.get("Part Image", ""))
                        if part_img_id:
                            st.markdown("📸 **Picture of Part:**")
                            st.markdown(f"[🔗 View](https://drive.google.com/file/d/{part_img_id}/view)")

                        problem_img_id = convert_drive_url_to_direct(row.get("Problem Image", ""))
                        if problem_img_id:
                            st.markdown("⚠️ **Picture of Problem:**")
                            st.markdown(f"[🔗 View](https://drive.google.com/file/d/{problem_img_id}/view)")

                # --- Summary by MarkupCode
                summary = filtered_df.groupby(markup_col).size().reset_index(name='Total')
                summary = pd.concat([summary, pd.DataFrame({markup_col: ['🔢 Total'], 'Total': [summary['Total'].sum()]})], ignore_index=True)
                st.markdown("📊 **Summary by Service**")
                st.dataframe(summary)

                # --- Summary by Region + Markup
                region_markup = (
                    filtered_df.groupby([region_col, markup_col])
                    .size()
                    .reset_index(name='Total')
                    .sort_values(by=[region_col, 'Total'], ascending=[True, False])
                )
                st.markdown("📍 **Region + Service Summary**")
                st.dataframe(region_markup)

                # --- Excel Export
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    filtered_df.to_excel(writer, sheet_name="Filtered Data", index=False)
                    summary.to_excel(writer, sheet_name="Service Summary", index=False)
                    region_markup.to_excel(writer, sheet_name="Region+Service", index=False)

                    for sheet in writer.sheets.values():
                        sheet.set_column('A:Z', 25)

                buffer.seek(0)
                st.download_button("⬇️ Download Excel Report", buffer, file_name="maintenance_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            else:
                st.error("❌ No matching record found.")

        except Exception as e:
            st.error(f"⚠️ Error: {e}")

st.caption("© Hamad M. Al Rugaib & Sons Trading Co. – Maintenance Department")
