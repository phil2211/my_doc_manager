from src.llm_service import extract_metadata_via_llm
from unittest.mock import patch

@patch('src.llm_service.completion')
def test_extract_metadata_via_llm(mock_completion):
    mock_completion.return_value.choices = [
        type('obj', (object,), {'message': type('obj', (object,), {'content': '{"date": "2026-05-27", "sender": "Unknown", "category": "Bill"}'})})
    ]
    result = extract_metadata_via_llm("Some text")
    assert result["category"] == "Bill"