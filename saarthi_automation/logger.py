"""
saarthi_automation/logger.py
Simple timestamped step logger for browser automation steps.
"""

from datetime import datetime
from typing import List
from saarthi_automation.contracts import StepLogEntry


class StepLogger:
    def __init__(self):
        self.entries: List[StepLogEntry] = []

    def log(self, step: str, message: str) -> None:
        ts = datetime.now().isoformat()
        entry = StepLogEntry(timestamp=ts, step=step, message=message)
        self.entries.append(entry)
        print(f"[{ts}] [{step}] {message}")

    def get_entries(self) -> List[StepLogEntry]:
        return list(self.entries)
