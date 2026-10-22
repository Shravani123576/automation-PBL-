"""
saarthi_automation/browser_agent.py
Core Playwright automation agent for SAARTHi Member 3.
Implements:
1. Field filling driven by form_mapping.json
2. Document upload and attachment confirmation
3. Client review triggering and PENDING REVIEW pause
4. Review value readback validation
5. confirm_and_submit_demo guard (rejects confirm if called before review)
6. Receipt extraction and DEMO / SIMULATED labeling
7. Full screenshot evidence capture and error reporting
"""

from pathlib import Path
import time
from typing import Dict, List, Optional
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from saarthi_automation.config_loader import FormConfig
from saarthi_automation.contracts import (
    AutomationErrorDetail,
    AutomationRequest,
    AutomationResult,
    DemoReceipt,
    DocumentResult,
    ValidationResult,
)
from saarthi_automation.document_checks import (
    get_resolved_document_path,
    validate_document,
)
from saarthi_automation.errors import (
    AutomationError,
    AutomationErrorCode,
    ConfirmationNotAllowedError,
    ReviewMismatchError,
    SelectorNotFoundError,
)
from saarthi_automation.logger import StepLogger
from saarthi_automation.validators import (
    get_nested_value,
    validate_citizen_profile,
)


class AutomationSession:
    """Represents an active or paused browser automation session."""

    def __init__(
        self,
        request: AutomationRequest,
        config: FormConfig,
        base_dir: Path,
        server_url: str,
        logger: StepLogger,
    ):
        self.request = request
        self.config = config
        self.base_dir = base_dir
        self.server_url = server_url
        self.logger = logger

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self.in_review_state: bool = False
        self.evidence_paths: List[str] = []
        self.validation_results: List[ValidationResult] = []
        self.doc_result: Optional[DocumentResult] = None
        self.demo_receipt: Optional[DemoReceipt] = None
        self.errors: List[AutomationErrorDetail] = []

    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.request.options.headless,
            slow_mo=self.request.options.slow_mo_ms,
        )
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def capture_screenshot(self, name_suffix: str) -> str:
        if not self.request.options.screenshots or not self.page:
            return ""
        evidence_dir = self.base_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{self.request.request_id}_{name_suffix}.png"
        path = evidence_dir / filename
        self.page.screenshot(path=str(path), full_page=True)
        path_str = str(path)
        self.evidence_paths.append(path_str)
        return path_str

    def close(self):
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
            self.browser = None
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass
            self.playwright = None


def fill_mapped_field(session: AutomationSession, field_key: str, field_def: dict):
    page = session.page
    data = session.request.citizen_data
    val = get_nested_value(data, field_key)
    selector = field_def.get("selector")
    field_type = field_def.get("type")
    is_required = field_def.get("required", False)

    # Check selector presence
    if field_type != "radio":
        if page.locator(selector).count() == 0:
            raise SelectorNotFoundError(
                AutomationErrorCode.SELECTOR_NOT_FOUND,
                f"Required form selector not found: '{selector}' for canonical field '{field_key}'.",
                field=field_key,
            )

    if field_type == "text" or field_type == "date" or field_type == "number":
        fill_val = str(val) if val is not None else ""
        page.fill(selector, fill_val, timeout=session.request.options.timeout_ms)
        session.logger.log("FIELD_FILLED", f"Filled '{field_key}' with value '{fill_val}'.")

    elif field_type == "select":
        fill_val = str(val) if val is not None else ""
        page.select_option(selector, fill_val, timeout=session.request.options.timeout_ms)
        session.logger.log("FIELD_SELECTED", f"Selected '{fill_val}' for '{field_key}'.")

    elif field_type == "radio":
        options_map = field_def.get("options_mapping", {})
        radio_sel = options_map.get(str(val))
        if not radio_sel or page.locator(radio_sel).count() == 0:
            raise SelectorNotFoundError(
                AutomationErrorCode.SELECTOR_NOT_FOUND,
                f"Radio button option selector not found for value '{val}' in '{field_key}'.",
                field=field_key,
            )
        page.check(radio_sel, timeout=session.request.options.timeout_ms)
        session.logger.log("RADIO_CHECKED", f"Checked radio '{val}' for '{field_key}'.")

    elif field_type == "checkbox":
        # Checkbox for consent: if required, tick it
        page.check(selector, timeout=session.request.options.timeout_ms)
        session.logger.log("CHECKBOX_CHECKED", f"Checked consent box for '{field_key}'.")


