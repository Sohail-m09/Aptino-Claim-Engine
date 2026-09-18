import json
from pathlib import Path

from app.agents.case_agent import run_case_agent
from app.agents.evidence_agent import run_evidence_agent
from app.agents.coverage_agent import run_coverage_agent
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
    state.update(
        run_case_agent(state)
    )

    # Agent 2
    state.update(
        run_evidence_agent(state)
    )

    # Agent 3
    state.update(
        run_coverage_agent(state)
    )

    print("\nCOVERAGE FINDINGS")

    for finding in state[
        "coverage_findings"
    ]:
        print(
            finding.model_dump()
        )

    print("\nFINANCIAL RULES")

    for rule in state[
        "applicable_financial_rules"
    ]:
        print(f"- {rule}")

    print("\nMISSING EVIDENCE")

    for item in state[
        "missing_evidence"
    ]:
        print(f"- {item}")

    print("\nTRACE")

    for step in state["trace"]:
        print(step.model_dump())


if __name__ == "__main__":
    main()