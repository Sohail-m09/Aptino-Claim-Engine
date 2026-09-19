from app.rag.dense_retriever import build_dense_index


def main():
    print("Building policy dense index...")

    vector_store = build_dense_index(
        reset=True
    )

    result = vector_store.get()

    print(
        f"Index created successfully "
        f"with {len(result.get('ids', []))} chunks."
    )


if __name__ == "__main__":
    main()