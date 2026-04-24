import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def open_page(url):
    print(f"\nLoading: {url}\n")

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error loading page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove junk
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text()

    lines = [line.strip() for line in text.splitlines()]
    clean_text = "\n".join(line for line in lines if line)

    print(clean_text[:2000])

    input("\nPress Enter to go back...")


API_KEY = 'API_KEY'
CSE_ID = 'CUSTOM SEARCH ENGINE ID'

def simple_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Search failed: {e}")
        return

    results = data.get("items", [])

    if not results:
        print("No results found.")
        return

    while True:
        print("\nResults:\n")
        for i, item in enumerate(results):
            print(f"{i+1}. {item['title']}")

        choice = input("\nEnter number to open (or 'b' to go back): ")

        if choice.lower() == 'b':
            break

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(results):
                open_page(results[index]["link"])