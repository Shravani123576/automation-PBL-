"""
scripts/run_visual_browser_review.py
Launches a real Chromium browser window (Headed), navigates to the demo form,
fills in all dummy citizen data with a realistic visual typing delay, attaches
the sample income certificate, clicks 'Review Application', and KEEPS the browser
window open at the 'PENDING REVIEW' screen for 120 seconds so you can see it live!
"""

from pathlib import Path
import sys
import time
from playwright.sync_api import sync_playwright

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from saarthi_automation.form_server import DemoServerManager


def run_visual_review():
    demo_form_dir = base_dir / "demo_form"
    sample_doc_file = base_dir / "sample_data" / "documents" / "sample_income_certificate.pdf"

    # Start the local demo server on a free port
    server_mgr = DemoServerManager(demo_form_dir)
    server_url, port = server_mgr.start()
    form_url = f"{server_url}/index.html"

    print("\n" + "="*70)
    print("SAARTHi MEMBER 3 — LIVE VISUAL AUTOFILL & REVIEW")
    print("="*70)
    print(f"Opening live Chromium browser on: {form_url}")
    print("Watch the browser window open on your screen!")
    print("="*70 + "\n")

    with sync_playwright() as p:
        # Launch real, visible Chromium browser window
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500,  # 500ms delay per interaction so you can watch everything typing
            args=["--start-maximized"]
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        # Step 1: Open the local demo website
        print(">> Opening website...")
        page.goto(form_url)
        time.sleep(1)

        # Step 2: Fill Applicant Details with dummy data
        print(">> Autofilling 1. Applicant Details...")
        page.fill("[data-testid='applicant-full-name']", "Test Citizen One")
        page.fill("[data-testid='applicant-dob']", "1992-05-15")
        page.select_option("[data-testid='applicant-gender']", "Female")
        page.fill("[data-testid='applicant-mobile']", "9000000001")
        page.fill("[data-testid='applicant-email']", "citizen.test@example.com")

        # Step 3: Fill Address Details
        print(">> Autofilling 2. Residential Address...")
        page.fill("[data-testid='address-house']", "Flat 402, Shanti Nilayam")
        page.fill("[data-testid='address-village-city']", "Nagpur")
        page.fill("[data-testid='address-district']", "Nagpur")
        page.select_option("[data-testid='address-state']", "Maharashtra")
        page.fill("[data-testid='address-pin']", "440001")

        # Step 4: Fill Scheme Details
        print(">> Autofilling 3. Scheme Details...")
        page.fill("[data-testid='scheme-income']", "120000")
        page.select_option("[data-testid='scheme-occupation']", "Self-Employed")
        page.check("[data-testid='category-obc']")
        page.check("[data-testid='scheme-consent']")

        # Step 5: Upload Document
        print(">> Attaching verified sample document...")
        page.set_input_files("[data-testid='document-upload']", str(sample_doc_file))
        time.sleep(1)

        # Step 6: Click Review Application
        print(">> Clicking 'Review Application' button...")
        page.click("[data-testid='btn-review-application']")
        time.sleep(1)

        # Capture evidence
        evidence_dir = base_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        live_shot = evidence_dir / "live_pending_review.png"
        page.screenshot(path=str(live_shot))
        print(f">> Screenshot captured at: {live_shot}")

        print("\n" + "="*70)
        print("STATUS: PENDING REVIEW (STOPPED FOR CITIZEN REVIEW)")
        print("The browser window will remain open on your screen for 2 minutes!")
        print("You can see all autofilled values and test the 'Edit' or 'Confirm' buttons.")
        print("="*70 + "\n")

        # Keep browser open for 120 seconds so user can see and interact with it
        for remaining in range(120, 0, -10):
            print(f"Browser remains open for citizen review... ({remaining}s remaining)")
            time.sleep(10)

        browser.close()

    server_mgr.stop()
    print("Demo session finished cleanly.")


if __name__ == "__main__":
    run_visual_review()
