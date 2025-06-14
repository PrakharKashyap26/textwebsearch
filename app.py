import gemini, search
print("welcome to TexWebsearch\n")
while True:
    question= input("enter exit to quit\nsearch: ")
    if question.lower() == "exit":
        print("exiting...")
        break
    gemini.ai_reply(question)
    search.simple_search(question)
