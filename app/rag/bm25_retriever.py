import re
from functools import lru_cache

from rank_bm25 import BM25Okapi

from app.rag.chunker import chunk_policy


def tokenize(text: str) -> list[str]:
    return re.findall(
        r"\b\w+\b",
        text.lower(),
    )


class BM25Retriever:
    def __init__(self):
        self.chunks = chunk_policy()

        self.tokenized_chunks = [
            tokenize(chunk.page_content)
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_chunks
        )

    def search(
        self,
        query: str,
        k: int = 5,
    ):
        tokenized_query = tokenize(query)

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:k]

        results = []

        for index in ranked_indices:
            results.append(
                (
                    self.chunks[index],
                    float(scores[index]),
                )
            )

        return results


@lru_cache(maxsize=1)
def get_bm25_retriever() -> BM25Retriever:
    return BM25Retriever()