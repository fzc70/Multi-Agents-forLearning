"""学习分析规则。

这些规则只作为 LLM 不可用时的降级方案；正常路径仍由 Agent 调用大模型输出结构化 JSON。
规则集中管理，避免关键词、默认错因和默认建议散落在各个 Agent 里。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DimensionRule:
    dimension_id: str
    patterns: tuple[str, ...]
    evidence_label: str


@dataclass(frozen=True)
class IntentRule:
    intent: str
    patterns: tuple[str, ...]
    need_retrieval: bool = True


PROFILE_RULES = (
    DimensionRule(
        "weakness",
        (r"不会|不懂|困难|卡住|出错|错题|薄弱|混淆|看不懂",),
        "来自对话中的困难表达",
    ),
    DimensionRule(
        "goal", (r"目标|希望|想要|准备|提升|掌握|通过|学会",), "来自对话中的目标表达"
    ),
    DimensionRule(
        "preference",
        (r"例子|代码|视频|图|练习|文档|案例|动画|实操",),
        "来自对话中的资源偏好",
    ),
    DimensionRule(
        "foundation",
        (r"基础|学过|没学过|入门|零基础|复习|了解过",),
        "来自对话中的基础描述",
    ),
)

INTENT_RULES = (
    IntentRule(
        "generate_resource", (r"生成|资料|资源|练习|题|文档|导图|图谱|阅读|案例",)
    ),
    IntentRule("plan", (r"路径|计划|下一步|安排|顺序|怎么学",)),
    IntentRule("assessment", (r"测评|测试|掌握|评分|评估|检测",)),
    IntentRule(
        "profile_update",
        (r"我的基础|我的目标|我喜欢|我希望|我想要",),
        need_retrieval=False,
    ),
)

EMPTY_MEANING_WORDS = {
    "无",
    "暂无",
    "没有",
    "无明显",
    "暂无明显",
    "none",
    "null",
    "n/a",
}

KG_STOP_WORDS = {
    "我们",
    "可以",
    "当前",
    "学习",
    "资料",
    "任务",
    "这个",
    "一个",
    "进行",
    "完成",
}
KG_MINIMAL_NODES = ("学习目标", "核心概念", "练习反馈", "下一步计划")


def match_rules(text: str, rules: tuple[DimensionRule, ...]) -> list[DimensionRule]:
    """返回与输入文本匹配的画像规则。"""
    return [
        rule
        for rule in rules
        if any(re.search(pattern, text, re.I) for pattern in rule.patterns)
    ]


def infer_intent(text: str) -> dict[str, Any]:
    """使用确定性降级规则识别用户意图。"""
    for rule in INTENT_RULES:
        if any(re.search(pattern, text, re.I) for pattern in rule.patterns):
            return {
                "intent": rule.intent,
                "need_retrieval": rule.need_retrieval,
                "confidence": 66,
            }
    return {"intent": "tutoring", "need_retrieval": True, "confidence": 52}


def clean_meaningful_values(values: Any) -> list[str]:
    """移除空值并按原顺序去重。"""
    cleaned = []
    for value in values:
        text = str(value or "").strip()
        if (
            not text
            or text.lower() in EMPTY_MEANING_WORDS
            or text.startswith(("无明显", "暂无明显"))
        ):
            continue
        cleaned.append(text)
    return list(dict.fromkeys(cleaned))


def evidence_text(source: str, text: str, limit: int = 60) -> str:
    """构建可追踪的画像证据摘要。"""
    return f"{source}：{text[:limit]}"
