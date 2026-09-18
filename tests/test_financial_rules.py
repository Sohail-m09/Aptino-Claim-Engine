from app.rules.financial_rules import (
    calculate_ambulance_limit,
    calculate_deduction,
    calculate_doctor_fee_limit,
    calculate_domiciliary_limit,
    calculate_medicines_limit,
    calculate_room_limit,
)


def test_room_limit():
    result = calculate_room_limit(
        sum_insured=500000,
        admission_hours=96,
    )

    assert result == 20000


def test_doctor_fee_limit():
    result = calculate_doctor_fee_limit(
        sum_insured=500000,
    )

    assert result == 125000


def test_medicines_limit():
    result = calculate_medicines_limit(
        sum_insured=500000,
    )

    assert result == 200000


def test_domiciliary_limit():
    result = calculate_domiciliary_limit(
        sum_insured=500000,
    )

    assert result == 100000


def test_ambulance_limit():
    result = calculate_ambulance_limit(
        sum_insured=500000,
    )

    assert result == 1000


def test_deduction():
    admissible, deduction = calculate_deduction(
        claimed_amount=30000,
        allowed_limit=20000,
    )

    assert admissible == 20000
    assert deduction == 10000