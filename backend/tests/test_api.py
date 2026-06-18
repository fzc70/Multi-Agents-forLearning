from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    """验证后端健康检查接口。"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_task_chat_resource_path_assessment_flow() -> None:
    """验证从任务创建到学习评估的主接口链路。"""
    created = client.post(
        "/api/v1/tasks",
        json={
            "title": "测试学习任务",
            "foundation": "基础一般",
            "expectedOutcome": "掌握核心概念",
        },
    )
    assert created.status_code == 200
    task = created.json()

    chat = client.post(
        "/api/v1/chat", json={"taskId": task["id"], "message": "我想要例子讲解"}
    )
    assert chat.status_code == 200
    assert chat.json()["reply"]["role"] == "assistant"

    resource = client.post(
        "/api/v1/resources/generate",
        json={"taskId": task["id"], "types": ["讲解文档"], "mode": "selected"},
    )
    assert resource.status_code == 200
    assert resource.json()["resources"]
    assert resource.json()["resources"][0]["detail"]
    resource_id = resource.json()["resources"][0]["id"]

    attach = client.post(
        f"/api/v1/resources/{resource_id}/attach-to-path", json={"taskId": task["id"]}
    )
    assert attach.status_code == 200
    assert attach.json()["path"][0]["resource"]

    quiz = client.post(
        "/api/v1/resources/generate",
        json={"taskId": task["id"], "types": ["练习题"], "mode": "selected"},
    )
    quiz_id = quiz.json()["resources"][0]["id"]
    submit = client.post(
        f"/api/v1/resources/{quiz_id}/submit",
        json={"taskId": task["id"], "answers": {"q1": "B"}},
    )
    assert submit.status_code == 200
    assert "score" in submit.json()["result"]

    path = client.post(
        "/api/v1/learning-path/adjust",
        json={"taskId": task["id"], "reason": "根据最新练习调整"},
    )
    assert path.status_code == 200
    assert path.json()["path"]

    assessment = client.post(
        "/api/v1/assessment/run",
        json={"taskId": task["id"], "answers": [{"id": "q1", "answer": "A"}]},
    )
    assert assessment.status_code == 200
    assert assessment.json()["assessment"]["tested"] is True
