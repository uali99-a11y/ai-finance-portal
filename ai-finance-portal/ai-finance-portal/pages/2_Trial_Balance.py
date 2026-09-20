import streamlit as st
import pandas as pd
from modules.db import get_supabase_client

st.set_page_config(page_title="Trial Balance", page_icon="📑", layout="wide")

st.title("📑 Trial Balance")

supabase = get_supabase_client()

companies_response = supabase.table("companies").select("*").order("name").execute()
companies = companies_response.data

if not companies:
    st.warning("No companies found yet. Please add a company first from the Dashboard page.")
    st.stop()

company_names = [c["name"] for c in companies]
selected_name = st.selectbox("Select Company", company_names)
selected_company = next(c for c in companies if c["name"] == selected_name)

st.markdown(
    "Upload your Trial Balance Excel file below. "
    "The file should have columns named **Account Name**, **Debit**, and **Credit**."
)

uploaded_file = st.file_uploader("Upload Trial Balance (Excel)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"File uploaded successfully — {len(df)} rows found.")

        st.subheader("Preview")
        st.dataframe(df, use_container_width=True)

        st.divider()
        st.subheader("Balance Check")

        if "Debit" in df.columns and "Credit" in df.columns:
            total_debit = df["Debit"].fillna(0).sum()
            total_credit = df["Credit"].fillna(0).sum()
            is_balanced = abs(total_debit - total_credit) < 0.01

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Debit", f"{total_debit:,.2f}")
            col2.metric("Total Credit", f"{total_credit:,.2f}")
            with col3:
                if is_balanced:
                    st.success("✅ Balanced")
                else:
                    st.error("⚠️ Not Balanced")

            st.session_state["trial_balance"] = df

            st.divider()
            if st.button("💾 Save to Database"):
                upload_result = supabase.table("tb_uploads").insert({
                    "company_id": selected_company["id"],
                    "file_name": uploaded_file.name
                }).execute()

                upload_id = upload_result.data[0]["id"]

                lines = []
                for _, row in df.iterrows():
                    lines.append({
                        "upload_id": upload_id,
                        "account_name": str(row.get("Account Name", "")),
                        "debit": float(row.get("Debit", 0) or 0),
                        "credit": float(row.get("Credit", 0) or 0)
                    })

                supabase.table("tb_lines").insert(lines).execute()
                st.success(f"Saved {len(lines)} rows to database for {selected_company['name']}!")
        else:
            st.warning(
                "Could not find 'Debit' and 'Credit' columns in your file. "
                "Please check that your Excel file has these exact column headers."
            )

    except Exception as e:
        st.error(f"Could not read the file. Please make sure it's a valid Excel file. Error: {e}")
else:
    st.info("Waiting for file upload...")
