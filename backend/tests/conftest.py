import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./data/test_app.db"


def pytest_sessionfinish(session, exitstatus):  # type: ignore[no-untyped-def]
    Path("data/test_app.db").unlink(missing_ok=True)
