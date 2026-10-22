"""
scripts/run_live_interactive.py
Launches Playwright in a VISIBLE (headed) browser window with slow motion (slow_mo=800ms).
Fills the form, attaches the sample document, clicks 'Review Application', and pauses
at the 'READY_FOR_REVIEW' screen so you can observe live testing and interact with it.
"""

from pathlib import Path
import sys
import time

# Ensure project root is in python path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from saarthi_automation.api import run_automation


def main():
    print("\n" + "="*70)
    print("SAARTHi MEMBER 3 — LIVE HEADED BROWSER TESTING")
    print("="*70)
    print("1. Opening a real Chromium browser window (Headed mode)...")
    print("2. Filling form fields with 800ms slow-motion delay...")
    print("3. Attaching test document...")
    print("4. Transitioning to 'PENDING REVIEW' screen...")
    print("5. Pausing so you can inspect the live page!")
    print("="*70 + "\n")

    request_payload = {
        "scheme_id": "demo_income_certificate_scheme",
        "citizen_data": {
            "applicant": {
                "full_name": "Test Citizen One",
                "date_of_birth": "1992-05-15",
                "gender": "Female",
                "mobile_number": "9000000001",
                "email": "citizen.one@example.com"
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
            "headless": False,       # VISIBLE BROWSER WINDOW
            "slow_mo_ms": 600,        # 600ms delay per interaction so you can watch
            "timeout_ms": 30000,
            "screenshots": True,
            "confirm_mode": "auto_confirm_for_test"  # Proceeds to show full simulated receipt
        }
    }

    result = run_automation(request_payload)

    print("\n" + "="*70)
    print("LIVE TESTING RESULT:")
    print("="*70)
    print(f"Status           : {result['status']}")
    print(f"Review Status    : {result['review_status']}")
    if result.get("demo_receipt"):
        print(f"Demo Reference   : {result['demo_receipt']['demo_reference']}")
        print(f"Receipt Label    : {result['demo_receipt']['label']}")
    print("Screenshots taken:")
    for shot in result.get("evidence", []):
        print(f"  - {shot}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
