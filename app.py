import streamlit as st

st.set_page_config(
    page_title="CVE Data Mining Final",
    page_icon="👋",
)

st.write("# Welcome to the NVD Data Mining Project! 👋")

st.markdown(
    """
    This application encompasses the entire data mining lifecycle:
    
    👈 **Select a page from the sidebar to explore:**
    
    * **1. Admin Review (HITL):** Review and edit AI-extracted vulnerabilities before pushing them to the CKAN Data Lake.
    * **2. Threat Feed:** Log in to search for specific technologies, track your software stack, and view MinHash duplication alerts.
    * **3. Run Pipelines:** The control center to trigger the ETL ingestion and the CKAN Analytics pull.
    """
)