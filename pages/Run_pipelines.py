import streamlit as st
import pandas as pd
import time
import sys
import os

# Add the backend folder to Python's path so we can import your scripts
sys.path.append(os.path.abspath('backend'))

from request_data import fetch_range_of_data, parse_nvd_record
from agent_parse import get_client, analyze_cve_with_gemini

st.title("⚙️ Master Pipeline Control")

st.subheader("Phase 1: Ingest & Extract")
if st.button("Run NVD -> Gemini Pipeline"):
    
    # 1. Ensure the database folder actually exists before we try to save to it!
    os.makedirs('database', exist_ok=True)
    
    with st.spinner("Fetching data from NVD and processing with Gemini. This may take a minute..."):
        try:
            client = get_client()
            
            # Keep it to 5 for a quick test run
            raw_data = fetch_range_of_data(results_per_page=5, total_wanted=5) 
            
            if not raw_data:
                st.error("Pipeline aborted: No data retrieved from NVD.")
            else:
                parsed_records = []
                progress_bar = st.progress(0)
                
                for i, log in enumerate(raw_data):
                    # A. Extract hard facts using Python
                    extracted_facts = parse_nvd_record(log)
                    cve_id = extracted_facts['cve_id']
                    
                    # B. Pass to Gemini
                    llm_prompt = extracted_facts['llm_prompt_text']
                    llm_insights = analyze_cve_with_gemini(llm_prompt, client)

                    # C. Combine and Append
                    if llm_insights:
                        final_row = {
                            "cve_id": cve_id,
                            "published_date": extracted_facts['published_date'],
                            "official_severity": extracted_facts['official_severity'],
                            "llm_prompt_text": extracted_facts['llm_prompt_text'],
                            **llm_insights 
                        }
                        parsed_records.append(final_row)
                    
                    # Update the visual progress bar
                    progress_bar.progress((i + 1) / len(raw_data))
                    time.sleep(4) # Respect Gemini API limits

                # D. Build Pandas and Save!
                df = pd.DataFrame(parsed_records)
                
                # Use the absolute path to ensure it drops exactly where we want it
                save_path = os.path.join("database", "pending_cves.csv")
                df.to_csv(save_path, index=False)
                
                st.success(f"✅ Successfully processed {len(df)} records and saved to `database/pending_cves.csv`!")
                st.dataframe(df) # Show a quick preview on the screen
                
        except Exception as e:
            st.error(f"An error occurred during the pipeline run: {e}")

st.divider()

st.subheader("Phase 2: Download & Mine")
if st.button("Run CKAN -> MinHash Pipeline"):
    with st.spinner("This will eventually run your analytics_pull.py and minhash.py..."):
        # We will plug your Phase 2 code in here once the NVD pipeline is 100% confirmed!
        time.sleep(2)
        st.success("Analytics pipeline placeholder triggered.")