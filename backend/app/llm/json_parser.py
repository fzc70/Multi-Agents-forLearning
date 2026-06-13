import json
import re
from typing import Any


def parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("LLM 输出不是 JSON 对象")
    value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("LLM 输出不是 JSON 对象")
    return value
