import json
from pathlib import Path

from app.agents.case_agent import run_case_agent
from app.agents.coverage_agent import run_coverage_agent
from app.agents.decision_agent import run_decision_agent
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

    state.update(
        run_case_agent(state)
    )

    state.update(
        run_evidence_agent(state)
    )

    state.update(
        run_coverage_agent(state)
    )

    state.update(
        run_decision_agent(state)
    )

    print("\nFINANCIAL LIMITS")

    for limit in state["financial_limits"]:
        print(limit.model_dump())

    print("\nDECISION DRAFT")

    print(
        state[
            "decision_draft"
        ].model_dump()
    )

    print("\nTRACE")

    for step in state["trace"]:
        print(step.model_dump())


if __name__ == "__main__":
    main()