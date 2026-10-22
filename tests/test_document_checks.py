"""
tests/test_document_checks.py
Unit tests for document security, path containment, extension, and size checks.
"""

from pathlib import Path
import pytest
from saarthi_automation.contracts import DocumentSpec
from saarthi_automation.document_checks import validate_document
from saarthi_automation.errors import AutomationErrorCode, DocumentSecurityError


@pytest.fixture
def base_dir():
    return Path(__file__).resolve().parent.parent


def test_valid_document(base_dir):
    doc_spec = DocumentSpec(
        document_type="Income Certificate",
        relative_path="sample_data/documents/sample_income_certificate.pdf"
    )
    res = validate_document(doc_spec, base_dir)
    assert res.accepted is True
    assert res.filename == "sample_income_certificate.pdf"
    assert res.size_bytes > 0


def test_document_outside_approved_dir(base_dir):
    # Attempt path traversal outside sample_data/documents
    doc_spec = DocumentSpec(
        document_type="Income Certificate",
        relative_path="../../requirements.txt"
    )
    with pytest.raises(DocumentSecurityError) as exc:
        validate_document(doc_spec, base_dir)
    assert exc.value.code == AutomationErrorCode.DOCUMENT_OUTSIDE_APPROVED_DIR


def test_document_not_found(base_dir):
    doc_spec = DocumentSpec(
        document_type="Income Certificate",
        relative_path="sample_data/documents/non_existent.pdf"
    )
    with pytest.raises(DocumentSecurityError) as exc:
        validate_document(doc_spec, base_dir)
    assert exc.value.code == AutomationErrorCode.DOCUMENT_NOT_FOUND


def test_invalid_extension(base_dir, tmp_path):
    # Create invalid extension inside approved dir for testing
    approved_dir = base_dir / "sample_data" / "documents"
    bad_file = approved_dir / "malicious_script.exe"
    bad_file.write_text("dummy binary content")
    try:
        doc_spec = DocumentSpec(
            document_type="Income Certificate",
            relative_path="sample_data/documents/malicious_script.exe"
        )
        with pytest.raises(DocumentSecurityError) as exc:
            validate_document(doc_spec, base_dir)
        assert exc.value.code == AutomationErrorCode.DOCUMENT_TYPE_NOT_ALLOWED
    finally:
        if bad_file.exists():
            bad_file.unlink()


def test_oversized_file(base_dir):
    approved_dir = base_dir / "sample_data" / "documents"
    large_file = approved_dir / "large_dummy.pdf"
    # Create a 2.1 MB dummy file
    with open(large_file, "wb") as f:
        f.seek(int(2.1 * 1024 * 1024))
        f.write(b"\0")
    try:
        doc_spec = DocumentSpec(
            document_type="Income Certificate",
            relative_path="sample_data/documents/large_dummy.pdf"
        )
        with pytest.raises(DocumentSecurityError) as exc:
            validate_document(doc_spec, base_dir)
        assert exc.value.code == AutomationErrorCode.DOCUMENT_TOO_LARGE
    finally:
        if large_file.exists():
            large_file.unlink()
