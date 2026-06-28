from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    """Abstract Base Class for AI summary providers."""

    @abstractmethod
    def summarize(self, query: str) -> str:
        """
        Generate a summary for the given query.

        Args:
            query: The user's search query.

        Returns:
            A string containing the summary or an error description.
        """
        pass
