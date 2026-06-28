import os
import json
from datetime import datetime
from typing import List, Dict

class HistoryManager:
    """Manages the history log and persists it to JSON."""

    def __init__(self, filepath: str = "data/history.json"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump([], f)

    def add_entry(self, query: str = None, url: str = None, title: str = None):
        """Append a new navigation or search entry to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "url": url,
            "title": title
        }
        history = self.get_history()
        history.append(entry)
        
        try:
            with open(self.filepath, "w") as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def get_history(self) -> List[Dict]:
        """Load and return the list of history entries."""
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
