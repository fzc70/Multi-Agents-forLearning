from pathlib import Path
from typing import BinaryIO

from app.core.config import get_settings


class FileStore:
    def __init__(self) -> None:
        """初始化 FileStore 所需的依赖。"""
        self.root = get_settings().data_path

    def material_pdf_dir(self, task_id: str) -> Path:
        """返回任务的 PDF 原文件目录。"""
        path = self.root / "materials" / task_id / "pdfs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def material_text_dir(self, task_id: str) -> Path:
        """返回任务的资料文本目录。"""
        path = self.root / "materials" / task_id / "texts"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resource_dir(self, task_id: str) -> Path:
        """返回任务的生成资源目录。"""
        path = self.root / "resources" / task_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def graph_dir(self, task_id: str) -> Path:
        """返回任务的知识图谱目录。"""
        path = self.root / "graphs" / task_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def safe_name(name: str) -> str:
        """生成可安全写入文件系统的文件名。"""
        keep = []
        for char in name:
            if char.isalnum() or char in "._-":
                keep.append(char)
            else:
                keep.append("_")
        return "".join(keep).strip("_") or "file"

    def save_upload(
        self, task_id: str, material_id: str, filename: str, fp: BinaryIO
    ) -> Path:
        """保存上传文件并返回存储路径。"""
        suffix = Path(filename).suffix.lower() or ".pdf"
        target = self.material_pdf_dir(task_id) / f"{material_id}{suffix}"
        with target.open("wb") as out:
            while chunk := fp.read(1024 * 1024):
                out.write(chunk)
        return target

    def save_text(self, task_id: str, material_id: str, text: str) -> Path:
        """保存文本内容并返回存储路径。"""
        target = self.material_text_dir(task_id) / f"{material_id}.txt"
        target.write_text(text, encoding="utf-8")
        return target
