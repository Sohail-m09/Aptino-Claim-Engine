from time import perf_counter

from app.core.llm import get_llm
from app.schemas.agent import CaseAnalysis
from app.schemas.decision import TraceStep
from app.schemas.state import ClaimState


def run_case_agent(
    state: ClaimState,
) -> dict:

    start_time = perf_counter()

    claim = state["case"]

    model = get_llm()

    structured_model = model.with_structured_output(
        CaseAnalysis
    )

    prompt = f"""
You are the Case Analysis Agent in a health-insurance
claim decision system.

Your responsibility is only to analyze the supplied
claim facts and prepare an investigation plan.

Do not make the final insurance decision.
Do not invent missing facts.
Do not use external medical or insurance knowledge.

Use the claim's investigation task to prioritize
which policy dimensions actually need investigation.

Do not create investigation dimensions for unrelated
optional benefits or policy definitions unless the
claim facts or task make them relevant.

Identify:

1. A short factual case summary.
2. Important facts relevant to investigation.
3. Decision dimensions that should be checked.
4. Missing or uncertain information.
5. Clear policy-search queries for the
   Policy Evidence Agent.

Keep the investigation queries short and specific.

Claim:

{claim.model_dump_json(indent=2)}
"""

    analysis = structured_model.invoke(prompt)

    queries = list(
        analysis.investigation_queries
    )

    if claim.treatment.experimental:
        queries.append(
            "experimental or unproven treatment exclusion"
        )

    if claim.treatment.pre_existing:
        queries.append(
            "pre-existing disease waiting period "
            "continuous coverage"
        )

    queries = list(
        dict.fromkeys(queries)
    )

    elapsed_ms = (
        perf_counter() - start_time
    ) * 1000

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        TraceStep(
            agent="Case Analysis Agent",
            action=(
                f"Identified "
                f"{len(analysis.decision_dimensions)} "
                f"decision dimensions and "
                f"{len(queries)} "
                f"policy queries"
            ),
            elapsed_ms=elapsed_ms,
        )
    )

    return {
        "case_analysis": analysis.model_dump(),
        "investigation_queries":
            queries,
        "trace": trace,
    }