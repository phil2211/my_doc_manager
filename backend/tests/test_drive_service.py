from src.drive_service import generate_filename

def test_generate_filename():
    metadata = {"date": "2026-05-27", "category": "Bill", "sender": "Electric Co"}
    assert generate_filename(metadata) == "2026-05-27_Bill_Electric Co.pdf"