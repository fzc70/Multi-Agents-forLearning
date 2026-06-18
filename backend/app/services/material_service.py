from __future__ import annotations

import os
from typing import Any

from fastapi import UploadFile

from app.core.errors import bad_request, not_found
from app.core.ids import new_id
from app.ingestion.chunker import chunk_pages
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.text_cleaner import clean_text
from app.repositories import MaterialRepository
from app.services.task_service import TaskService
from app.storage.file_store import FileStore


class MaterialService:
    """学习资料服务。

    上传时完成 PDF 保存、解析、切片入库；聊天与资源生成只读取已入库资料。
    """

    max_pdf_size = 30 * 1024 * 1024

    def __init__(self) -> None:
        self.tasks = TaskService()
        self.repo = MaterialRepository()
        self.files = FileStore()

    def list_materials(self, task_id: str) -> list[dict[str, Any]]:
        return self.tasks.get_task(task_id)["materials"]

    def upload_pdf(self, task_id: str, file: UploadFile) -> dict[str, Any]:
        self.tasks.get_task(task_id)
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise bad_request("只支持上传 PDF 文件")

        material_id = new_id("mat")
        path = self.files.save_upload(task_id, material_id, file.filename, file.file)
        size = os.path.getsize(path)
        if size > self.max_pdf_size:
            path.unlink(missing_ok=True)
            raise bad_request("单个 PDF 不能超过 30MB")

        pages = parse_pdf(path)
        text = clean_text("\n\n".join(str(page["text"]) for page in pages))
        if not text:
            path.unlink(missing_ok=True)
            raise bad_request("PDF 未解析到有效文本")

        text_path = self.files.save_text(task_id, material_id, text)
        self.repo.insert_with_id(material_id, task_id, file.filename, size, len(text), str(path), str(text_path))
        self.repo.add_chunks(task_id, material_id, chunk_pages(pages))
        return self.tasks.get_task(task_id)

    def delete_material(self, task_id: str, material_id: str) -> dict[str, Any]:
        material = self.repo.get(material_id, task_id)
        if not material:
            raise not_found("资料不存在")
        for key in ("file_path", "text_path"):
            if material.get(key):
                try:
                    os.remove(material[key])
                except OSError:
                    pass
        self.repo.delete(material_id, task_id)
        return self.tasks.get_task(task_id)
