import os
import json
from typing import List, Dict

class BookmarkManager:
    """Manages bookmarks list and persists it to JSON."""

    def __init__(self, filepath: str = "data/bookmarks.json"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump([], f)

    def add_bookmark(self, url: str, title: str) -> bool:
        """Add a website URL to bookmarks, avoiding duplicates."""
        bookmarks = self.get_bookmarks()
        for bm in bookmarks:
            if bm["url"] == url:
                return False

        bookmarks.append({"url": url, "title": title})
        try:
            with open(self.filepath, "w") as f:
                json.dump(bookmarks, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving bookmarks: {e}")
            return False

    def get_bookmarks(self) -> List[Dict]:
        """Load and return the list of bookmarked sites."""
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def remove_bookmark(self, url: str) -> bool:
        """Remove a bookmark by its URL."""
        bookmarks = self.get_bookmarks()
        filtered = [bm for bm in bookmarks if bm["url"] != url]
        
        if len(filtered) == len(bookmarks):
            return False

        try:
            with open(self.filepath, "w") as f:
                json.dump(filtered, f, indent=4)
            return True
        except Exception as e:
            print(f"Error removing bookmark: {e}")
            return False
