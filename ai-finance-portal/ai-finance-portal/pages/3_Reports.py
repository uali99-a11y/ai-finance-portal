import streamlit as st
import pandas as pd
from modules.db import get_supabase_client

st.set_page_config(page_title="Reports", page_icon="📈", layout="wide")

st.title("📈 Reports")

supabase = get_supabase_client()

companies_response = supabase.table("companies").select("*").order("name").execute()
companies = companies_response.data

if not companies:
    st.warning("No companies found yet. Please add a company first from the Dashboard page.")
    st.stop()

company_names = [c["name"] for c in companies]
selected_name = st.selectbox("Select Company", company_names)
selected_company = next(c for c in companies if c["name"] == selected_name)

uploads_response = (
    supabase.table("tb_uploads")
    .select("*")
    .eq("company_id", selected_company["id"])
    .order("uploaded_at", desc=True)
    .execute()
)
uploads = uploads_response.data

if not uploads:
    st.info("No Trial Balance uploaded yet for this company. Go to the Trial Balance page first.")
    st.stop()

upload_labels = [f"{u['file_name']} — {u['uploaded_at'][:16].replace('T', ' ')}" for u in uploads]
selected_upload_label = st.selectbox("Select Trial Balance Upload", upload_labels)
selected_upload = uploads[upload_labels.index(selected_upload_label)]

lines_response = (
    supabase.table("tb_lines")
    .select("*")
    .eq("upload_id", selected_upload["id"])
    .execute()
)
lines = lines_response.data

if not lines:
    st.warning("No line items found for this upload.")
    st.stop()

df = pd.DataFrame(lines)
df["debit"] = df["debit"].fillna(0)
df["credit"] = df["credit"].fillna(0)
df["account_type"] = df["account_type"].fillna("Asset")


def type_total(account_type, flip=False):
    subset = df[df["account_type"] == account_type]
    net = subset["debit"].sum() - subset["credit"].sum()
    return -net if flip else net


assets = type_total("Asset")
liabilities = type_total("Liability", flip=True)
equity = type_total("Equity", flip=True)
revenue = type_total("Revenue", flip=True)
expense = type_total("Expense")

net_profit = revenue - expense
total_equity = equity + net_profit

tab1, tab2 = st.tabs(["📊 Profit & Loss", "🏦 Balance Sheet"])

with tab1:
    st.subheader("Profit & Loss Statement")

    st.markdown("**Revenue**")
    revenue_df = df[df["account_type"] == "Revenue"].copy()
    revenue_df["Amount"] = revenue_df["credit"] - revenue_df["debit"]
    st.dataframe(
        revenue_df[["account_name", "Amount"]].rename(columns={"account_name": "Account"}),
        use_container_width=True, hide_index=True
    )
    st.metric("Total Revenue", f"{revenue:,.2f}")

    st.markdown("**Expenses**")
    expense_df = df[df["account_type"] == "Expense"].copy()
    expense_df["Amount"] = expense_df["debit"] - expense_df["credit"]
    st.dataframe(
        expense_df[["account_name", "Amount"]].rename(columns={"account_name": "Account"}),
        use_container_width=True, hide_index=True
    )
    st.metric("Total Expenses", f"{expense:,.2f}")

    st.divider()
    if net_profit >= 0:
        st.success(f"### Net Profit: {net_profit:,.2f}")
    else:
        st.error(f"### Net Loss: {net_profit:,.2f}")

with tab2:
    st.subheader("Balance Sheet")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Assets**")
        assets_df = df[df["account_type"] == "Asset"].copy()
        assets_df["Amount"] = assets_df["debit"] - assets_df["credit"]
        st.dataframe(
            assets_df[["account_name", "Amount"]].rename(columns={"account_name": "Account"}),
            use_container_width=True, hide_index=True
        )
        st.metric("Total Assets", f"{assets:,.2f}")

    with col2:
        st.markdown("**Liabilities**")
        liab_df = df[df["account_type"] == "Liability"].copy()
        liab_df["Amount"] = liab_df["credit"] - liab_df["debit"]
        st.dataframe(
            liab_df[["account_name", "Amount"]].rename(columns={"account_name": "Account"}),
            use_container_width=True, hide_index=True
        )
        st.metric("Total Liabilities", f"{liabilities:,.2f}")

        st.markdown("**Equity**")
        equity_df = df[df["account_type"] == "Equity"].copy()
        equity_df["Amount"] = equity_df["credit"] - equity_df["debit"]
        st.dataframe(
            equity_df[["account_name", "Amount"]].rename(columns={"account_name": "Account"}),
            use_container_width=True, hide_index=True
        )
        st.write(f"Retained Earnings (Current Period Profit): {net_profit:,.2f}")
        st.metric("Total Equity", f"{total_equity:,.2f}")

    st.divider()
    total_liab_equity = liabilities + total_equity
    check_col1, check_col2, check_col3 = st.columns(3)
    check_col1.metric("Total Assets", f"{assets:,.2f}")
    check_col2.metric("Total Liabilities + Equity", f"{total_liab_equity:,.2f}")
    with check_col3:
        if abs(assets - total_liab_equity) < 0.01:
            st.success("✅ Balance Sheet Balanced")
        else:
            st.error("⚠️ Not Balanced")
