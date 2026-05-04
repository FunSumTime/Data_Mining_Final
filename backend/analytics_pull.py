import requests
import pandas as pd
import io
import os
import dotenv

# Load your environment variables (Make sure CKAN_API_TOKEN is in your .env file)
dotenv.load_dotenv()
api_token = os.getenv("CKAN_KEY")

def download_ckan_dataset(dataset_id):
    # 1. The Route to find the dataset metadata
    metadata_route = "http://YOUR_DEPARTMENT_CKAN_SERVER/api/3/action/package_show"
    
    # we are going to see the avalble onnes first
    headers = {"Authorization": api_token}
    params = {"id": dataset_id}
    
    print(f"🔍 Searching CKAN for dataset: {dataset_id}...")
    
    # First Request: Get the metadata
    response = requests.get(metadata_route, params=params, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to find dataset. Server returned: {response.status_code}")
        return None
        
    data = response.json()
    
    # 2. Dig through the resources to find the CSV file
    # A single dataset might have a CSV, a PDF, and a JSON file. We just want the CSV.
    print(data)
    resources = data.get('result', {}).get('resources', [])
    csv_url = None
    
    # get the CSV to get from the server
    for resource in resources:
        if resource.get('format', '').upper() == 'CSV':
            csv_url = resource.get('url')
            break
            
    if not csv_url:
        print("❌ Dataset found, but no CSV file was attached to it.")
        return None
        
    print(f"✅ Found CSV! Downloading from: {csv_url}")
    
    # 3. Second Request: Download the actual file contents
    csv_response = requests.get(csv_url, headers=headers)
    
    if csv_response.status_code == 200:
        # Use io.StringIO to trick Pandas into reading the text stream as a physical file
        df = pd.read_csv(io.StringIO(csv_response.text))
        print("\n🚀 Download complete! Data loaded into Pandas:")
        print(df.head())
        return df
    else:
        print(f"❌ Failed to download the CSV. Server returned: {csv_response.status_code}")
        return None

# Run the pull using the same ID you used in Milestone 4
my_dataframe = download_ckan_dataset("your-target-dataset-id")