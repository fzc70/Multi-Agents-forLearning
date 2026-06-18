from app.ingestion.text_cleaner import clean_text


def chunk_pages(
    pages: list[dict[str, str | int]], chunk_size: int = 900, overlap: int = 120
) -> list[dict[str, str | int]]:
    """将分页文本切分为可检索的文本块。"""
    chunks: list[dict[str, str | int]] = []
    for page in pages:
        text = clean_text(str(page["text"]))
        start = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            content = text[start:end].strip()
            if content:
                chunks.append(
                    {
                        "page": int(page["page"]),
                        "chunk_index": len(chunks),
                        "content": content,
                    }
                )
            if end >= len(text):
                break
            start = max(0, end - overlap)
    return chunks
