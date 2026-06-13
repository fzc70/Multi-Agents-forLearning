# 12. 基于当前前端的后端架构梳理

## 目标

当前前端已经形成 6 个学生端页面：

```text
任务 / 画像 / 对话 / 资源 / 路径 / 评估
```

后端第一阶段应围绕这 6 个页面建立稳定 API 和领域模型，先保证前后端可联调，再逐步接入真实多智能体、资料检索和 LLM。

核心原则：

- 前端只展示和交互，不写复杂业务逻辑。
- API 只校验参数和调用 Service。
- Service 负责业务用例和数据保存。
- Workflow 负责编排 Agent / Tool。
- Agent 只输出结构化 JSON，不直接读写数据库。
- 所有画像、资源、路径、评估结果必须可追踪 evidence。

## 后端分层

```text
backend/
  app/
    api/              # FastAPI 路由，只收参、鉴权、调 Service
    schemas/          # Pydantic 请求/响应 DTO
    domain/           # 领域实体和枚举
    services/         # 任务、画像、资料、对话、资源、路径、评估用例
    workflows/        # LangGraph 工作流
    agents/           # 7 个核心 Agent
    repositories/     # SQLite/PostgreSQL 数据访问
    storage/          # 文件、向量库、图谱文件适配
    ingestion/        # PDF 解析、切片、入库流程
    llm/              # DeepSeek/OpenAI-compatible 适配器
    tools/            # 检索、图谱、评分、代码运行等确定性工具
    core/             # 配置、日志、错误、依赖注入
```

依赖方向：

```text
api -> service -> workflow -> agent -> llm/tools
service -> repository -> storage/db
workflow -> tool node
```

禁止：

```text
api -> agent
api -> llm
agent -> repository
agent -> database
React 页面 -> 业务流程
```

## 当前前端页面到后端模块映射

| 前端页面 | 主要能力 | 后端 API | Service | Workflow | Agent |
|---|---|---|---|---|---|
| 任务 | 创建任务、切换任务、查看任务概览 | `/api/tasks` | TaskService | 无/可选 InitTaskWorkflow | Profile Agent 可选 |
| 画像 | 查看画像维度、证据、可信度 | `/api/tasks/{task_id}/profile` | ProfileService | ChatProfileWorkflow / AssessmentWorkflow 更新 | Profile Agent |
| 对话 | 问答、画像随学更新、资源建议 | `/api/chat` | ChatService | ChatProfileWorkflow | Intent/Tutor/Profile/Resource |
| 资源 | 上传资料、生成资源、使用资源、加入路径 | `/api/materials`, `/api/resources` | MaterialService / ResourceService | MaterialIngestionWorkflow / ResourceGenerationWorkflow | Resource Agent |
| 路径 | 查看路径、调整路径、生成配套资源 | `/api/learning-paths` | LearningPathService | LearningPathWorkflow | Planner Agent |
| 评估 | 开始测评、查看诊断、生成练习 | `/api/assessments`, `/api/exercises` | AssessmentService / ExerciseService | AssessmentWorkflow | Evaluator/Profile/Planner |

## API 设计建议

### 1. 任务

#### GET `/api/tasks?student_id=stu_001`

返回前端任务列表需要的完整摘要。

```json
{
  "tasks": [
    {
      "id": "task_001",
      "title": "提升议论文写作能力",
      "category": "语文",
      "next_action": "完成一段中心论点训练",
      "reason": "最近练习中观点容易分散，先练论点表达更有效。",
      "path_progress": {
        "completed": 1,
        "total": 3,
        "percent": 33
      },
      "materials_count": 2,
      "resources_count": 2,
      "exercise_count": 8,
      "updated_at": "2026-06-13T09:20:00"
    }
  ]
}
```

注意：前端当前“路径进度”应由后端返回，不再使用模糊的 `progress`。

#### POST `/api/tasks`

```json
{
  "student_id": "stu_001",
  "title": "学习现代文阅读",
  "foundation": "基础一般",
  "expected_outcome": "两周内提升正确率"
}
```

后端行为：

```text
TaskService 创建 LearningTask
ProfileService 创建初始画像版本
LearningPathService 创建初始 3 步路径
```

### 2. 画像

#### GET `/api/tasks/{task_id}/profile`

对应前端画像页。

```json
{
  "task_id": "task_001",
  "summary": "当前更适合围绕中心论点进行小步练习。",
  "version": 4,
  "average_confidence": 82,
  "dimensions": [
    {
      "id": "weakness",
      "label": "薄弱点/易错点",
      "value": "论点不够集中",
      "confidence": 88,
      "evidence": "来自最近 3 次练习",
      "updated_at": "2026-06-13T09:20:00"
    }
  ],
  "recent_evidences": [
    "最近建议：完成一段中心论点训练",
    "评估反馈：论证展开仍需加强"
  ]
}
```

