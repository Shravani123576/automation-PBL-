# SAARTHi Member 3 — Architecture & System Design

## 1. Overview
The **Browser Automation module (Member 3)** acts as the robotic execution layer of the SAARTHi citizen assistant. It isolates complex browser interactions, web form filling, and evidence capture behind clean data interfaces.

```
+-------------------------------------------------------------------------------+
|                             SAARTHi Ecosystem                                 |
+-------------------------------------------------------------------------------+
|  Member 1: Citizen Profile & Eligibility Check                                |
|  Member 2: Document Readiness Verification                                    |
|                                                                               |
|                                    v                                          |
|  Member 3 (This Module): Browser Automation                                   |
|   +-----------------------------------------------------------------------+   |
|   | 1. Request Ingestion & Pre-Run Validation (validators.py)            |   |
|   | 2. Document Security & Directory Containment (document_checks.py)      |   |
|   | 3. Ephemeral Local Server Manager (form_server.py)                    |   |
|   | 4. Form Selector Mapping (config/form_mapping.json)                   |   |
|   | 5. Playwright Sync Automation Driver (browser_agent.py)               |   |
|   | 6. Citizen Review Pause & Confirmation Guard                          |   |
|   | 7. Evidence & Simulated Receipt Generation                            |   |
|   +-----------------------------------------------------------------------+   |
|                                    v                                          |
|  Member 4: Web Frontend & Citizen Interaction                                 |
+-------------------------------------------------------------------------------+
```

---

## 2. Component Structure

- **`saarthi_automation/api.py`**: Public interface exposing `run_automation(request: dict) -> dict`.
- **`saarthi_automation/validators.py`**: Validates citizen profile data formats before launching any browser.
- **`saarthi_automation/document_checks.py`**: Sandboxes document paths within `sample_data/documents/`, checks file size (<= 2MB), and verifies allowed file extensions (`.pdf`, `.jpg`, `.jpeg`, `.png`).
- **`saarthi_automation/form_server.py`**: Automatically spins up and tears down an ephemeral Python `http.server` on an open localhost port.
- **`saarthi_automation/browser_agent.py`**: Manages the Playwright lifecycle, fills forms, verifies attachments, pauses at `READY_FOR_REVIEW`, and blocks confirmation if review has not occurred.
- **`saarthi_automation/errors.py`**: Centralized domain error codes and exceptions.
- **`saarthi_automation/contracts.py`**: Typed dataclasses and serializers for requests, results, errors, receipts, and step logs.
- **`config/form_mapping.json`**: Decouples HTML selectors from automation code.
