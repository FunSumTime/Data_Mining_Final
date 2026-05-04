import streamlit as st
import pandas as pd
import sqlite3
import streamlit_authenticator as stauth

st.set_page_config(layout="wide", page_title="CVE Review Dashboard")

# --- 1. Database & Auth Setup ---
def get_user_credentials():
    conn = sqlite3.connect('database/users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, email, password_hash FROM users")
    users = cursor.fetchall()
    conn.close()
    
    credentials = {"usernames": {}}
    for user in users:
        credentials["usernames"][user[0]] = {"name": user[1], "email": user[2], "password": user[3]}
    return credentials

authenticator = stauth.Authenticate(
    credentials=get_user_credentials(),
    cookie_name="nvd_dashboard_cookie",
    key="some_random_secret_string",
    cookie_expiry_days=30
)

authenticator.login()

# --- 2. The Secure Admin Dashboard ---
if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar')
    st.title("🛡️ Secure Human-in-the-Loop Review")
    
    # --- Load Data ---
    @st.cache_data
    def load_pending_data():
        try:
            return pd.read_csv("database/pending_cves.csv")
        except FileNotFoundError:
            return pd.DataFrame()

    df = load_pending_data()

    if df.empty:
        st.info("No pending data found! Please run your Ingestion pipeline first.")
        st.stop()

    # --- Manage State ---
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'approved_records' not in st.session_state:
        st.session_state.approved_records = []

    # --- Completion Screen ---
    if st.session_state.current_index >= len(df):
        st.success("🎉 All records have been reviewed!")
        final_df = pd.DataFrame(st.session_state.approved_records)
        st.dataframe(final_df)
        
        if st.button("💾 Save Final Dataset for CKAN Upload"):
            final_df.to_csv("database/processed_cves.csv", index=False)
            st.success("Saved to database/processed_cves.csv!")
        st.stop()

    # --- The Review UI ---
    record = df.iloc[st.session_state.current_index]
    st.progress((st.session_state.current_index) / len(df), text=f"Reviewing record {st.session_state.current_index + 1} of {len(df)}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 Raw Source Data")
        st.text_area("Original Description", record.get('llm_prompt_text', 'No text'), height=300, disabled=True)
        st.info(f"**Severity:** {record['official_severity']} | **Published:** {record['published_date']}")

    with col2:
        st.markdown("### 🤖 AI Extraction (Editable)")
        edited_tech = st.text_input("Affected Technology", record['affected_technology'])
        edited_patch = st.checkbox("Requires Patch", value=bool(record['requires_patch']))
        edited_rating = st.selectbox("Vulnerability Rating", ["Critical", "High", "Medium", "Low", "Unknown"], index=0)
        edited_summary = st.text_area("Plain English Summary", record['plain_english_summary'], height=150)

    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        if st.button("✅ Approve & Next", use_container_width=True):
            approved_row = {
                "cve_id": record['cve_id'],
                "published_date": record['published_date'],
                "official_severity": record['official_severity'],
                "affected_technology": edited_tech,
                "requires_patch": edited_patch,
                "vulnerability_rating": edited_rating,
                "plain_english_summary": edited_summary
            }
            st.session_state.approved_records.append(approved_row)
            st.session_state.current_index += 1
            st.rerun()
    with col4:
        if st.button("❌ Reject (Trash)", type="primary", use_container_width=True):
            st.session_state.current_index += 1
            st.rerun()

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')