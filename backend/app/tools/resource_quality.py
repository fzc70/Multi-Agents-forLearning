from __future__ import annotations

from typing import Any


RESOURCE_TYPES = {"讲解文档", "练习题", "思维导图", "拓展阅读", "代码案例", "知识图谱"}


class ResourceQualityGate:
    """保证资源内容结构完整，LLM 输出缺字段时进行确定性补齐。"""

    def normalize(self, resource: dict[str, Any], task_title: str, next_action: str) -> dict[str, Any]:
        type_ = str(resource.get("type") or "讲解文档")
        if type_ not in RESOURCE_TYPES:
            type_ = "讲解文档"
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
        if type_ == "练习题":
            return {
                "instructions": "先独立完成，再提交答案。系统会根据正确率、答题完整度和错因给出反馈。",
                "questions": [
                    {
                        "id": "q1",
                        "type": "single_choice",
                        "stem": f"学习“{task_title}”时，最适合作为第一步的是？",
                        "options": ["直接背最终结论", "先明确核心概念、适用条件和基本步骤", "只做高难题", "跳过例题直接测验"],
                        "answer": "B",
                        "analysis": "基础阶段先建立概念、条件和步骤，后续做题才有依据。",
                        "difficulty": "基础",
                        "knowledge_points": [task_title, next_action],
                    },
                    {
                        "id": "q2",
                        "type": "short_answer",
                        "stem": f"请用 2-3 句话说明“{task_title}”主要解决什么问题，以及为什么要学它。",
                        "answer": "能说清它处理的问题、适用场景和学习价值。",
                        "analysis": "好的答案不只是复述名词，还要说明问题、场景和价值。",
                        "difficulty": "基础",
                        "knowledge_points": [task_title],
                    },
                    {
                        "id": "q3",
                        "type": "short_answer",
                        "stem": f"结合“{next_action}”，写出你完成本阶段学习后应达到的 3 个检查标准。",
                        "answer": "能复述核心概念、能完成基础题、能解释错因或迁移到新例子。",
                        "analysis": "检查标准要可观察、可验证，不能只写“我看懂了”。",
                        "difficulty": "进阶",
                        "knowledge_points": ["学习评估", "复盘"],
                    },
                    {
                        "id": "q4",
                        "type": "single_choice",
                        "stem": "如果练习中连续出错，最合适的处理方式是？",
                        "options": ["继续刷更多题", "只看正确答案", "回到概念和错因重新梳理", "直接跳到下一章"],
                        "answer": "C",
                        "analysis": "连续出错通常说明概念或方法没有稳定，需要先定位错因再练。",
                        "difficulty": "进阶",
                        "knowledge_points": ["错因分析", task_title],
                    },
                    {
                        "id": "q5",
                        "type": "short_answer",
                        "stem": f"请给“{task_title}”设计一个 10 分钟复盘步骤，要求包含回忆、纠错和验证。",
                        "answer": "先不看资料复述概念，再回看错题定位错因，最后用一道同类题验证。",
                        "analysis": "好的复盘应包含回忆、纠错和迁移验证。",
                        "difficulty": "综合",
                        "knowledge_points": ["复盘策略", next_action],
                    },
                ],
            }
        if type_ == "思维导图":
            return {
                "center": task_title,
                "nodes": [
                    {"id": "n1", "label": task_title, "level": 0},
                    {"id": "n2", "label": "先理解概念", "level": 1},
                    {"id": "n3", "label": "再掌握方法", "level": 1},
                    {"id": "n4", "label": "最后完成练习", "level": 1},
                    {"id": "n5", "label": "复盘易错点", "level": 1},
                    {"id": "n6", "label": "定义与边界", "level": 2},
                    {"id": "n7", "label": next_action, "level": 2},
                    {"id": "n8", "label": "自检标准", "level": 2},
                    {"id": "n9", "label": "错因归类", "level": 2},
                ],
                "edges": [
                    {"source": "n1", "target": "n2", "label": "第一步"},
                    {"source": "n1", "target": "n3", "label": "第二步"},
                    {"source": "n1", "target": "n4", "label": "第三步"},
                    {"source": "n1", "target": "n5", "label": "复盘"},
                    {"source": "n2", "target": "n6", "label": "展开"},
                    {"source": "n3", "target": "n7", "label": "聚焦"},
                    {"source": "n4", "target": "n8", "label": "验证"},
                    {"source": "n5", "target": "n9", "label": "记录"},
                ],
            }
        if type_ == "拓展阅读":
            return {
                "summary": f"围绕“{task_title}”补充背景、应用场景和常见误区。",
                "readings": [
                    {"title": "核心概念背景", "reason": "帮助建立整体框架", "estimated_minutes": 8},
                    {"title": "典型例子与应用", "reason": "把抽象知识放到具体场景", "estimated_minutes": 10},
                    {"title": "常见错误清单", "reason": "提前避开高频误区", "estimated_minutes": 6},
                    {"title": "同类问题对比", "reason": "看清相似概念之间的边界", "estimated_minutes": 8},
                    {"title": "一页式复盘模板", "reason": "把阅读内容转化成可执行复盘", "estimated_minutes": 5},
                ],
                "guiding_questions": ["这个知识解决什么问题？", "它和已有知识有什么关系？", "最容易错在哪里？"],
            }
        if type_ == "代码案例":
            return {
                "language": "Python",
                "scenario": f"用代码演示“{task_title}”的关键步骤。",
                "starter_code": "def solve():\n    # TODO: 根据学习目标补全实现\n    pass\n",
                "tasks": ["阅读示例代码", "补全核心函数", "运行测试并解释结果"],
                "reference_solution": "def solve():\n    return '完成核心步骤后，再用测试验证结果'\n",
                "tests": ["调用 solve()，检查返回值是否符合预期"],
                "explanation": f"代码案例用于把“{next_action}”转成可执行过程。",
            }
        if type_ == "知识图谱":
            return {
                "nodes": [
                    {"id": "n1", "label": task_title, "type": "topic"},
                    {"id": "n2", "label": "前置知识", "type": "concept"},
                    {"id": "n3", "label": "核心概念", "type": "concept"},
                    {"id": "n4", "label": "关键方法", "type": "method"},
                    {"id": "n5", "label": "适用条件", "type": "condition"},
                    {"id": "n6", "label": "典型题型", "type": "example"},
                    {"id": "n7", "label": "高频误区", "type": "weakness"},
                    {"id": "n8", "label": next_action, "type": "goal"},
                    {"id": "n9", "label": "推荐资源", "type": "resource"},
                ],
                "edges": [
                    {"source": "n2", "target": "n1", "label": "支撑"},
                    {"source": "n1", "target": "n3", "label": "包含"},
                    {"source": "n3", "target": "n4", "label": "转化为方法"},
                    {"source": "n4", "target": "n5", "label": "受条件约束"},
                    {"source": "n4", "target": "n6", "label": "应用于"},
                    {"source": "n6", "target": "n7", "label": "暴露"},
                    {"source": "n7", "target": "n8", "label": "决定下一目标"},
                    {"source": "n8", "target": "n9", "label": "需要"},
                ],
            }
        return {
            "sections": [
                {
                    "heading": "你先要学会什么",
                    "body": f"本节围绕“{task_title}”展开。学完后，你至少要能说清它解决的问题、适用条件、基本步骤，以及如何用一道基础题验证自己是否掌握。",
                    "steps": [
                        f"先用一句话说明“{task_title}”解决什么问题。",
                        "列出本节出现的适用条件、对象和结论。",
                        "把概念放入一道基础题中，判断输入、规则和输出。",
                        "用自己的话复述本节结论，并指出一个可能出错的位置。",
                    ],
                    "key_points": [task_title, "适用条件", "基础题验证"],
                    "common_mistakes": ["只背概念名称，不说明解决的问题。", "忽略适用条件，导致方法乱用。"],
                    "example": f"如果学习主题是“{task_title}”，不要只写定义，还要能说明它在题目中如何被使用。",
                    "self_check": "合上资料后，能否在 1 分钟内说清本节知识的对象、条件和输出？",
                },
                {
                    "heading": "核心概念",
                    "body": f"先把“{task_title}”看成一个可以被拆解的问题：它通常包含对象、规则、步骤和结果四部分。学习时不要只记名词，要把每个概念和具体例子对应起来。",
                    "steps": [
                        "标出本节所有核心名词。",
                        "为每个名词补充一句自己的解释。",
                        "找出名词之间的顺序或依赖关系。",
                        "用一个例子验证这些名词是否能串成完整过程。",
                    ],
                    "key_points": ["对象", "规则", "步骤", "结果"],
                    "common_mistakes": ["把相近名词混用。", "只记结论，不知道步骤从哪里来。"],
                    "example": "可以把任意一道题拆成：给了什么对象、使用什么规则、经过哪些步骤、得到什么结果。",
                    "self_check": "能否把本节概念画成“对象 -> 规则 -> 步骤 -> 结果”的链条？",
                },
                {
                    "heading": "推荐学习步骤",
                    "body": f"第一步：用自己的话解释概念。第二步：列出适用条件。第三步：跟着一个例题走完整流程。第四步：不看答案独立完成一道同类题。当前重点是“{next_action}”。",
                    "steps": [
                        "用自己的话解释概念，不照抄教材定义。",
                        "列出适用条件，判断什么时候可以用这个方法。",
                        "跟着一个例题走完整流程，并标出每一步依据。",
                        "不看答案独立完成一道同类题。",
                        f"围绕“{next_action}”记录还不稳定的步骤。",
                    ],
                    "key_points": ["解释概念", "适用条件", "例题流程", next_action],
                    "common_mistakes": ["跳过适用条件直接套公式。", "例题看懂了但无法独立复现。"],
                    "example": "看完例题后，把答案遮住，只保留题干，重新写出每一步。",
                    "self_check": "同类题能否在不看答案时完成 70% 以上步骤？",
                },
                {
                    "heading": "示例化理解",
                    "body": f"遇到抽象表述时，先问三个问题：输入是什么？中间规则是什么？输出或结论是什么？把“{task_title}”放进这个框架，就能避免只背结论。",
                    "steps": [
                        "从题目中圈出输入信息。",
                        "写下本节允许使用的中间规则。",
                        "根据规则逐步推出输出或结论。",
                        "回头检查每一步是否都能对应题目条件。",
                    ],
                    "key_points": ["输入", "规则", "输出", "条件对应"],
                    "common_mistakes": ["没有确认输入就开始推。", "中间规则和题目条件对不上。"],
                    "example": "遇到抽象题时，先写“输入/规则/输出”三栏，再开始解题。",
                    "self_check": "能否把一个例题拆成输入、规则、输出三部分？",
                },
                {
                    "heading": "常见错误",
                    "body": "常见问题包括：只记结论不理解条件、例题能看懂但不会迁移、做错后只改答案不分析错因。每次出错都要写下“我错在概念、步骤、条件还是表达”。",
                    "steps": [
                        "把错题归类为概念、步骤、条件或表达问题。",
                        "回到对应知识点，补一句正确规则。",
                        "重做原题，检查错误是否消失。",
                        "再做一道同类题，验证不是只记住答案。",
                    ],
                    "key_points": ["错因分类", "规则修正", "同类验证"],
                    "common_mistakes": ["只改答案不改方法。", "错因写得太笼统，无法指导下次练习。"],
                    "example": "如果归结题出错，要标明是子句化、合一、变量替换还是归结顺序的问题。",
                    "self_check": "每道错题能否写出一个明确错因和一个修正动作？",
                },
                {
                    "heading": "学完自检",
                    "body": "关闭资料后，用 3 分钟复述核心概念；用 5 分钟完成一道基础题；最后用 2 分钟写出错因或易混点。三项都能完成，才算进入下一步。",
                    "steps": [
                        "关闭资料，复述核心概念。",
                        "限时完成一道基础题。",
                        "对照答案标出缺失步骤。",
                        "写出一个易混点和一个下次避免的方法。",
                    ],
                    "key_points": ["复述", "限时练习", "缺失步骤", "易混点"],
                    "common_mistakes": ["看着资料觉得会，合上资料不会做。", "只检查答案对错，不检查过程质量。"],
                    "example": "自检时不要只问“我懂了吗”，要问“我能独立做出一道题吗”。",
                    "self_check": "如果基础题无法独立完成，应回到前一节重新学习。",
                },
            ],
            "key_points": [task_title, next_action, "适用条件", "步骤拆解", "例子迁移", "错因复盘"],
            "checkpoints": ["能复述核心概念", "能说明适用条件", "能独立完成基础练习", "能解释错因"],
        }

    def _repair_detail(self, type_: str, detail: dict[str, Any], task_title: str, next_action: str) -> dict[str, Any]:
        fallback = self.default_detail(type_, task_title, next_action)
        if type_ == "练习题" and len(detail.get("questions", [])) < 5:
            detail["questions"] = fallback["questions"]
        if type_ == "练习题":
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
        if type_ == "讲解文档":
            detail = self._repair_lecture_detail(detail, fallback, task_title, next_action)
        if type_ in {"思维导图", "知识图谱"}:
            detail["nodes"] = self._repair_nodes(detail.get("nodes", []), fallback["nodes"])
            detail["edges"] = self._repair_edges(detail.get("edges", []), fallback["edges"])
            if len(detail.get("nodes", [])) < 8:
                detail["nodes"] = fallback["nodes"]
            if len(detail.get("edges", [])) < 7:
                detail["edges"] = fallback["edges"]
        if type_ == "拓展阅读" and len(detail.get("readings", [])) < 5:
            detail = fallback
        if type_ == "代码案例" and not detail.get("starter_code"):
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
        if type_ == "讲解文档":
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
        if type_ == "练习题":
            return "\n\n".join(f"{i + 1}. {q.get('stem')}" for i, q in enumerate(detail.get("questions", [])))
        if type_ in {"思维导图", "知识图谱"}:
            nodes = "、".join(item.get("label", "") for item in detail.get("nodes", []))
            return f"## {task_title}\n\n节点：{nodes}"
        if type_ == "拓展阅读":
            return f"## 拓展阅读\n\n{detail.get('summary', '')}"
        if type_ == "代码案例":
            return f"## 代码案例\n\n```python\n{detail.get('starter_code', '')}\n```"
        return str(detail)
