from __future__ import annotations

import re
from datetime import datetime

import dateparser

from app.services.classification.rules import normalize_sender
from app.services.types import MetadataResult

DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b"),
    re.compile(r"\b(\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+\d{4})\b", re.I),
    re.compile(r"\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b", re.I),
]

SENDER_SKIP = re.compile(r"^(seite|page|datum|date|tel|fax|www\.|http)", re.I)


class RegexExtractor:
    def extract_metadata(self, pages_text: list[str], doc_type: str) -> MetadataResult:
        combined = "\n".join(pages_text)
        header = "\n".join(pages_text[:1]) if pages_text else combined
        header_lines = [line.strip() for line in header.splitlines() if line.strip()]

        document_date, date_confidence = self._extract_date(combined)
        sender_name, sender_confidence = self._extract_sender(header_lines)

        extra_fields: dict = {}
        invoice_match = re.search(r"(?:rechnungs?nr\.?|invoice\s*(?:no|number)?\.?)\s*[:#]?\s*([\w-]+)", combined, re.I)
        if invoice_match:
            extra_fields["invoice_number"] = invoice_match.group(1)

        return MetadataResult(
            document_date=document_date,
            sender_name=sender_name,
            sender_normalized=normalize_sender(sender_name),
            confidence={
                "document_date": date_confidence,
                "sender_name": sender_confidence,
            },
            extra_fields=extra_fields,
        )

    def _extract_date(self, text: str) -> tuple[str | None, float]:
        candidates: list[tuple[datetime, float, str]] = []
        for pattern in DATE_PATTERNS:
            for match in pattern.finditer(text):
                parsed = dateparser.parse(match.group(1), languages=["de", "en"])
                if parsed:
                    candidates.append((parsed, 0.75, match.group(1)))

        if not candidates:
            parsed = dateparser.parse(text, languages=["de", "en"], settings={"STRICT_PARSING": False})
            if parsed:
                return parsed.date().isoformat(), 0.45
            return None, 0.0

        parsed, confidence, _ = max(candidates, key=lambda item: item[0])
        return parsed.date().isoformat(), confidence

    def _extract_sender(self, header_lines: list[str]) -> tuple[str | None, float]:
        for line in header_lines[:8]:
            if SENDER_SKIP.search(line):
                continue
            if len(line) < 4 or len(line) > 80:
                continue
            if re.search(r"\d{4,}", line):
                continue
            return line, 0.65

        for line in header_lines[:3]:
            if line and not SENDER_SKIP.search(line):
                return line[:80], 0.4
        return None, 0.0
