from flashrank import Ranker, RerankRequest


RERANK_MODEL = "ms-marco-TinyBERT-L-2-v2"


ranker = Ranker(
    model_name=RERANK_MODEL,
)


def rerank_results(
    query: str,
    fused_results: list[dict],
    top_k: int = 5,
):
    passages = []

    for result in fused_results:
        document = result["document"]

        passages.append(
            {
                "id": document.metadata["chunk_id"],
                "text": document.page_content,
                "meta": document.metadata,
            }
        )

    request = RerankRequest(
        query=query,
        passages=passages,
    )

    reranked = ranker.rerank(request)

    original_results = {
        result["document"].metadata["chunk_id"]: result
        for result in fused_results
    }

    final_results = []

    for item in reranked[:top_k]:
        original = original_results[item["id"]]

        final_results.append(
            {
                "document": original["document"],
                "rerank_score": float(item["score"]),
                "rrf_score": original["rrf_score"],
                "dense_rank": original["dense_rank"],
                "bm25_rank": original["bm25_rank"],
            }
        )

    return final_results