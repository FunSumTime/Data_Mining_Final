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
      
            batch =  data.get("vulnerablilities", [])
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
    
data = fetch_range_of_data()