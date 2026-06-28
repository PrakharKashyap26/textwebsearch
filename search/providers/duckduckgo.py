import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from search.base import BaseSearchProvider
from utils.http import get_http_headers

class DuckDuckGoSearchProvider(BaseSearchProvider):
    """DuckDuckGo HTML-scraping keyless fallback search provider."""

    def search(self, query: str, max_results: int = 7) -> List[Dict[str, str]]:
        search_url = "https://lite.duckduckgo.com/lite/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        data = {"q": query}

        try:
            response = requests.post(search_url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # Target DuckDuckGo Lite structured result format
        links = soup.find_all("a", class_="result-link")
        snippets = soup.find_all("td", class_="result-snippet")
        
        for lnk, snp in zip(links, snippets):
            title = lnk.get_text(strip=True)
            url = lnk.get("href")
            snippet = snp.get_text(strip=True)
            if title and url:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
                if len(results) >= max_results:
                    break

        # Fallback target if DDG changes markup
        if not results:
            for link_tag in soup.select("a"):
                href = link_tag.get("href")
                title = link_tag.get_text(strip=True)
                if href and title and href.startswith("http") and "duckduckgo.com" not in href:
                    results.append({
                        "title": title,
                        "url": href,
                        "snippet": ""
                    })
                    if len(results) >= max_results:
                        break

        return results
