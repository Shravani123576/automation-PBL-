# SAARTHi Member 3 — Test & Verification Report

**Date of Execution**: 2026-10-12  
**Environment**: Windows 11, Python 3.12.7, Playwright 1.49.1, pytest 8.3.4  
**Project**: `saarthi_member3_automation`

---

## 1. Test Execution Summary

| Test Suite | Total Tests | Passed | Failed | Status |
| :--- | :--- | :--- | :--- | :--- |
| `tests/test_config_loader.py` | 1 | 1 | 0 | **PASSED** |
| `tests/test_document_checks.py` | 5 | 5 | 0 | **PASSED** |
| `tests/test_validators.py` | 7 | 7 | 0 | **PASSED** |
| `tests/test_e2e_valid_flow.py` | 5 | 5 | 0 | **PASSED** |
| `tests/test_e2e_invalid_flow.py` | 2 | 2 | 0 | **PASSED** |
| **Total** | **20** | **20** | **0** | **100% PASS** |

---

## 2. Test Details

### Configuration Loader Tests (`test_config_loader.py`)
- `test_load_form_mapping`: Verifies JSON deserialization and access to fields, buttons, and views.

### Document Security Tests (`test_document_checks.py`)
- `test_valid_document`: Verifies valid sample PDF passes.
- `test_document_outside_approved_dir`: Confirms traversal attempts (`../../requirements.txt`) are blocked (`DOCUMENT_OUTSIDE_APPROVED_DIR`).
- `test_document_not_found`: Confirms non-existent files are blocked (`DOCUMENT_NOT_FOUND`).
- `test_invalid_extension`: Confirms disallowed file extensions (`.exe`) are blocked (`DOCUMENT_TYPE_NOT_ALLOWED`).
- `test_oversized_file`: Confirms files larger than 2 MB are rejected (`DOCUMENT_TOO_LARGE`).

### Pre-Run Validators (`test_validators.py`)
- `test_validate_valid_profile`: Validates complete dummy profile against all 6 canonical rules.
- `test_missing_full_name`: Catches empty full name (`MISSING_REQUIRED_FIELD`).
- `test_invalid_mobile_digit_count`: Catches 8-digit mobile (`INVALID_FIELD_VALUE`).
- `test_invalid_mobile_prefix`: Catches non-6/7/8/9 starting digit (`INVALID_FIELD_VALUE`).
- `test_invalid_pin_code`: Catches 4-digit PIN (`INVALID_FIELD_VALUE`).
- `test_negative_income`: Catches negative income amount (`INVALID_FIELD_VALUE`).
- `test_future_dob`: Catches future date of birth (`INVALID_FIELD_VALUE`).

### End-to-End Workflows (`test_e2e_valid_flow.py` & `test_e2e_invalid_flow.py`)
- `test_valid_flow_pauses_at_review`: Confirms engine stops at `READY_FOR_REVIEW` with review values read back.
- `test_valid_flow_simulated_submission`: Confirms `--auto-confirm` (test mode) transitions to `SIMULATED_SUBMITTED` with demo reference and simulated receipt label.
- `test_confirm_before_review_prohibited`: Enforces `ConfirmationNotAllowedError` (`CONFIRMATION_NOT_ALLOWED`) if confirmation is called before review.
- `test_headed_default_pauses_before_confirm`: Proves default headed flow pauses before confirmation (`READY_FOR_REVIEW`) and does not auto-confirm.
- `test_manual_confirmation_only_reaches_receipt`: Proves receipt is reached ONLY after an explicit confirmation action, and cannot be reached while remaining at review.
- `test_invalid_profile_fails`: Confirms `VALIDATION_FAILED` status and clean error reporting on bad input.
- `test_document_outside_approved_dir_fails`: Confirms traversal attacks produce `VALIDATION_FAILED`.

---

## 3. Evidence Artifacts

Generated screenshots in `evidence/`:
1. `req_*_01_form_filled.png`: Form completed with valid dummy profile and attached PDF.
2. `req_*_02_review.png`: PENDING REVIEW screen with summary table.
3. `req_*_03_receipt.png`: SIMULATED DEMO RECEIPT with reference number.
