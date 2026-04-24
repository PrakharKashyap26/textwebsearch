import requests
from bs4 import BeautifulSoup
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# -------------------------------
# Open and display a webpage
# -------------------------------
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

    print("\n" + "="*60 + "\n")
    print(clean_text[:2000])
    print("\n" + "="*60)

    input("\nPress Enter to go back...")


# -------------------------------
# SIMPLE GOOGLE SEARCH (no API)
# -------------------------------
def simple_search(query):
    print("\nSearching...\n")

    search_url = "https://www.google.com/search"
    params = {"q": query}

    try:
        response = requests.get(search_url, params=params, headers=HEADERS, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Search failed: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    
    # Extract links from Google results
    for a in soup.select("a"):
        href = a.get("href")
        if href and "/url?q=" in href:
            link = href.split("/url?q=")[1].split("&")[0]
            title = a.get_text().strip()

            if title and link.startswith("http"):
                results.append((title, link))

    if not results:
        print("No results found.")
        return

    while True:
        print("\nResults:\n")

        for i, (title, link) in enumerate(results[:10]):
            print(f"{i+1}. {title}")
            print(f"   {link}")

        choice = input("\nEnter number to open (or 'b' to go back): ")

        if choice.lower() == "b":
            break

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(results):
                open_page(results[index][1])