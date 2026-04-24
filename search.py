import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def _clean_page_text(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def open_page(url):
    print(f"\nLoading: {url}\n")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error loading page: {e}")
        return

    clean_text = _clean_page_text(response.text)
    preview = clean_text[:2000].rstrip()

    print("\n" + "=" * 60 + "\n")
    print(preview)
    if len(clean_text) > len(preview):
        print("\n...content truncated to 2000 characters...")
    print("\n" + "=" * 60)

    input("\nPress Enter to return to results...")


def search_query(query, max_results=7):
    print("\nSearching...\n")
    search_url = "https://html.duckduckgo.com/html/"
    params = {"q": query}

    try:
        response = requests.get(search_url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Search failed: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for link_tag in soup.select("a.result__a"):
        href = link_tag.get("href")
        title = link_tag.get_text(strip=True)
        if href and title and href.startswith("http"):
            results.append((title, href))
            if len(results) >= max_results:
                break

    if not results:
        for link_tag in soup.select("a"):
            href = link_tag.get("href")
            title = link_tag.get_text(strip=True)
            if href and title and href.startswith("http"):
                results.append((title, href))
                if len(results) >= max_results:
                    break

    if not results:
        print("No results found.")
    return results