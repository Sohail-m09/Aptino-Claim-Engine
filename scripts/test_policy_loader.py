from app.rag.loader import load_policy


def main():
    pages = load_policy()

    print(f"Total pages loaded: {len(pages)}")

    first_page = pages[0]

    print("\nFirst page metadata:")
    print(first_page.metadata)

    print("\nFirst 500 characters:")
    print(first_page.page_content[:500])


if __name__ == "__main__":
    main()