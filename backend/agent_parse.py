from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import dotenv
import os
import json
import pandas as pd
import time




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
def analyze_cve_with_gemini(cve_description: str, client, max_retries=3) -> dict:
    """Passes the raw CVE text to Gemini and forces it into our JSON schema, with retries."""
    prompt = f"Analyze the following security vulnerability description and extract the required fields:\n\n{cve_description}"
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                # If 2.5-flash stays completely down, can temporarily change this to 'gemini-1.5-flash'
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CVEAnalysis,
                    temperature=0.1, 
                ),
            )
            
            # If successful, parse the JSON and return immediately
            return json.loads(response.text)
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a 503 Server Busy error
            if "503" in error_msg or "UNAVAILABLE" in error_msg:
                wait_time = 5 * (attempt + 1) # Waits 5s, then 10s, then 15s
                print(f"      [!] API busy. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                # If it's a different error (like a schema validation failure), print it and stop trying
                print(f"      [!] LLM extraction failed: {e}")
                return None
                
    print("      [!] Max retries reached. Skipping this record for now.")
    return None