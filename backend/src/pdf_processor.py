import pdfplumber

def extract_text_from_page(pdf_path: str, page_num: int) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        if page_num >= len(pdf.pages):
            raise ValueError("Page number out of range")
        page = pdf.pages[page_num]
        return page.extract_text() or ""