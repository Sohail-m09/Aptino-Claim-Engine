from typing import NotRequired, TypedDict

from app.schemas.claim import ClaimCase
from app.schemas.decision import (
    ApplicableLimit,
    Citation,
    DecisionDraft,
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

    applicable_financial_rules: NotRequired[list[str]]

    missing_evidence: NotRequired[list[str]]

    # Deterministic financial rules
    financial_limits: NotRequired[list[ApplicableLimit]]

    # Decision Agent
    decision: NotRequired[FinalDecision]

    decision_draft: NotRequired[DecisionDraft]

    # Validation Agent
    validation: NotRequired[ValidationResult]

    citations: NotRequired[list[Citation]]

    # Visible execution trace
    trace: NotRequired[list[TraceStep]]

    # Used for one controlled validation retry
    revision_count: NotRequired[int]

    # Graceful failure handling
    error: NotRequired[str]