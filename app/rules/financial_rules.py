import math
from app.schemas.claim import ClaimCase
from app.schemas.decision import ApplicableLimit


def calculate_room_limit(
    sum_insured: int,
    admission_hours: int,
) -> float:
    daily_limit = sum_insured * 0.01

    admission_days = max(
        1,
        math.ceil(admission_hours / 24),
    )

    return daily_limit * admission_days


def calculate_doctor_fee_limit(
    sum_insured: int,
) -> float:
    return sum_insured * 0.25


def calculate_medicines_limit(
    sum_insured: int,
) -> float:
    return sum_insured * 0.40


def calculate_domiciliary_limit(
    sum_insured: int,
) -> float:
    return sum_insured * 0.20


def calculate_ambulance_limit(
    sum_insured: int,
) -> float:
    percentage_limit = sum_insured * 0.01

    return min(
        percentage_limit,
        1000,
    )


def calculate_deduction(
    claimed_amount: float,
    allowed_limit: float,
) -> tuple[float, float]:
    admissible_amount = min(
        claimed_amount,
        allowed_limit,
    )

    deduction = max(
        0,
        claimed_amount - admissible_amount,
    )

    return admissible_amount, deduction

def apply_financial_rules(
    claim: ClaimCase,
    rules: list[str],
) -> list[ApplicableLimit]:

    results = []

    expenses = claim.expenses_inr

    # Remove duplicate rule names
    unique_rules = list(dict.fromkeys(rules))

    for rule in unique_rules:

        if rule == "room_rent" and expenses.room > 0:

            allowed_limit = calculate_room_limit(
                claim.sum_insured_inr,
                claim.treatment.admission_hours,
            )

            admissible, deduction = calculate_deduction(
                expenses.room,
                allowed_limit,
            )

            results.append(
                ApplicableLimit(
                    category="Room Rent",
                    limit_description=(
                        "1% of Basic Sum Insured per day"
                    ),
                    claimed_amount=expenses.room,
                    admissible_amount=admissible,
                    deduction=deduction,
                )
            )

        elif rule == "doctor_fees" and expenses.doctor_fees > 0:

            allowed_limit = calculate_doctor_fee_limit(
                claim.sum_insured_inr
            )

            admissible, deduction = calculate_deduction(
                expenses.doctor_fees,
                allowed_limit,
            )

            results.append(
                ApplicableLimit(
                    category="Doctor Fees",
                    limit_description=(
                        "25% of Basic Sum Insured"
                    ),
                    claimed_amount=expenses.doctor_fees,
                    admissible_amount=admissible,
                    deduction=deduction,
                )
            )

        elif (
            rule == "medicines_diagnostics"
            and expenses.medicines_diagnostics > 0
        ):

            allowed_limit = calculate_medicines_limit(
                claim.sum_insured_inr
            )

            admissible, deduction = calculate_deduction(
                expenses.medicines_diagnostics,
                allowed_limit,
            )

            results.append(
                ApplicableLimit(
                    category="Medicines & Diagnostics",
                    limit_description=(
                        "40% of Basic Sum Insured"
                    ),
                    claimed_amount=expenses.medicines_diagnostics,
                    admissible_amount=admissible,
                    deduction=deduction,
                )
            )

        elif rule == "ambulance" and expenses.ambulance > 0:

            allowed_limit = calculate_ambulance_limit(
                claim.sum_insured_inr
            )

            admissible, deduction = calculate_deduction(
                expenses.ambulance,
                allowed_limit,
            )

            results.append(
                ApplicableLimit(
                    category="Ambulance",
                    limit_description=(
                        "1% of Basic Sum Insured or "
                        "INR 1,000, whichever is lower"
                    ),
                    claimed_amount=expenses.ambulance,
                    admissible_amount=admissible,
                    deduction=deduction,
                )
            )

        elif rule == "domiciliary":

            claimed_amount = (
                expenses.room
                + expenses.doctor_fees
                + expenses.medicines_diagnostics
            )

            allowed_limit = calculate_domiciliary_limit(
                claim.sum_insured_inr
            )

            admissible, deduction = calculate_deduction(
                claimed_amount,
                allowed_limit,
            )

            results.append(
                ApplicableLimit(
                    category="Domiciliary Treatment",
                    limit_description=(
                        "20% of Basic Sum Insured"
                    ),
                    claimed_amount=claimed_amount,
                    admissible_amount=admissible,
                    deduction=deduction,
                )
            )

    return results