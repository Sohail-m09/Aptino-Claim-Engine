from app.schemas.decision import (
    FinalDecision,
    TraceStep,
)
from app.schemas.state import ClaimState


def finalize_decision(
    state: ClaimState,
) -> dict:

    draft = state["decision_draft"]

    validation = state["validation"]

    financial_limits = state.get(
        "financial_limits",
        [],
    )

    citations = state.get(
        "citations",
        [],
    )

    # Combine missing evidence from both
    # coverage analysis and decision draft.
    missing_evidence = list(
        dict.fromkeys(
            state.get(
                "missing_evidence",
                [],
            )
            + draft.missing_evidence
        )
    )

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        TraceStep(
            agent="Workflow Controller",
            action=(
                "Assembled final structured "
                "claim decision"
            ),
            elapsed_ms=0,
        )
    )

    final_decision = FinalDecision(
        case_id=draft.case_id,
        decision=draft.decision,
        confidence=draft.confidence,
        key_findings=draft.key_findings,
        applicable_limits=financial_limits,
        missing_evidence=missing_evidence,
        citations=citations,
        validation=validation,
        trace=trace,
    )

    return {
        "decision": final_decision,
        "trace": trace,
    }