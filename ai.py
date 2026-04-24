import os
import gemini


def summarize_query(query):
    """Return a short AI-powered summary of the user's query using Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = "AIzaSyDS6JKC_Jqa0XnSxI8LDRCTwj6Qi5-waSY"

    try:
        return gemini.summarize_query(query, api_key=api_key)
    except Exception as error:
        return f"AI unavailable: {error}"
