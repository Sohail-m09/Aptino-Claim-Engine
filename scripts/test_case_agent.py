import json
from pathlib import Path
from app.agents.case_agent import run_case_agent
from app.schemas.claim import ClaimCase


DATA_PATH = Path(
    "data/public_cases/public_test_cases.json"
)


def main():
    with open(
        DATA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    pub_001_data = next(
        case
        for case in cases
        if case["case_id"] == "PUB-001"
    )

    claim = ClaimCase.model_validate(
        pub_001_data
    )

    state = {
        "case": claim,
        "trace": [],
    }

    result = run_case_agent(state)

    print("\nCASE ANALYSIS")
    print(result["case_analysis"])

    print("\nINVESTIGATION QUERIES")

    for query in result[
        "investigation_queries"
    ]:
        print(f"- {query}")

    print("\nTRACE")

    for step in result["trace"]:
        print(step.model_dump())


if __name__ == "__main__":
    main()