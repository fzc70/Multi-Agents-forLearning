import json

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.llm.adapter import DeepSeekAdapter, LLMNotConfigured
from app.schemas.agent_run import AgentRunLog
from app.schemas.assessment import AssessmentRequest
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.health import HealthResponse
from app.schemas.knowledge_graph import KnowledgeGraph, KnowledgeGraphRequest
from app.schemas.material import LearningMaterial
from app.schemas.path import AdjustPathRequest, CompleteStepRequest
from app.schemas.resource import (
    AttachResourceRequest,
    GenerateResourceRequest,
    LearningResource,
    ResourceMasteryRequest,
    SubmitExerciseRequest,
)
from app.schemas.responses import GenerateResourceResponse, SubmitExerciseResponse
from app.schemas.task import CreateTaskRequest, LearningTask
from app.services.agent_run_service import AgentRunService
from app.services.assessment_service import AssessmentService
from app.services.chat_service import ChatService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.learning_path_service import LearningPathService
from app.services.material_service import MaterialService
from app.services.resource_service import ResourceService
from app.services.task_service import TaskService

router = APIRouter(prefix="/api")
v1 = APIRouter(prefix="/v1")


@router.get("/health", response_model=HealthResponse)
def health() -> dict:
    """返回后端基础健康状态。"""
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "llm_provider": settings.llm_provider,
        "model": settings.deepseek_model,
        "api_key_configured": bool(settings.deepseek_api_key),
    }


@router.get("/health/llm")
def health_llm() -> dict:
    """通过真实请求验证大模型配置。"""
    settings = get_settings()
    if not settings.deepseek_api_key:
        return {
            "status": "not_configured",
            "message": "请在 backend/.env 中填写 DEEPSEEK_API_KEY",
            "model": settings.deepseek_model,
            "base_url": settings.deepseek_base_url,
        }
    try:
        adapter = DeepSeekAdapter(settings)
        output = adapter.complete_json(
            agent_name="HealthCheck",
            prompt_version="v1",
            system_prompt='只输出 JSON：{"ok":true,"message":"..."}',
            user_payload={"message": "ping"},
        )
        return {"status": "ok", "model": settings.deepseek_model, "output": output}
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "model": settings.deepseek_model,
        }


@v1.get("/tasks", response_model=list[LearningTask])
def list_tasks() -> list[dict]:
    """返回全部学习任务。"""
    return TaskService().list_tasks()


@v1.post("/tasks", response_model=LearningTask)
def create_task(payload: CreateTaskRequest) -> dict:
    """创建学习任务。"""
    return TaskService().create_task(
        payload.title, payload.foundation, payload.expected_outcome
    )


@v1.get("/tasks/{task_id}", response_model=LearningTask)
def get_task(task_id: str) -> dict:
    """返回指定学习任务。"""
    return TaskService().get_task(task_id)


@v1.delete("/tasks/{task_id}")
def delete_task(task_id: str) -> dict:
    """删除指定学习任务。"""
    return TaskService().delete_task(task_id)


@v1.get("/profile/{task_id}")
def get_profile(task_id: str) -> dict:
    """返回任务对应的学生画像。"""
    return TaskService().get_task(task_id)["profile"]


@v1.get("/materials", response_model=list[LearningMaterial])
def list_materials(task_id: str = Query(...)) -> list[dict]:
    """返回任务关联的学习资料。"""
    return MaterialService().list_materials(task_id)


@v1.post("/materials/upload", response_model=LearningTask)
def upload_material(task_id: str = Query(...), file: UploadFile = File(...)) -> dict:
    """上传并解析学习资料。"""
    return MaterialService().upload_pdf(task_id, file)


@v1.delete("/materials/{material_id}", response_model=LearningTask)
def delete_material(material_id: str, task_id: str = Query(...)) -> dict:
    """删除指定学习资料。"""
    return MaterialService().delete_material(task_id, material_id)


@v1.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> dict:
    """处理非流式学习对话请求。"""
    return ChatService().chat(payload.task_id, payload.message, payload.use_rag)


@v1.post("/chat/stream")
def chat_stream(payload: ChatRequest):
    """处理流式学习对话请求。"""

    def event_stream():
        """将对话事件编码为 NDJSON 流。"""
        try:
            for event in ChatService().chat_stream_events(
                payload.task_id, payload.message, payload.use_rag
            ):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception as exc:
            yield json.dumps(
                {"type": "error", "message": f"对话服务暂时不可用：{exc}"},
                ensure_ascii=False,
            ) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@v1.post("/resources/generate", response_model=GenerateResourceResponse)
def generate_resource(payload: GenerateResourceRequest) -> dict:
    """生成个性化学习资源。"""
    return ResourceService().generate(payload.task_id, payload.types, payload.mode)


@v1.post("/resources/{resource_id}/attach-to-path", response_model=LearningTask)
def attach_resource_to_path(resource_id: str, payload: AttachResourceRequest) -> dict:
    """将资源关联到当前学习路径步骤。"""
    return ResourceService().attach_to_path(payload.task_id, resource_id)


@v1.get("/resources/{resource_id}", response_model=LearningResource)
def get_resource(resource_id: str, task_id: str = Query(...)) -> dict:
    """返回完整学习资源。"""
    return ResourceService().get_resource(task_id, resource_id)


@v1.post("/resources/{resource_id}/submit", response_model=SubmitExerciseResponse)
def submit_resource(resource_id: str, payload: SubmitExerciseRequest) -> dict:
    """批改已提交的练习答案。"""
    return ResourceService().submit_exercise(
        payload.task_id, resource_id, payload.answers
    )


@v1.post("/resources/{resource_id}/mastery", response_model=LearningTask)
def mark_resource_mastery(resource_id: str, payload: ResourceMasteryRequest) -> dict:
    """记录学生自报的资源掌握度。"""
    return ResourceService().mark_mastery(
        payload.task_id, resource_id, payload.mastery, payload.note
    )


@v1.post("/learning-path/adjust", response_model=LearningTask)
def adjust_path(payload: AdjustPathRequest) -> dict:
    """调整当前学习路径。"""
    return LearningPathService().adjust(payload.task_id, payload.reason)


@v1.post("/learning-path/complete-step", response_model=LearningTask)
def complete_step(payload: CompleteStepRequest) -> dict:
    """将学习路径步骤标记为已完成。"""
    return LearningPathService().complete_step(payload.task_id, payload.step_id)


@v1.post("/assessment/run", response_model=LearningTask)
def run_assessment(payload: AssessmentRequest) -> dict:
    """执行学习效果评估。"""
    return AssessmentService().assess(payload.task_id, payload.answers)


@v1.post("/knowledge-graph/build", response_model=KnowledgeGraph)
def build_kg(payload: KnowledgeGraphRequest) -> dict:
    """为任务生成知识图谱。"""
    return KnowledgeGraphService().build(payload.task_id)


@v1.get("/knowledge-graph/{task_id}", response_model=KnowledgeGraph | None)
def get_kg(task_id: str) -> dict | None:
    """返回任务最新的知识图谱。"""
    return KnowledgeGraphService().latest(task_id)


@v1.get("/agent-runs", response_model=list[AgentRunLog])
def list_agent_runs(task_id: str | None = None, limit: int = 50) -> list[dict]:
    """返回智能体运行日志。"""
    return AgentRunService().list(task_id, limit)


router.include_router(v1)
