import requests
import json
import time


# module  to make a   request to  a  webpage  (api)

# make a request to the server to  get records,  can specify how many records you want.
# should maybe  update it so you can  change the  starting  index

def fetch_range_of_data(results_per_page=20,total_wanted=100):
    start_index = 0
    all_vulnerabilities =  []
    # print(f"Requesting  data with this  url:  {url}")
    # headers
    # headers = {
    #     # for a  api  key
    # }

    while len(all_vulnerabilities) < total_wanted:
        
        print(f"fetching  records {start_index} to  {start_index +  results_per_page}")

        
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0/?resultsPerPage={results_per_page}&startIndex={start_index}"
        

        response  = requests.get(url)

        if response.status_code == 200:
        # everything  is  good parse the data
            data = response.json()
        # best to  use data.get  as  if the sever  messed up  we wont mess  up
        # data.get("vulnerablilites,  []") second  param is  what to  defualt  to
      
            batch =  data.get("vulnerabilities", [])
            if not batch:
                print("no more  data found  on server")
                break
            
            # extend  is better then append  as it dose one memory  allocation
            all_vulnerabilities.extend(batch)

            # increase our  range
            start_index +=  results_per_page

            # sleep for  6 seconds  so  i  dont  get  timed  out
            time.sleep(6)
     

        else:
            print(f"API Error {response.status_code}. The server might be blocking us. Stopping.")
            break
    
    print(f"Fetching complete!  got {len(all_vulnerabilities)} records")
    return  all_vulnerabilities
    

def parse_nvd_record(record):
    # 1. Drill down into the main 'cve' dictionary
    cve_data = record.get('cve', {})
    
    # 2. Extract the basic programmatic facts
    cve_id = cve_data.get('id', 'Unknown ID')
    published_date = cve_data.get('published', 'Unknown Date')
    
    # Safely get the description text
    descriptions = cve_data.get('descriptions', [])
    english_desc = "No description available."
    for desc in descriptions:
        if desc.get('lang') == 'en':
            english_desc = desc.get('value')
            break
            
    # Safely extract the CVSS Severity Score (NVD uses V2, V3.0, or V3.1 depending on the year)
    # This checks V2 since that's what your 1999 record uses
    severity = "Unknown"
    metrics = cve_data.get('metrics', {})
    if 'cvssMetricV2' in metrics:
        severity = metrics['cvssMetricV2'][0].get('baseSeverity', 'Unknown')
        
    # Safely extract the CPE strings (The software names)
    cpe_strings = []
    configs = cve_data.get('configurations', [])
    for config in configs:
        for node in config.get('nodes', []):
            for match in node.get('cpeMatch', []):
                cpe_strings.append(match.get('criteria'))
                
    # 3. Format the text to send to Gemini
    # We combine the description and the raw CPEs into one prompt
    llm_prompt = f"""
    Analyze this vulnerability.
    
    Description: {english_desc}
    Affected Software (CPEs): {', '.join(cpe_strings)}
    """
    
    return {
        "cve_id": cve_id,
        "published_date": published_date,
        "official_severity": severity,
        "llm_prompt_text": llm_prompt
    }

# Assuming 'my_raw_json' is the dictionary you pasted above