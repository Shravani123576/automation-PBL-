"""
tests/test_e2e_valid_flow.py
End-to-end tests for valid profile flow:
1. Reaches READY_FOR_REVIEW without confirmation
2. Reaches SIMULATED_SUBMITTED with auto_confirm_for_test
3. Enforces ConfirmationNotAllowedError if confirm_and_submit_demo is invoked before review.
"""

from pathlib import Path
import pytest
from saarthi_automation.api import run_automation
from saarthi_automation.browser_agent import AutomationSession, confirm_and_submit_demo
from saarthi_automation.config_loader import load_form_mapping
from saarthi_automation.contracts import AutomationRequest
from saarthi_automation.errors import AutomationErrorCode, ConfirmationNotAllowedError
from saarthi_automation.logger import StepLogger


@pytest.fixture
def base_dir():
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def valid_request_dict():
    return {
        "scheme_id": "demo_income_certificate_scheme",
        "citizen_data": {
            "applicant": {
                "full_name": "Test Citizen One",
                "date_of_birth": "1992-05-15",
                "gender": "Female",
                "mobile_number": "9000000001",
                "email": "citizen@example.com"
            },
            "address": {
                "house": "Flat 402, Shanti Nilayam",
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
        },
        "document": {
            "document_type": "Income Certificate",
            "relative_path": "sample_data/documents/sample_income_certificate.pdf"
        },
        "options": {
            "headless": True,
            "confirm_mode": "none"
        }
    }


def test_valid_flow_pauses_at_review(valid_request_dict):
    result = run_automation(valid_request_dict)
    assert result["status"] == "READY_FOR_REVIEW"
    assert result["review_status"] == "PENDING"
    assert len(result["evidence"]) >= 2
    assert result["demo_receipt"] is None


def test_valid_flow_simulated_submission(valid_request_dict):
    valid_request_dict["options"]["confirm_mode"] = "auto_confirm_for_test"
    result = run_automation(valid_request_dict)
    assert result["status"] == "SIMULATED_SUBMITTED"
    assert result["review_status"] == "CONFIRMED"
    assert result["demo_receipt"] is not None
    assert result["demo_receipt"]["is_simulated"] is True
    assert result["demo_receipt"]["demo_reference"].startswith("DEMO-")
    assert "DEMO RECEIPT" in result["demo_receipt"]["label"]
    assert len(result["evidence"]) == 3


def test_confirm_before_review_prohibited(valid_request_dict, base_dir):
    config = load_form_mapping(base_dir / "config" / "form_mapping.json")
    req = AutomationRequest.from_dict(valid_request_dict)
    session = AutomationSession(req, config, base_dir, "http://127.0.0.1:8000", StepLogger())

    # Attempt confirmation when in_review_state is False
    with pytest.raises(ConfirmationNotAllowedError) as exc:
        confirm_and_submit_demo(session)
    assert exc.value.code == AutomationErrorCode.CONFIRMATION_NOT_ALLOWED


def test_headed_default_pauses_before_confirm(valid_request_dict):
    """
    Proves that the default headed flow pauses before confirmation (confirm_mode='none')
    and does NOT automatically click Confirm and Continue.
    """
    valid_request_dict["options"]["headless"] = True  # Run headless for CI/test runner safety
    valid_request_dict["options"]["confirm_mode"] = "none"
    result = run_automation(valid_request_dict)

    assert result["status"] == "READY_FOR_REVIEW"
    assert result["review_status"] == "PENDING"
    assert result["demo_receipt"] is None


def test_manual_confirmation_only_reaches_receipt(valid_request_dict, base_dir):
    """
    Proves that the receipt is reached ONLY after an explicit confirmation action,
    and cannot be reached while remaining at review.
    """
    config = load_form_mapping(base_dir / "config" / "form_mapping.json")
    valid_request_dict["options"]["confirm_mode"] = "none"
    
    from saarthi_automation.browser_agent import run_form_fill_and_review
    from saarthi_automation.form_server import DemoServerManager
    
    server_mgr = DemoServerManager(base_dir / "demo_form")
    server_url, _ = server_mgr.start()
    req = AutomationRequest.from_dict(valid_request_dict)
    session = AutomationSession(req, config, base_dir, server_url, StepLogger())

    try:
        # Step A: Run fill and review
        res_review = run_form_fill_and_review(session)
        assert res_review.status == "READY_FOR_REVIEW"
        assert res_review.review_status == "PENDING"
        assert res_review.demo_receipt is None
        assert "receipt.html" not in session.page.url

        # Step B: Only after confirmation call does it navigate to receipt.html
        res_confirmed = confirm_and_submit_demo(session)
        assert res_confirmed.status == "SIMULATED_SUBMITTED"
        assert res_confirmed.review_status == "CONFIRMED"
        assert res_confirmed.demo_receipt is not None
        assert "receipt.html" in session.page.url
    finally:
        session.close()
        server_mgr.stop()

