"""
tests/test_config_loader.py
Unit tests for loading and parsing form mapping JSON config.
"""

from pathlib import Path
from saarthi_automation.config_loader import load_form_mapping


def test_load_form_mapping():
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "form_mapping.json"
    cfg = load_form_mapping(config_path)

    assert cfg.scheme_id == "demo_income_certificate_scheme"
    assert "applicant.full_name" in cfg.fields
    assert cfg.fields["applicant.full_name"]["type"] == "text"
    assert "review" in cfg.buttons
    assert "confirm" in cfg.buttons
