from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import dotenv
import os
import json
import pandas as pd




dotenv.load_dotenv()

def get_api_key(key_name):
    api_key = os.getenv(key_name)
    if not api_key:
        msg = (f"{key_name} not set. "
               f"Be sure .env has {key_name}. "
               f"Be sure dotenv.load_dotenv() is called at initialization.")
        raise ValueError(msg)
    return api_key


# 1. Define the exact schema you want the LLM to output
class CVEAnalysis(BaseModel):
    affected_technology: str
    requires_patch: bool
    plain_english_summary: str
    vulnerability_rating: str 

# make our model with the key we are given 
def get_client():

    client = genai.Client(api_key=get_api_key("GEMINI_API_KEY"))
    return client

# function to give the contents of the data comming in to a llm to have it categorize it
def analyze_cve_with_gemini(cve_description: str,client) -> dict:
    """Passes the raw CVE text to Gemini and forces it into our JSON schema."""
    prompt = f"Analyze the following security vulnerability description and extract the required fields:\n\n{cve_description}"
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CVEAnalysis,
                temperature=0.1, 
            ),
            # tempurature keeps the model factual if it is low as it controls the 'creativity'
        )
        
        # The response.text is a JSON string. We convert it to a Python dictionary.
        return json.loads(response.text)
        
    except Exception as e:
        print(f"LLM extraction failed: {e}")
        return None

# --- 4. Putting it all together (Assuming you have your raw_cves list from Milestone 1) ---

# Mock list of data just for this example


# for item in raw_cves:
#     cve_id = item['id']
#     description = item['description']
    
#     print(f"Analyzing {cve_id}...")
    
#     # Run the description through Gemini
#     extracted_data = analyze_cve_with_gemini(description)
    
#     if extracted_data:
#         # Combine the original ID with the Gemini insights
#         record = {"cve_id": cve_id, **extracted_data}
#         parsed_records.append(record)

# # --- 5. Convert to Pandas ---
# df = pd.DataFrame(parsed_records)
# print("\nFinal Extracted DataFrame:")
# print(df.head())