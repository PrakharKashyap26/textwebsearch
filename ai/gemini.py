from google import genai
from ai.base import BaseAIProvider

class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider implementation using the new google-genai SDK."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception:
                # Do not crash the application if initialization fails
                pass

    def summarize(self, query: str) -> str:
        if not self.api_key or not self.client:
            return "AI summary unavailable: Gemini API key is not configured."

        print("[INFO] Generating AI overview with Gemini")
        try:
            response = self.client.models.generate_content(
                model="gemini-3.5-flash",
                contents="Summarize this query in one or two short sentences:\n" + query
            )
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            return str(response).strip()
        except Exception as e:
            print(f"[ERROR] Gemini request failed: {e}")
            return "AI summary unavailable."
