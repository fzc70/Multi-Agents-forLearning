from datetime import datetime, timezone


def now_iso() -> str:
    """返回 ISO 格式的当前 UTC 时间。"""
    return datetime.now(timezone.utc).isoformat()
