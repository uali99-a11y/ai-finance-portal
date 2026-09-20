import streamlit as st
from modules.db import get_supabase_client

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard")

supabase = get_supabase_client()

st.subheader("Add a Company")

with st.form("new_company_form"):
    new_company_name = st.text_input("Company Name")
    submitted = st.form_submit_button("Add Company")
    if submitted and new_company_name.strip():
        supabase.table("companies").insert({"name": new_company_name.strip()}).execute()
        st.success(f"Company '{new_company_name}' added.")
        st.rerun()

st.divider()
st.subheader("Existing Companies")

companies_response = supabase.table("companies").select("*").order("created_at", desc=True).execute()
companies = companies_response.data

if companies:
    for c in companies:
        st.write(f"🏢 **{c['name']}**")
else:
    st.info("No companies yet. Add one above.")
