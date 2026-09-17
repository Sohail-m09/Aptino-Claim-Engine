from app.rag.bm25_retriever import BM25Retriever
from app.rag.dense_retriever import dense_search
from app.rag.reranker import rerank_results

def reciprocal_rank_fusion(
    dense_results,
    bm25_results,
    rrf_k: int = 60,
):
    fused_results = {}

    result_lists = [
        ("dense", dense_results),
        ("bm25", bm25_results),
    ]

    for source_name, results in result_lists:

        for rank, (document, original_score) in enumerate(
            results,
            start=1,
        ):
            chunk_id = document.metadata["chunk_id"]

            rrf_score = 1 / (rrf_k + rank)

            if chunk_id not in fused_results:
                fused_results[chunk_id] = {
                    "document": document,
                    "rrf_score": 0.0,
                    "dense_rank": None,
                    "bm25_rank": None,
                }

            fused_results[chunk_id]["rrf_score"] += rrf_score
            fused_results[chunk_id][f"{source_name}_rank"] = rank

    ranked_results = sorted(
        fused_results.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return ranked_results


def hybrid_search(
    query: str,
    dense_k: int = 10,
    bm25_k: int = 10,
    final_k: int = 5,
):
    dense_results = dense_search(
        query=query,
        k=dense_k,
    )

    bm25_retriever = BM25Retriever()

    bm25_results = bm25_retriever.search(
        query=query,
        k=bm25_k,
    )

    fused_results = reciprocal_rank_fusion(
        dense_results=dense_results,
        bm25_results=bm25_results,
    )

    reranked_results = rerank_results(
        query=query,
        fused_results=fused_results,
        top_k=final_k,
    )

    return reranked_results