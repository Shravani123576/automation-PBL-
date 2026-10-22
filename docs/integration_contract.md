# SAARTHi Member 3 — Integration Contract

This document specifies the integration contract for the **SAARTHi Browser Automation module (Member 3)**. It defines the formal input (`AutomationRequest`) and output (`AutomationResult`) structures, validation behavior, error codes, and instructions for how other members (Member 1, Member 2, and Member 4) interface with this module.

> [!IMPORTANT]
> **SIMULATED / PROTOTYPE ENVIRONMENT**:
> All executions target only the local test application form. Outputs are simulated receipts. No real government databases are accessed or altered.

---

## 1. Invocation Interface

Future modules can invoke the automation engine via the standard Python function:

```python
from saarthi_automation.api import run_automation

result_dict = run_automation(request_payload)
```

No direct browser management or HTML knowledge is required by the caller.

---

## 2. Input Specification: `AutomationRequest`

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request_id` | `string` | Optional | Unique transaction identifier (auto-generated if omitted). |
| `scheme_id` | `string` | Required | Identifier of the target scheme, e.g., `"demo_income_certificate_scheme"`. |
| `citizen_data` | `object` | Required | Canonical citizen profile data with dotted or nested structure. |
| `document` | `object` | Required | Document specification containing `document_type` and `relative_path`. |
| `options` | `object` | Optional | Execution options (`headless`, `slow_mo_ms`, `timeout_ms`, `confirm_mode`). |

### Approved Document Path Rule
`document.relative_path` must resolve strictly inside `sample_data/documents/`. Any attempt to traverse out of this approved folder is rejected with `DOCUMENT_OUTSIDE_APPROVED_DIR`.

---

## 3. Output Specification: `AutomationResult`

| Field | Type | Description |
| :--- | :--- | :--- |
| `request_id` | `string` | Echoed or generated request identifier. |
| `status` | `string` | `READY_FOR_REVIEW`, `SIMULATED_SUBMITTED`, `VALIDATION_FAILED`, or `AUTOMATION_FAILED`. |
| `review_status` | `string` | `PENDING`, `CONFIRMED`, or `NOT_REACHED`. |
| `validation_results` | `array` | List of field checks with `field`, `expected`, `actual`, and `passed`. |
| `document_result` | `object` | Info on attached document (`filename`, `size_bytes`, `accepted`, `reason`). |
| `demo_receipt` | `object / null`| Populated on `SIMULATED_SUBMITTED`. Always has `is_simulated: true`. |
| `evidence` | `array` | Paths to saved evidence screenshots. |
| `step_log` | `array` | Timestamped step log. |
| `errors` | `array` | List of `{ code, message, field }` entries. |

---

## 4. Standardized Error Codes

- `MISSING_REQUIRED_FIELD`: Missing mandatory field in citizen profile.
- `INVALID_FIELD_VALUE`: Format or value mismatch (e.g. invalid PIN or mobile).
- `DOCUMENT_NOT_FOUND`: Target document file does not exist.
- `DOCUMENT_OUTSIDE_APPROVED_DIR`: Document path outside approved directory.
- `DOCUMENT_TYPE_NOT_ALLOWED`: Extension not in `.pdf`, `.jpg`, `.jpeg`, `.png`.
- `DOCUMENT_TOO_LARGE`: File size exceeds 2 MB limit.
- `FORM_NOT_REACHABLE`: Demo server or URL could not be opened.
- `SELECTOR_NOT_FOUND`: Missing DOM selector in form mapping.
- `UPLOAD_FAILED`: File upload input failed or filename not displayed.
- `REVIEW_MISMATCH`: Review summary does not match citizen data.
- `CONFIRMATION_NOT_ALLOWED`: Attempted confirmation before reaching review state.

---

## 5. Sample Request & Response Payloads

### Example 1: Valid Execution (Stopping at Review)
**Request:**
```json
{
  "scheme_id": "demo_income_certificate_scheme",
  "citizen_data": {
    "applicant": {
      "full_name": "Test Citizen One",
      "date_of_birth": "1992-05-15",
      "gender": "Female",
      "mobile_number": "9000000001",
      "email": "citizen@example.com"
    },
    "address": {
      "house": "Flat 402, Shanti Nilayam",
      "village_city": "Nagpur",
      "district": "Nagpur",
      "state": "Maharashtra",
      "pin_code": "440001"
    },
    "scheme": {
      "annual_income": 120000,
      "occupation": "Self-Employed",
      "category": "OBC"
    }
  },
  "document": {
    "document_type": "Income Certificate",
    "relative_path": "sample_data/documents/sample_income_certificate.pdf"
  },
  "options": {
    "headless": true,
    "confirm_mode": "none"
  }
}
```

**Response:**
```json
{
  "request_id": "req_cc4a1521",
  "status": "READY_FOR_REVIEW",
  "review_status": "PENDING",
  "validation_results": [
    {
      "field": "applicant.full_name",
      "expected": "Test Citizen One",
      "actual": "Test Citizen One",
      "passed": true,
      "message": "Valid full name"
    }
  ],
  "document_result": {
    "filename": "sample_income_certificate.pdf",
    "size_bytes": 622,
    "accepted": true,
    "reason": "Document passed all security, format, and size validation checks."
  },
  "demo_receipt": null,
  "evidence": [
    "C:/.../evidence/req_cc4a1521_01_form_filled.png",
    "C:/.../evidence/req_cc4a1521_02_review.png"
  ],
  "errors": []
}
```

### Example 2: Failed Request (Invalid PIN Code)
**Response:**
```json
{
  "request_id": "req_9e252c08",
  "status": "VALIDATION_FAILED",
  "review_status": "NOT_REACHED",
  "validation_results": [],
  "document_result": null,
  "demo_receipt": null,
  "evidence": [],
  "errors": [
    {
      "code": "INVALID_FIELD_VALUE",
      "message": "The PIN code must be exactly 6 digits.",
      "field": "address.pin_code"
    }
  ]
}
```
