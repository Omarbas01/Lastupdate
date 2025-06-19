import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import re

st.set_page_config(page_title="🔧 Maintenance Tracker & Dashboard", layout="wide")

# ---------- Sidebar Navigation ----------
page = st.sidebar.radio("📍 Navigate", ["Search", "Dashboard"])

# ---------- Load Data ----------
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1MitHqD5SZfm-yAUsrc8jkki7zD9zFlH1JXhHTKjfAhs/export?format=csv&gid=2031108065"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

# ---------- Convert Google Drive URL to Direct Image ID ----------
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

# ---------- SEARCH PAGE ----------
if page == "Search":
    st.title("🛠️ Maintenance Tracker - Al Rugaib")

    try:
        logo = Image.open("logo.png")
        st.image(logo, width=400)
    except FileNotFoundError:
        st.warning("⚠️ 'logo.png' not found. Please make sure it's in the same folder.")

    user_input = st.text_input("🔎 Enter Mobile Number or Invoice Number:")

    if st.button("Search"):
        if user_input.strip() == "":
            st.warning("Please enter a mobile number or invoice number.")
        else:
            with st.spinner("🔄 Loading data..."):
                df = load_data()

            phone_col = df.columns[19]       # T
            invoice_col = df.columns[1]      # B
            name_col = df.columns[2]         # C
            address_col = df.columns[20]     # U
            d365_col = df.columns[12]        # M
            markup_col = df.columns[14]      # O
            date_col = df.columns[15]        # P
            info_col = df.columns[28]        # AC
            part_img_col = df.columns[29]    # AD
            problem_img_col = df.columns[30] # AE
            supervisor_col = df.columns[33]  # AH

            result = df[
                df[phone_col].astype(str).str.contains(user_input, case=False, na=False) |
                df[invoice_col].astype(str).str.contains(user_input, case=False, na=False)
            ]

            if not result.empty:
                st.success(f"✅ {len(result)} record(s) found.")
                for _, row in result.iterrows():
                    with st.expander(f"🔍 Result for Invoice: {row[invoice_col]}"):
                        st.markdown(f"""
<div style='background:#f9f9f9; padding:10px; border-radius:8px;'>
<b>👤 Name:</b> {row[name_col]}<br>
<b>📱 Mobile:</b> {row[phone_col]}<br>
<b>🧾 Invoice:</b> {row[invoice_col]}<br>
<b>📍 Address:</b> {row[address_col]}<br>
<b>🔄 D365 Update:</b> {row[d365_col]}<br>
<b>🛠️ Service Type:</b> {row[markup_col]}<br>
<b>📅 Scheduled Date:</b> {row[date_col]}<br>
<b>📝 Extra Info:</b> {row[info_col]}<br>
<b>👨‍🔧 Shift Supervisor:</b> {row[supervisor_col]}
</div>
                        """, unsafe_allow_html=True)

                        part_img_id = convert_drive_url_to_direct(row[part_img_col])
                        if part_img_id:
                            st.markdown(f"📸 [Picture of Part](https://drive.google.com/file/d/{part_img_id}/view)")

                        problem_img_id = convert_drive_url_to_direct(row[problem_img_col])
                        if problem_img_id:
                            st.markdown(f"⚠️ [Picture of Problem](https://drive.google.com/file/d/{problem_img_id}/view)")
            else:
                st.error("❌ No matching record found.")

# ---------- DASHBOARD PAGE ----------
elif page == "Dashboard":
    st.title("📊 Maintenance Dashboard - Al Rugaib")

    with st.spinner("Loading data..."):
        df = load_data()

    try:
        status_col = df.columns[12]      # M - D365 Update
        region_col = df.columns[20]      # U - Address
        service_col = df.columns[14]     # O - Service Type
        date_col = df.columns[15]        # P - Scheduled Date

        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])

        total_requests = len(df)
        total_regions = df[region_col].nunique()
        total_services = df[service_col].nunique()

        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Total Requests", total_requests)
        col2.metric("📍 Unique Regions", total_regions)
        col3.metric("🛠️ Service Types", total_services)

        st.markdown("---")

        colA, colB = st.columns(2)

        with colA:
            st.subheader("🗂️ Requests by Status (D365 Update)")
            fig_status = px.pie(df, names=status_col, title="Status Distribution", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_status, use_container_width=True)

        with colB:
            st.subheader("📍 Requests by Region")
            fig_region = px.bar(df[region_col].value_counts().reset_index(), 
                                x='index', y=region_col, 
                                labels={'index': 'Region', region_col: 'Request Count'},
                                color='index', 
                                color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_region, use_container_width=True)

        st.markdown("---")
        st.subheader("📅 Scheduled Requests Over Time")
        date_data = df[date_col].dt.date.value_counts().sort_index()
        date_df = pd.DataFrame({"Date": date_data.index, "Count": date_data.values})
        fig_timeline = px.line(date_df, x="Date", y="Count", markers=True, title="Scheduled Request Trend")
        st.plotly_chart(fig_timeline, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

# ---------- Footer ----------
st.caption("Made with ❤️ for Hamad M. Al Rugaib & Sons - Powered by Streamlit")
