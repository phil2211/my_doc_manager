from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class OcrResult:
    text: str
    confidence: float


class OcrBackend(Protocol):
    def extract_text(self, page_image: bytes) -> OcrResult: ...
