# streamlit_app.py

import streamlit as st
import pandas as pd
from PIL import Image
import re
import io
from datetime import datetime, time  # Include time

# Conditionally import xlsxwriter only when needed (at export time)
try:
    import xlsxwriter
except ModuleNotFoundError:
    xlsxwriter = None

st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

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

try:
    logo = Image.open("logo.png")
    st.image(logo, width=350)
except FileNotFoundError:
    st.warning("\u26a0\ufe0f 'logo.png' not found. Please make sure it's in the same folder.")

st.markdown("<h2 style='text-align:center; font-family:sans-serif;'>\ud83d\udee0\ufe0f Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)

user_input = st.text_input(" Enter Mobile Number or Invoice Number:")

if st.button("\ud83d\udd04 Refresh Data"):
    st.cache_data.clear()
    st.success("\u2705 Data refreshed. Please click Search again.")

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
    target_keywords = ["Phone Number | \u0631\u0642\u0645 \u0627\u0644\u062c\u0648\u0627\u0644 ", "\u062c\u0648\u0627\u0644", "\u0631\u0642\u0645", "phone"]
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

def detect_invoice_column(df):
    for col in df.columns:
        sample = df[col].astype(str).str.strip().dropna().head(100)
        if sample.str.match(r"SO[0-9]{9}").any():
            return col
    return df.columns[1]

def load_data():
    url = "https://docs.google.com/spreadsheets/d/1ZZOFElk1ZOKSzRuVE_d_Et46JR-How-qo5xwij8NXho/export?format=csv&gid=1295915446"
    return pd.read_csv(url, encoding="utf-8")

# Fix: Replace nonexistent datetime_input with date_input + time_input
start_date = st.date_input("\ud83d\uddd3\ufe0f Start Date (Optional):")
start_time = st.time_input("\u23f0 Start Time:", value=time(0, 0))
start_datetime = datetime.combine(start_date, start_time)

end_date = st.date_input("\ud83d\uddd3\ufe0f End Date (Optional):")
end_time = st.time_input("\u23f0 End Time:", value=time(23, 59))
end_datetime = datetime.combine(end_date, end_time)

if st.button("Search"):
    if not user_input.strip() and not start_datetime and not end_datetime:
        st.warning("Please enter a mobile number, invoice number, or select a timestamp filter.")
    else:
        try:
            with st.spinner("\ud83d\udee0\ufe0f Loading data..."):
                df = load_data()

            invoice_col = detect_invoice_column(df)
            phone_col = detect_mobile_column(df)

            if not phone_col:
                st.error("\u274c Could not detect mobile number column. Please check the sheet.")
                st.stop()

            name_col = "First Name " if "\u0627\u0644\u0627\u0633\u0645 \u0627\u0644\u0623\u0648\u0644" in df.columns else df.columns[4]
            address_col = "Address | \u0627\u0644\u0639\u0646\u0648\u0627\u0646" if "\u0627\u0644\u0639\u0646\u0648\u0627\u0646" in df.columns else df.columns[18]
            d365_col = "D365" if "D365" in df.columns else df.columns[10]
            markup_col = "MarkupCode" if "MarkupCode" in df.columns else df.columns[14]
            date_col = "Date" if "Scheduled" in df.columns else df.columns[14]
            info_col = "\u0627\u0644\u062a\u0642\u064a\u064a\u0645" if "Info" in df.columns else df.columns[2]
            part_img_col = "Picture of Part" if "Part Image" in df.columns else df.columns[26]
            problem_img_col = "Problem Image" if "Problem Image" in df.columns else df.columns[27]
            supervisor_col = "Supervisor" if "Supervisor" in df.columns else None

            unique_services = df[markup_col].dropna().unique()
            selected_service = st.selectbox("\ud83d\udcc2 Filter by Service Type (Optional):", ["All"] + list(unique_services))

            result = df

            if user_input.strip():
                query = user_input.strip().lower()
                result = result[
                    result[phone_col].astype(str).str.strip().str.lower().str.contains(query, na=False) |
                    result[invoice_col].astype(str).str.strip().str.lower().str.contains(query, na=False)
                ]

            if selected_service != "All":
                result = result[result[markup_col] == selected_service]

            result[date_col] = pd.to_datetime(result[date_col], errors='coerce')

            if start_datetime:
                result = result[result[date_col] >= pd.to_datetime(start_datetime)]
            if end_datetime:
                result = result[result[date_col] <= pd.to_datetime(end_datetime)]

            if not result.empty:
                st.success(f"\u2705 {len(result)} record(s) found.")

                st.markdown("### \ud83d\udcca Summary")
                st.write(result[[markup_col, date_col]].groupby(markup_col).count().rename(columns={date_col: "Total"}))

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
                                st.markdown("\ud83d\udcf8 **Picture of Part:**")
                                st.markdown(f"[\ud83d\udd17 Open Image](https://drive.google.com/file/d/{part_img_id}/view)")

                        if problem_img_col:
                            problem_img_id = convert_drive_url_to_direct(row.get(problem_img_col))
                            if problem_img_id:
                                st.markdown("\u26a0\ufe0f **Picture of Problem:**")
                                st.markdown(f"[\ud83d\udd17 Open Image](https://drive.google.com/file/d/{problem_img_id}/view)")

                if xlsxwriter:
                    st.markdown("---")
                    st.markdown("### \ud83d\udcc1 Download Report")
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        result.to_excel(writer, index=False, sheet_name="Maintenance Report")
                        workbook = writer.book
                        worksheet = writer.sheets["Maintenance Report"]
                        header_format = workbook.add_format({"bold": True, "align": "center"})
                        for col_num, value in enumerate(result.columns.values):
                            worksheet.write(0, col_num, value, header_format)
                            worksheet.set_column(col_num, col_num, 20)
                        writer.close()
                    output.seek(0)
                    st.download_button(
                        label="\ud83d\udcc4 Download Report as Excel",
                        data=output,
                        file_name="maintenance_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("\u26a0\ufe0f Excel export requires `xlsxwriter`. Please install it using `pip install xlsxwriter`.")
            else:
                st.error("\u274c No matching record found.")

        except Exception as e:
            st.error(f"\u26a0\ufe0f Error: {e}")

st.caption("\u00a9 Hamad M. Al Rugaib & Sons Trading Co. – Maintenance Department")
