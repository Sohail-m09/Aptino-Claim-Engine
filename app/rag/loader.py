from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


POLICY_PATH = Path(
    "data/policy/USGIC-CSCIndividualHealthInsurance_2017-2018.pdf"
)


def load_policy():
    if not POLICY_PATH.exists():
        raise FileNotFoundError(
            f"Policy PDF not found: {POLICY_PATH}"
        )

    loader = PyPDFLoader(str(POLICY_PATH))

    pages = loader.load()

    return pages