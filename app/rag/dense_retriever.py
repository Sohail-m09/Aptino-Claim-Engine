from pathlib import Path
import shutil
from langchain_chroma import Chroma
from app.rag.chunker import chunk_policy
from app.rag.embeddings import get_embedding_model
from functools import lru_cache


CHROMA_PATH = Path("chroma_db")
COLLECTION_NAME = "aptino_policy"


def build_dense_index(
    reset: bool = False,
) -> Chroma:

    if reset and CHROMA_PATH.exists():
        shutil.rmtree(CHROMA_PATH)

    chunks = chunk_policy()

    embedding_model = get_embedding_model()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_PATH),
    )

    return vector_store

@lru_cache(maxsize=1)
def load_dense_index() -> Chroma:
    embedding_model = get_embedding_model()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=str(CHROMA_PATH),
    )


def dense_search(
    query: str,
    k: int = 5,
):
    vector_store = load_dense_index()

    return vector_store.similarity_search_with_relevance_scores(
        query=query,
        k=k,
    )