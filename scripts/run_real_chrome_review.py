"""
scripts/run_real_chrome_review.py
Launches Google Chrome installed on your system via Playwright's channel="chrome" option.
Fills the form with visible typing delay, uploads the dummy document, clicks Review,
and keeps your real Google Chrome browser open on your screen!
"""

from pathlib import Path
import sys
import time
from playwright.sync_api import sync_playwright

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from saarthi_automation.form_server import DemoServerManager


def run_in_real_chrome():
    demo_form_dir = base_dir / "demo_form"
    sample_doc_file = base_dir / "sample_data" / "documents" / "sample_income_certificate.pdf"

    server_mgr = DemoServerManager(demo_form_dir)
    server_url, port = server_mgr.start()
    form_url = f"{server_url}/index.html"

    print("\n" + "="*70)
    print("LAUNCHING REAL GOOGLE CHROME VIA PLAYWRIGHT")
    print("="*70)
    print(f"URL: {form_url}")
    print("Opening Google Chrome window on your screen now...")
    print("="*70 + "\n")

    with sync_playwright() as p:
        # Launch using the installed Google Chrome browser on Windows
        try:
            browser = p.chromium.launch(
                channel="chrome",     # Uses installed Google Chrome!
                headless=False,
                slow_mo=600,
                args=["--start-maximized"]
            )
            print(">> Successfully launched installed Google Chrome!")
        except Exception as e:
            print(f">> Could not launch channel='chrome' ({e}), falling back to standard Chromium...")
            browser = p.chromium.launch(
                headless=False,
                slow_mo=600,
                args=["--start-maximized"]
            )

        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        # 1. Open Website
        print(">> Chrome: Navigating to local demo portal...")
        page.goto(form_url)
        time.sleep(1)

        # 2. Autofill Applicant Details
        print(">> Chrome: Typing Applicant Details...")
        page.fill("[data-testid='applicant-full-name']", "Test Citizen One")
        page.fill("[data-testid='applicant-dob']", "1992-05-15")
        page.select_option("[data-testid='applicant-gender']", "Female")
        page.fill("[data-testid='applicant-mobile']", "9000000001")
        page.fill("[data-testid='applicant-email']", "citizen.one@example.com")

        # 3. Autofill Address
        print(">> Chrome: Typing Residential Address...")
        page.fill("[data-testid='address-house']", "Flat 402, Shanti Nilayam")
        page.fill("[data-testid='address-village-city']", "Nagpur")
        page.fill("[data-testid='address-district']", "Nagpur")
        page.select_option("[data-testid='address-state']", "Maharashtra")
        page.fill("[data-testid='address-pin']", "440001")

        # 4. Autofill Scheme
        print(">> Chrome: Filling Scheme Details...")
        page.fill("[data-testid='scheme-income']", "120000")
        page.select_option("[data-testid='scheme-occupation']", "Self-Employed")
        page.check("[data-testid='category-obc']")
        page.check("[data-testid='scheme-consent']")

        # 5. Upload Document
        print(">> Chrome: Attaching Sample Income Certificate...")
        page.set_input_files("[data-testid='document-upload']", str(sample_doc_file))
        time.sleep(1)

        # 6. Click Review
        print(">> Chrome: Clicking 'Review Application'...")
        page.click("[data-testid='btn-review-application']")
        time.sleep(1)

        # Evidence
        evidence_dir = base_dir / "evidence"
        shot_path = evidence_dir / "chrome_pending_review.png"
        page.screenshot(path=str(shot_path))
        print(f">> Screenshot saved to: {shot_path}")

        print("\n" + "="*70)
        print("CHROME IS CURRENTLY OPEN IN 'PENDING REVIEW' MODE ON YOUR SCREEN!")
        print("Window will stay open for 3 minutes for you to inspect & interact.")
        print("="*70 + "\n")

        for remaining in range(180, 0, -15):
            print(f"Google Chrome open on screen... ({remaining}s remaining)")
            time.sleep(15)

        browser.close()

    server_mgr.stop()
    print("Chrome automation completed.")


if __name__ == "__main__":
    run_in_real_chrome()