def run_form_fill_and_review(session: AutomationSession) -> AutomationResult:
    """
    Executes pre-run validation, browser initialization, field filling,
    file upload, and pauses at READY_FOR_REVIEW.
    """
    logger = session.logger
    req = session.request

    try:
        # Step 1: Pre-run citizen data validation
        logger.log("PRE_VALIDATION", "Validating citizen profile canonical fields...")
        val_results = validate_citizen_profile(req.citizen_data)
        session.validation_results.extend(val_results)
        logger.log("PRE_VALIDATION_PASS", f"Pre-validation passed for {len(val_results)} canonical rules.")

        # Step 2: Validate document security, containment & size
        logger.log("DOCUMENT_CHECK", f"Checking document specification: {req.document.relative_path}")
        doc_result = validate_document(req.document, session.base_dir)
        session.doc_result = doc_result
        logger.log("DOCUMENT_CHECK_PASS", f"Document passed security checks: {doc_result.filename} ({doc_result.size_bytes} bytes).")

        # Step 3: Launch browser & navigate to form
        logger.log("BROWSER_LAUNCH", f"Launching Chromium (headless={req.options.headless})...")
        session.start_browser()
        target_url = f"{session.server_url}/{session.config.form_relative_url}"
        logger.log("NAVIGATE", f"Navigating to {target_url}")
        session.page.goto(target_url, wait_until="networkidle", timeout=req.options.timeout_ms)

        # Step 4: Fill form fields
        for field_key, field_def in session.config.fields.items():
            if field_def.get("type") == "file":
                continue
            fill_mapped_field(session, field_key, field_def)

        # Step 5: Upload document
        resolved_doc_path = get_resolved_document_path(req.document, session.base_dir)
        file_def = session.config.fields.get("document.income_certificate", {})
        file_selector = file_def.get("selector", "[data-testid='document-upload']")
        session.page.set_input_files(file_selector, str(resolved_doc_path))
        logger.log("DOCUMENT_UPLOADED", f"Attached file: {resolved_doc_path.name}")

        # Post-upload check: verify uploaded file name appears
        display_sel = file_def.get("file_display_selector", "[data-testid='file-name-display']")
        display_text = session.page.locator(display_sel).inner_text()
        if resolved_doc_path.name not in display_text:
            raise AutomationError(
                AutomationErrorCode.UPLOAD_FAILED,
                f"Page did not display uploaded document name '{resolved_doc_path.name}'."
            )
        session.logger.log("UPLOAD_VERIFIED", f"File display text verified: {display_text}")

        # Capture evidence: Form Filled
        shot_filled = session.capture_screenshot("01_form_filled")
        logger.log("EVIDENCE_CAPTURED", f"Saved form filled screenshot: {shot_filled}")

        # Step 6: Click Review Application
        review_btn_sel = session.config.buttons.get("review", "[data-testid='btn-review-application']")
        session.page.click(review_btn_sel)
        time.sleep(0.3)

        # Step 7: Verify transition to review state
        review_view_sel = session.config.views.get("review", "[data-testid='review-summary-view']")
        if not session.page.locator(review_view_sel).is_visible():
            raise AutomationError(
                AutomationErrorCode.TIMEOUT,
                "Form failed to transition to the review summary view."
            )

        badge_sel = session.config.views.get("review_badge", "[data-testid='review-badge']")
        badge_text = session.page.locator(badge_sel).inner_text().strip()
        if "PENDING REVIEW" not in badge_text:
            raise AutomationError(
                AutomationErrorCode.REVIEW_MISMATCH,
                f"Review state badge mismatch. Expected 'PENDING REVIEW', got '{badge_text}'."
            )

        # Mark review state as active
        session.in_review_state = True
        logger.log("REVIEW_PAUSE", "Successfully reached citizen review state (PENDING REVIEW).")

        # Step 8: Read back review summary values and compare to input data
        for field_key, field_def in session.config.fields.items():
            rev_sel = field_def.get("review_selector")
            if not rev_sel:
                continue
            if session.page.locator(rev_sel).count() > 0:
                displayed_val = session.page.locator(rev_sel).inner_text().strip()
                expected_val = str(get_nested_value(req.citizen_data, field_key) or "")
                
                # Check match (lenient for formatted numbers / consent strings)
                passed = True
                if field_def.get("type") == "checkbox":
                    passed = "Confirmed" in displayed_val
                elif field_def.get("type") == "file":
                    passed = resolved_doc_path.name in displayed_val
                elif field_def.get("type") == "number":
                    passed = expected_val in displayed_val.replace(",", "")
                else:
                    passed = expected_val.lower() in displayed_val.lower()

                session.validation_results.append(
                    ValidationResult(
                        field=f"review.{field_key}",
                        expected=expected_val,
                        actual=displayed_val,
                        passed=passed,
                        message="Review value readback matched" if passed else "Review value mismatch"
                    )
                )

        # Capture evidence: Review Screen
        shot_review = session.capture_screenshot("02_review")
        logger.log("EVIDENCE_CAPTURED", f"Saved review screenshot: {shot_review}")

        return AutomationResult(
            request_id=req.request_id,
            status="READY_FOR_REVIEW",
            review_status="PENDING",
            validation_results=session.validation_results,
            document_result=session.doc_result,
            evidence=session.evidence_paths,
            step_log=logger.get_entries(),
            errors=session.errors,
        )

    except AutomationError as ae:
        session.errors.append(AutomationErrorDetail(code=ae.code, message=ae.message, field=ae.field))
        validation_error_codes = {
            AutomationErrorCode.MISSING_REQUIRED_FIELD,
            AutomationErrorCode.INVALID_FIELD_VALUE,
            AutomationErrorCode.DOCUMENT_NOT_FOUND,
            AutomationErrorCode.DOCUMENT_OUTSIDE_APPROVED_DIR,
            AutomationErrorCode.DOCUMENT_TYPE_NOT_ALLOWED,
            AutomationErrorCode.DOCUMENT_TOO_LARGE,
        }
        status = "VALIDATION_FAILED" if ae.code in validation_error_codes else "AUTOMATION_FAILED"
        return AutomationResult(
            request_id=req.request_id,
            status=status,
            review_status="NOT_REACHED",
            validation_results=session.validation_results,
            document_result=session.doc_result,
            evidence=session.evidence_paths,
            step_log=logger.get_entries(),
            errors=session.errors,
        )
    except Exception as e:
        session.errors.append(AutomationErrorDetail(code=AutomationErrorCode.BROWSER_ERROR, message=str(e)))
        return AutomationResult(
            request_id=req.request_id,
            status="AUTOMATION_FAILED",
            review_status="NOT_REACHED",
            validation_results=session.validation_results,
            document_result=session.doc_result,
            evidence=session.evidence_paths,
            step_log=logger.get_entries(),
            errors=session.errors,
        )


