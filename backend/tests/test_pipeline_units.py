from __future__ import annotations

import pytest

from app.services.classification.rules import RuleBasedClassifier, normalize_sender
from app.services.extraction.regex_extractor import RegexExtractor
from app.services.grouping.heuristic import HeuristicGrouper
from app.services.types import PageContext


def test_rule_based_classifier_detects_bill():
    classifier = RuleBasedClassifier()
    result = classifier.classify(["Rechnung Nr. 12345", "Betrag CHF 100.00"])
    assert result.doc_type == "bill"
    assert result.confidence > 0.5


def test_rule_based_classifier_detects_contract():
    classifier = RuleBasedClassifier()
    result = classifier.classify(["Mietvertrag zwischen Parteien", "Unterschrift"])
    assert result.doc_type == "contract"


def test_regex_extractor_finds_date_and_sender():
    extractor = RegexExtractor()
    result = extractor.extract_metadata(
        ["ACME GmbH\nRechnung\nDatum: 15.03.2024\nTotal 50 EUR"],
        "bill",
    )
    assert result.document_date == "2024-03-15"
    assert result.sender_name == "ACME GmbH"
    assert result.sender_normalized == "acme gmbh"


def test_normalize_sender():
    assert normalize_sender("  ACME GmbH! ") == "acme gmbh"


def test_heuristic_grouper_splits_on_blank_page():
    grouper = HeuristicGrouper()
    pages = [
        PageContext("p1", 1, "Doc A page 1", {"top_lines": ["Doc A"], "perceptual_hash": "aaa", "is_blank": False}, False),
        PageContext("p2", 2, "", {"top_lines": [], "perceptual_hash": "bbb", "is_blank": True}, True),
        PageContext("p3", 3, "Doc B page 1", {"top_lines": ["Doc B"], "perceptual_hash": "ccc", "is_blank": False}, False),
    ]
    groups = grouper.group_pages(pages)
    assert len(groups) == 2
    assert groups[0].page_ids == ["p1"]
    assert groups[1].page_ids == ["p3"]


def test_heuristic_grouper_splits_on_page_one_pattern():
    grouper = HeuristicGrouper()
    pages = [
        PageContext("p1", 1, "First doc", {"top_lines": ["First"], "perceptual_hash": "aaa", "is_blank": False}, False),
        PageContext("p2", 2, "Seite 1 von 2\nSecond doc", {"top_lines": ["Seite 1 von 2"], "perceptual_hash": "aab", "is_blank": False}, False),
    ]
    groups = grouper.group_pages(pages)
    assert len(groups) == 2
