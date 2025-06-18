import streamlit as st

# Page setup
st.set_page_config(page_title="Maintenance Tracker - Rugaib", layout="centered")

# Custom styling
st.markdown("""
    <style>
        body {
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
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

# Display company logo
st.image("logo.png", width=300)

# App title
st.markdown("<h2 style='text-align: center;'>🔍 Maintenance Tracker - Rugaib</h2>", unsafe_allow_html=True)
st.markdown("#### Please enter mobile number or invoice number:")

# Input field
user_input = st.text_input("", max_chars=15)

# Example data (replace with actual lookup logic)
def fetch_maintenance_data(input_value):
    return {
        "Name": "Salman",
        "Mobile Number": "0501762520",
        "Invoice Number": "SO000697361",
        "Address": "Al-Ahsa, Al-Ghassaniyah",
        "D365 Update": "Not Available"
    }

# Search button
if st.button("🔍 Search"):
    if not user_input:
        st.warning("Please enter a mobile number or invoice number.")
    else:
        result = fetch_maintenance_data(user_input)
        st.markdown("---")
        for k, v in result.items():
            st.markdown(f"**{k}**: {v}")
