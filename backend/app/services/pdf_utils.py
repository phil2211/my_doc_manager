from __future__ import annotations

import io
import re
from pathlib import Path

import fitz
import imagehash
from PIL import Image

from app.core.config import get_settings


def ensure_storage_dir(source_file_id: str) -> Path:
    settings = get_settings()
    storage_dir = Path(settings.file_storage_path) / source_file_id
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


def render_page_to_image(page: fitz.Page, dpi: int) -> bytes:
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    return pix.tobytes("png")


def extract_native_text(page: fitz.Page) -> str:
    return page.get_text("text").strip()


def is_scanned_page(text: str, threshold: int | None = None) -> bool:
    settings = get_settings()
    limit = threshold if threshold is not None else settings.scanned_text_threshold
    return len(text) < limit


def save_thumbnail(image_bytes: bytes, path: Path) -> None:
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail((240, 320))
    image.save(path, format="PNG")


def compute_layout_features(image_bytes: bytes, text_content: str) -> dict:
    image = Image.open(io.BytesIO(image_bytes)).convert("L")
    width, height = image.size
    pixels = list(image.getdata())
    avg_brightness = sum(pixels) / len(pixels) if pixels else 255
    is_blank = avg_brightness > 245 and len(text_content.strip()) < 20

    perceptual_hash = str(imagehash.phash(image))
    top_lines = [line.strip() for line in text_content.splitlines() if line.strip()][:5]

    return {
        "perceptual_hash": perceptual_hash,
        "avg_brightness": avg_brightness,
        "is_blank": is_blank,
        "text_density": len(text_content) / max(width * height, 1),
        "top_lines": top_lines,
        "width": width,
        "height": height,
    }


def split_pdf_to_pages(pdf_path: Path) -> list[dict]:
    settings = get_settings()
    doc = fitz.open(pdf_path)
    pages_data: list[dict] = []

    try:
        for index, page in enumerate(doc):
            page_number = index + 1
            native_text = extract_native_text(page)
            scanned = is_scanned_page(native_text)
            image_bytes = render_page_to_image(page, settings.ocr_dpi)
            pages_data.append(
                {
                    "page_number": page_number,
                    "native_text": native_text,
                    "is_scanned": scanned,
                    "image_bytes": image_bytes,
                }
            )
    finally:
        doc.close()

    return pages_data


def hash_distance(hash_a: str, hash_b: str) -> int:
    if not hash_a or not hash_b:
        return 64
    try:
        return imagehash.hex_to_hash(hash_a) - imagehash.hex_to_hash(hash_b)
    except Exception:
        return 64


FIRST_PAGE_PATTERN = re.compile(r"(?:seite|page)\s*1\b", re.IGNORECASE)