画像更新只由工作流产生：

```text
ChatProfileWorkflow
AssessmentWorkflow
MaterialIngestionWorkflow 可补充资料偏好/课程背景
```

### 3. 学习资料

#### GET `/api/tasks/{task_id}/materials`

```json
{
  "materials": [
    {
      "id": "mat_001",
      "name": "chapter3.pdf",
      "type": "PDF",
      "size": "2.4 MB",
      "status": "indexed",
      "text_length": 12000,
      "used_for": ["resource_generation", "tutoring", "path_planning"],
      "updated_at": "2026-06-13T10:00:00"
    }
  ]
}
```

#### POST `/api/tasks/{task_id}/materials/upload`

`multipart/form-data`

后端链路：

```text
MaterialAPI
-> MaterialService
-> MaterialIngestionWorkflow
-> FileStorage 保存原文件
-> PDFParserTool 抽文本
-> ChunkTool 切片
-> EmbeddingTool 入向量库
-> MaterialRepository 保存 material/chunk
```

返回：

```json
{
  "material_id": "mat_001",
  "name": "chapter3.pdf",
  "status": "indexed",
  "text_length": 12000,
  "chunk_count": 42
}
```

### 4. 对话

#### POST `/api/chat`

```json
{
  "student_id": "stu_001",
  "task_id": "task_001",
  "message": "我写作文经常偏题",
  "conversation_id": null
}
```

后端链路：

```text
ChatService
-> ChatProfileWorkflow
-> Load Task/Profile/Memory
-> Intent Agent
-> Retrieval Tool: 当前任务资料 + 会话摘要
-> Tutor Agent
-> Profile Agent 输出 ProfilePatch
-> Service 保存 Message/Profile/Memory/AgentRunLog
```

返回：

```json
{
  "conversation_id": "conv_001",
  "assistant_message": {
    "id": "msg_002",
    "role": "assistant",
    "content": "可以先用一句话锁定观点..."
  },
  "profile_updated": true,
  "suggested_actions": [
    {
      "type": "generate_exercise",
      "label": "出一道小题"
    }
  ],
  "sources": [
    {
      "type": "material",
      "material_id": "mat_001",
      "page": 12
    }
  ]
}
```

### 5. 资源

#### POST `/api/tasks/{task_id}/resources/generate`

对应：

- 任务页生成资源
- 资源页生成资源
- 路径页生成配套资源
- 评估页薄弱点生成练习

```json
{
  "student_id": "stu_001",
  "mode": "smart",
  "resource_types": null,
  "topic": "中心论点表达",
  "source": "task_next_action"
}
```

自选生成：

```json
{
  "student_id": "stu_001",
  "mode": "selected",
  "resource_types": ["course_doc", "exercise", "mindmap"]
}
```

返回：

```json
{
  "resources": [
    {
      "id": "res_001",
      "type": "exercise",
      "title": "中心论点改写练习",
      "description": "把模糊观点改写为可论证观点。",
      "recommendation_reason": "当前薄弱点是论点不够集中，适合马上练习。",
      "source_refs": [
        {
          "type": "profile_dimension",
          "id": "weakness"
        }
      ],
      "created_at": "2026-06-13T10:20:00"
    }
  ]
}
```

后端链路：

```text
ResourceService
-> ResourceGenerationWorkflow
-> Load Profile/Materials/Path/Assessment
-> Retrieval Tool
-> Resource Agent
-> Validate Schema
-> Save LearningResource / Exercise
```

#### POST `/api/tasks/{task_id}/resources/{resource_id}/use`

用于前端“开始使用”。

```json
{
  "student_id": "stu_001"
}
```

后端行为：

```text
ResourceService 记录资源使用
MemoryService 写入 resource_usage
ChatService 可创建一条引导消息
```

#### POST `/api/tasks/{task_id}/resources/{resource_id}/attach-to-path`

用于“加入路径”。

```json
{
  "student_id": "stu_001",
  "step_id": "step_current"
}
```

后端行为：

```text
LearningPathService 将 resource_id 绑定到当前 step
```

### 6. 学习路径

#### GET `/api/tasks/{task_id}/learning-path`

```json
{
  "path_id": "path_001",
  "version": 2,
  "progress": {
    "completed": 1,
    "total": 3,
    "percent": 33
  },
  "current_step": {
    "id": "step_002",
    "title": "展开分论点",
    "exercise": "补全一组分论点"
  },
  "steps": [
    {
      "id": "step_001",
      "title": "明确中心论点",
      "objective": "能用一句话表达清楚自己的观点。",
      "resource_ids": ["res_001"],
      "exercise_ids": ["ex_001"],
      "status": "done"
    }
  ],
  "adjustment_note": "下一阶段已更新为：展开分论点"
}
```

