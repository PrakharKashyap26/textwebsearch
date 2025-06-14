from google import genai

def ai_reply(user_input):
    client = genai.Client(api_key="API_KEY")

    predefined_prompt = "answer in a brief\n"
    full_prompt = predefined_prompt + user_input

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt,
    )
    
    print(response.text)
