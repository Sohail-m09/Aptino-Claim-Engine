from app.rag.chunker import chunk_policy


def main():
    chunks = chunk_policy()

    print(f"Total chunks created: {len(chunks)}")

    print("\nFirst 3 chunks:")

    for chunk in chunks[:3]:
        print("\n----------------------------")
        print("Metadata:")
        print(chunk.metadata)

        print("\nContent:")
        print(chunk.page_content[:400])


if __name__ == "__main__":
    main()