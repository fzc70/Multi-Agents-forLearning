from __future__ import annotations

from typing import Any

from app.core.errors import bad_request
from app.services.task_service import TaskService
from app.workflows.chat_profile_workflow import ChatProfileWorkflow


class ChatService:
    """对话服务。

    负责校验请求、调用 ChatProfileWorkflow，并把最新任务聚合结果返回给前端。
    """

    def __init__(self) -> None:
        """初始化 ChatService 所需的依赖。"""
        self.tasks = TaskService()
        self.workflow = ChatProfileWorkflow()

    def chat(self, task_id: str, message: str, use_rag: bool = True) -> dict[str, Any]:
        """执行非流式学习对话。"""
        if not message.strip():
            raise bad_request("消息不能为空")
        task = self.tasks.get_task(task_id)
        result = self.workflow.run(task, message.strip(), use_rag)
        return {"task": self.tasks.get_task(task_id), **result}

    def chat_stream_events(self, task_id: str, message: str, use_rag: bool = True):
        """以事件流方式执行学习对话。"""
        if not message.strip():
            yield {"type": "error", "message": "消息不能为空"}
            return
        yield {"type": "status", "message": "thinking"}
        task = self.tasks.get_task(task_id)
        for event in self.workflow.stream_events(task, message.strip(), use_rag):
            if event.get("type") == "done":
                event["task"] = self.tasks.get_task(task_id)
            yield event
