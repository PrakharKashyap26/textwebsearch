# TexBrowse

TexBrowse is a beginner-friendly terminal web browser, similar to how Nano is a beginner-friendly alternative to Vim. It provides an intuitive terminal interface to search and browse the web, with optional AI-powered summaries.

## Vision
* **Not an AI Chatbot**: TexBrowse is a browser interface.
* **Optional AI**: Works perfectly even without AI configured.
* **Extensible & Provider-Agnostic**: Designed to easily add new AI and search providers.
* **Terminal First**: Optimized for clean CLI reading and navigation.

## Project Structure
```
texbrowse/
│
├── main.py              # Application entrypoint and loop
├── requirements.txt     # Dependency list
├── README.md            # Documentation
├── .gitignore           # Git ignore configurations
├── .env                 # Local environment keys (ignored)
├── .env.example         # Environment template
│
├── config/              # Configuration & Settings management
│   ├── __init__.py
│   └── settings.py
│
├── ai/                  # AI Summary providers (Gemini, etc.)
│   ├── __init__.py
│   ├── base.py
│   ├── gemini.py
│   └── manager.py
│
├── search/              # Search engine integration (Google, DuckDuckGo, etc.)
│   ├── __init__.py
│   ├── base.py
│   ├── google.py
│   ├── duckduckgo.py
│   └── manager.py
│
├── browser/             # Page rendering, history and bookmarks
│   ├── __init__.py
│   ├── renderer.py
│   ├── navigation.py
│   ├── history.py
│   └── bookmarks.py
│
├── data/                # Persistent JSON data
│   ├── bookmarks.json
│   └── history.json
│
└── utils/               # Common helper utilities
    ├── __init__.py
    ├── http.py
    └── text.py
```

## Installation

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy the template environment file:
   ```bash
   copy .env.example .env
   ```
3. Set your API credentials in `.env`.

## Configuration
All application settings are managed via `.env`.
* `AI_PROVIDER`: The AI engine to use for summaries (e.g., `gemini`).
* `GEMINI_API_KEY`: API key for Google Gemini model.
* `SEARCH_PROVIDER`: The search engine to use (e.g., `searxng` or `duckduckgo`).
* `SEARXNG_URL`: The URL of the SearXNG instance (defaults to `https://searx.be`).

*If the SearXNG instance fails, is offline, or rate limits requests, TexBrowse automatically falls back to DuckDuckGo HTML scraping.*


## Usage

Start the browser interface:
```bash
python main.py
```

### CLI Controls
* `Search: [query]`: Enter search query.
* `[number]`: Open a specific search result by index.
* `s`: Return to start a new search.
* `q`: Quit TexBrowse.