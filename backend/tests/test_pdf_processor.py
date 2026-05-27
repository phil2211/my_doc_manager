import os
import pytest
from src.pdf_processor import extract_text_from_page

def test_extract_text_from_page(tmp_path):
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample.pdf")
    text = extract_text_from_page(fixture_path, page_num=0)
    assert isinstance(text, str)