#### POST `/api/tasks/{task_id}/learning-path/adjust`

用于“调整路径”。

后端链路：

```text
LearningPathService
-> LearningPathWorkflow
-> Load Profile/Assessment/ResourceUsage
-> Planner Agent
-> Save new LearningPath version
```

返回：

```json
{
  "path_id": "path_001",
  "version": 3,
  "current_step_id": "step_003",
  "adjustment_note": "下一阶段已更新为：完成短段论证",
  "progress": {
    "completed": 2,
    "total": 3,
    "percent": 67
  }
}
```

### 7. 评估

#### POST `/api/tasks/{task_id}/assessments/run`

对应“开始测评”。

```json
{
  "student_id": "stu_001",
  "mode": "quick"
}
```

后端链路：

```text
AssessmentService
-> AssessmentWorkflow
-> Load ExerciseAttempts/Chat/ResourceUsage
-> Evaluator Agent
-> Profile Agent
-> Planner Agent 可选
-> Save Assessment/ProfilePatch/PathSuggestion
```

返回：

```json
{
  "assessment_id": "assess_001",
  "score": 76,
  "mastery": "基础稳定，论证展开仍需加强",
  "weak_points": ["论点不够集中"],
  "mistake_types": ["观点泛化"],
  "next_suggestion": "建议先完成“完成短段论证”，再复盘错误原因。",
  "profile_updated": true,
  "path_adjusted": false
}
```

## 后端 Service 划分

```text
TaskService
  create_task()
  list_tasks()
  get_task_overview()

ProfileService
  get_task_profile()
  apply_profile_patch()

MaterialService
  upload_material()
  list_materials()
  delete_material()

ChatService
  send_message()
  list_messages()

ResourceService
  generate_resources()
  list_resources()
  use_resource()

LearningPathService
  get_path()
  adjust_path()
  attach_resource_to_step()

AssessmentService
  run_assessment()
  get_latest_assessment()

MemoryService
  save_memory_record()
  get_task_memory_summary()

AgentLogService
  list_agent_runs()
```

## Workflow 和 Agent 对应关系

| Workflow | 触发场景 | Agent | Tool |
|---|---|---|---|
| ChatProfileWorkflow | 对话页发送消息 | Intent / Tutor / Profile / Resource 可选 | Retrieval |
| MaterialIngestionWorkflow | 上传资料 | 无 Agent | PDFParser / Chunk / Embedding |
| ResourceGenerationWorkflow | 生成资源 | Resource | Retrieval / Mindmap / CodeRunner |
| LearningPathWorkflow | 生成/调整路径 | Planner | ResourceIndex |
| AssessmentWorkflow | 开始测评/提交练习 | Evaluator / Profile / Planner | Grading |
| KnowledgeGraphWorkflow | 后续图谱页 | KG | Retrieval / Graph |

## 数据表优先级

第一阶段联调必须先有：

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

第二阶段再补：

```text
exercises
exercise_attempts
recommendations
knowledge_graphs
graph_nodes
graph_edges
```

## 前后端联调顺序

建议不要一开始就接完整多智能体。按这个顺序最稳：

```text
1. 任务 CRUD + 任务概览
2. 路径 GET + 路径进度
3. 画像 GET
4. 资料上传 + 资料列表
5. 对话 POST + 消息列表
6. 资源生成 + 资源列表
7. 资源开始使用 / 加入路径
8. 评估运行 + 评估结果
9. 接入真实 LangGraph Workflow
10. 接入真实 LLM / Retrieval / AgentRunLog
```

## 与当前前端最需要对齐的字段

前端当前最依赖这些字段：

```text
LearningTask:
  id
  title
  category
  nextAction
  reason
  materialsCount
  exerciseCount
  resources[]
  path[]
  assessment
  messages
  profile
  materials
  pathAdjustmentNote

StudentProfile:
  summary
  dimensions[]
  recentEvidences[]

LearningMaterial:
  id
  name
  type
  size
  status
  textLength
  usedFor
  updatedAt

LearningResource:
  id
  type
  title
  description
  recommendationReason 后端建议新增

LearningStep:
  id
  title
  objective
  resource
  exercise
  status

Assessment:
  score
  mastery
  weakPoints
  mistakeTypes
  effort
  nextSuggestion
  tested
```

后端建议使用 snake_case，前端 API client 统一转换为 camelCase。

## 关键工程约束

- 画像更新必须有 evidence。
- 资源推荐必须有 reason。
- 资源生成必须记录 source_refs。
- 路径调整必须生成新 version，不直接覆盖旧路径。
- 评估结果必须能反向影响画像和路径。
- 上传资料必须先入库，再进入解析工作流。
- LLM 输出必须过 Pydantic schema 校验。
- AgentRunLog 必须记录 input/output/prompt_version/model。

