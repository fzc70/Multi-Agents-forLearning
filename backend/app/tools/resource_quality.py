from __future__ import annotations

from typing import Any

from app.domain.constants import (
    RESOURCE_TYPE_CODE,
    RESOURCE_TYPE_EXERCISE,
    RESOURCE_TYPE_KG,
    RESOURCE_TYPE_LECTURE,
    RESOURCE_TYPE_MINDMAP,
    RESOURCE_TYPE_READING,
    RESOURCE_TYPE_SET,
)
from app.tools.resource_defaults import ResourceDefaultFactory


class ResourceQualityGate:
    """资源质量门禁。

    Agent 负责生成主要内容；门禁只做结构校验、缺字段修复和兜底内容补齐，
    避免空详情、空题目、不可渲染图谱进入前端。
    """

    def __init__(self) -> None:
        self.defaults = ResourceDefaultFactory()

    def normalize(self, resource: dict[str, Any], task_title: str, next_action: str) -> dict[str, Any]:
        type_ = str(resource.get("type") or RESOURCE_TYPE_LECTURE)
        if type_ not in RESOURCE_TYPE_SET:
            type_ = RESOURCE_TYPE_LECTURE
        title = str(resource.get("title") or f"{task_title} · {type_}")
        description = str(resource.get("description") or self.description(type_, next_action))
        focus = self._focus_title(title, task_title, type_)
        detail = resource.get("detail")
        if not isinstance(detail, dict) or not detail:
            detail = self.default_detail(type_, focus, next_action)
        detail = self._repair_detail(type_, detail, focus, next_action)
        content = str(resource.get("content") or self.markdown_from_detail(type_, detail, focus))
        return {
            "type": type_,
            "title": title,
            "description": description,
            "content": content,
            "detail": detail,
            "recommendation_reason": str(
                resource.get("recommendation_reason") or f"当前目标是“{next_action}”，该资源可直接支持本阶段学习。"
            ),
        }

    def default_detail(self, type_: str, task_title: str, next_action: str) -> dict[str, Any]:
        return self.defaults.default_detail(type_, task_title, next_action)

    def _repair_detail(self, type_: str, detail: dict[str, Any], task_title: str, next_action: str) -> dict[str, Any]:
        fallback = self.default_detail(type_, task_title, next_action)
        if type_ == RESOURCE_TYPE_EXERCISE and len(detail.get("questions", [])) < 5:
            detail["questions"] = fallback["questions"]
        if type_ == RESOURCE_TYPE_EXERCISE:
            repaired = []
            fallback_questions = fallback["questions"]
            for index, question in enumerate(detail.get("questions", [])):
                base = fallback_questions[min(index, len(fallback_questions) - 1)]
                q_type = str(question.get("type") or "").strip()
                stem = (
                    question.get("stem")
                    or question.get("question")
                    or question.get("title")
                    or question.get("content")
                    or base["stem"]
                )
                options = question.get("options")
                if isinstance(options, dict):
                    options = [f"{key}. {value}" for key, value in options.items()]
                stem, inline_options = self._extract_inline_options(str(stem))
                if inline_options and self._options_are_only_labels(options):
                    options = inline_options
                if (not isinstance(options, list) or not options) and q_type == "single_choice":
                    options = base.get("options", [])
                if not isinstance(options, list):
                    options = []
                options = [self._clean_option(str(item)) for item in options]
                answer = str(question.get("answer") or question.get("correct_answer") or base.get("answer", "")).strip()
                answer = self._normalize_answer(answer, options)
                repaired.append(
                    {
                        "id": str(question.get("id") or f"q{index + 1}"),
                        "type": q_type or ("single_choice" if options else "short_answer"),
                        "stem": str(stem),
                        "options": options,
                        "answer": answer,
                        "analysis": str(question.get("analysis") or question.get("explanation") or base.get("analysis", "请复盘关键步骤。")),
                        "difficulty": str(question.get("difficulty") or base.get("difficulty", "基础")),
                        "knowledge_points": question.get("knowledge_points") or base.get("knowledge_points", []),
                    }
                )
            detail["questions"] = repaired
        if type_ == RESOURCE_TYPE_LECTURE:
            detail = self._repair_lecture_detail(detail, fallback, task_title, next_action)
        if type_ in {RESOURCE_TYPE_MINDMAP, RESOURCE_TYPE_KG}:
            detail["nodes"] = self._repair_nodes(detail.get("nodes", []), fallback["nodes"])
            detail["edges"] = self._repair_edges(detail.get("edges", []), fallback["edges"])
            if len(detail.get("nodes", [])) < 8:
                detail["nodes"] = fallback["nodes"]
            if len(detail.get("edges", [])) < 7:
                detail["edges"] = fallback["edges"]
        if type_ == RESOURCE_TYPE_READING and len(detail.get("readings", [])) < 5:
            detail = fallback
        if type_ == RESOURCE_TYPE_CODE and not detail.get("starter_code"):
            detail = fallback
        return detail

    def _repair_lecture_detail(
        self,
        detail: dict[str, Any],
        fallback: dict[str, Any],
        task_title: str,
        next_action: str,
    ) -> dict[str, Any]:
        sections = detail.get("sections")
        if not isinstance(sections, list) or len(sections) < 3:
            sections = fallback["sections"]
        repaired_sections = []
        for index, section in enumerate(sections):
            if not isinstance(section, dict):
                continue
            base = fallback["sections"][min(index, len(fallback["sections"]) - 1)]
            heading = str(section.get("heading") or section.get("title") or base["heading"])
            body = str(section.get("body") or section.get("content") or section.get("text") or base["body"])
            repaired_sections.append(
                {
                    "heading": heading,
                    "body": body,
                    "overview": str(section.get("overview") or self._first_sentence(body) or base["body"]),
                    "steps": self._repair_lecture_steps(section.get("steps"), body, heading, next_action),
                    "key_points": self._repair_text_list(section.get("key_points") or section.get("keyPoints"), self._derive_key_points(body, heading)),
                    "common_mistakes": self._repair_text_list(
                        section.get("common_mistakes") or section.get("mistakes") or section.get("warnings"),
                        self._derive_mistakes(body, heading),
                    ),
                    "example": str(section.get("example") or self._derive_example(body, heading, task_title)),
                    "self_check": str(section.get("self_check") or section.get("selfCheck") or self._derive_self_check(heading)),
                }
            )
        detail["sections"] = repaired_sections or fallback["sections"]
        detail["key_points"] = self._repair_text_list(detail.get("key_points"), fallback.get("key_points", [task_title, next_action]))
        detail["checkpoints"] = self._repair_text_list(detail.get("checkpoints"), fallback.get("checkpoints", []))
        return detail

    def _repair_lecture_steps(self, steps: Any, body: str, heading: str, next_action: str) -> list[str]:
        existing = [
            item for item in self._repair_text_list(steps, [])
            if not any(
                marker in item
                for marker in [
                    "涉及的关键对象",
                    "确认不是只记住名词",
                    "再写出本节规则或条件",
                    "然后按题目条件逐步套用规则",
                    "最后用同类题复现完整过程",
                    "最后围绕",
                    "易错点",
                    "自检",
                ]
            )
        ]
        extracted = self._extract_steps_from_text(body)
        merged: list[str] = []
        for item in [*existing, *extracted, *self._derive_steps(body, heading, next_action)]:
            text = str(item).strip(" ；;。")
            if text and text not in merged:
                merged.append(text)
            if len(merged) >= 6:
                break
        return merged[:6]

    @staticmethod
    def _repair_text_list(value: Any, fallback: list[str]) -> list[str]:
        if isinstance(value, list):
            items = [str(item).strip() for item in value if str(item).strip()]
            if items:
                return items
        if isinstance(value, str) and value.strip():
            return [item.strip() for item in value.replace("；", ";").split(";") if item.strip()]
        return fallback

    @staticmethod
    def _first_sentence(text: str) -> str:
        import re

        parts = [item.strip() for item in re.split(r"(?<=[。！？；;])", text) if item.strip()]
        return "".join(parts[:2]) if parts else text[:120]

    @staticmethod
    def _extract_steps_from_text(text: str) -> list[str]:
        import re

        patterns = [
            r"(?:步骤[:：]\s*)?(\d+)[)）.、]\s*([^；;。]+)",
            r"第[一二三四五六七八九十]+步[:：]\s*([^；;。]+)",
        ]
        steps: list[str] = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                value = match.group(match.lastindex or 1).strip()
                if value and value not in steps:
                    steps.append(value)
        return steps

    @staticmethod
    def _derive_steps(body: str, heading: str, next_action: str) -> list[str]:
        import re

        sentences = [item.strip() for item in re.split(r"[。！？；;]", body) if len(item.strip()) > 8]
        first_fact = sentences[0] if sentences else f"理解“{heading}”的基本含义"
        example_sentence = next((item for item in sentences if any(word in item for word in ["例如", "例子", "比如"])), "")
        return [
            f"先读懂本节主结论：{first_fact}。",
            f"再整理“{heading}”涉及的条件、对象和结论，并写成自己的笔记。",
            example_sentence or f"然后选一个与“{heading}”相关的小例子，按本节规则完整演示一遍。",
            f"最后做一道与“{heading}”相关的同类题，记录自己卡住的具体步骤。",
        ]

    @staticmethod
    def _derive_key_points(body: str, heading: str) -> list[str]:
        import re

        sentences = [item.strip() for item in re.split(r"[。！？；;]", body) if item.strip()]
        matched = [item for item in sentences if any(word in item for word in ["核心", "概念", "关键", "规则", "方法", "条件", "例"])]
        if matched:
            return matched[:4]
        return [f"理解“{heading}”的核心对象", "明确适用条件", "掌握操作顺序", "能用例题验证"]

    @staticmethod
    def _derive_mistakes(body: str, heading: str) -> list[str]:
        import re

        sentences = [item.strip() for item in re.split(r"[。！？；;]", body) if item.strip()]
        matched = [item for item in sentences if any(word in item for word in ["易错", "错误", "注意", "不能", "不要", "混淆"])]
        if matched:
            return matched[:3]
        return [f"学习“{heading}”时容易只记结论，忽略条件和步骤。", "做题后只看答案，不复盘错误发生在哪一步。"]

    @staticmethod
    def _derive_example(body: str, heading: str, task_title: str) -> str:
        import re

        sentences = [item.strip() for item in re.split(r"[。！？；;]", body) if item.strip()]
        for sentence in sentences:
            if "例如" in sentence or "例子" in sentence or "比如" in sentence:
                return sentence
        return f"学习“{task_title}”时，可以选一道与“{heading}”相关的小题，把条件、规则和结论逐步写出来。"

    @staticmethod
    def _derive_self_check(heading: str) -> str:
        return f"不看资料时，能否说清“{heading}”的适用条件，并独立完成一个小例子？"

    @staticmethod
    def _focus_title(title: str, task_title: str, type_: str) -> str:
        focus = title.replace(f"· {type_}", "").replace(type_, "").strip(" ：:-")
        return focus or task_title

    @staticmethod
    def _clean_option(value: str) -> str:
        import re

        return re.sub(r"^[A-Da-d][.、\s]+", "", value).strip()

    @staticmethod
    def _options_are_only_labels(options: Any) -> bool:
        import re

        if not isinstance(options, list) or not options:
            return True
        return all(bool(re.fullmatch(r"[A-Da-d]", str(item).strip())) for item in options)

    @staticmethod
    def _extract_inline_options(stem: str) -> tuple[str, list[str]]:
        import re

        first = re.search(r"\sA[.、]\s*", stem)
        if not first:
            return stem, []
        question_text = stem[: first.start()].strip()
        options_text = stem[first.start():].strip()
        matches = re.findall(r"([A-Da-d])[.、]\s*(.*?)(?=\s+[A-Da-d][.、]\s*|$)", options_text)
        options = [text.strip() for _, text in matches if text.strip()]
        return (question_text or stem, options) if len(options) >= 2 else (stem, [])

    @staticmethod
    def _normalize_answer(answer: str, options: list[str]) -> str:
        if not options:
            return answer
        trimmed = answer.strip()
        if len(trimmed) == 1 and trimmed.upper() in {"A", "B", "C", "D"}:
            return trimmed.upper()
        for index, option in enumerate(options):
            label = chr(65 + index)
            if trimmed == option or trimmed in option or option in trimmed:
                return label
        return trimmed[:1].upper() if trimmed else trimmed

    @staticmethod
    def _repair_nodes(nodes: Any, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not isinstance(nodes, list):
            return fallback
        repaired = []
        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            label = node.get("label") or node.get("name") or node.get("title") or node.get("text")
            if not str(label or "").strip():
                continue
            repaired.append({
                "id": str(node.get("id") or f"n{index + 1}"),
                "label": str(label),
                **{key: value for key, value in node.items() if key not in {"id", "label", "name", "title", "text"}},
            })
        return repaired or fallback

    @staticmethod
    def _repair_edges(edges: Any, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not isinstance(edges, list):
            return fallback
        repaired = []
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source = edge.get("source") or edge.get("from")
            target = edge.get("target") or edge.get("to")
            if not source or not target:
                continue
            repaired.append({
                "source": str(source),
                "target": str(target),
                "label": str(edge.get("label") or edge.get("relation") or "关联"),
            })
        return repaired or fallback

    @staticmethod
    def description(type_: str, next_action: str) -> str:
        return f"围绕“{next_action}”生成的{type_}，可直接进入学习使用。"

    @staticmethod
    def markdown_from_detail(type_: str, detail: dict[str, Any], task_title: str) -> str:
        if type_ == RESOURCE_TYPE_LECTURE:
            sections = detail.get("sections", [])
            blocks = []
            for item in sections:
                steps = "\n".join(f"{index + 1}. {step}" for index, step in enumerate(item.get("steps", [])))
                key_points = "；".join(item.get("key_points", []))
                mistakes = "；".join(item.get("common_mistakes", []))
                blocks.append(
                    f"## {item.get('heading')}\n"
                    f"{item.get('body')}\n\n"
                    f"### 学习步骤\n{steps}\n\n"
                    f"### 理解要点\n{key_points}\n\n"
                    f"### 易错提醒\n{mistakes}\n\n"
                    f"### 例子\n{item.get('example', '')}\n\n"
                    f"### 自检\n{item.get('self_check', '')}"
                )
            return "\n\n".join(blocks)
        if type_ == RESOURCE_TYPE_EXERCISE:
            return "\n\n".join(f"{i + 1}. {q.get('stem')}" for i, q in enumerate(detail.get("questions", [])))
        if type_ in {RESOURCE_TYPE_MINDMAP, RESOURCE_TYPE_KG}:
            nodes = "、".join(item.get("label", "") for item in detail.get("nodes", []))
            return f"## {task_title}\n\n节点：{nodes}"
        if type_ == RESOURCE_TYPE_READING:
            return f"## 拓展阅读\n\n{detail.get('summary', '')}"
        if type_ == RESOURCE_TYPE_CODE:
            return f"## 代码案例\n\n```python\n{detail.get('starter_code', '')}\n```"
        return str(detail)
