"""
tests/test_e2e_invalid_flow.py
End-to-end tests for failure handling and edge cases:
1. Invalid profile input fails with VALIDATION_FAILED
2. Document traversal rejected
3. Invalid document extension rejected
"""

import pytest
from saarthi_automation.api import run_automation
from saarthi_automation.errors import AutomationErrorCode


def test_invalid_profile_fails():
    invalid_req = {
        "scheme_id": "demo_income_certificate_scheme",
        "citizen_data": {
            "applicant": {
                "full_name": "",  # missing required
                "date_of_birth": "1992-05-15",
                "gender": "Female",
                "mobile_number": "9000000001"
            },
            "address": {
                "house": "Flat 402",
                "village_city": "Nagpur",
                "district": "Nagpur",
                "state": "Maharashtra",
                "pin_code": "4400"  # invalid 4-digit PIN
            },
            "scheme": {
                "annual_income": -500,
                "occupation": "Self-Employed",
                "category": "OBC"
            }
        },
        "document": {
            "document_type": "Income Certificate",
            "relative_path": "sample_data/documents/sample_income_certificate.pdf"
        }
    }
    result = run_automation(invalid_req)
    assert result["status"] == "VALIDATION_FAILED"
    assert result["review_status"] == "NOT_REACHED"
    assert len(result["errors"]) > 0
    assert result["errors"][0]["code"] == AutomationErrorCode.MISSING_REQUIRED_FIELD


def test_document_outside_approved_dir_fails():
    req = {
        "scheme_id": "demo_income_certificate_scheme",
        "citizen_data": {
            "applicant": {
                "full_name": "Test Citizen One",
                "date_of_birth": "1992-05-15",
                "gender": "Female",
                "mobile_number": "9000000001"
            },
            "address": {
                "house": "Flat 402",
                "village_city": "Nagpur",
                "district": "Nagpur",
                "state": "Maharashtra",
                "pin_code": "440001"
            },
            "scheme": {
                "annual_income": 100000,
                "occupation": "Self-Employed",
                "category": "OBC"
            }
        },
        "document": {
            "document_type": "Income Certificate",
            "relative_path": "../../requirements.txt"  # Directory traversal attempt
        }
    }
    result = run_automation(req)
    assert result["status"] == "VALIDATION_FAILED"
    assert any(err["code"] == AutomationErrorCode.DOCUMENT_OUTSIDE_APPROVED_DIR for err in result["errors"])
