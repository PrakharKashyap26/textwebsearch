from abc import ABC, abstractmethod
from typing import List, Dict

class BaseSearchProvider(ABC):
    """Abstract Base Class for search engines."""

    @abstractmethod
    def search(self, query: str, max_results: int = 7) -> List[Dict[str, str]]:
        """
        Perform a search query.

        Args:
            query: The user's query string.
            max_results: Max number of results to return.

        Returns:
            A list of dicts, each containing 'title', 'url', and 'snippet'.
        """
        pass

