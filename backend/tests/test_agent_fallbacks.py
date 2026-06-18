from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.intent_agent import IntentAgent
from app.agents.profile_agent import ProfileAgent


class EmptyLLM:
    """让 Agent 进入 fallback，避免测试依赖外部模型。"""

    model = "empty"

    def complete_json(self, **kwargs):
        """调用大模型并返回结构化 JSON 结果。"""
        return None


def test_profile_fallback_uses_central_rules() -> None:
    """验证画像降级逻辑能依据集中规则生成带证据的画像维度。"""
    message = "\u6211\u603b\u662f\u6df7\u6dc6\u6761\u4ef6\uff0c\u5e0c\u671b\u591a\u4e00\u70b9\u4f8b\u5b50"
    output = ProfileAgent(llm=EmptyLLM()).run({"message": message}, "task_test")
    dimensions = {item["dimension_id"] for item in output["updates"]}
    assert {"weakness", "goal", "preference"}.issubset(dimensions)


def test_intent_fallback_uses_central_rules() -> None:
    """验证意图降级逻辑能够识别资源生成请求。"""
    message = "\u5e2e\u6211\u751f\u6210\u4e00\u7ec4\u7ec3\u4e60\u9898"
    output = IntentAgent(llm=EmptyLLM()).run({"message": message}, "task_test")
    assert output["intent"] == "generate_resource"
    assert output["confidence"] < 70


def test_evaluator_fallback_depends_on_answers() -> None:
    """验证评估降级结果会随作答证据变化。"""
    output = EvaluatorAgent(llm=EmptyLLM()).run(
        {
            "task_title": "\u786e\u5b9a\u6027\u63a8\u7406",
            "answers": [
                {"correct": True, "weak_point": ""},
                {
                    "correct": False,
                    "weak_point": "\u6761\u4ef6\u5224\u65ad",
                    "mistake_type": "\u4f9d\u636e\u4e0d\u8db3",
                },
            ],
        },
        "task_test",
    )
    assert output["score"] == 50
    assert output["weak_points"] == ["\u6761\u4ef6\u5224\u65ad"]
    assert output["mistake_types"] == ["\u4f9d\u636e\u4e0d\u8db3"]
