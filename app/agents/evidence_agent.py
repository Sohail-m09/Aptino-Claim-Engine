from time import perf_counter

from app.rag.hybrid_retriever import hybrid_search
from app.schemas.decision import Evidence, TraceStep
from app.schemas.state import ClaimState


def run_evidence_agent(
    state: ClaimState,
) -> dict:

    start_time = perf_counter()

    queries = state.get(
        "investigation_queries",
        [],
    )

    collected_evidence = {}

    for query in queries:
        results = hybrid_search(
            query=query,
            dense_k=10,
            bm25_k=10,
            final_k=5,
        )

        for result in results:
            document = result["document"]

            chunk_id = document.metadata[
                "chunk_id"
            ]

            # Avoid storing the same policy chunk twice
            if chunk_id in collected_evidence:
                continue

            collected_evidence[chunk_id] = Evidence(
                content=document.page_content,
                source=document.metadata["source"],
                page=document.metadata["page"],
                section=document.metadata["section"],
                chunk_id=chunk_id,
                score=result["rerank_score"],
            )

    evidence = list(
        collected_evidence.values()
    )

    elapsed_ms = (
        perf_counter() - start_time
    ) * 1000

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        TraceStep(
            agent="Policy Evidence Agent",
            action=(
                f"Processed {len(queries)} policy queries "
                f"and retrieved {len(evidence)} unique "
                f"policy evidence chunks"
            ),
            elapsed_ms=elapsed_ms,
        )
    )

    return {
        "retrieved_evidence": evidence,
        "trace": trace,
    }