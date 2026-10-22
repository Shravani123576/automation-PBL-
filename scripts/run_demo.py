"""
scripts/run_demo.py
CLI entry point for running the SAARTHi Browser Automation module.
Supports:
  --profile <path_to_json>
  --headless / --headed
  --auto-confirm (test mode only)
  --json (outputs raw JSON result)
"""

import argparse
import json
from pathlib import Path
import sys

# Ensure module path is accessible
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from saarthi_automation.api import run_automation


def main():
    parser = argparse.ArgumentParser(description="SAARTHi Browser Automation Prototype Runner")
    parser.add_argument("--profile", required=True, help="Path to citizen profile JSON file")
    parser.add_argument("--document", default="sample_data/documents/sample_income_certificate.pdf", help="Relative path to test document")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode (default)")
    parser.add_argument("--headed", dest="headless", action="store_false", help="Run browser in visible headed mode for citizen inspection")
    parser.add_argument("--auto-confirm", action="store_true", help="Simulate explicit citizen confirmation (automated test mode only)")
    parser.add_argument("--slow-mo", type=int, default=0, help="Slow down browser operations by specified milliseconds")
    parser.add_argument("--json", dest="output_json", action="store_true", help="Print result as raw JSON")

    args = parser.parse_args()

    profile_path = Path(args.profile)
    if not profile_path.is_absolute():
        profile_path = base_dir / profile_path

    if not profile_path.exists():
        print(f"Error: Profile file not found at {profile_path}")
        sys.exit(1)

    with open(profile_path, "r", encoding="utf-8") as f:
        citizen_data = json.load(f)

    # Confirmation mode determination:
    # 1. If explicit --auto-confirm is provided: auto_confirm_for_test (automated testing only)
    # 2. If headed mode: interactive_human (keeps browser open and waits for citizen action)
    # 3. If headless without auto-confirm: none (pauses and returns READY_FOR_REVIEW)
    if args.auto_confirm:
        confirm_mode = "auto_confirm_for_test"
    elif not args.headless:
        confirm_mode = "interactive_human"
    else:
        confirm_mode = "none"

    request_payload = {
        "scheme_id": "demo_income_certificate_scheme",
        "citizen_data": citizen_data,
        "document": {
            "document_type": "Income Certificate",
            "relative_path": args.document
        },
        "options": {
            "headless": args.headless,
            "slow_mo_ms": args.slow_mo,
            "timeout_ms": 0 if not args.headless else 10000,
            "screenshots": True,
            "confirm_mode": confirm_mode
        }
    }

    result = run_automation(request_payload)

    if args.output_json:
        print(json.dumps(result, indent=2))
        return

    print("\n" + "="*60)
    print("SAARTHi BROWSER AUTOMATION EXECUTION SUMMARY")
    print("="*60)
    print(f"Request ID       : {result['request_id']}")
    print(f"Status           : {result['status']}")
    print(f"Review Status    : {result['review_status']}")
    
    if result.get("demo_receipt"):
        rcpt = result["demo_receipt"]
        print(f"Demo Reference   : {rcpt['demo_reference']}")
        print(f"Receipt Label    : {rcpt['label']}")
        print(f"Is Simulated     : {rcpt['is_simulated']}")
    
    if result.get("errors"):
        print("\nERRORS ENCOUNTERED:")
        for err in result["errors"]:
            print(f" - [{err['code']}] {err['message']}" + (f" (Field: {err.get('field')})" if err.get('field') else ""))

    passed_val = sum(1 for v in result.get("validation_results", []) if v["passed"])
    total_val = len(result.get("validation_results", []))
    print(f"\nValidation Checks: {passed_val}/{total_val} passed")

    if result.get("evidence"):
        print("\nEvidence Screenshots:")
        for ev in result["evidence"]:
            print(f" - {ev}")

    print("="*60 + "\n")


if __name__ == "__main__":
    main()