def confirm_and_submit_demo(session: AutomationSession) -> AutomationResult:
    """
    Submits application ONLY after review has been reached.
    Raises CONFIRMATION_NOT_ALLOWED if called prior to the review step.
    """
    logger = session.logger
    req = session.request

    if not session.in_review_state:
        logger.log("CONFIRM_REJECTED", "Cannot confirm: application is not in READY_FOR_REVIEW state.")
        raise ConfirmationNotAllowedError(
            AutomationErrorCode.CONFIRMATION_NOT_ALLOWED,
            "Confirmation action is prohibited prior to citizen review verification."
        )

    logger.log("CITIZEN_CONFIRMATION", "Citizen confirmation received. Clicking Confirm and Continue...")
    confirm_btn_sel = session.config.buttons.get("confirm", "[data-testid='btn-confirm-application']")
    session.page.click(confirm_btn_sel)
    session.page.wait_for_url("**/receipt.html", timeout=req.options.timeout_ms)
    time.sleep(0.3)

    # Extract demo receipt data
    ref_sel = session.config.receipt.get("reference", "[data-testid='demo-reference']")
    label_sel = session.config.receipt.get("label", "[data-testid='receipt-label']")

    ref_num = session.page.locator(ref_sel).inner_text().strip()
    label_text = session.page.locator(label_sel).inner_text().strip()

    demo_receipt = DemoReceipt(
        demo_reference=ref_num,
        is_simulated=True,
        label=label_text,
    )
    session.demo_receipt = demo_receipt
    logger.log("SIMULATED_RECEIPT", f"Generated simulated receipt with demo reference: {ref_num}")

    # Capture evidence: Receipt
    shot_receipt = session.capture_screenshot("03_receipt")
    logger.log("EVIDENCE_CAPTURED", f"Saved receipt screenshot: {shot_receipt}")

    return AutomationResult(
        request_id=req.request_id,
        status="SIMULATED_SUBMITTED",
        review_status="CONFIRMED",
        validation_results=session.validation_results,
        document_result=session.doc_result,
        demo_receipt=demo_receipt,
        evidence=session.evidence_paths,
        step_log=logger.get_entries(),
        errors=session.errors,
    )


