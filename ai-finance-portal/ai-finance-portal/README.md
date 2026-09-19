# 💼 AI Finance Portal

AI-powered web portal for generating financial statements and reports from uploaded Excel files, with planned integration for SAP Business One and Odoo.

## Current Status: V0.1 (Skeleton)

This is the starting skeleton of the portal, built with [Streamlit](https://streamlit.io).

### What's included
- `app.py` — Home page
- `pages/` — Dashboard, Trial Balance, Reports (placeholders for now)
- `modules/` — Backend logic (Trial Balance engine, Financial Statements — to be built)
- `data/` — Folder for uploaded files (never uploaded to GitHub, see `.gitignore`)

### Roadmap
1. ✅ Portal skeleton
2. Database design (Supabase)
3. Login / Authentication
4. Company creation
5. Excel Trial Balance upload
6. Trial Balance engine
7. Chart of Accounts mapping
8. P&L, Balance Sheet, Cash Flow
9. Financial ratios
10. AI-powered analysis
11. Cloud deployment
12. SAP B1 / Odoo integration

## Running this project

This app is deployed via Streamlit Community Cloud — no local installation needed to use it.

To run it locally instead:
```
pip install -r requirements.txt
streamlit run app.py
```
