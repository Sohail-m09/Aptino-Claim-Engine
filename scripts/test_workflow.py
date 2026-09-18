import json
from pathlib import Path

from app.schemas.claim import ClaimCase
from app.workflow.graph import claim_graph


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

    case_data = next(
        case
        for case in cases
        if case["case_id"] == "PUB-001"
    )

    claim = ClaimCase.model_validate(
        case_data
    )

    initial_state = {
        "case": claim,
        "trace": [],
        "revision_count": 0,
    }

    result = claim_graph.invoke(
    initial_state
    )

    print("\nFINAL DECISION")

    print(
        result[
            "decision"
        ].model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()