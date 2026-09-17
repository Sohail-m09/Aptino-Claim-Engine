from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Patient(BaseModel):
    age: int = Field(ge=0, le=120)


class Hospital(BaseModel):
    name: str
    network_provider: bool | None = None


class Treatment(BaseModel):
    type: Literal["inpatient", "day_care", "domiciliary"]
    admission_hours: int = Field(ge=0)

    diagnosis: str
    procedure: str | None = None

    pre_existing: bool = False
    experimental: bool = False

    patient_cannot_be_moved: bool | None = None
    hospital_room_unavailable: bool | None = None


class Expenses(BaseModel):
    room: int = Field(default=0, ge=0)
    doctor_fees: int = Field(default=0, ge=0)
    medicines_diagnostics: int = Field(default=0, ge=0)
    pre_hospitalization: int = Field(default=0, ge=0)
    post_hospitalization: int = Field(default=0, ge=0)
    ambulance: int = Field(default=0, ge=0)


class PriorPolicy(BaseModel):
    insurer_type: str
    continuous_years: int = Field(ge=0)
    database_and_claim_history_received: bool
    previous_sum_insured_inr: int = Field(ge=0)


class EvidenceContext(BaseModel):
    hospital_registered: bool | None = None
    hospital_minimum_criteria_documented: bool | None = None
    medical_necessity_confirmed: bool | None = None


class ExpenseTiming(BaseModel):
    pre_hospitalization_days_before_admission: int | None = Field(
        default=None,
        ge=0,
    )

    post_hospitalization_days_after_discharge: int | None = Field(
        default=None,
        ge=0,
    )

    same_condition_confirmed: bool | None = None


class ClaimCase(BaseModel):
    model_config = ConfigDict(extra="allow")

    case_id: str
    policy_id: str

    policy_start_date: date
    claim_date: date

    sum_insured_inr: int = Field(gt=0)
    continuous_coverage_months: int = Field(ge=0)
    prior_insurer_continuous_years: int = Field(default=0, ge=0)

    patient: Patient
    hospital: Hospital
    treatment: Treatment
    expenses_inr: Expenses

    documents: list[str]
    task: str

    prior_policy: PriorPolicy | None = None
    evidence_context: EvidenceContext | None = None
    expense_timing: ExpenseTiming | None = None