from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_health_endpoint():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert (
        data["service"]
        == "aptino-claim-engine"
    )


def test_analyze_rejects_empty_body():

    response = client.post(
        "/analyze",
        json={},
    )

    assert response.status_code == 422


def test_analyze_rejects_negative_sum_insured():

    invalid_claim = {
        "case_id": "INVALID-001",
        "policy_id": "TEST",
        "policy_start_date": "2025-01-01",
        "claim_date": "2025-02-01",
        "sum_insured_inr": -500000,
        "continuous_coverage_months": 1,
        "patient": {
            "age": 30
        },
        "hospital": {
            "name": "Test Hospital",
            "network_provider": True
        },
        "treatment": {
            "type": "inpatient",
            "admission_hours": 48,
            "diagnosis": "Test illness"
        },
        "expenses_inr": {},
        "documents": [],
        "task": "Test invalid input"
    }

    response = client.post(
        "/analyze",
        json=invalid_claim,
    )

    assert response.status_code == 422


def test_analyze_rejects_invalid_treatment_type():

    invalid_claim = {
        "case_id": "INVALID-002",
        "policy_id": "TEST",
        "policy_start_date": "2025-01-01",
        "claim_date": "2025-02-01",
        "sum_insured_inr": 500000,
        "continuous_coverage_months": 1,
        "patient": {
            "age": 30
        },
        "hospital": {
            "name": "Test Hospital",
            "network_provider": True
        },
        "treatment": {
            "type": "unknown_type",
            "admission_hours": 48,
            "diagnosis": "Test illness"
        },
        "expenses_inr": {},
        "documents": [],
        "task": "Test invalid treatment"
    }

    response = client.post(
        "/analyze",
        json=invalid_claim,
    )

    assert response.status_code == 422