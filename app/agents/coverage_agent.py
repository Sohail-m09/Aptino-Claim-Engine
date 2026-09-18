from time import perf_counter

from app.core.llm import get_llm
from app.schemas.agent import CoverageAnalysis
from app.schemas.decision import TraceStep
from app.schemas.state import ClaimState


def run_coverage_agent(
    state: ClaimState,
) -> dict:

    start_time = perf_counter()

    claim = state["case"]

    evidence = state.get(
        "retrieved_evidence",
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

    model = get_llm()

    structured_model = model.with_structured_output(
        CoverageAnalysis
    )

    prompt = f"""
You are the Coverage & Exclusion Agent in a
health-insurance claim decision system.

Your responsibility is to compare the claim facts
with ONLY the supplied policy evidence.

Do not make the final claim decision.
Do not calculate rupee deductions.
Do not use external medical or insurance knowledge.
Do not invent missing facts.

IMPORTANT FACT-HANDLING RULES:

1. Treat explicit structured fields in the CLAIM as
   established facts for this synthetic evaluation.

   Examples:
   - continuous_coverage_months
   - prior_insurer_continuous_years
   - pre_existing
   - experimental
   - evidence_context values
   - expense_timing values
   - prior_policy values

2. If a boolean field explicitly says true or false,
   do not request additional verification of that
   same fact unless the policy specifically requires
   evidence that is not represented in the claim.

3. The documents list represents documents supplied
   with the claim. Do not report a document as
   missing when that document type is already listed.

4. If prior_insurer_continuous_years is 0 and no
   prior_policy is supplied, treat that as no prior
   continuous insurance being claimed. Do not ask
   for previous-policy records.

5. Only apply policy clauses that are materially
   relevant to this claim and its investigation task.

   Do not apply requirements belonging to unrelated
   optional benefits, extensions, or definitions
   simply because retrieval returned them.

6. missing_evidence must contain ONLY evidence whose
   absence prevents a safe final claim decision.

   Do not include:
   - nice-to-have verification
   - facts already explicitly supplied
   - irrelevant evidence
   - documents already listed as available

7. If the supplied facts are sufficient to apply a
   policy rule, apply that rule rather than returning
   uncertainty.

8. When treatment.experimental is explicitly true,
   evaluate the policy's experimental or unproven
   treatment exclusion directly.

   Do not request additional proof that the treatment
   is experimental because that fact is already
   established by the structured synthetic claim.

For every important policy issue:

1. Create a clear finding.
2. Mark it as:
   - SUPPORTED
   - NOT_SUPPORTED
   - UNCERTAIN
3. Reference the supporting policy chunk IDs.
4. Identify financial rules that may need
   deterministic calculation later.
5. Identify decision-blocking missing evidence only
   when the supplied claim truly cannot establish a
   required policy condition.

Examples of financial rules:
- room_rent
- doctor_fees
- medicines_diagnostics
- domiciliary
- ambulance

CLAIM:

{claim.model_dump_json(indent=2)}

INVESTIGATION TASK:

{claim.task}

POLICY EVIDENCE:

{evidence_text}
"""

    analysis = structured_model.invoke(
        prompt
    )

    missing_evidence = list(
        analysis.missing_evidence
    )

    evidence_context = claim.evidence_context

    if evidence_context is not None:

        if (
            evidence_context.hospital_registered
            is None
        ):
            missing_evidence.append(
                "Evidence confirming that the hospital "
                "meets the policy's registration requirements"
            )

        if (
            evidence_context.medical_necessity_confirmed
            is None
        ):
            missing_evidence.append(
                "Evidence confirming medical necessity "
                "of the hospitalization"
            )

    missing_evidence = list(
        dict.fromkeys(missing_evidence)
    )

    elapsed_ms = (
        perf_counter() - start_time
    ) * 1000

    trace = list(
        state.get("trace", [])
    )

    trace.append(
        TraceStep(
            agent="Coverage & Exclusion Agent",
            action=(
                f"Produced "
                f"{len(analysis.findings)} findings, "
                f"identified "
                f"{len(analysis.applicable_financial_rules)} "
                f"financial rules and "
                f"{len(missing_evidence)} "
                f"missing evidence items"
            ),
            elapsed_ms=elapsed_ms,
        )
    )

    return {
        "coverage_findings":
            analysis.findings,

        "applicable_financial_rules":
            analysis.applicable_financial_rules,

        "missing_evidence":
            missing_evidence,

        "trace": trace,
    }