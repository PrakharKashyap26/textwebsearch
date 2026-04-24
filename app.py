import ai
import search


def main():
    print("Welcome to TextWebSearch")
    print("Type a query, or 'exit' to quit.")

    while True:
        query = input("\nSearch: ").strip()
        if not query:
            print("Please enter a search query or type 'exit'.")
            continue

        if query.lower() == "exit":
            print("Goodbye!")
            break

        print("\nAI Summary:")
        print("-" * 60)
        summary = ai.summarize_query(query)
        print(summary)
        print("-" * 60)

        results = search.search_query(query, max_results=7)
        if not results:
            continue

        print("\nSearch results:")
        for index, (title, url) in enumerate(results, start=1):
            print(f"{index}. {title}")
            print(f"   {url}")

        while True:
            choice = input("\nEnter result number to open, or 'b' to search again: ").strip().lower()
            if choice == "b":
                break
            if choice.isdigit():
                selected = int(choice) - 1
                if 0 <= selected < len(results):
                    search.open_page(results[selected][1])
                    break
                print("Number out of range. Choose an available result.")
            else:
                print("Invalid input. Enter a number or 'b'.")


if __name__ == "__main__":
    main()
