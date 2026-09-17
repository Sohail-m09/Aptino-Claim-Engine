from app.rag.chunker import chunk_policy


CHECKS = {
    "Room Rent Limit":
        "normal room expenses",

    "Ambulance Limit":
        "ambulance charges",

    "30-Day Waiting Period":
        "a waiting period of 30 days",

    "Pre-Existing Disease":
        "48 months of continuous coverage",

    "Domiciliary Limit":
        "domiciliary hospitalization will be paid",

    "Pre-Hospitalization":
        "pre-hospitalisation up to a maximum of 30 days",

    "Cosmetic Exclusion":
        "cosmetic or aesthetic treatment",

    "Experimental Treatment":
        "experimental or unproven",
}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def main():
    chunks = chunk_policy()

    print(f"Total chunks: {len(chunks)}")

    for name, phrase in CHECKS.items():

        matches = [
            chunk
            for chunk in chunks
            if phrase in normalize(chunk.page_content)
        ]

        print("\n" + "=" * 60)
        print(name)
        print(f"Matches found: {len(matches)}")

        if matches:
            first_match = matches[0]

            print("Metadata:")
            print(first_match.metadata)

            print("\nContent:")
            print(first_match.page_content[:350])

        else:
            print("WARNING: Important clause not found!")


if __name__ == "__main__":
    main()