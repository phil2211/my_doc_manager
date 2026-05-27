import os
import pytest
from src.pdf_processor import extract_text_from_page

def test_extract_text_from_page(tmp_path):
    text = extract_text_from_page("tests/fixtures/sample.pdf", page_num=0)
    assert isinstance(text, str)