from app.rag.dense_retriever import dense_search


def main():
    query = "What is the initial waiting period?"

    print(f"Query: {query}")

    results = dense_search(
        query=query,
        k=5,
    )

    for position, (document, score) in enumerate(
        results,
        start=1,
    ):
        print("\n" + "=" * 60)

        print(f"Result {position}")
        print(f"Score: {score:.4f}")

        print("Metadata:")
        print(document.metadata)

        print("\nContent:")
        print(document.page_content[:500])


if __name__ == "__main__":
    main()