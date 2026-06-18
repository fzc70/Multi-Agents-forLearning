from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.repositories import MaterialRepository


def _tokens(text: str) -> list[str]:
    latin = re.findall(r"[A-Za-z0-9_]{2,}", text.lower())
    chinese = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    chars: list[str] = []
    for item in chinese:
        chars.extend(item[i : i + 2] for i in range(max(0, len(item) - 1)))
    return latin + chars


class RetrievalTool:
    def __init__(self, material_repo: MaterialRepository | None = None) -> None:
        self.material_repo = material_repo or MaterialRepository()

    def search(self, task_id: str, query: str, top_k: int = 5, anchors: list[str] | None = None) -> list[dict[str, Any]]:
        chunks = self.material_repo.list_chunks(task_id)
        if not chunks:
            return []

        query_text = " ".join([query, *(anchors or [])])
        q_tokens = _tokens(query_text)
        if not q_tokens:
            return [self._to_result(0.01, chunk) for chunk in chunks[:top_k]]
        q_counter = Counter(q_tokens)
        doc_tokens = [_tokens(str(chunk["content"])) for chunk in chunks]
        avg_len = sum(len(tokens) for tokens in doc_tokens) / max(len(doc_tokens), 1)
        doc_freq = Counter()
        for tokens in doc_tokens:
            doc_freq.update(set(tokens))

        scored: list[tuple[float, dict[str, Any]]] = []
        for chunk, c_tokens in zip(chunks, doc_tokens):
            if not c_tokens:
                continue
            c_counter = Counter(c_tokens)
            score = 0.0
            for token, q_weight in q_counter.items():
                freq = c_counter.get(token, 0)
                if not freq:
                    continue
                idf = self._idf(len(chunks), doc_freq[token])
                denom = freq + 1.5 * (1 - 0.75 + 0.75 * len(c_tokens) / max(avg_len, 1))
                score += idf * (freq * 2.5 / denom) * q_weight
            if score <= 0:
                continue
            scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        if not scored:
            scored = [(0.01, chunk) for chunk in chunks[:top_k]]
        return [self._to_result(score, chunk) for score, chunk in scored[:top_k]]

    @staticmethod
    def _idf(total_docs: int, doc_freq: int) -> float:
        import math

        return math.log(1 + (total_docs - doc_freq + 0.5) / (doc_freq + 0.5))

    @staticmethod
    def _to_result(score: float, chunk: dict[str, Any]) -> dict[str, Any]:
        return {
            "score": round(score, 4),
            "chunk_id": chunk["id"],
            "material_id": chunk["material_id"],
            "page": chunk["page"],
            "content": chunk["content"],
            "source_ref": {
                "type": "material_chunk",
                "id": chunk["material_id"],
                "title": chunk.get("material_name") or "学习资料",
                "page": chunk["page"],
                "chunk_id": chunk["id"],
            },
        }
