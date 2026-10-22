# SAARTHi Browser Automation Module (Member 3 Prototype)

> [!IMPORTANT]
> **DEMO / SIMULATED DISCLAIMER**:  
> This project is a local standalone prototype for SAARTHi (Member 3 - Browser Automation). It automates **ONLY** the local demonstration application form served from this project on `127.0.0.1`. It **NEVER** interacts with or submits data to any real government portal. All data and documents are simulated dummy test fixtures.

---

## 1. Project Purpose & Scope

SAARTHi assists citizens in discovering government schemes, validating eligibility, checking document readiness, and completing application forms.

This module (Member 3) automates form filling on a local test target:
1. Loads canonical citizen profile data.
2. Validates formats pre-run (fail-fast validation).
3. Enforces document security (directory containment, file extension, max 2 MB).
4. Fills mapped form fields and uploads approved sample test documents.
5. Performs post-fill and read-back validation.
6. **Pauses for citizen review** (`READY_FOR_REVIEW`).
7. Only proceeds to final simulated receipt generation after explicit citizen confirmation (`SIMULATED_SUBMITTED`).

---

## 2. Directory Layout

```text
saarthi_member3_automation/
  README.md                           # Documentation & quickstart
  requirements.txt                    # Pinned Python dependencies (playwright, pytest)
  .gitignore                          # Git ignore rules
  config/
    form_mapping.json                 # Selector & field mapping configuration
  demo_form/                          # Local civic application form (HTML/CSS/JS)
    index.html                        # Application form with applicant, address, scheme, upload, and review
    receipt.html                      # Simulated completion receipt with DEMO reference
    styles.css                        # Universal Times New Roman font & civic portal palette
    app.js                            # Client-side validation, review summary, and confirmation logic
  sample_data/
    citizen_profile_valid.json        # Canonical valid test profile
    citizen_profile_invalid.json      # Invalid test profile for failure testing
    documents/
      sample_income_certificate.pdf   # Minimal safe dummy test PDF
  saarthi_automation/                 # Core automation engine
    __init__.py                       # Package initializer
    api.py                            # Public entry point `run_automation(request: dict) -> dict`
    browser_agent.py                  # Playwright sync agent & confirmation guard
    config_loader.py                  # Form mapping config loader
    contracts.py                      # Integration data contracts & dataclasses
    document_checks.py                # Security, traversal guard, and size bounds
    errors.py                         # Standardized domain error codes
    form_server.py                    # Ephemeral background server manager
    logger.py                         # Timestamped step logger
    validators.py                     # Canonical field validators & readback comparison
  scripts/
    generate_sample_document.py       # Generates safe dummy test PDF
    serve_demo.py                     # Standalone localhost demo server
    verify_demo_form.py               # DOM & CSS verification smoke test
    run_demo.py                       # CLI execution runner
  docs/                               # Technical documentation
    integration_contract.md           # Input/output schema and examples
    architecture.md                   # System architecture and workflow diagram
    test_report.md                    # Pytest test execution results
  tests/                              # Automated test suites
    test_config_loader.py             # Config parser tests
    test_document_checks.py           # Document security & traversal tests
    test_validators.py                # Pre-run format validator tests
    test_e2e_valid_flow.py            # End-to-end valid flow tests
    test_e2e_invalid_flow.py          # End-to-end failure handling tests
  evidence/                           # Automated screenshots & artifacts (gitignored)
  logs/                               # Execution logs (gitignored)
```

---

## 3. Environment Setup

### Prerequisites
- Python 3.10 or higher.
- Operating System: Windows, macOS, or Linux.

### Setup Commands

#### Windows (PowerShell)
```powershell
# Navigate into the project folder
cd saarthi_member3_automation

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install pinned dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

#### macOS / Linux (Bash)
```bash
# Navigate into the project folder
cd saarthi_member3_automation

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install pinned dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

---

## 4. Run Commands

### 1. Default Flow: Pause at Citizen Review (Default Behavior)
Fills the form, uploads the test document, verifies read-back values, and halts at `READY_FOR_REVIEW`:
```bash
python scripts/run_demo.py --profile sample_data/citizen_profile_valid.json
```

### 2. Automated Test Mode: Complete Simulated Submission
For automated testing only, `--auto-confirm` simulates explicit confirmation after review to generate the simulated receipt:
```bash
python scripts/run_demo.py --profile sample_data/citizen_profile_valid.json --auto-confirm
```

### 3. Interactive Headed Mode for Human Review
Opens Chromium in visible headed mode so a citizen can visually inspect entered details, test "Edit Application", or click "Confirm and Continue":
```bash
python scripts/run_demo.py --profile sample_data/citizen_profile_valid.json --headed
```

### 4. Failure Mode Test (Invalid Profile)
Demonstrates pre-run fail-fast validation returning `VALIDATION_FAILED` with clear error codes:
```bash
python scripts/run_demo.py --profile sample_data/citizen_profile_invalid.json
```

### 5. Running the Pytest Suite
Runs all 18 unit and end-to-end integration tests:
```bash
pytest tests/ -v
```

### 6. Serving the Form Standalone
To manually explore the demo form in any browser:
```bash
python scripts/serve_demo.py
```
Browse to `http://127.0.0.1:8000/index.html`.

---

## 5. Deliverable Verification Checklist

- [x] Project runs end to end from a fresh clone with README instructions.
- [x] Demo form shows non-negotiable DEMO banner, Times New Roman typography, and distinct states.
- [x] Valid dummy profile reaches `READY_FOR_REVIEW` by default.
- [x] Explicit confirmation produces `SIMULATED_SUBMITTED` with a simulated demo reference number.
- [x] Invalid profile fails with clear human-readable errors and error codes.
- [x] Wrong file types, oversized files (> 2 MB), and path traversal attacks are rejected.
- [x] Confirmation is strictly prohibited before review (`CONFIRMATION_NOT_ALLOWED`).
- [x] No real government websites or endpoints are referenced.
- [x] Zero OTP, CAPTCHA, or auth bypass logic exists.
- [x] All 18 pytest tests pass (`pytest tests/`).
- [x] Screenshot evidence is saved to `evidence/`.
- [x] `docs/integration_contract.md`, `docs/architecture.md`, and `docs/test_report.md` are documented.
- [x] Automation engine (`saarthi_automation/`) is completely decoupled from the demo form HTML and UI frameworks.
