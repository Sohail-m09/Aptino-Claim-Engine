from app.rag.bm25_retriever import BM25Retriever


def main():
    retriever = BM25Retriever()

    query = "30 day initial waiting period"

    print(f"Query: {query}")

    results = retriever.search(
        query=query,
        k=5,
    )

    for position, (document, score) in enumerate(
        results,
        start=1,
    ):
        print("\n" + "=" * 60)

        print(f"Result {position}")
        print(f"BM25 Score: {score:.4f}")

        print("Metadata:")
        print(document.metadata)

        print("\nContent:")
        print(document.page_content[:500])


if __name__ == "__main__":
    main()