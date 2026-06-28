from typing import Dict, List
from search.base import BaseSearchProvider
from search.providers.searxng import SearXNGSearchProvider
from search.providers.duckduckgo import DuckDuckGoSearchProvider
from config import settings

class SearchManager:
    """Manages search providers, registers them, and dispatches queries with fallbacks."""

    def __init__(self):
        self._providers: Dict[str, BaseSearchProvider] = {}
        self._setup_providers()

    def _setup_providers(self):
        # Register SearXNG provider using configurations from settings
        searxng_url = settings.SEARXNG_URL or "https://searx.be"
        self.register_provider("searxng", SearXNGSearchProvider(searxng_url))
        
        # Register DuckDuckGo provider
        self.register_provider("duckduckgo", DuckDuckGoSearchProvider())

    def register_provider(self, name: str, provider: BaseSearchProvider):
        """Register a new search provider."""
        self._providers[name.lower()] = provider

    def get_provider(self, name: str) -> BaseSearchProvider:
        """Retrieve a search provider by name."""
        return self._providers.get(name.lower())

    def search(self, query: str, max_results: int = None, provider_name: str = None) -> List[Dict[str, str]]:
        """
        Perform a search query using the selected or default provider.
        If the primary provider fails, times out, or returns no results,
        it automatically falls back to DuckDuckGo search.
        """
        if not provider_name:
            provider_name = settings.SEARCH_PROVIDER

        if not max_results:
            max_results = settings.DEFAULT_MAX_RESULTS

        provider = self.get_provider(provider_name)
        results = []

        if provider:
            print(f"[INFO] Using search provider: {provider_name}")
            try:
                results = provider.search(query, max_results=max_results)
                # Keep lowercase provider name in the result log for uniformity, e.g. [INFO] SearXNG returned 10 results -> [INFO] searxng returned 10 results, or capitalized if preferred.
                # Let's capitalize SearXNG as "SearXNG" and duckduckgo as "DuckDuckGo" or just format exactly.
                # The user request examples say:
                # [INFO] SearXNG returned 10 results
                # [INFO] DuckDuckGo returned 8 results
                # Let's match this capitalization exactly.
                cap_name = "SearXNG" if provider_name == "searxng" else "DuckDuckGo" if provider_name == "duckduckgo" else provider_name.capitalize()
                print(f"[INFO] {cap_name} returned {len(results)} results")
            except Exception as e:
                pass

        # Fallback to DuckDuckGo if primary provider failed, was missing, or returned empty results
        if not results and provider_name != "duckduckgo":
            print(f"[WARNING] SearXNG unavailable, switching to DuckDuckGo")
            fallback_provider = self.get_provider("duckduckgo")
            if fallback_provider:
                print(f"[INFO] Using search provider: duckduckgo")
                try:
                    results = fallback_provider.search(query, max_results=max_results)
                    print(f"[INFO] DuckDuckGo returned {len(results)} results")
                except Exception as e:
                    pass

        return results
