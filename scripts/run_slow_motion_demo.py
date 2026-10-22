"""
scripts/run_slow_motion_demo.py
Demonstration script with slow typing and interaction speed (1500ms delay per action)
using Playwright in a visible (headed) Google Chrome / Chromium browser.

Workflow:
1. Opens the local demo portal.
2. Slowly types and fills every field with clear visual delays so you can see each keystroke.
3. Attaches the sample income certificate.
4. Pauses visibly, then clicks 'Review Application'.
5. Displays 'PENDING REVIEW'.
6. Pauses for 5 seconds on the review table so you can inspect all values.
7. Clicks 'Confirm and Continue'.
8. Navigates to the simulated receipt page displaying 'DEMO RECEIPT — SIMULATED' and the reference number.
9. Keeps the receipt open on your screen for 20 seconds so you can examine the final simulated output!
"""

from pathlib import Path
import sys
import time
from playwright.sync_api import sync_playwright

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from saarthi_automation.form_server import DemoServerManager


def run_slow_demo():
    demo_form_dir = base_dir / "demo_form"
    sample_doc_file = base_dir / "sample_data" / "documents" / "sample_income_certificate.pdf"

    server_mgr = DemoServerManager(demo_form_dir)
    server_url, port = server_mgr.start()
    form_url = f"{server_url}/index.html"

    print("\n" + "="*70)
    print("SAARTHi MEMBER 3 — SLOW-MOTION LIVE AUTOMATION & CONFIRMATION")
    print("="*70)
    print("Launching visible browser with slow-motion typing (1500ms per step)...")
    print(f"Portal: {form_url}")
    print("="*70 + "\n")

    with sync_playwright() as p:
        # Launch browser with 1500ms slow_mo per action
        browser = None
        try:
            browser = p.chromium.launch(
                channel="chrome",
                headless=False,
                slow_mo=1200,   # Generous 1.2s delay per interaction
                args=["--start-maximized"]
            )
            print(">> Launched installed Google Chrome!")
        except Exception:
            browser = p.chromium.launch(
                headless=False,
                slow_mo=1200,
                args=["--start-maximized"]
            )
            print(">> Launched Chromium!")

        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        # Step 1: Open demo form
        print(">> [Step 1/7] Opening Demo Application Form...")
        page.goto(form_url)
        time.sleep(2)

        # Step 2: Fill Applicant Details slowly
        print(">> [Step 2/7] Typing Applicant Details...")
        page.click("[data-testid='applicant-full-name']")
        page.type("[data-testid='applicant-full-name']", "Test Citizen One", delay=60)
        time.sleep(1)

        page.fill("[data-testid='applicant-dob']", "1992-05-15")
        time.sleep(1)

        page.select_option("[data-testid='applicant-gender']", "Female")
        time.sleep(1)

        page.click("[data-testid='applicant-mobile']")
        page.type("[data-testid='applicant-mobile']", "9000000001", delay=80)
        time.sleep(1)

        page.click("[data-testid='applicant-email']")
        page.type("[data-testid='applicant-email']", "citizen.test@example.com", delay=50)
        time.sleep(1)

        # Step 3: Fill Address Details slowly
        print(">> [Step 3/7] Typing Residential Address...")
        page.click("[data-testid='address-house']")
        page.type("[data-testid='address-house']", "Flat 402, Shanti Nilayam", delay=50)
        time.sleep(1)

        page.click("[data-testid='address-village-city']")
        page.type("[data-testid='address-village-city']", "Nagpur", delay=60)
        time.sleep(1)

        page.click("[data-testid='address-district']")
        page.type("[data-testid='address-district']", "Nagpur", delay=60)
        time.sleep(1)

        page.select_option("[data-testid='address-state']", "Maharashtra")
        time.sleep(1)

        page.click("[data-testid='address-pin']")
        page.type("[data-testid='address-pin']", "440001", delay=80)
        time.sleep(1)

        # Step 4: Fill Scheme Details slowly
        print(">> [Step 4/7] Filling Scheme Details & Consent...")
        page.click("[data-testid='scheme-income']")
        page.type("[data-testid='scheme-income']", "120000", delay=80)
        time.sleep(1)

        page.select_option("[data-testid='scheme-occupation']", "Self-Employed")
        time.sleep(1)

        page.check("[data-testid='category-obc']")
        time.sleep(1)

        page.check("[data-testid='scheme-consent']")
        time.sleep(1.5)

        # Step 5: Upload Document
        print(">> [Step 5/7] Uploading Income Certificate...")
        page.set_input_files("[data-testid='document-upload']", str(sample_doc_file))
        time.sleep(2)

        # Step 6: Click Review Application
        print(">> [Step 6/7] Clicking 'Review Application' button...")
        page.click("[data-testid='btn-review-application']")
        page.wait_for_selector("[data-testid='review-summary-view']")
        print(">> Portal is now at PENDING REVIEW state!")
        
        # Pause at the review screen so you can inspect everything
        print(">> Pausing at Review Table for 6 seconds so you can see all reviewed values...")
        time.sleep(6)

        # Step 7: Click Confirm and Continue
        print(">> [Step 7/7] Clicking 'Confirm and Continue' now...")
        page.click("[data-testid='btn-confirm-application']")
        page.wait_for_url("**/receipt.html")
        time.sleep(1)

        # Extract receipt details
        ref_num = page.locator("[data-testid='demo-reference']").inner_text().strip()
        label_text = page.locator("[data-testid='receipt-label']").inner_text().strip()

        # Capture evidence
        evidence_dir = base_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        rcpt_shot = evidence_dir / "slow_motion_receipt.png"
        page.screenshot(path=str(rcpt_shot))

        print("\n" + "="*70)
        print("SIMULATED RECEIPT REACHED!")
        print(f"Receipt Label  : {label_text}")
        print(f"Demo Reference : {ref_num}")
        print(f"Evidence Saved : {rcpt_shot}")
        print("="*70)
        print(">> The browser window with your DEMO RECEIPT is now OPEN on your screen.")
        print(">> It will NOT close automatically. Take your time to review it!")
        try:
            input(">> Press [ENTER] in this terminal when you are ready to close the browser: ")
        except (KeyboardInterrupt, EOFError):
            pass

        browser.close()

    server_mgr.stop()
    print("Slow-motion demonstration finished cleanly.")


if __name__ == "__main__":
    run_slow_demo()
