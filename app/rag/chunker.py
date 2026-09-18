import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.loader import load_policy


SECTION_HEADINGS = {
    "PROSPECTUS",
    "DEFINITIONS",
    "SCOPE OF COVER",
    "WHAT WE COVER",
    "WHAT WE EXCLUDE",
    "EXTENSIONS",
    "CLAIMS PROCEDURE",
    "STANDARD TERMS AND CONDITIONS:",
}


def clean_page_text(text: str) -> str:
    cleaned_lines = []

    for line in text.splitlines():
        line = " ".join(line.split())

        if not line:
            cleaned_lines.append("")
            continue

        # Remove repeated PDF header
        if line == "UNIVERSAL SOMPO GENERAL INSURANCE CO LTD":
            continue

        # Remove repeated page footer
        if "CSC- Individual Health Insurance-Policy Wording" in line:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def split_page_by_sections(
    text: str,
    current_section: str,
):
    sections = []
    buffer = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line in SECTION_HEADINGS:
            if buffer:
                sections.append(
                    (
                        current_section,
                        "\n".join(buffer),
                    )
                )
                buffer = []

            current_section = line.rstrip(":")
            continue

        buffer.append(line)

    if buffer:
        sections.append(
            (
                current_section,
                "\n".join(buffer),
            )
        )

    return sections, current_section


def make_section_slug(section: str) -> str:
    slug = section.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)

    return slug.strip("_")


def chunk_policy() -> list[Document]:
    pages = load_policy()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            "•",
            ". ",
            " ",
        ],
    )

    chunks = []

    current_section = "INTRODUCTION"

    for page_number, page in enumerate(
        pages,
        start=1,
    ):
        cleaned_text = clean_page_text(
            page.page_content
        )

        page_sections, current_section = (
            split_page_by_sections(
                cleaned_text,
                current_section,
            )
        )

        for section, section_text in page_sections:

            # Only split further if the section is large
            section_chunks = text_splitter.split_text(
                section_text
            )

            section_slug = make_section_slug(section)

            for part_number, chunk_text in enumerate(
                section_chunks,
                start=1,
            ):
                chunk_id = (
                    f"policy_p{page_number:02d}_"
                    f"{section_slug}_"
                    f"{part_number:02d}"
                )

                chunk = Document(
                    page_content=chunk_text,
                    metadata={
                        "source": (
                            "USGIC-CSCIndividualHealthInsurance_"
                            "2017-2018.pdf"
                        ),
                        "page": page_number,
                        "section": section,
                        "chunk_id": chunk_id,
                    },
                )

                chunks.append(chunk)

    return chunks