import google as genai

def ai_reply(user_input):
    try:
        genai.configure(api_key="AIzaSyDS6JKC_Jqa0XnSxI8LDRCTwj6Qi5-waSY")

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("answer briefly:\n" + user_input)

        print("\nAI Overview:\n")
        print(response.text)

    except Exception:
        print("\nAI unavailable (quota or key issue)\n")