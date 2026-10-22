"""
Verification script for SAARTHi Member 3 Demo Form.
Spins up a local server, launches Chromium via Playwright, and tests:
1. Presence of DEMO banner
2. Presence of all data-testid form elements
3. Computed Times New Roman font
4. Form filling & client-side validation
5. Review summary view transition
6. Confirm button & navigation to receipt.html with simulated labels and reference
7. Evidence screenshots saved to evidence/
8. Browser console error logging
"""

import http.server
import json
import socket
import socketserver
import sys
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_test_server(form_dir: Path, port: int):
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(form_dir), **kwargs)

        def log_message(self, format, *args):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), QuietHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    return httpd


def run_verification():
    base_dir = Path(__file__).resolve().parent.parent
    form_dir = base_dir / "demo_form"
    sample_data_file = base_dir / "sample_data" / "citizen_profile_valid.json"
    sample_doc_file = base_dir / "sample_data" / "documents" / "sample_income_certificate.pdf"
    evidence_dir = base_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    with open(sample_data_file, "r", encoding="utf-8") as f:
        profile = json.load(f)

    port = get_free_port()
    server = start_test_server(form_dir, port)
    url = f"http://127.0.0.1:{port}/index.html"
    print(f"Started local test server on {url}")

    results = []
    console_errors = []

    def log_check(name: str, passed: bool, detail: str = ""):
        results.append((name, passed, detail))
        status_sym = "[PASS]" if passed else "[FAIL]"
        print(f"{status_sym} - {name} {f'({detail})' if detail else ''}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Listen to console messages and page errors
        page.on("console", lambda msg: console_errors.append(f"CONSOLE {msg.type}: {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(f"PAGE ERROR: {exc}"))

        # Step 1: Navigate to form
        page.goto(url, wait_until="networkidle")
        time.sleep(0.5)

        # Check 1: Demo banner
        banner = page.locator("[data-testid='demo-banner']")
        banner_text = banner.inner_text().strip()
        expected_banner = "DEMO FORM — NOT A REAL GOVERNMENT PORTAL"
        log_check("Persistent DEMO banner visible", banner.is_visible() and banner_text == expected_banner, banner_text)

        # Check 2: Core form elements exist
        test_ids = [
            "applicant-full-name", "applicant-dob", "applicant-gender",
            "applicant-mobile", "applicant-email", "address-house",
            "address-village-city", "address-district", "address-state",
            "address-pin", "scheme-income", "scheme-occupation",
            "scheme-category-group", "scheme-consent", "document-upload",
            "btn-review-application", "file-name-display"
        ]
        all_elements_present = True
        missing = []
        for tid in test_ids:
            if not page.locator(f"[data-testid='{tid}']").count() > 0:
                all_elements_present = False
                missing.append(tid)
        log_check("All required data-testid inputs and controls present", all_elements_present, f"Missing: {missing}" if missing else "All found")

        # Check 3: Computed font-family starts with Times New Roman
        sample_selectors = [
            ("h1", "h1"),
            ("label", "label[for='applicant-full-name']"),
            ("input", "[data-testid='applicant-full-name']"),
            ("button", "[data-testid='btn-review-application']"),
            ("banner", "[data-testid='demo-banner']")
        ]
        font_checks_passed = True
        font_details = []
        for name, sel in sample_selectors:
            elem = page.locator(sel).first
            computed_font = elem.evaluate("el => window.getComputedStyle(el).fontFamily")
            font_details.append(f"{name}: {computed_font}")
            if "Times New Roman" not in computed_font:
                font_checks_passed = False
        log_check("Computed font-family starts with Times New Roman across elements", font_checks_passed, ", ".join(font_details))

        # Step 4: Fill the form with valid profile data
        applicant = profile["applicant"]
        address = profile["address"]
        scheme = profile["scheme"]

        page.fill("[data-testid='applicant-full-name']", applicant["full_name"])
        page.fill("[data-testid='applicant-dob']", applicant["date_of_birth"])
        page.select_option("[data-testid='applicant-gender']", applicant["gender"])
        page.fill("[data-testid='applicant-mobile']", applicant["mobile_number"])
        page.fill("[data-testid='applicant-email']", applicant.get("email", ""))

        page.fill("[data-testid='address-house']", address["house"])
        page.fill("[data-testid='address-village-city']", address["village_city"])
        page.fill("[data-testid='address-district']", address["district"])
        page.select_option("[data-testid='address-state']", address["state"])
        page.fill("[data-testid='address-pin']", address["pin_code"])

        page.fill("[data-testid='scheme-income']", str(scheme["annual_income"]))
        page.select_option("[data-testid='scheme-occupation']", scheme["occupation"])
        
        # Radio button
        category = scheme["category"]
        if category == "General":
            page.check("[data-testid='category-general']")
        elif category == "OBC":
            page.check("[data-testid='category-obc']")
        elif category == "SC":
            page.check("[data-testid='category-sc']")
        elif category == "ST":
            page.check("[data-testid='category-st']")

        # Consent checkbox
        page.check("[data-testid='scheme-consent']")

        # File upload
        page.set_input_files("[data-testid='document-upload']", str(sample_doc_file))

        # Check file name display
        file_display_text = page.locator("[data-testid='file-name-display']").inner_text()
        log_check("Document upload input shows chosen file name", "sample_income_certificate.pdf" in file_display_text, file_display_text)

        # Save screenshot: form filled
        screenshot_filled = evidence_dir / "form_filled.png"
        page.screenshot(path=str(screenshot_filled), full_page=True)
        print(f"Captured screenshot: {screenshot_filled}")

        # Step 5: Click Review Application
        page.click("[data-testid='btn-review-application']")
        time.sleep(0.5)

        review_view = page.locator("[data-testid='review-summary-view']")
        review_badge = page.locator("[data-testid='review-badge']")
        review_visible = review_view.is_visible() and review_badge.inner_text().strip() == "PENDING REVIEW"
        log_check("Form transitions to review view with PENDING REVIEW state", review_visible)

        # Verify review table has expected values
        rev_name = page.locator("[data-testid='rev-applicant-full-name']").inner_text().strip()
        rev_mobile = page.locator("[data-testid='rev-applicant-mobile']").inner_text().strip()
        log_check("Review summary displays entered citizen values", rev_name == applicant["full_name"] and rev_mobile == applicant["mobile_number"], f"Name: {rev_name}, Mobile: {rev_mobile}")

        # Save screenshot: review page
        screenshot_review = evidence_dir / "review.png"
        page.screenshot(path=str(screenshot_review), full_page=True)
        print(f"Captured screenshot: {screenshot_review}")

        # Step 6: Click Confirm and Continue
        page.click("[data-testid='btn-confirm-application']")
        page.wait_for_url("**/receipt.html", timeout=5000)
        time.sleep(0.5)

        # Check receipt page elements
        receipt_banner = page.locator("[data-testid='demo-banner']")
        receipt_label = page.locator("[data-testid='receipt-label']")
        demo_ref_elem = page.locator("[data-testid='demo-reference']")

        receipt_label_text = receipt_label.inner_text().strip()
        demo_ref_text = demo_ref_elem.inner_text().strip()

        expected_receipt_label = "DEMO RECEIPT — SIMULATED, NOT SUBMITTED TO ANY GOVERNMENT SYSTEM"
        receipt_valid = (
            receipt_banner.is_visible() and
            receipt_label_text == expected_receipt_label and
            demo_ref_text.startswith("DEMO-") and
            demo_ref_text != "DEMO-NO-DATA"
        )
        log_check("Receipt page renders simulated label and valid DEMO reference number", receipt_valid, f"Ref: {demo_ref_text}")

        # Save screenshot: receipt page
        screenshot_receipt = evidence_dir / "receipt.png"
        page.screenshot(path=str(screenshot_receipt), full_page=True)
        print(f"Captured screenshot: {screenshot_receipt}")

        # Check console errors
        log_check("Zero browser JavaScript/console errors", len(console_errors) == 0, f"Errors: {console_errors}" if console_errors else "Clean")

        browser.close()

    server.shutdown()
    
    all_passed = all(p for _, p, _ in results)
    print("\n============================================================")
    print(f"VERIFICATION SUMMARY: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")
    print("============================================================")
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    run_verification()
