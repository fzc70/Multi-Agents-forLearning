# 后端完整实现计划：第一版即接入 DeepSeek 多智能体

## 结论

后端第一版不做纯 mock 后端，也不等后期再接大模型。

第一版目标就是：

```text
FastAPI + SQLite + 本地文件 + LangGraph + DeepSeek deepseek-v4-flash
```

构建完成后，你只需要在后端环境文件里填写 API Key：

```text
backend/.env
```

核心配置：

```env
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
LLM_PROVIDER=deepseek
```

我已联网确认：DeepSeek 官方 API 文档当前 Flash 模型名是：

```text
deepseek-v4-flash
```

官方文档还说明：

```text
OpenAI-compatible Base URL: https://api.deepseek.com
deepseek-chat / deepseek-reasoner 将在 2026-07-24 后废弃
```

所以本项目后端第一版直接使用：

```text
model = deepseek-v4-flash
```

## 核心目标

一次性构建一个完整可运行后端，支持当前前端 6 个页面：

```text
任务 / 画像 / 对话 / 资源 / 路径 / 评估
```

并且具备真实多智能体能力：

```text
Intent Agent
Profile Agent
Tutor Agent
Resource Agent
Planner Agent
Evaluator Agent
KG Agent
```

第一版必须做到：

- 后端可启动。
- 前端可联调。
- DeepSeek API 可真实调用。
- 无 API Key 时启动阶段给出明确错误，不静默假装成功。
- Agent 运行有日志。
- LLM 输出经过 JSON Schema 校验。
- 上传资料可解析。
- 对话、画像、资源、路径、评估能形成闭环。

## 实现原则

### 1. 不做超级 Agent

每个 Agent 只负责一件事：

| Agent | 职责 |
|---|---|
| Intent Agent | 判断用户意图、主题、是否需要资料检索 |
| Profile Agent | 从对话、资料、评估中抽取画像更新 patch |
| Tutor Agent | 个性化答疑、讲解、学习引导 |
| Resource Agent | 生成讲解文档、练习题、思维导图、拓展阅读、视频脚本、代码案例、知识图谱结构 |
| Planner Agent | 生成和调整学习路径 |
| Evaluator Agent | 学习效果评估、薄弱点、下一步建议 |
| KG Agent | 抽取知识图谱 nodes / edges |

### 2. Agent 不直接写数据库

```text
Agent -> 输出 JSON
Workflow -> 校验 JSON
Service -> 保存数据库
```

### 3. Service 不写 Prompt

Prompt 只放在：

```text
backend/app/agents/prompts/
```

### 4. API 不直接调用 LLM

```text
API -> Service -> Workflow -> Agent -> LLMAdapter
```

### 5. 第一版真实 DeepSeek，测试才允许 FakeLLM

运行模式分两种：

```env
LLM_PROVIDER=deepseek
```

用于正常运行。

```env
LLM_PROVIDER=fake
```

只用于自动化测试或离线测试。

不能把 fake 当成主实现。

## 目标目录结构

```text
backend/
  app/
    main.py
    api/
      router.py
      health.py
      tasks.py
      profile.py
      materials.py
      chat.py
      resources.py
      learning_path.py
      assessment.py
      agent_runs.py
    schemas/
      common.py
      task.py
      profile.py
      material.py
      chat.py
      resource.py
      learning_path.py
      assessment.py
      agent_run.py
    domain/
      enums.py
      models.py
    services/
      task_service.py
      profile_service.py
      material_service.py
      chat_service.py
      resource_service.py
      learning_path_service.py
      assessment_service.py
      memory_service.py
      agent_log_service.py
    workflows/
      state.py
      chat_profile_workflow.py
      material_ingestion_workflow.py
      resource_generation_workflow.py
      learning_path_workflow.py
      assessment_workflow.py
      knowledge_graph_workflow.py
    agents/
      base.py
      intent_agent.py
      profile_agent.py
      tutor_agent.py
      resource_agent.py
      planner_agent.py
      evaluator_agent.py
      kg_agent.py
      prompts/
        intent_agent_v1.md
        profile_agent_v1.md
        tutor_agent_v1.md
        resource_agent_v1.md
        planner_agent_v1.md
        evaluator_agent_v1.md
        kg_agent_v1.md
    repositories/
      base.py
      task_repo.py
      profile_repo.py
      material_repo.py
      conversation_repo.py
      resource_repo.py
      learning_path_repo.py
      assessment_repo.py
      memory_repo.py
      agent_run_repo.py
    storage/
      database.py
      file_store.py
      vector_store.py
      graph_store.py
    ingestion/
      pdf_parser.py
      chunker.py
    llm/
      adapter.py
      deepseek_adapter.py
      fake_adapter.py
      json_parser.py
    tools/
      retrieval_tool.py
      grading_tool.py
      graph_tool.py
      code_runner_tool.py
    core/
      config.py
      errors.py
      logging.py
      ids.py
  data/
    materials/
    resources/
    graphs/
    vector/
    app.db
  tests/
  .env.example
  requirements.txt
  README.md
```

