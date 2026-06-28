import os
import warnings
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check for legacy Google search environment variables and warn user
if os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_CSE_ID"):
    warnings.warn(
        "Google API Key or CSE ID detected. Google search provider is deprecated and removed. "
        "Please migrate to SearXNG or DuckDuckGo settings.",
        DeprecationWarning
    )

# Provider selection
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "searxng").lower()

# SearXNG Configuration
SEARXNG_URL = os.getenv("SEARXNG_URL", "https://searx.be").rstrip("/")

# Default Configurations
DEFAULT_MAX_RESULTS = 7
MAX_RENDER_CHARS = 2000

