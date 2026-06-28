def clean_whitespace(text: str) -> str:
    """Standardize whitespace in string content."""
    if not text:
        return ""
    return " ".join(text.split())
