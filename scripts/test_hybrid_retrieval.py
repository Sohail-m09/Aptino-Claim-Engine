from app.rag.hybrid_retriever import hybrid_search


def main():
    query = "What is the initial waiting period?"

    print(f"Query: {query}")

    results = hybrid_search(
        query=query,
        dense_k=10,
        bm25_k=10,
        final_k=5,
    )

    for position, result in enumerate(
        results,
        start=1,
    ):
        document = result["document"]

        print("\n" + "=" * 60)

        print(f"Result {position}")

        print(
            f"Rerank Score: "
            f"{result['rerank_score']:.6f}"
        )

        print(
            f"RRF Score: "
            f"{result['rrf_score']:.6f}"
        )

        print(
            f"Dense Rank: "
            f"{result['dense_rank']}"
        )

        print(
            f"BM25 Rank: "
            f"{result['bm25_rank']}"
        )

        print("\nMetadata:")
        print(document.metadata)

        print("\nContent:")
        print(document.page_content[:500])


if __name__ == "__main__":
    main()