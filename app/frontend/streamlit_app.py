import json
import os
from pathlib import Path

import httpx
import streamlit as st
from dotenv import load_dotenv


load_dotenv()


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

PUBLIC_CASES_PATH = Path(
    "data/public_cases/public_test_cases.json"
)


st.set_page_config(
    page_title="Aptino Claim Decision Engine",
    page_icon="📄",
    layout="wide",
)


def load_public_cases():
    with open(
        PUBLIC_CASES_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def analyze_claim(claim_data: dict):
    response = httpx.post(
        f"{API_BASE_URL}/analyze",
        json=claim_data,
        timeout=180,
    )

    response.raise_for_status()

    return response.json()


st.title(
    "Policy-Aware Claim Decision Engine"
)

st.write(
    "Analyze a synthetic health-insurance claim "
    "against the supplied policy using multi-agent RAG."
)


input_mode = st.radio(
    "Choose claim input",
    [
        "Public Test Case",
        "Paste JSON",
    ],
    horizontal=True,
)


claim_data = None


if input_mode == "Public Test Case":

    public_cases = load_public_cases()

    case_ids = [
        case["case_id"]
        for case in public_cases
    ]

    selected_case_id = st.selectbox(
        "Select a public case",
        case_ids,
    )

    claim_data = next(
        case
        for case in public_cases
        if case["case_id"]
        == selected_case_id
    )

    with st.expander(
        "View claim JSON"
    ):
        st.json(claim_data)


else:

    claim_json = st.text_area(
        "Paste claim JSON",
        height=350,
        placeholder=(
            '{\n'
            '  "case_id": "CUSTOM-001",\n'
            '  ...\n'
            '}'
        ),
    )

    if claim_json.strip():

        try:
            claim_data = json.loads(
                claim_json
            )

        except json.JSONDecodeError:
            st.error(
                "Invalid JSON. Please check "
                "the claim format."
            )


if st.button(
    "Analyze Claim",
    type="primary",
):

    if claim_data is None:

        st.warning(
            "Please provide a valid claim."
        )

    else:

        try:

            with st.spinner(
                "Analyzing claim..."
            ):

                result = analyze_claim(
                    claim_data
                )

            st.success(
                "Claim analysis completed."
            )

            st.divider()

            # -------------------------
            # Main decision
            # -------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Decision",
                    result["decision"],
                )

            with col2:

                confidence = (
                    result["confidence"]
                    * 100
                )

                st.metric(
                    "Confidence",
                    f"{confidence:.1f}%",
                )

            # -------------------------
            # Key findings
            # -------------------------

            st.subheader(
                "Key Findings"
            )

            findings = result.get(
                "key_findings",
                [],
            )

            if findings:

                for finding in findings:
                    st.write(
                        f"- {finding}"
                    )

            else:
                st.write(
                    "No key findings returned."
                )

            # -------------------------
            # Financial limits
            # -------------------------

            st.subheader(
                "Applicable Limits & Deductions"
            )

            limits = result.get(
                "applicable_limits",
                [],
            )

            if limits:

                st.dataframe(
                    limits,
                    use_container_width=True,
                )

            else:

                st.info(
                    "No financial limits "
                    "were applied."
                )

            # -------------------------
            # Missing evidence
            # -------------------------

            st.subheader(
                "Missing Evidence"
            )

            missing_evidence = result.get(
                "missing_evidence",
                [],
            )

            if missing_evidence:

                for item in missing_evidence:
                    st.warning(item)

            else:

                st.success(
                    "No material evidence "
                    "is missing."
                )

            # -------------------------
            # Citations
            # -------------------------

            st.subheader(
                "Policy Citations"
            )

            citations = result.get(
                "citations",
                [],
            )

            if citations:

                for citation in citations:

                    with st.expander(
                        (
                            f"Page "
                            f"{citation['page']} — "
                            f"{citation['section']}"
                        )
                    ):

                        st.write(
                            "**Supported claim:**"
                        )

                        st.write(
                            citation["claim"]
                        )

                        st.write(
                            "**Source:**",
                            citation["source"],
                        )

                        st.write(
                            "**Chunk ID:**",
                            citation[
                                "chunk_id"
                            ],
                        )

            else:

                st.info(
                    "No citations returned."
                )

            # -------------------------
            # Validation
            # -------------------------

            st.subheader(
                "Validation"
            )

            validation = result[
                "validation"
            ]

            if (
                validation["status"]
                == "PASS"
            ):

                st.success(
                    "Validation: PASS"
                )

            else:

                st.error(
                    "Validation: FAIL"
                )

            unsupported = validation.get(
                "unsupported_claims",
                [],
            )

            if unsupported:

                for claim in unsupported:
                    st.write(
                        f"- {claim}"
                    )

            # -------------------------
            # Execution trace
            # -------------------------

            st.subheader(
                "Agent Execution Trace"
            )

            trace = result.get(
                "trace",
                [],
            )

            for index, step in enumerate(
                trace,
                start=1,
            ):

                with st.expander(
                    f"{index}. {step['agent']}"
                ):

                    st.write(
                        "**Action:**",
                        step["action"],
                    )

                    st.write(
                        "**Elapsed time:**",
                        (
                            f"{step['elapsed_ms']:.2f} ms"
                        ),
                    )

        except httpx.HTTPStatusError as exc:

            st.error(
                "Backend returned an error."
            )

            try:
                st.json(
                    exc.response.json()
                )
            except Exception:
                st.write(
                    exc.response.text
                )

        except httpx.RequestError:

            st.error(
                "Could not connect to the API. "
                "Make sure the FastAPI backend "
                "is running."
            )

        except Exception as exc:

            st.error(
                f"Unexpected error: {exc}"
            )