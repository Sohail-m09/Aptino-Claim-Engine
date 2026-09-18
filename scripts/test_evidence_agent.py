import json
from pathlib import Path

from app.agents.case_agent import run_case_agent
from app.agents.evidence_agent import run_evidence_agent
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

    # Agent 1
    case_result = run_case_agent(
        state
    )

    state.update(case_result)

    # Agent 2
    evidence_result = run_evidence_agent(
        state
    )

    state.update(evidence_result)

    print(
        f"\nTotal evidence chunks: "
        f"{len(state['retrieved_evidence'])}"
    )

    for evidence in state[
        "retrieved_evidence"
    ][:5]:

        print("\n" + "=" * 60)

        print(
            f"Page: {evidence.page}"
        )

        print(
            f"Section: {evidence.section}"
        )

        print(
            f"Chunk ID: {evidence.chunk_id}"
        )

        print(
            f"Score: {evidence.score}"
        )

        print("\nContent:")
        print(
            evidence.content[:500]
        )

    print("\nTRACE")

    for step in state["trace"]:
        print(step.model_dump())


if __name__ == "__main__":
    main()