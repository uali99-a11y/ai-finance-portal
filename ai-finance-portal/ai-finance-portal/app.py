import streamlit as st

st.set_page_config(
    page_title="AI Finance Portal",
    page_icon="💼",
    layout="wide"
)

st.title("💼 AI Finance Portal")

st.markdown(
    """
    ### Financial Reporting & Intelligence Platform

    Upload financial data to generate:
    - Trial Balance
    - Profit & Loss
    - Balance Sheet
    - Cash Flow
    - Financial Ratios
    - AI Financial Analysis
    """
)

st.divider()

st.subheader("Welcome")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Companies", "0")

with col2:
    st.metric("Reports", "0")

with col3:
    st.metric("AI Insights", "0")

st.info(
    "V0.1 is under development. "
    "Trial Balance upload and financial reporting will be added next."
)
