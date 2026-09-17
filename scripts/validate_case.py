import json
from pathlib import Path

from pydantic import ValidationError

from app.schemas.claim import ClaimCase


DATA_PATH = Path("data/public_cases/public_test_cases.json")


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        cases = json.load(file)

    pub_001 = next(
        case for case in cases
        if case["case_id"] == "PUB-001"
    )

    try:
        claim = ClaimCase.model_validate(pub_001)

        print("PUB-001 validation successful")
        print(f"Case ID: {claim.case_id}")
        print(f"Diagnosis: {claim.treatment.diagnosis}")
        print(f"Sum Insured: ₹{claim.sum_insured_inr}")
        print(f"Claim Date: {claim.claim_date}")

    except ValidationError as error:
        print("Validation failed")
        print(error)


if __name__ == "__main__":
    main()