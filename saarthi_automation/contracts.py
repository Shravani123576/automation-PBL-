"""
saarthi_automation/contracts.py
Integration data contracts (request and result) for Member 3.
Provides serializable dataclasses and to_dict() helpers for future modules.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class AutomationOptions:
    headless: bool = True
    slow_mo_ms: int = 0
    timeout_ms: int = 10000
    screenshots: bool = True
    confirm_mode: str = "none"  # "none" | "auto_confirm_for_test" | "interactive_human"


@dataclass
class DocumentSpec:
    document_type: str
    relative_path: str


@dataclass
class AutomationRequest:
    scheme_id: str
    citizen_data: Dict[str, Any]
    document: DocumentSpec
    request_id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    options: AutomationOptions = field(default_factory=AutomationOptions)

    @classmethod
    def from_dict(cls, data: dict) -> "AutomationRequest":
        doc_data = data.get("document", {})
        doc = DocumentSpec(
            document_type=doc_data.get("document_type", "Income Certificate"),
            relative_path=doc_data.get("relative_path", "")
        )
        opt_data = data.get("options", {})
        opts = AutomationOptions(
            headless=opt_data.get("headless", True),
            slow_mo_ms=opt_data.get("slow_mo_ms", 0),
            timeout_ms=opt_data.get("timeout_ms", 10000),
            screenshots=opt_data.get("screenshots", True),
            confirm_mode=opt_data.get("confirm_mode", "none"),
        )
        return cls(
            request_id=data.get("request_id") or f"req_{uuid.uuid4().hex[:8]}",
            scheme_id=data.get("scheme_id", "demo_scheme"),
            citizen_data=data.get("citizen_data", {}),
            document=doc,
            options=opts,
        )


@dataclass
class ValidationResult:
    field: str
    expected: Any
    actual: Any
    passed: bool
    message: str


@dataclass
class DocumentResult:
    filename: str
    size_bytes: int
    accepted: bool
    reason: str


@dataclass
class DemoReceipt:
    demo_reference: str
    is_simulated: bool = True
    label: str = "DEMO RECEIPT — SIMULATED, NOT SUBMITTED TO ANY GOVERNMENT SYSTEM"


@dataclass
class StepLogEntry:
    timestamp: str
    step: str
    message: str


@dataclass
class AutomationErrorDetail:
    code: str
    message: str
    field: Optional[str] = None


@dataclass
class AutomationResult:
    request_id: str
    status: str  # READY_FOR_REVIEW | SIMULATED_SUBMITTED | VALIDATION_FAILED | AUTOMATION_FAILED
    review_status: str  # PENDING | CONFIRMED | NOT_REACHED
    validation_results: List[ValidationResult] = field(default_factory=list)
    document_result: Optional[DocumentResult] = None
    demo_receipt: Optional[DemoReceipt] = None
    evidence: List[str] = field(default_factory=list)
    step_log: List[StepLogEntry] = field(default_factory=list)
    errors: List[AutomationErrorDetail] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
