"""
saarthi_automation/validators.py
Pre-run canonical profile validators and post-fill readback validation.
"""

from datetime import date, datetime
import re
from typing import Any, Dict, List, Optional
from saarthi_automation.contracts import ValidationResult
from saarthi_automation.errors import (
    AutomationErrorCode,
    PreRunValidationError,
)


def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """Helper to retrieve dotted paths like 'applicant.full_name'."""
    parts = path.split(".")
    curr = data
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            return None
    return curr


def validate_citizen_profile(citizen_data: Dict[str, Any]) -> List[ValidationResult]:
    """
    Validates canonical fields and formats prior to launching the browser.
    Fails fast with human-readable error messages.
    """
    results: List[ValidationResult] = []

    # 1. Full name
    full_name = get_nested_value(citizen_data, "applicant.full_name")
    if not full_name or not str(full_name).strip():
        raise PreRunValidationError(
            AutomationErrorCode.MISSING_REQUIRED_FIELD,
            "Please enter your full name.",
            field="applicant.full_name"
        )
    results.append(ValidationResult("applicant.full_name", full_name, full_name, True, "Valid full name"))

    # 2. Date of birth
    dob = get_nested_value(citizen_data, "applicant.date_of_birth")
    if not dob:
        raise PreRunValidationError(
            AutomationErrorCode.MISSING_REQUIRED_FIELD,
            "Please enter your date of birth.",
            field="applicant.date_of_birth"
        )
    try:
        parsed_dob = datetime.strptime(str(dob), "%Y-%m-%d").date()
        if parsed_dob > date.today():
            raise PreRunValidationError(
                AutomationErrorCode.INVALID_FIELD_VALUE,
                "Date of birth cannot be in the future.",
                field="applicant.date_of_birth"
            )
    except ValueError:
        raise PreRunValidationError(
            AutomationErrorCode.INVALID_FIELD_VALUE,
            "Date of birth must be in YYYY-MM-DD format.",
            field="applicant.date_of_birth"
        )
    results.append(ValidationResult("applicant.date_of_birth", dob, dob, True, "Valid date of birth"))

    # 3. Mobile number: 10 digits starting with 6-9
    mobile = str(get_nested_value(citizen_data, "applicant.mobile_number") or "").strip()
    if not mobile:
        raise PreRunValidationError(
            AutomationErrorCode.MISSING_REQUIRED_FIELD,
            "Please enter your 10-digit mobile number.",
            field="applicant.mobile_number"
        )
    if not re.match(r"^[6-9]\d{9}$", mobile):
        raise PreRunValidationError(
            AutomationErrorCode.INVALID_FIELD_VALUE,
            "The mobile number must be exactly 10 digits and start with 6, 7, 8, or 9.",
            field="applicant.mobile_number"
        )
    results.append(ValidationResult("applicant.mobile_number", mobile, mobile, True, "Valid 10-digit mobile number"))

    # 4. Gender
    gender = get_nested_value(citizen_data, "applicant.gender")
    if not gender:
        raise PreRunValidationError(
            AutomationErrorCode.MISSING_REQUIRED_FIELD,
            "Please select your gender.",
            field="applicant.gender"
        )
    results.append(ValidationResult("applicant.gender", gender, gender, True, "Valid gender"))

    # 5. Address fields
    house = get_nested_value(citizen_data, "address.house")
    village_city = get_nested_value(citizen_data, "address.village_city")
    district = get_nested_value(citizen_data, "address.district")
    state = get_nested_value(citizen_data, "address.state")
    pin = str(get_nested_value(citizen_data, "address.pin_code") or "").strip()

    if not house:
        raise PreRunValidationError(AutomationErrorCode.MISSING_REQUIRED_FIELD, "Please enter house or street address.", "address.house")
    if not village_city:
        raise PreRunValidationError(AutomationErrorCode.MISSING_REQUIRED_FIELD, "Please enter village or city.", "address.village_city")
    if not district:
        raise PreRunValidationError(AutomationErrorCode.MISSING_REQUIRED_FIELD, "Please enter district name.", "address.district")
    if not state:
        raise PreRunValidationError(AutomationErrorCode.MISSING_REQUIRED_FIELD, "Please select your state.", "address.state")
    if not pin:
        raise PreRunValidationError(AutomationErrorCode.MISSING_REQUIRED_FIELD, "Please enter your 6-digit PIN code.", "address.pin_code")
    if not re.match(r"^\d{6}$", pin):
        raise PreRunValidationError(
            AutomationErrorCode.INVALID_FIELD_VALUE,
            "The PIN code must be exactly 6 digits.",
            field="address.pin_code"
        )
    results.append(ValidationResult("address.pin_code", pin, pin, True, "Valid 6-digit PIN"))

    # 6. Scheme Income
    income = get_nested_value(citizen_data, "scheme.annual_income")
    if income is None:
        raise PreRunValidationError(AutomationErrorCode.MISSING_REQUIRED_FIELD, "Please enter annual family income.", "scheme.annual_income")
    try:
        income_val = float(income)
        if income_val < 0:
            raise PreRunValidationError(
                AutomationErrorCode.INVALID_FIELD_VALUE,
                "Annual family income must be a non-negative number.",
                field="scheme.annual_income"
            )
    except (ValueError, TypeError):
        raise PreRunValidationError(
            AutomationErrorCode.INVALID_FIELD_VALUE,
            "Annual family income must be a valid number.",
            field="scheme.annual_income"
        )
    results.append(ValidationResult("scheme.annual_income", income, income, True, "Valid non-negative income"))

    # 7. Category & Occupation
    category = get_nested_value(citizen_data, "scheme.category")
    if not category:
        raise PreRunValidationError(AutomationErrorCode.MISSING_REQUIRED_FIELD, "Please select social category.", "scheme.category")
    occupation = get_nested_value(citizen_data, "scheme.occupation")
    if not occupation:
        raise PreRunValidationError(AutomationErrorCode.MISSING_REQUIRED_FIELD, "Please select occupation.", "scheme.occupation")

    return results
