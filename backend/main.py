import pandas as pd
import time

from agent_parse import get_client, analyze_cve_with_gemini
from request_data import fetch_range_of_data, parse_nvd_record

def main():
    print("🚀 Starting Data Mining Pipeline...")
    
    # 1. Initialize Gemini Client once at the start
    client = get_client()

    # 2. Ingest Data
    print("\n[1/3] Fetching data from NVD...")
    # I set this to 5 just for your first full test run so you don't wait forever
    raw_data = fetch_range_of_data(results_per_page=5, total_wanted=5) 
    
    if not raw_data:
        print("No data fetched. Exiting.")
        return

    parsed_records = []

    # 3. Process each record
    print(f"\n[2/3] Processing {len(raw_data)} records with Python and Gemini...")
    for log in raw_data:
        
        # A. Extract hard facts using your Python parser
        # print(log)
        extracted_facts = parse_nvd_record(log)
        cve_id = extracted_facts['cve_id']
        print(f"  -> Analyzing {cve_id}...")

        # B. Pass the combined prompt to Gemini
        llm_prompt = extracted_facts['llm_prompt_text']
        llm_insights = analyze_cve_with_gemini(llm_prompt, client)

        # C. Combine everything into one final row for the database
        if llm_insights:
            final_row = {
                "cve_id": cve_id,
                "published_date": extracted_facts['published_date'],
                "official_severity": extracted_facts['official_severity'],
                "llm_prompt_text": extracted_facts['llm_prompt_text'],
                **llm_insights # This unpacks the Gemini dictionary (affected_technology, etc.)
            }
            parsed_records.append(final_row)
        
        # D. Sleep to respect Gemini API rate limits 
        # The free tier allows 15 requests per minute, so 4 seconds guarantees you stay under the limit.
        time.sleep(4) 

    # 4. Load into Pandas
    print("\n[3/3] Building Pandas DataFrame...")
    df = pd.DataFrame(parsed_records)
    
    print("\n✅ Final Extracted Dataset:")
    print(df.head())

    # 5. Save the data! 
    df.to_csv("nvd_processed_data.csv", index=False)
    print("\n💾 Saved to nvd_processed_data.csv")

if __name__ == '__main__':
    main()