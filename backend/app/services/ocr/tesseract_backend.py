from __future__ import annotations

import io

import pytesseract
from PIL import Image

from app.services.ocr.protocol import OcrResult


class TesseractOcrBackend:
    def extract_text(self, page_image: bytes) -> OcrResult:
        image = Image.open(io.BytesIO(page_image))
        data = pytesseract.image_to_data(image, lang="deu+eng", output_type=pytesseract.Output.DICT)
        text = pytesseract.image_to_string(image, lang="deu+eng").strip()

        confidences = [float(conf) for conf in data.get("conf", []) if conf not in ("-1", -1)]
        avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0

        return OcrResult(text=text, confidence=avg_confidence)
