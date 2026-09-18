import json
from time import perf_counter

from app.core.llm import get_llm
from app.schemas.agent import ValidationAnalysis
from app.schemas.decision import (
    Citation,
    TraceStep,
    ValidationResult,
)
from app.schemas.state import ClaimState


def run_validation_agent(
    state: ClaimState,
) -> dict:

    start_time = perf_counter()

    decision = state["decision_draft"]

    evidence = state.get(
        "retrieved_evidence",
        [],
    )

    findings = state.get(
        "coverage_findings",
        [],
    )

    financial_limits = state.get(
        "financial_limits",
        [],
    )

    evidence_text = "\n\n".join(
        [
            (
                f"CHUNK ID: {item.chunk_id}\n"
                f"PAGE: {item.page}\n"
                f"SECTION: {item.section}\n"
                f"CONTENT:\n{item.content}"
            )
            for item in evidence
        ]
    )

    findings_data = [
        finding.model_dump()
        for finding in findings
    ]

    limits_data = [
        limit.model_dump()
        for limit in financial_limits
    ]

    model = get_llm()

    structured_model = model.with_structured_output(
        ValidationAnalysis
    )

    prompt = f"""
You are the Citation Validation Agent in a
health-insurance claim decision system.

Audit the draft decision using ONLY the supplied
claim findings, financial-rule results, and retrieved
policy evidence.

Your responsibilities:

1. Verify that every material POLICY-BASED decision
   statement is supported by retrieved evidence.

2. Verify that each applicable financial limit has
   policy evidence supporting the rule.

3. Verify that the selected decision status is
   consistent with the supported findings.

4. Return FAIL if a material policy conclusion is
   unsupported.

5. Do not use external medical or insurance
   knowledge.

6. Do not expose chain-of-thought.

7. For citations, use ONLY chunk IDs appearing in
   the supplied evidence.

Claim facts themselves do not require policy
citations. Policy conclusions do.

Do not recompute monetary arithmetic.
The financial amounts were calculated
deterministically in Python. Validate only that the
policy rule behind the calculation is supported.

DECISION DRAFT:

{decision.model_dump_json(indent=2)}

POLICY FINDINGS:

{json.dumps(findings_data, indent=2)}

FINANCIAL LIMITS:

{json.dumps(limits_data, indent=2)}

RETRIEVED POLICY EVIDENCE:

{evidence_text}
"""

    audit = structured_model.invoke(
        prompt
    )

    # Real evidence lookup
    evidence_map = {
        item.chunk_id: item
        for item in evidence
    }

    citations = []

    invalid_references = []

    for reference in audit.citation_references:

        evidence_item = evidence_map.get(
            reference.chunk_id
        )

        if evidence_item is None:
            invalid_references.append(
                reference.chunk_id
            )
            continue

        citations.append(
            Citation(
                claim=reference.claim,
                source=evidence_item.source,
                page=evidence_item.page,
                section=evidence_item.section,
                chunk_id=evidence_item.chunk_id,
            )
        )

    unsupported_claims = list(
        audit.unsupported_claims
    )

    # Never accept a citation invented by the LLM
    if invalid_references:
        unsupported_claims.append(
            "Invalid evidence references: "
            + ", ".join(invalid_references)
        )

    final_status = audit.status

    if unsupported_claims:
        final_status = "FAIL"

    validation = ValidationResult(
        status=final_status,
        unsupported_claims=unsupported_claims,
    )

    elapsed_ms = (
        perf_counter() - start_time
    ) * 1000

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        TraceStep(
            agent="Validation Agent",
            action=(
                f"Validation {validation.status}; "
                f"{len(citations)} citations verified "
                f"and "
                f"{len(unsupported_claims)} "
                f"unsupported claims found"
            ),
            elapsed_ms=elapsed_ms,
        )
    )

    return {
        "validation": validation,
        "citations": citations,
        "trace": trace,
    }