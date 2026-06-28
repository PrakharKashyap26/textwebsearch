from typing import Dict
from ai.base import BaseAIProvider
from ai.gemini import GeminiProvider
from config import settings

class AIManager:
    """Manages AI providers and coordinates generating query overviews."""

    def __init__(self):
        self._providers: Dict[str, BaseAIProvider] = {}
        self._setup_providers()

    def _setup_providers(self):
        # Register standard Gemini provider
        gemini_key = settings.GEMINI_API_KEY or ""
        self.register_provider("gemini", GeminiProvider(gemini_key))

    def register_provider(self, name: str, provider: BaseAIProvider):
        """Register a new AI provider."""
        self._providers[name.lower()] = provider

    def get_provider(self, name: str) -> BaseAIProvider:
        """Retrieve an AI provider by name."""
        return self._providers.get(name.lower())

    def summarize(self, query: str, provider_name: str = None) -> str:
        """
        Generate a summary using the selected provider.
        If no provider is specified, falls back to the configured default.
        """
        if not provider_name:
            provider_name = settings.AI_PROVIDER

        provider = self.get_provider(provider_name)
        if not provider:
            return f"AI summary unavailable: Provider '{provider_name}' not configured or supported."

        return provider.summarize(query)
