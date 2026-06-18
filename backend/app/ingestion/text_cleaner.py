import re


def clean_text(text: str) -> str:
    """规范化空白字符并移除无效字符。"""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
