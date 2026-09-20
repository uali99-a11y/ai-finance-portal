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

ACCOUNT_TYPES = ["Asset", "Liability", "Equity", "Revenue", "Expense"]

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"File uploaded successfully — {len(df)} rows found.")

        st.subheader("Preview")
        st.dataframe(df, use_container_width=True)

        if "Debit" not in df.columns or "Credit" not in df.columns or "Account Name" not in df.columns:
            st.warning(
                "Could not find 'Account Name', 'Debit' and 'Credit' columns in your file. "
                "Please check that your Excel file has these exact column headers."
            )
            st.stop()

        st.divider()
        st.subheader("Balance Check")

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
        st.subheader("Map Account Types")
        st.caption(
            "Tell us what type each account is, so we can build the P&L and Balance Sheet. "
            "Previously mapped accounts are filled in automatically."
        )

        existing_mapping_response = (
            supabase.table("account_mapping")
            .select("account_name, account_type")
            .eq("company_id", selected_company["id"])
            .execute()
        )
        existing_mapping = {
            row["account_name"]: row["account_type"] for row in existing_mapping_response.data
        }

        unique_accounts = df["Account Name"].dropna().unique().tolist()
        mapping_df = pd.DataFrame({
            "Account Name": unique_accounts,
            "Account Type": [existing_mapping.get(name, "Asset") for name in unique_accounts]
        })

        edited_mapping = st.data_editor(
            mapping_df,
            column_config={
                "Account Type": st.column_config.SelectboxColumn(
                    "Account Type",
                    options=ACCOUNT_TYPES,
                    required=True,
                )
            },
            disabled=["Account Name"],
            use_container_width=True,
            hide_index=True,
            key="account_mapping_editor"
        )

        st.divider()
        if st.button("💾 Save to Database"):
            mapping_records = [
                {
                    "company_id": selected_company["id"],
                    "account_name": row["Account Name"],
                    "account_type": row["Account Type"],
                }
                for _, row in edited_mapping.iterrows()
            ]
            supabase.table("account_mapping").upsert(
                mapping_records, on_conflict="company_id,account_name"
            ).execute()

            upload_result = supabase.table("tb_uploads").insert({
                "company_id": selected_company["id"],
                "file_name": uploaded_file.name
            }).execute()
            upload_id = upload_result.data[0]["id"]

            type_lookup = dict(zip(edited_mapping["Account Name"], edited_mapping["Account Type"]))
            lines = []
            for _, row in df.iterrows():
                account_name = str(row.get("Account Name", ""))
                lines.append({
                    "upload_id": upload_id,
                    "account_name": account_name,
                    "debit": float(row.get("Debit", 0) or 0),
                    "credit": float(row.get("Credit", 0) or 0),
                    "account_type": type_lookup.get(account_name, "Asset")
                })

            supabase.table("tb_lines").insert(lines).execute()
            st.success(
                f"Saved {len(lines)} rows to database for {selected_company['name']}! "
                "Go to the Reports page to view P&L and Balance Sheet."
            )

    except Exception as e:
        st.error(f"Could not read the file. Please make sure it's a valid Excel file. Error: {e}")
else:
    st.info("Waiting for file upload...")
