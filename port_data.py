from agent_parse import analyze_cve_with_gemini, get_api_key,CVEAnalysis
from request_data import fetch_range_of_data, parse_nvd_record

def main():
    # get the data from the server
    # its a list of dictonarys
    # base is 100 items
    data = fetch_range_of_data()
    print(data)
    for log in data:
        print(log)

if __name__ == '__main__':
    main()




