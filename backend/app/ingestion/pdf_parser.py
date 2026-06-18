from pathlib import Path

from pypdf import PdfReader


def parse_pdf(path: Path) -> list[dict[str, str | int]]:
    """从 PDF 中按页提取文本。"""
    reader = PdfReader(str(path))
    pages: list[dict[str, str | int]] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"page": index, "text": text})
    return pages
