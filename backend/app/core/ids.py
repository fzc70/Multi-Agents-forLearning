from uuid import uuid4


def new_id(prefix: str) -> str:
    """生成带业务前缀的唯一标识。"""
    return f"{prefix}_{uuid4().hex[:12]}"
