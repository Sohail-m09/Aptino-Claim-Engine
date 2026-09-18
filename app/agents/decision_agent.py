import json
from time import perf_counter

from app.core.llm import get_llm
from app.rules.financial_rules import apply_financial_rules
from app.schemas.decision import (
    DecisionDraft,
    TraceStep,
)
from app.schemas.state import ClaimState


def run_decision_agent(
    state: ClaimState,
) -> dict:

    start_time = perf_counter()

    claim = state["case"]

    findings = state.get(
        "coverage_findings",
        [],
    )

    financial_rules = state.get(
        "applicable_financial_rules",
        [],
    )

    missing_evidence = state.get(
        "missing_evidence",
        [],
    )

    # Exact financial calculations happen in Python
    financial_limits = apply_financial_rules(
        claim=claim,
        rules=financial_rules,
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
        DecisionDraft
    )

    prompt = f"""
You are the Decision Agent in a health-insurance
claim decision system.

Use ONLY the supplied claim facts, policy findings,
financial calculations, and missing-evidence list.

Do not use external insurance or medical knowledge.
Do not invent facts.
Do not calculate monetary limits yourself because
the Python financial engine has already calculated
them.

Choose exactly one decision:

ADMISSIBLE
ADMISSIBLE_WITH_LIMITS
PARTIALLY_ADMISSIBLE
NOT_ADMISSIBLE
NEEDS_REVIEW

Decision guidance:

- NEEDS_REVIEW:
  required evidence is missing or uncertainty prevents
  a safe decision.

- NOT_ADMISSIBLE:
  policy-supported exclusion/rejection applies.

- PARTIALLY_ADMISSIBLE:
  only part of the claim is policy-supported.

- ADMISSIBLE_WITH_LIMITS:
  claim is admissible but policy limits or deductions
  reduce the payable amount.

- ADMISSIBLE:
  claim is supported and no material deduction or
  exclusion applies.

Do not create citations yet.
The Validation Agent will audit the decision next.

CLAIM:

{claim.model_dump_json(indent=2)}

POLICY FINDINGS:

{json.dumps(findings_data, indent=2)}

FINANCIAL CALCULATIONS:

{json.dumps(limits_data, indent=2)}

MISSING EVIDENCE:

{json.dumps(missing_evidence, indent=2)}
"""

    decision = structured_model.invoke(
        prompt
    )

    # Simple deterministic guardrail:
    # evidence required for a safe decision is missing.
    if missing_evidence:
        decision.decision = "NEEDS_REVIEW"

    # Prevent ADMISSIBLE when Python found a deduction.
    has_deduction = any(
        limit.deduction > 0
        for limit in financial_limits
    )

    if (
        decision.decision == "ADMISSIBLE"
        and has_deduction
    ):
        decision.decision = (
            "ADMISSIBLE_WITH_LIMITS"
        )

    elapsed_ms = (
        perf_counter() - start_time
    ) * 1000

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        TraceStep(
            agent="Decision Agent",
            action=(
                f"Generated {decision.decision} "
                f"decision with "
                f"{len(financial_limits)} "
                f"financial limit calculations"
            ),
            elapsed_ms=elapsed_ms,
        )
    )

    return {
        "financial_limits": financial_limits,
        "decision_draft": decision,
        "trace": trace,
    }