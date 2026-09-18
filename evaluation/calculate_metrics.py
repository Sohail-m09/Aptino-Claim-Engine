import json
from pathlib import Path


RESULTS_PATH = Path(
    "evaluation/results/public_results.json"
)


def main():

    with open(
        RESULTS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    cases = data["cases"]

    total_cases = len(cases)

    correct_cases = sum(
        1
        for case in cases
        if case.get("correct")
    )

    validation_passes = sum(
        1
        for case in cases
        if case.get("validation_status") == "PASS"
    )

    cases_with_citations = sum(
        1
        for case in cases
        if case.get("citation_count", 0) > 0
    )

    expected_review_cases = [
        case
        for case in cases
        if case.get("expected_decision")
        == "NEEDS_REVIEW"
    ]

    correct_review_cases = sum(
        1
        for case in expected_review_cases
        if (
            case.get("predicted_decision")
            == "NEEDS_REVIEW"
        )
    )

    revised_cases = sum(
        1
        for case in cases
        if case.get(
            "revision_count",
            0,
        ) > 0
    )

    total_citations = sum(
        case.get(
            "citation_count",
            0,
        )
        for case in cases
    )

    decision_accuracy = (
        correct_cases / total_cases
        if total_cases
        else 0
    )

    validation_pass_rate = (
        validation_passes / total_cases
        if total_cases
        else 0
    )

    citation_coverage = (
        cases_with_citations / total_cases
        if total_cases
        else 0
    )

    abstention_accuracy = (
        correct_review_cases
        / len(expected_review_cases)
        if expected_review_cases
        else 0
    )

    average_citations = (
        total_citations / total_cases
        if total_cases
        else 0
    )

    metrics = {
        "total_public_cases":
            total_cases,

        "decision_accuracy":
            round(
                decision_accuracy,
                4,
            ),

        "validation_pass_rate":
            round(
                validation_pass_rate,
                4,
            ),

        "citation_coverage_rate":
            round(
                citation_coverage,
                4,
            ),

        "abstention_accuracy":
            round(
                abstention_accuracy,
                4,
            ),

        "cases_using_revision":
            revised_cases,

        "average_citations_per_case":
            round(
                average_citations,
                2,
            ),
    }

    output_path = Path(
        "evaluation/results/public_metrics.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2,
        )

    print(
        "\nPUBLIC EVALUATION METRICS"
    )

    print("=" * 50)

    print(
        f"Decision Accuracy: "
        f"{decision_accuracy * 100:.2f}%"
    )

    print(
        f"Validation Pass Rate: "
        f"{validation_pass_rate * 100:.2f}%"
    )

    print(
        f"Citation Coverage: "
        f"{citation_coverage * 100:.2f}%"
    )

    print(
        f"Abstention Accuracy: "
        f"{abstention_accuracy * 100:.2f}%"
    )

    print(
        f"Cases Using Revision: "
        f"{revised_cases}/{total_cases}"
    )

    print(
        f"Average Citations per Case: "
        f"{average_citations:.2f}"
    )

    print(
        "\nSaved to:",
        output_path,
    )


if __name__ == "__main__":
    main()