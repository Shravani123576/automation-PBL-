"""
saarthi_automation/api.py
Public entry point for SAARTHi Browser Automation module.
Future modules (FastAPI, backend runners, orchestrator) invoke run_automation(request: dict) -> dict.
"""

from pathlib import Path
from typing import Any, Dict

from saarthi_automation.browser_agent import (
    AutomationSession,
    confirm_and_submit_demo,
    run_form_fill_and_review,
    wait_for_human_review,
)
from saarthi_automation.config_loader import load_form_mapping
from saarthi_automation.contracts import AutomationRequest, AutomationResult
from saarthi_automation.form_server import DemoServerManager
from saarthi_automation.logger import StepLogger


def run_automation(request_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the automation flow from a request dictionary and returns a JSON-serializable dictionary.
    """
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "form_mapping.json"
    demo_form_dir = base_dir / "demo_form"

    config = load_form_mapping(config_path)
    request = AutomationRequest.from_dict(request_dict)
    logger = StepLogger()

    server_mgr = DemoServerManager(demo_form_dir)
    server_url, _ = server_mgr.start()
    session = AutomationSession(request, config, base_dir, server_url, logger)

    try:
        # Step 1: Pre-validation, form fill, upload, and pause at review
        result: AutomationResult = run_form_fill_and_review(session)

        # Step 2: Handle confirmation modes
        if result.status == "READY_FOR_REVIEW":
            if request.options.confirm_mode == "auto_confirm_for_test":
                result = confirm_and_submit_demo(session)
            elif request.options.confirm_mode == "interactive_human":
                result = wait_for_human_review(session, timeout_ms=request.options.timeout_ms)

        return result.to_dict()

    finally:
        session.close()
        server_mgr.stop()
