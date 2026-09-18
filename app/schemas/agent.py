from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.decision import Finding


FinancialRule = Literal[
    "room_rent",
    "doctor_fees",
    "medicines_diagnostics",
    "domiciliary",
    "ambulance",
]


class CaseAnalysis(BaseModel):
    summary: str

    important_facts: list[str] = Field(
        default_factory=list
    )

    decision_dimensions: list[str] = Field(
        default_factory=list
    )

    missing_fields: list[str] = Field(
        default_factory=list
    )

    investigation_queries: list[str] = Field(
        default_factory=list
    )


class CoverageAnalysis(BaseModel):
    findings: list[Finding] = Field(
        default_factory=list
    )

    applicable_financial_rules: list[FinancialRule] = Field(
        default_factory=list
    )

    missing_evidence: list[str] = Field(
        default_factory=list
    )

class CitationReference(BaseModel):
    claim: str
    chunk_id: str


class ValidationAnalysis(BaseModel):
    status: Literal["PASS", "FAIL"]

    unsupported_claims: list[str] = Field(
        default_factory=list
    )

    citation_references: list[CitationReference] = Field(
        default_factory=list
    )