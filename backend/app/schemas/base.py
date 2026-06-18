from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    """将蛇形字段名转换为小驼峰格式。"""
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class ApiModel(BaseModel):
    """API Schema 基类：统一 snake_case <-> camelCase 转换。"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
