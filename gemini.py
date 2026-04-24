import google as genai


def summarize_query(query, api_key=None):
    if api_key is None:
        raise ValueError("Gemini API key is required.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Summarize this query in one or two short sentences:\n" + query)

    if hasattr(response, "text"):
        return response.text.strip()
    return str(response).strip()
