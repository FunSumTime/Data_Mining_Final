import requests
import json
# module  to make a   request to  a  webpage  (api)

def fetch_recent_data(results_per_page=5):
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0/?resultsPerPage={results_per_page}"
    print(f"Requesting  data with this  url:  {url}")
    # headers
    headers = {
        # for a  api  key
    }

    response  = requests.get(url,headers=headers)

    if response.status_code == 200:
        # everything  is  good parse the data
        data = response.json()
        # look at data for now  to  see  what i want to pull out
        print(data)
        print(data['vulnerabilities'])
    else:
        print(f"Failed  to  fetch data: {response.status_code}")
    
fetch_recent_data()