from typing import NotRequired, TypedDict

from app.schemas.claim import ClaimCase
from app.schemas.decision import (
    ApplicableLimit,
    Evidence,
    FinalDecision,
    Finding,
    TraceStep,
    ValidationResult,
)


class ClaimState(TypedDict):
    # Original input
    case: ClaimCase

    # Case Analysis Agent
    case_analysis: NotRequired[dict]
    investigation_queries: NotRequired[list[str]]

    # Policy Evidence Agent
    retrieved_evidence: NotRequired[list[Evidence]]

    # Coverage & Exclusion Agent
    coverage_findings: NotRequired[list[Finding]]

    # Deterministic financial rules
    financial_limits: NotRequired[list[ApplicableLimit]]

    # Decision Agent
    decision: NotRequired[FinalDecision]

    # Validation Agent
    validation: NotRequired[ValidationResult]

    # Visible execution trace
    trace: NotRequired[list[TraceStep]]

    # Used for one controlled validation retry
    revision_count: NotRequired[int]

    # Graceful failure handling
    error: NotRequired[str]