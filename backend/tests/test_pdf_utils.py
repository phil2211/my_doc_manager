from __future__ import annotations

import fitz
import pytest

from app.services.pdf_utils import compute_layout_features, is_scanned_page, split_pdf_to_pages


@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Sample invoice from Test AG\nRechnung 01.05.2024")
    doc.save(pdf_path)
    doc.close()
    return pdf_path


def test_split_pdf_to_pages(sample_pdf):
    pages = split_pdf_to_pages(sample_pdf)
    assert len(pages) == 1
    assert pages[0]["page_number"] == 1
    assert "Rechnung" in pages[0]["native_text"]


def test_is_scanned_page():
    assert is_scanned_page("short", threshold=50) is True
    assert is_scanned_page("x" * 100, threshold=50) is False


def test_compute_layout_features():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Header line")
    pix = page.get_pixmap()
    image_bytes = pix.tobytes("png")
    doc.close()

    features = compute_layout_features(image_bytes, "Header line with enough content to avoid blank detection")
    assert "perceptual_hash" in features
    assert "text_density" in features
