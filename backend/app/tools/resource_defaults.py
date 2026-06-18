from __future__ import annotations

from typing import Any

from app.domain.constants import (
    RESOURCE_TYPE_CODE,
    RESOURCE_TYPE_EXERCISE,
    RESOURCE_TYPE_KG,
    RESOURCE_TYPE_LECTURE,
    RESOURCE_TYPE_MINDMAP,
    RESOURCE_TYPE_READING,
)


class ResourceDefaultFactory:
    """生成资源结构兜底模板。

    仅在 LLM 输出缺失或结构不可渲染时使用，避免前端出现空资源。
    """

    def default_detail(
        self, type_: str, task_title: str, next_action: str
    ) -> dict[str, Any]:
        """生成指定资源类型的完整降级详情。"""
        if type_ == RESOURCE_TYPE_EXERCISE:
            return {
                "instructions": "先独立完成，再提交答案。系统会根据正确率、答题完整度和错因给出反馈。",
                "questions": [
                    {
                        "id": "q1",
                        "type": "single_choice",
                        "stem": f"学习“{task_title}”时，最适合作为第一步的是？",
                        "options": [
                            "直接背最终结论",
                            "先明确核心概念、适用条件和基本步骤",
                            "只做高难题",
                            "跳过例题直接测验",
                        ],
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
                        "options": [
                            "继续刷更多题",
                            "只看正确答案",
                            "回到概念和错因重新梳理",
                            "直接跳到下一章",
                        ],
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
        if type_ == RESOURCE_TYPE_MINDMAP:
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
        if type_ == RESOURCE_TYPE_READING:
            return {
                "summary": f"围绕“{task_title}”补充背景、应用场景和常见误区。",
                "readings": [
                    {
                        "title": "核心概念背景",
                        "reason": "帮助建立整体框架",
                        "estimated_minutes": 8,
                    },
                    {
                        "title": "典型例子与应用",
                        "reason": "把抽象知识放到具体场景",
                        "estimated_minutes": 10,
                    },
                    {
                        "title": "常见错误清单",
                        "reason": "提前避开高频误区",
                        "estimated_minutes": 6,
                    },
                    {
                        "title": "同类问题对比",
                        "reason": "看清相似概念之间的边界",
                        "estimated_minutes": 8,
                    },
                    {
                        "title": "一页式复盘模板",
                        "reason": "把阅读内容转化成可执行复盘",
                        "estimated_minutes": 5,
                    },
                ],
                "guiding_questions": [
                    "这个知识解决什么问题？",
                    "它和已有知识有什么关系？",
                    "最容易错在哪里？",
                ],
            }
        if type_ == RESOURCE_TYPE_CODE:
            return {
                "language": "Python",
                "scenario": f"用代码演示“{task_title}”的关键步骤。",
                "starter_code": "def solve():\n    # TODO: 根据学习目标补全实现\n    pass\n",
                "tasks": ["阅读示例代码", "补全核心函数", "运行测试并解释结果"],
                "reference_solution": "def solve():\n    return '完成核心步骤后，再用测试验证结果'\n",
                "tests": ["调用 solve()，检查返回值是否符合预期"],
                "explanation": f"代码案例用于把“{next_action}”转成可执行过程。",
            }
        if type_ == RESOURCE_TYPE_KG:
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
                    "common_mistakes": [
                        "只背概念名称，不说明解决的问题。",
                        "忽略适用条件，导致方法乱用。",
                    ],
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
                    "common_mistakes": [
                        "把相近名词混用。",
                        "只记结论，不知道步骤从哪里来。",
                    ],
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
                    "common_mistakes": [
                        "跳过适用条件直接套公式。",
                        "例题看懂了但无法独立复现。",
                    ],
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
                    "common_mistakes": [
                        "没有确认输入就开始推。",
                        "中间规则和题目条件对不上。",
                    ],
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
                    "common_mistakes": [
                        "只改答案不改方法。",
                        "错因写得太笼统，无法指导下次练习。",
                    ],
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
                    "common_mistakes": [
                        "看着资料觉得会，合上资料不会做。",
                        "只检查答案对错，不检查过程质量。",
                    ],
                    "example": "自检时不要只问“我懂了吗”，要问“我能独立做出一道题吗”。",
                    "self_check": "如果基础题无法独立完成，应回到前一节重新学习。",
                },
            ],
            "key_points": [
                task_title,
                next_action,
                "适用条件",
                "步骤拆解",
                "例子迁移",
                "错因复盘",
            ],
            "checkpoints": [
                "能复述核心概念",
                "能说明适用条件",
                "能独立完成基础练习",
                "能解释错因",
            ],
        }
