import json
from pathlib import Path

from app.schemas.claim import ClaimCase
from app.workflow.graph import claim_graph


CASES_PATH = Path(
    "data/public_cases/public_test_cases.json"
)

EXPECTED_PATH = Path(
    "evaluation/expected_public_results.json"
)

RESULTS_PATH = Path(
    "evaluation/results/public_results.json"
)


def load_json(path: Path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():

    cases = load_json(
        CASES_PATH
    )

    expected_results = load_json(
        EXPECTED_PATH
    )

    expected_map = {
        item["case_id"]: item
        for item in expected_results
    }

    results = []

    correct_count = 0

    for index, case_data in enumerate(
        cases,
        start=1,
    ):

        case_id = case_data[
            "case_id"
        ]

        print(
            f"\n[{index}/{len(cases)}] "
            f"Evaluating {case_id}..."
        )

        claim = ClaimCase.model_validate(
            case_data
        )

        initial_state = {
            "case": claim,
            "trace": [],
            "revision_count": 0,
        }

        try:

            state = claim_graph.invoke(
                initial_state
            )

            decision = state[
                "decision"
            ]

            expected = expected_map[
                case_id
            ]

            predicted_status = (
                decision.decision
            )

            expected_status = expected[
                "expected_decision"
            ]

            correct = (
                predicted_status
                == expected_status
            )

            if correct:
                correct_count += 1

            results.append(
                {
                    "case_id": case_id,
                    "expected_decision":
                        expected_status,
                    "predicted_decision":
                        predicted_status,
                    "correct": correct,
                    "confidence":
                        decision.confidence,
                    "validation_status":
                        decision.validation.status,
                    "citation_count":
                        len(
                            decision.citations
                        ),
                    "revision_count":
                        state.get(
                            "revision_count",
                            0,
                        ),
                    "missing_evidence":
                        decision.missing_evidence,
                }
            )

            print(
                f"Expected:  {expected_status}"
            )

            print(
                f"Predicted: {predicted_status}"
            )

            print(
                "Result:   ",
                "PASS"
                if correct
                else "FAIL",
            )

        except Exception as exc:

            print(
                f"ERROR: {exc}"
            )

            results.append(
                {
                    "case_id": case_id,
                    "expected_decision":
                        expected_map[
                            case_id
                        ][
                            "expected_decision"
                        ],
                    "predicted_decision":
                        "ERROR",
                    "correct": False,
                    "error": str(exc),
                }
            )

    total_cases = len(cases)

    accuracy = (
        correct_count
        / total_cases
        if total_cases
        else 0
    )

    output = {
        "summary": {
            "total_cases": total_cases,
            "correct_cases":
                correct_count,
            "decision_accuracy":
                round(
                    accuracy,
                    4,
                ),
        },
        "cases": results,
    }

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
        )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "PUBLIC EVALUATION COMPLETE"
    )

    print(
        f"Correct: "
        f"{correct_count}/{total_cases}"
    )

    print(
        f"Decision Accuracy: "
        f"{accuracy * 100:.2f}%"
    )

    print(
        f"Results saved to: "
        f"{RESULTS_PATH}"
    )


if __name__ == "__main__":
    main()