def wait_for_human_review(session: AutomationSession, timeout_ms: int = 0) -> AutomationResult:
    """
    Genuine human review pause.
    Keeps browser open and terminal running until the citizen:
    1. Clicks 'Confirm and Continue' in the browser (navigates to receipt.html)
    2. Clicks 'Edit Application' or 'Cancel Application' in the browser
    3. Closes the browser window
    4. Interrupts via terminal (Ctrl+C)
    """
    logger = session.logger
    req = session.request
    page = session.page

    if not session.in_review_state:
        raise ConfirmationNotAllowedError(
            AutomationErrorCode.CONFIRMATION_NOT_ALLOWED,
            "Cannot wait for human review: session has not reached READY_FOR_REVIEW state."
        )

    logger.log("HUMAN_PAUSE_ACTIVE", "Browser is now paused at the review screen awaiting citizen action...")
    print("\n" + "="*70)
    print(">>> CITIZEN REVIEW IN PROGRESS <<<")
    print("The application has reached READY_FOR_REVIEW.")
    print("Please inspect the application in the open browser window.")
    print(" - Click 'Confirm and Continue' in the browser to complete.")
    print(" - Click 'Edit Application' to return and adjust values.")
    print(" - Click 'Cancel Application' to discard.")
    print("="*70 + "\n")

    start_time = time.time()
    try:
        while True:
            # Check if browser or page was closed by the user
            if not page or page.is_closed():
                logger.log("CITIZEN_DISMISSAL", "Browser window was closed by the citizen without confirming.")
                return AutomationResult(
                    request_id=req.request_id,
                    status="READY_FOR_REVIEW",
                    review_status="CANCELLED",
                    validation_results=session.validation_results,
                    document_result=session.doc_result,
                    evidence=session.evidence_paths,
                    step_log=logger.get_entries(),
                    errors=session.errors,
                )

            current_url = page.url

            # Condition 1: Citizen clicked 'Confirm and Continue' -> navigated to receipt.html
            if "receipt.html" in current_url:
                logger.log("CITIZEN_CONFIRMED", "Citizen clicked 'Confirm and Continue' in browser. Extracting receipt...")
                # Wait briefly for receipt DOM elements to settle
                page.wait_for_selector(session.config.receipt.get("reference", "[data-testid='demo-reference']"))

                ref_sel = session.config.receipt.get("reference", "[data-testid='demo-reference']")
                label_sel = session.config.receipt.get("label", "[data-testid='receipt-label']")

                ref_num = page.locator(ref_sel).inner_text().strip()
                label_text = page.locator(label_sel).inner_text().strip()

                demo_receipt = DemoReceipt(
                    demo_reference=ref_num,
                    is_simulated=True,
                    label=label_text,
                )
                session.demo_receipt = demo_receipt
                shot_receipt = session.capture_screenshot("03_receipt")
                logger.log("SIMULATED_RECEIPT", f"Generated simulated receipt with demo reference: {ref_num}")

                return AutomationResult(
                    request_id=req.request_id,
                    status="SIMULATED_SUBMITTED",
                    review_status="CONFIRMED",
                    validation_results=session.validation_results,
                    document_result=session.doc_result,
                    demo_receipt=demo_receipt,
                    evidence=session.evidence_paths,
                    step_log=logger.get_entries(),
                    errors=session.errors,
                )

            # Condition 2: Citizen clicked 'Edit' or 'Cancel' (returned to form-entry-view)
            entry_view_sel = session.config.views.get("entry", "[data-testid='form-entry-view']")
            review_view_sel = session.config.views.get("review", "[data-testid='review-summary-view']")
            try:
                if page.locator(entry_view_sel).is_visible() and not page.locator(review_view_sel).is_visible():
                    logger.log("CITIZEN_EDIT_OR_CANCEL", "Citizen navigated back to edit or cancel application.")
                    # Keep waiting until citizen re-reviews, confirms, or closes browser
            except Exception:
                pass

            # Optional timeout check if specified (> 0)
            if timeout_ms > 0 and ((time.time() - start_time) * 1000) > timeout_ms:
                logger.log("TIMEOUT", "Human review wait timed out.")
                return AutomationResult(
                    request_id=req.request_id,
                    status="READY_FOR_REVIEW",
                    review_status="PENDING",
                    validation_results=session.validation_results,
                    document_result=session.doc_result,
                    evidence=session.evidence_paths,
                    step_log=logger.get_entries(),
                    errors=session.errors,
                )

            time.sleep(0.3)

    except KeyboardInterrupt:
        logger.log("INTERRUPT", "Human review session interrupted by user from terminal.")
        return AutomationResult(
            request_id=req.request_id,
            status="READY_FOR_REVIEW",
            review_status="INTERRUPTED",
            validation_results=session.validation_results,
            document_result=session.doc_result,
            evidence=session.evidence_paths,
            step_log=logger.get_entries(),
            errors=session.errors,
        )

