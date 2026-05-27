from src.rules_engine import extract_metadata_via_rules

def test_extract_metadata_via_rules():
    text = "Invoice Date: 2026-05-27\nFrom: Electric Company\nTotal: $50.00"
    # Mock DB call for known senders
    known_senders = ["Electric Company"]
    metadata = extract_metadata_via_rules(text, known_senders)
    assert metadata["date"] == "2026-05-27"
    assert metadata["sender"] == "Electric Company"