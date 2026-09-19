import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trial Balance", page_icon="📑", layout="wide")

st.title("📑 Trial Balance")

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

            # Save to session so other pages can use it later
            st.session_state["trial_balance"] = df
        else:
            st.warning(
                "Could not find 'Debit' and 'Credit' columns in your file. "
                "Please check that your Excel file has these exact column headers."
            )

    except Exception as e:
        st.error(f"Could not read the file. Please make sure it's a valid Excel file. Error: {e}")
else:
    st.info("Waiting for file upload...")
