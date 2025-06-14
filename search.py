import requests

API_KEY = 'API_KEY'
CSE_ID = 'CUSTOM SEARCH ENGINE ID'

def simple_search(query):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query
    }

    response = requests.get(url, params=params)
    data = response.json()

    for item in data.get("items", []):
        print(item["title"])
        print(item["link"])
        print()
        