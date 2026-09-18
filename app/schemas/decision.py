from typing import Literal

from pydantic import BaseModel, Field


DecisionStatus = Literal[
    "ADMISSIBLE",
    "ADMISSIBLE_WITH_LIMITS",
    "PARTIALLY_ADMISSIBLE",
    "NOT_ADMISSIBLE",
    "NEEDS_REVIEW",
]


class Evidence(BaseModel):
    content: str
    source: str
    page: int
    section: str
    chunk_id: str
    score: float | None = None


class Finding(BaseModel):
    finding: str
    status: Literal["SUPPORTED", "NOT_SUPPORTED", "UNCERTAIN"]
    evidence_ids: list[str] = Field(default_factory=list)


class ApplicableLimit(BaseModel):
    category: str
    limit_description: str

    claimed_amount: float = Field(ge=0)
    admissible_amount: float = Field(ge=0)
    deduction: float = Field(ge=0)


class Citation(BaseModel):
    claim: str
    source: str
    page: int
    section: str
    chunk_id: str


class ValidationResult(BaseModel):
    status: Literal["PASS", "FAIL"]
    unsupported_claims: list[str] = Field(default_factory=list)


class TraceStep(BaseModel):
    agent: str
    action: str
    elapsed_ms: float = Field(ge=0)


class FinalDecision(BaseModel):
    case_id: str
    decision: DecisionStatus

    confidence: float = Field(
        ge=0,
        le=1,
    )

    key_findings: list[str] = Field(default_factory=list)

    applicable_limits: list[ApplicableLimit] = Field(default_factory=list)

    missing_evidence: list[str] = Field(default_factory=list)

    citations: list[Citation] = Field(default_factory=list)

    validation: ValidationResult

    trace: list[TraceStep] = Field(default_factory=list)

class DecisionDraft(BaseModel):
    case_id: str

    decision: DecisionStatus

    confidence: float = Field(
        ge=0,
        le=1,
    )

    key_findings: list[str] = Field(
        default_factory=list
    )

    missing_evidence: list[str] = Field(
        default_factory=list
    )