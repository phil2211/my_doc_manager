from __future__ import annotations

import re

from app.core.constants import DOC_TYPES
from app.services.types import ClassificationResult

KEYWORDS: dict[str, list[str]] = {
    "bill": [
        "rechnung",
        "invoice",
        "zahlungsaufforderung",
        "betrag",
        "mwst",
        "total",
        "fällig",
        "kundennummer",
    ],
    "contract": [
        "vertrag",
        "contract",
        "agreement",
        "vereinbarung",
        "unterschrift",
        "parteien",
        "kündigung",
    ],
    "commercial": [
        "angebot",
        "werbung",
        "aktion",
        "newsletter",
        "promotion",
        "sale",
        "rabatt",
    ],
    "information": [
        "information",
        "mitteilung",
        "bekanntgabe",
        "hinweis",
        "info",
        "notice",
    ],
}


class RuleBasedClassifier:
    def classify(self, pages_text: list[str]) -> ClassificationResult:
        combined = "\n".join(pages_text).lower()
        scores: dict[str, float] = {}
        signals: list[str] = []

        for doc_type, keywords in KEYWORDS.items():
            hits = [keyword for keyword in keywords if keyword in combined]
            if hits:
                scores[doc_type] = min(0.95, 0.45 + 0.1 * len(hits))
                signals.extend(hits[:3])

        if not scores:
            return ClassificationResult(doc_type="other", confidence=0.4, signals=["no_keyword_match"])

        best_type = max(scores, key=scores.get)
        return ClassificationResult(doc_type=best_type, confidence=scores[best_type], signals=signals)


def normalize_sender(name: str | None) -> str | None:
    if not name:
        return None
    normalized = re.sub(r"[^\w\s&.-]", "", name.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized or None
