from langgraph.graph import END, START, StateGraph
from app.agents.case_agent import run_case_agent
from app.agents.coverage_agent import run_coverage_agent
from app.agents.decision_agent import run_decision_agent
from app.agents.evidence_agent import run_evidence_agent
from app.agents.validation_agent import run_validation_agent
from app.schemas.decision import TraceStep
from app.schemas.state import ClaimState
from app.workflow.finalizer import finalize_decision


def case_node(state: ClaimState) -> dict:
    return run_case_agent(state)


def evidence_node(state: ClaimState) -> dict:
    return run_evidence_agent(state)


def coverage_node(state: ClaimState) -> dict:
    return run_coverage_agent(state)


def decision_node(state: ClaimState) -> dict:
    return run_decision_agent(state)


def validation_node(state: ClaimState) -> dict:
    return run_validation_agent(state)

def finalize_node(state: ClaimState,) -> dict:
    return finalize_decision(state)

def revision_node(
    state: ClaimState,
) -> dict:

    revision_count = (
        state.get("revision_count", 0) + 1
    )

    validation = state["validation"]

    current_queries = list(
        state.get(
            "investigation_queries",
            [],
        )
    )

    new_queries = [
        f"policy evidence for {claim}"
        for claim in validation.unsupported_claims
    ]

    combined_queries = list(
        dict.fromkeys(
            current_queries + new_queries
        )
    )

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        TraceStep(
            agent="Workflow Controller",
            action=(
                "Validation failed. Added targeted "
                "policy queries for one revision."
            ),
            elapsed_ms=0,
        )
    )

    return {
        "revision_count": revision_count,
        "investigation_queries": combined_queries,
        "trace": trace,
    }

def mark_needs_review_node(
    state: ClaimState,
) -> dict:

    decision = state[
        "decision_draft"
    ]

    validation = state[
        "validation"
    ]

    missing_evidence = list(
        decision.missing_evidence
    )

    missing_evidence.extend(
        validation.unsupported_claims
    )

    updated_decision = decision.model_copy(
        update={
            "decision": "NEEDS_REVIEW",
            "missing_evidence": list(
                dict.fromkeys(
                    missing_evidence
                )
            ),
        }
    )

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        TraceStep(
            agent="Workflow Controller",
            action=(
                "Validation remained unsupported "
                "after revision. Marked claim as "
                "NEEDS_REVIEW."
            ),
            elapsed_ms=0,
        )
    )

    return {
        "decision_draft": updated_decision,
        "trace": trace,
    }

def route_after_validation(
    state: ClaimState,
) -> str:

    validation = state[
        "validation"
    ]

    if validation.status == "PASS":
        return "finalize"

    revision_count = state.get(
        "revision_count",
        0,
    )

    if revision_count < 1:
        return "revise"

    return "needs_review"

def build_claim_graph():

    workflow = StateGraph(
        ClaimState
    )

    workflow.add_node(
        "case_analysis",
        case_node,
    )

    workflow.add_node(
        "policy_evidence",
        evidence_node,
    )

    workflow.add_node(
        "coverage_analysis",
        coverage_node,
    )

    workflow.add_node(
        "decision",
        decision_node,
    )

    workflow.add_node(
        "validation",
        validation_node,
    )

    workflow.add_node(
        "revision",
        revision_node,
    )

    workflow.add_node(
        "needs_review",
        mark_needs_review_node,
    )

    workflow.add_node(
        "finalize",
        finalize_node,
    )

    workflow.add_edge(
        START,
        "case_analysis",
    )

    workflow.add_edge(
        "case_analysis",
        "policy_evidence",
    )

    workflow.add_edge(
        "policy_evidence",
        "coverage_analysis",
    )

    workflow.add_edge(
        "coverage_analysis",
        "decision",
    )

    workflow.add_edge(
        "decision",
        "validation",
    )

    workflow.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "finalize": "finalize",
            "revise": "revision",
            "needs_review": "needs_review",
        },
    )

    workflow.add_edge(
        "revision",
        "policy_evidence",
    )

    workflow.add_edge(
        "needs_review",
        "finalize",
    )

    workflow.add_edge(
        "finalize",
        END,
    )

    return workflow.compile()


claim_graph = build_claim_graph()