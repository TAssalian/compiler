from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Diagnostic:
    severity: str
    code: str
    message: str
    line: int
