"""
saarthi_automation/errors.py
Standardized error codes and exceptions for the SAARTHi Browser Automation module.
"""

from typing import Optional


class AutomationErrorCode:
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FIELD_VALUE = "INVALID_FIELD_VALUE"
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    DOCUMENT_OUTSIDE_APPROVED_DIR = "DOCUMENT_OUTSIDE_APPROVED_DIR"
    DOCUMENT_TYPE_NOT_ALLOWED = "DOCUMENT_TYPE_NOT_ALLOWED"
    DOCUMENT_TOO_LARGE = "DOCUMENT_TOO_LARGE"
    FORM_NOT_REACHABLE = "FORM_NOT_REACHABLE"
    SELECTOR_NOT_FOUND = "SELECTOR_NOT_FOUND"
    FIELD_VALUE_MISMATCH = "FIELD_VALUE_MISMATCH"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    REVIEW_MISMATCH = "REVIEW_MISMATCH"
    TIMEOUT = "TIMEOUT"
    BROWSER_ERROR = "BROWSER_ERROR"
    CONFIRMATION_NOT_ALLOWED = "CONFIRMATION_NOT_ALLOWED"


class AutomationError(Exception):
    """Base exception for all browser automation errors."""

    def __init__(self, code: str, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field

    def to_dict(self) -> dict:
        data = {"code": self.code, "message": self.message}
        if self.field:
            data["field"] = self.field
        return data


class PreRunValidationError(AutomationError):
    pass


class DocumentSecurityError(AutomationError):
    pass


class SelectorNotFoundError(AutomationError):
    pass


class ReviewMismatchError(AutomationError):
    pass


class ConfirmationNotAllowedError(AutomationError):
    pass
