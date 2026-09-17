from app.rag.dense_retriever import build_dense_index


def main():
    print("Building dense policy index...")

    vector_store = build_dense_index(
        reset=True
    )

    count = vector_store._collection.count()

    print("Dense index built successfully")
    print(f"Indexed chunks: {count}")


if __name__ == "__main__":
    main()