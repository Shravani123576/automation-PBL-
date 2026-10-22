"""
tests/test_validators.py
Unit tests for pre-run profile validators and field format rules.
"""

import pytest
from saarthi_automation.errors import AutomationErrorCode, PreRunValidationError
from saarthi_automation.validators import validate_citizen_profile


@pytest.fixture
def valid_profile():
    return {
        "applicant": {
            "full_name": "Test Citizen One",
            "date_of_birth": "1992-05-15",
            "gender": "Female",
            "mobile_number": "9000000001",
            "email": "test@example.com"
        },
        "address": {
            "house": "Flat 402",
            "village_city": "Nagpur",
            "district": "Nagpur",
            "state": "Maharashtra",
            "pin_code": "440001"
        },
        "scheme": {
            "annual_income": 120000,
            "occupation": "Self-Employed",
            "category": "OBC"
        }
    }


def test_validate_valid_profile(valid_profile):
    results = validate_citizen_profile(valid_profile)
    assert len(results) >= 6
    assert all(r.passed for r in results)


def test_missing_full_name(valid_profile):
    valid_profile["applicant"]["full_name"] = ""
    with pytest.raises(PreRunValidationError) as exc:
        validate_citizen_profile(valid_profile)
    assert exc.value.code == AutomationErrorCode.MISSING_REQUIRED_FIELD
    assert exc.value.field == "applicant.full_name"


def test_invalid_mobile_digit_count(valid_profile):
    valid_profile["applicant"]["mobile_number"] = "90000001"  # 8 digits
    with pytest.raises(PreRunValidationError) as exc:
        validate_citizen_profile(valid_profile)
    assert exc.value.code == AutomationErrorCode.INVALID_FIELD_VALUE
    assert exc.value.field == "applicant.mobile_number"


def test_invalid_mobile_prefix(valid_profile):
    valid_profile["applicant"]["mobile_number"] = "2000000001"  # Starts with 2
    with pytest.raises(PreRunValidationError) as exc:
        validate_citizen_profile(valid_profile)
    assert exc.value.code == AutomationErrorCode.INVALID_FIELD_VALUE


def test_invalid_pin_code(valid_profile):
    valid_profile["address"]["pin_code"] = "4400"  # 4 digits
    with pytest.raises(PreRunValidationError) as exc:
        validate_citizen_profile(valid_profile)
    assert exc.value.code == AutomationErrorCode.INVALID_FIELD_VALUE
    assert exc.value.field == "address.pin_code"


def test_negative_income(valid_profile):
    valid_profile["scheme"]["annual_income"] = -100
    with pytest.raises(PreRunValidationError) as exc:
        validate_citizen_profile(valid_profile)
    assert exc.value.code == AutomationErrorCode.INVALID_FIELD_VALUE
    assert exc.value.field == "scheme.annual_income"


def test_future_dob(valid_profile):
    valid_profile["applicant"]["date_of_birth"] = "2099-01-01"
    with pytest.raises(PreRunValidationError) as exc:
        validate_citizen_profile(valid_profile)
    assert exc.value.code == AutomationErrorCode.INVALID_FIELD_VALUE
    assert exc.value.field == "applicant.date_of_birth"
