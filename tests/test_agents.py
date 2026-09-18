import json
from pathlib import Path

import pytest

from app.agents.case_agent import run_case_agent
from app.agents.coverage_agent import run_coverage_agent
from app.agents.decision_agent import run_decision_agent
from app.agents.evidence_agent import run_evidence_agent
from app.agents.validation_agent import run_validation_agent
from app.schemas.claim import ClaimCase


DATA_PATH = Path(
    "data/public_cases/public_test_cases.json"
)


@pytest.fixture
def pub_001_claim():
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

    return ClaimCase.model_validate(
        case_data
    )


def test_case_agent(pub_001_claim):
    state = {
        "case": pub_001_claim,
        "trace": [],
    }

    result = run_case_agent(state)

    assert "case_analysis" in result
    assert "investigation_queries" in result
    assert len(
        result["investigation_queries"]
    ) > 0


def test_evidence_agent(pub_001_claim):
    state = {
        "case": pub_001_claim,
        "trace": [],
    }

    state.update(
        run_case_agent(state)
    )

    result = run_evidence_agent(state)

    assert "retrieved_evidence" in result
    assert len(
        result["retrieved_evidence"]
    ) > 0

    first = result[
        "retrieved_evidence"
    ][0]

    assert first.page > 0
    assert first.section
    assert first.chunk_id


def test_coverage_agent(pub_001_claim):
    state = {
        "case": pub_001_claim,
        "trace": [],
    }

    state.update(
        run_case_agent(state)
    )

    state.update(
        run_evidence_agent(state)
    )

    result = run_coverage_agent(state)

    assert "coverage_findings" in result
    assert "applicable_financial_rules" in result
    assert "missing_evidence" in result


def test_decision_agent(pub_001_claim):
    state = {
        "case": pub_001_claim,
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

    result = run_decision_agent(state)

    assert "decision_draft" in result
    assert "financial_limits" in result

    valid_decisions = {
        "ADMISSIBLE",
        "ADMISSIBLE_WITH_LIMITS",
        "PARTIALLY_ADMISSIBLE",
        "NOT_ADMISSIBLE",
        "NEEDS_REVIEW",
    }

    assert (
        result["decision_draft"].decision
        in valid_decisions
    )


def test_validation_agent(pub_001_claim):
    state = {
        "case": pub_001_claim,
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

    result = run_validation_agent(state)

    assert "validation" in result
    assert "citations" in result

    assert result[
        "validation"
    ].status in {
        "PASS",
        "FAIL",
    }