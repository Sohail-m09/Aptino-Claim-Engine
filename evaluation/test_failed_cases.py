import json
from pathlib import Path

from app.schemas.claim import ClaimCase
from app.workflow.graph import claim_graph


CASES_PATH = Path(
    "data/public_cases/public_test_cases.json"
)

CASE_IDS = [
    "PUB-006",
    "PUB-012"
]


def main():

    with open(
        CASES_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    case_map = {
        case["case_id"]: case
        for case in cases
    }

    print(
        "Available cases:",
        list(case_map.keys()),
    )

    for case_id in CASE_IDS:

        print(
            f"\nRunning {case_id}..."
        )

        case_data = case_map.get(
            case_id
        )

        if case_data is None:
            print(
                f"{case_id} not found!"
            )
            continue

        claim = ClaimCase.model_validate(
            case_data
        )

        result = claim_graph.invoke(
            {
                "case": claim,
                "trace": [],
                "revision_count": 0,
            }
        )

        decision = result["decision"]

        print(
            "\n"
            + "=" * 60
        )

        print(
            "CASE:",
            decision.case_id,
        )

        print(
            "DECISION:",
            decision.decision,
        )

        print(
            "MISSING EVIDENCE:",
            decision.missing_evidence,
        )

        print(
            "VALIDATION:",
            decision.validation.status,
        )


if __name__ == "__main__":
    main()