## 配置设计

必须提供：

```text
backend/.env.example
```

内容：

```env
APP_NAME=multi-agent-learning-backend
ENV=dev

DATABASE_URL=sqlite:///./data/app.db
DATA_DIR=./data

LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
LLM_TEMPERATURE=0.2
LLM_TIMEOUT_SECONDS=60
LLM_MAX_RETRIES=2

CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

构建完成后我会提醒你：

```text
复制 backend/.env.example 为 backend/.env
填写 DEEPSEEK_API_KEY
```

## DeepSeek 调用方式

DeepSeek 使用 OpenAI-compatible API。

后端统一用 OpenAI SDK 兼容方式：

```python
from openai import OpenAI

client = OpenAI(
    api_key=settings.deepseek_api_key,
    base_url=settings.deepseek_base_url,
)

response = client.chat.completions.create(
    model=settings.deepseek_model,
    messages=messages,
    temperature=0.2,
    response_format={"type": "json_object"},
)
```

所有 Agent 默认调用：

```text
deepseek-v4-flash
```

需要强推理时，后续可加：

```text
deepseek-v4-pro
```

但第一版统一用 `deepseek-v4-flash`，减少复杂度。

## 数据库第一版必须实现

第一版就实现这些表：

```text
students
learning_tasks
student_profiles
profile_dimensions
materials
material_chunks
conversations
messages
learning_resources
learning_paths
learning_steps
assessment_results
memory_records
workflow_runs
agent_run_logs
```

可后补但预留接口：

```text
exercises
exercise_attempts
recommendations
knowledge_graphs
graph_nodes
graph_edges
```

## API 第一版必须实现

### Health

```http
GET /api/health
```

### 任务

```http
GET  /api/tasks?student_id=default
POST /api/tasks
GET  /api/tasks/{task_id}
```

### 画像

```http
GET /api/tasks/{task_id}/profile
```

### 学习资料

```http
GET    /api/tasks/{task_id}/materials
POST   /api/tasks/{task_id}/materials/upload
DELETE /api/tasks/{task_id}/materials/{material_id}
```

### 对话

```http
GET  /api/tasks/{task_id}/messages
POST /api/chat
```

### 资源

```http
GET  /api/tasks/{task_id}/resources
POST /api/tasks/{task_id}/resources/generate
POST /api/tasks/{task_id}/resources/{resource_id}/use
POST /api/tasks/{task_id}/resources/{resource_id}/attach-to-path
```

### 路径

```http
GET  /api/tasks/{task_id}/learning-path
POST /api/tasks/{task_id}/learning-path/adjust
```

### 评估

```http
GET  /api/tasks/{task_id}/assessment
POST /api/tasks/{task_id}/assessments/run
```

### Agent 日志

```http
GET /api/tasks/{task_id}/agent-runs
```

## 多智能体工作流第一版要求

### ChatProfileWorkflow

触发：

```text
POST /api/chat
```

必须真实调用：

```text
Intent Agent
Tutor Agent
Profile Agent
```

如果意图建议资源，再调用：

```text
Resource Agent
```

必须落库：

```text
messages
profile_dimensions
memory_records
workflow_runs
agent_run_logs
```

### ResourceGenerationWorkflow

触发：

```text
POST /api/tasks/{task_id}/resources/generate
```

必须真实调用：

```text
Resource Agent
```

输入必须包含：

```text
task
profile summary
current path
latest assessment
retrieved material chunks
```

输出必须包含：

```text
type
title
description
content_json
recommendation_reason
source_refs
```

### LearningPathWorkflow

触发：

```text
POST /api/tasks/{task_id}/learning-path/adjust
```

必须真实调用：

```text
Planner Agent
```

必须生成新版本路径，不直接覆盖旧版本。

### AssessmentWorkflow

触发：

```text
POST /api/tasks/{task_id}/assessments/run
```

必须真实调用：

```text
Evaluator Agent
Profile Agent
Planner Agent 可选
```

### MaterialIngestionWorkflow

触发：

```text
POST /api/tasks/{task_id}/materials/upload
```

不需要 LLM。

必须完成：

```text
保存文件
抽取文本
切片
建立本地检索索引
写入 materials / material_chunks
```

### KnowledgeGraphWorkflow

第一版可先不接前端页面，但后端必须实现基础能力：

```text
POST /api/tasks/{task_id}/knowledge-graph/generate
```

调用：

```text
KG Agent
Graph Tool
```

保存：

```text
data/graphs/{task_id}/{graph_id}.json
```

## 防幻觉第一版要求

第一版必须具备最小防幻觉闭环：

```text
1. Tutor / Resource / KG Agent 输入必须带 retrieved_context。
2. 输出必须有 source_refs。
3. 如果没有资料依据，grounded=false。
4. 前端可暂不展示，但 API 要返回 sources。
5. AgentRunLog 记录完整输入输出。
6. LLM 输出 JSON 解析失败必须重试。
7. 重试仍失败，返回明确错误，不写入业务表。
```

## 测试要求

第一版后端完成后必须能跑：

```bash
cd backend
python -m pytest
```

必须覆盖：

```text
health
task create/list
profile get
material upload/list
chat send
resource generate
path get/adjust
assessment run
agent runs list
```

其中 LLM 测试分两类：

```text
单元测试：LLM_PROVIDER=fake
联调测试：LLM_PROVIDER=deepseek，需要真实 API Key
```

## 前后端联调顺序

虽然第一版就有 DeepSeek，但实现仍按这个顺序保证可控：

```text
1. FastAPI 工程、配置、CORS、错误处理。
2. SQLite 数据库、Repository、初始 seed 数据。
3. Task/Profile/Path 基础 API。
4. Material 上传和 PDF 解析。
5. DeepSeek LLMAdapter 连通测试。
6. Agent 基类、Prompt、JSON Schema 校验、AgentRunLog。
7. ChatProfileWorkflow。
8. ResourceGenerationWorkflow。
9. LearningPathWorkflow。
10. AssessmentWorkflow。
11. KnowledgeGraphWorkflow 基础接口。
12. 前端逐页接 API。
13. 修联调 bug。
```

## 质量门禁

每个阶段完成后必须检查：

```text
1. 后端能启动。
2. 测试通过。
3. API 返回字段和前端一致。
4. Agent 输出可解析。
5. AgentRunLog 有记录。
6. 没有 API 直接调用 LLM。
7. 没有 Agent 直接写数据库。
```

## 启动方式目标

最终启动：

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
# 在 .env 填写 DEEPSEEK_API_KEY
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```text
http://127.0.0.1:8000/api/health
```

## 我后续实现时的完成标准

你让我开始实现后，我必须完成到以下程度再交付：

```text
1. backend/app/main.py 存在并可启动。
2. backend/.env.example 明确标出 DEEPSEEK_API_KEY 填写位置。
3. DeepSeek deepseek-v4-flash 真实调用链路存在。
4. 7 个 Agent 文件存在并接入工作流。
5. API 覆盖当前前端页面。
6. SQLite 表自动初始化。
7. PDF 上传可解析。
8. AgentRunLog 可查询。
9. pytest 通过。
10. 给出启动命令和 API Key 填写说明。
```

