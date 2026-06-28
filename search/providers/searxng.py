import requests
from typing import List, Dict
from search.base import BaseSearchProvider
from utils.http import get_http_headers

class SearXNGSearchProvider(BaseSearchProvider):
    """SearXNG JSON-based search provider."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def search(self, query: str, max_results: int = 7) -> List[Dict[str, str]]:
        if not self.base_url:
            print("[WARNING] SearXNG base URL is not configured.")
            return []

        search_url = f"{self.base_url}/search"
        params = {
            "q": query,
            "format": "json"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            # Short timeout so fallback is rapid if SearXNG is offline
            response = requests.get(search_url, params=params, headers=headers, timeout=6)
            response.raise_for_status()
            data = response.json()
            results = []
            
            raw_results = data.get("results", [])
            for item in raw_results:
                title = item.get("title")
                url = item.get("url")
                snippet = item.get("content", "")
                if title and url:
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
                    if len(results) >= max_results:
                        break
            return results
        except requests.Timeout:
            # Silence stack traces, print simple status
            return []
        except requests.RequestException as e:
            if e.response is not None and e.response.status_code == 403:
                # Handled gracefully, will fall back
                pass
            return []
        except ValueError:
            return []
        except Exception:
            return []
