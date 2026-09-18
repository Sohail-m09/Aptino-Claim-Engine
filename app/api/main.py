from fastapi import FastAPI, HTTPException

from app.schemas.claim import ClaimCase
from app.schemas.decision import FinalDecision
from app.workflow.graph import claim_graph


app = FastAPI(
    title="Aptino Claim Decision Engine",
    description=(
        "Policy-aware multi-agent RAG system "
        "for health-insurance claim analysis."
    ),
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "aptino-claim-engine",
    }


@app.post(
    "/analyze",
    response_model=FinalDecision,
)
def analyze_claim(
    claim: ClaimCase,
):

    try:
        initial_state = {
            "case": claim,
            "trace": [],
            "revision_count": 0,
        }

        result = claim_graph.invoke(
            initial_state
        )

        return result["decision"]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Claim analysis failed. "
                "Please try again."
            ),
        ) from exc