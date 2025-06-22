# TexWebsearch
A simple Python application that combines AI-powered responses using Google's Gemini model with web search capabilities via Google Custom Search API.

## Features
- **AI Response**: Uses the Gemini model to provide brief answers to user queries.
- **Web Search**: Performs web searches using Google's Custom Search API and displays relevant results with titles and links.
- **Interactive CLI**: Continuously prompts the user for input until they choose to exit.

## Prerequisites
- Python 3.x
- Required Python packages:
  - `requests`
- Google API Key for Gemini and Custom Search Engine
- Custom Search Engine ID (CSE ID)

## Installation
1. Clone or download the repository.
2. Install the required package:
   ```
   pip install requests
   ```
3. Replace `API_KEY` in `gemini.py` and `search.py` with your Google API Key.
4. Replace `CUSTOM SEARCH ENGINE ID` in `search.py` with your Google Custom Search Engine ID.

## Usage
1. Run the main application:
   ```
   python app.py
   ```
   or via the .bat file (".sh for linux and mac") 
2. Enter a search query when prompted or type `exit` to quit.
3. The application will:
   - Display a brief AI-generated response from the Gemini model.
   - Show web search results with titles and links.

## Files
- `app.py`: Main application script that handles user input and integrates AI and search functionalities.
- `gemini.py`: Contains the `ai_reply` function to interact with the Gemini model for AI responses.
- `search.py`: Contains the `simple_search` function to perform web searches using Google Custom Search API.

## Notes
- Ensure you have a valid Google API Key and CSE ID configured in the respective files.
- The Gemini model used is `gemini-2.0-flash`. Verify model availability or update as needed.
- The application assumes an active internet connection for API calls.

## Limitations
- Requires manual configuration of API keys.
- Error handling for API failures or invalid inputs is minimal.
- Search results are limited to the default response from the Google Custom Search API.

## License
This project is unlicensed. Use and modify at your own discretion.