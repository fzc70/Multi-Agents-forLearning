import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./data/test_app.db"


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束后删除临时数据库。"""
    Path("data/test_app.db").unlink(missing_ok=True)
