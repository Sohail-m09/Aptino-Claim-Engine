import json
from pathlib import Path

import httpx


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

    pub_001 = next(
        case
        for case in cases
        if case["case_id"] == "PUB-001"
    )

    response = httpx.post(
        "http://127.0.0.1:8000/analyze",
        json=pub_001,
        timeout=180,
    )

    print(
        "STATUS:",
        response.status_code,
    )

    print(
        json.dumps(
            response.json(),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()