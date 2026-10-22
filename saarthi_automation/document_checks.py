"""
saarthi_automation/document_checks.py
Strict document path security, format verification, and size bounds checks.
Ensures no path traversal outside the approved document directory.
"""

from pathlib import Path
from saarthi_automation.contracts import DocumentResult, DocumentSpec
from saarthi_automation.errors import (
    AutomationErrorCode,
    DocumentSecurityError,
)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


def validate_document(doc_spec: DocumentSpec, base_dir: Path) -> DocumentResult:
    """
    Validates document containment, existence, extension, and size.
    Approved folder: base_dir / "sample_data" / "documents"
    """
    approved_dir = (base_dir / "sample_data" / "documents").resolve()

    if not doc_spec.relative_path:
        raise DocumentSecurityError(
            AutomationErrorCode.DOCUMENT_NOT_FOUND,
            "Document relative path is required."
        )

    # Resolve target document path
    # If provided as relative path under approved dir (e.g. 'sample_income_certificate.pdf' or 'documents/sample.pdf')
    target_path = (base_dir / doc_spec.relative_path).resolve()
    if not target_path.exists():
        # Also try directly under approved_dir
        target_path_alt = (approved_dir / doc_spec.relative_path).resolve()
        if target_path_alt.exists():
            target_path = target_path_alt

    # Strict containment check (anti-traversal)
    try:
        target_path.relative_to(approved_dir)
    except ValueError:
        raise DocumentSecurityError(
            AutomationErrorCode.DOCUMENT_OUTSIDE_APPROVED_DIR,
            f"Security violation: Document '{doc_spec.relative_path}' resolves outside the approved documents directory."
        )

    # Existence check
    if not target_path.exists() or not target_path.is_file():
        raise DocumentSecurityError(
            AutomationErrorCode.DOCUMENT_NOT_FOUND,
            f"The specified document file was not found: {target_path.name}"
        )

    # Extension check
    suffix = target_path.suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise DocumentSecurityError(
            AutomationErrorCode.DOCUMENT_TYPE_NOT_ALLOWED,
            f"Document type '{suffix}' is not permitted. Allowed formats: PDF, JPG, JPEG, PNG."
        )

    # Size check
    file_size = target_path.stat().st_size
    if file_size == 0:
        raise DocumentSecurityError(
            AutomationErrorCode.DOCUMENT_TYPE_NOT_ALLOWED,
            "The document file is empty (0 bytes)."
        )
    if file_size > MAX_FILE_SIZE_BYTES:
        raise DocumentSecurityError(
            AutomationErrorCode.DOCUMENT_TOO_LARGE,
            f"Document file size ({file_size} bytes) exceeds the maximum allowed limit of 2 MB."
        )

    return DocumentResult(
        filename=target_path.name,
        size_bytes=file_size,
        accepted=True,
        reason="Document passed all security, format, and size validation checks."
    )


def get_resolved_document_path(doc_spec: DocumentSpec, base_dir: Path) -> Path:
    approved_dir = (base_dir / "sample_data" / "documents").resolve()
    target_path = (base_dir / doc_spec.relative_path).resolve()
    if not target_path.exists():
        target_path_alt = (approved_dir / doc_spec.relative_path).resolve()
        if target_path_alt.exists():
            target_path = target_path_alt
    return target_path
