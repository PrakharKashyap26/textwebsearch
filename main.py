import sys
from config import settings
from ai import AIManager
from search import SearchManager
from browser import NavigationController, HistoryManager

def main():
    # Force stdout to UTF-8 to prevent Windows cp1252 UnicodeEncodeError
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    # Initialize managers
    ai_manager = AIManager()
    search_manager = SearchManager()
    nav_controller = NavigationController()
    history_manager = HistoryManager()

    print("Welcome to TexBrowse")
    print("A beginner-friendly terminal web browser.")
    print("Type your search query to begin, or 'q' to quit.\n")

    while True:
        try:
            query = input("Search: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break

        # Log query to history
        history_manager.add_entry(query=query)

        # Retrieve AI Overview and Search Results
        print("\nRetrieving AI Overview...")
        try:
            ai_summary = ai_manager.summarize(query)
        except KeyboardInterrupt:
            print("\nAI summary retrieval cancelled.")
            continue

        print("Executing web search...")
        try:
            results = search_manager.search(query)
        except KeyboardInterrupt:
            print("\nSearch cancelled.")
            continue

        while True:
            # Output Layout
            print("\n---")
            print("## AI OVERVIEW")
            print(ai_summary)
            print("\n---")
            print("## SEARCH RESULTS")
            if not results:
                print("No results found.")
            else:
                for index, result in enumerate(results, start=1):
                    print(f"[{index}] {result['title']}")
                    print(f"    {result['url']}")

            print("\n---")
            print("## COMMANDS")
            print("[number] Open Result")
            print("s        New Search")
            print("q        Quit")
            print()

            try:
                cmd = input("> ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                return

            if not cmd:
                continue

            if cmd == "q":
                print("Goodbye!")
                return
            elif cmd == "s":
                break  # Exit results loop to prompt new search
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(results):
                    result = results[idx]
                    url = result["url"]
                    nav_controller.enter_browser_loop(url, history_manager)
                else:
                    print(f"Error: Number must be between 1 and {len(results)}.")
                    input("\nPress Enter to continue...")
            else:
                print(f"Unknown command: '{cmd}'. Enter a result number, 's', or 'q'.")
                input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()


