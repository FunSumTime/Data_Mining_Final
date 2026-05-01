import streamlit as st
import pandas as pd

# --- 1. Page Setup ---
st.set_page_config(layout="wide", page_title="CVE Review Dashboard")
st.title("🛡️ NVD Human-in-the-Loop Review")

# --- 2. Load Data --
# We use st.cache_data so it doesn't reload the CSV every time you click a button
@st.cache_data
def load_pending_data():
    # Make sure this matches the filename from your Milestone 2 output
    try:
        # we are gettinn gthe data  froom the csv by using pandas  to read it
        return pd.read_csv("nvd_processed_data.csv")
    except FileNotFoundError:
        return pd.DataFrame()

df = load_pending_data()

if df.empty:
    st.error("No data found! Please run your main.py pipeline first.")
    st.stop()

# --- 3. Manage State (The "Breakpoint") ---
# Streamlit reruns top-to-bottom on every click. 
# session_state remembers our place in the list and our approved records.
if 'current_index' not in st.session_state:
    # like a statemachine
    st.session_state.current_index = 0
if 'approved_records' not in st.session_state:
    st.session_state.approved_records = []

# --- 4. Completion Screen ---
if st.session_state.current_index >= len(df):
    st.success("🎉 All records have been reviewed!")
    
    # Show the final approved dataset
    # should be a list just  want  to see it for debugging
    print(st.session_state.approved_records)
    final_df = pd.DataFrame(st.session_state.approved_records)
    st.dataframe(final_df)
    
    # Save the final approved list for Milestone 4
    if st.button("💾 Save Final Dataset for CKAN Upload"):
        final_df.to_csv("approved_cves_for_upload.csv", index=False)
        st.success("Saved to approved_cves_for_upload.csv!")
    
    st.stop()

# --- 5. The Review UI ---
# Grab the current record based on our index
record = df.iloc[st.session_state.current_index]
print("records")
print(record)
# loading bar
st.progress((st.session_state.current_index) / len(df), text=f"Reviewing record {st.session_state.current_index + 1} of {len(df)}")
st.subheader(f"Evaluating: {record['cve_id']}")

# Create a side-by-side layout
col1, col2 = st.columns(2)

with col1:
    # Everything here renders on the left side of the screen
    st.markdown("### 📄 Raw Source Data")
    # Displaying the raw prompt text we fed to Gemini
    st.text_area("Original Description & CPEs", record.get('llm_prompt_text', 'No raw text found'), height=400, disabled=True)
    st.info(f"**Official Severity:** {record['official_severity']}")
    st.info(f"**Published Date:** {record['published_date']}")

with col2:
    st.markdown("### 🤖 AI Extraction (Editable)")
    # By using Streamlit input fields, we instantly create the "Edit" functionality!
    # The default value is what Gemini extracted, but you can type over it.
    edited_tech = st.text_input("Affected Technology", record['affected_technology'])
    edited_patch = st.checkbox("Requires Patch", value=bool(record['requires_patch']))
    edited_rating = st.selectbox("Vulnerability Rating", ["Critical", "High", "Medium", "Low", "Unknown"], index=["Critical", "High", "Medium", "Low", "Unknown"].index(record.get('vulnerability_rating', 'Unknown')))
    edited_summary = st.text_area("Plain English Summary", record['plain_english_summary'], height=150)

st.divider()
# add  a thing so if the  cve_id is already on the server  skip it  so we donnt add  a duplicate.

# --- 6. The Action Buttons ---
col3, col4, col5 = st.columns([1, 1, 1])

with col3:
    # APPROVE (and automatically apply any edits made in the text boxes above)
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

with col5:
    # REJECT (skips the record entirely)
    if st.button("❌ Reject (Trash)", type="primary", use_container_width=True):
        st.session_state.current_index += 1
        st.rerun()