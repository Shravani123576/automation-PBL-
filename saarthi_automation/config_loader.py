"""
saarthi_automation/config_loader.py
Loads and validates form mapping configuration from JSON files.
"""

import json
from pathlib import Path
from typing import Any, Dict


class FormConfig:
    def __init__(self, raw: Dict[str, Any]):
        self.scheme_id: str = raw.get("scheme_id", "default_scheme")
        self.form_relative_url: str = raw.get("form_relative_url", "index.html")
        self.fields: Dict[str, Dict[str, Any]] = raw.get("fields", {})
        self.buttons: Dict[str, str] = raw.get("buttons", {})
        self.views: Dict[str, str] = raw.get("views", {})
        self.receipt: Dict[str, str] = raw.get("receipt", {})


def load_form_mapping(config_path: Path) -> FormConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Form mapping config not found at: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return FormConfig(data)
