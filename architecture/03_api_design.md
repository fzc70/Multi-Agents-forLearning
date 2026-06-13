# 03. API 设计

API 层只做参数校验、鉴权、调用 Service、返回响应。API 不直接调用 Agent、Tool、LLM。

统一响应错误格式：

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "参数错误",
  "details": {}
}
```

## 1. 任务管理

### POST /api/tasks

功能：创建学习任务。

Request：

```json
{
  "student_id": "stu_001",
  "title": "人工智能导论第3章",
  "course": "人工智能导论",
  "goal": "掌握确定性推理"
}
```

Response：

```json
{
  "task_id": "task_ai_ch3",
  "status": "active",
  "created_at": "2026-06-12T21:00:00"
}
```

链路：

```text
TaskAPI -> TaskService -> TaskRepository
```

## 2. PDF / 学习资料管理

### POST /api/materials/upload

功能：上传 PDF 并触发解析、切片、向量入库。

Request：`multipart/form-data`

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai_ch3",
  "file": "chapter3.pdf"
}
```

Response：

```json
{
  "material_id": "mat_001",
  "filename": "chapter3.pdf",
  "status": "indexed",
  "page_count": 26,
  "chunk_count": 42
}
```

链路：

```text
MaterialAPI -> MaterialService -> MaterialIngestionWorkflow
Tool: PDF Parser, Chunk, Embedding, File Storage
写入: materials, material_chunks, vector collection
```

### GET /api/materials?task_id=task_ai_ch3

Response：

```json
{
  "materials": [
    {
      "material_id": "mat_001",
      "filename": "chapter3.pdf",
      "status": "indexed",
      "chunk_count": 42
    }
  ]
}
```

## 3. 对话

### POST /api/chat

功能：发送消息，触发意图识别、检索、答疑、画像更新。

Request：

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai_ch3",
  "conversation_id": null,
  "message": "我不理解归结推理，能结合例子讲吗？"
}
```

Response：

```json
{
  "conversation_id": "conv_001",
  "message_id": "msg_002",
  "answer": "归结推理可以理解为通过消去互补文字来证明结论...",
  "intent": "tutoring_question",
  "profile_updated": true,
  "profile_patch_id": "patch_001",
  "suggested_resources": [
    {
      "type": "exercise",
      "title": "归结推理入门练习"
    }
  ],
  "sources": [
    {
      "source_type": "material",
      "page": 73
    }
  ]
}
```

链路：

```text
ChatAPI -> ChatService -> ChatProfileWorkflow
Agents: Intent, Tutor, Profile, Resource
Tools: Retrieval
写入: conversations, messages, profile_dimensions, memory_records, agent_run_logs
```

## 4. 学生画像

### GET /api/profiles/{student_id}

Response：

```json
{
  "student_id": "stu_001",
  "version": 4,
  "dimensions": {
    "major": "计算机科学",
    "knowledge_level": "初中级",
    "learning_goal": "掌握人工智能基础",
    "cognitive_style": "例子驱动",
    "learning_preference": ["图解", "步骤化讲解"],
    "weak_points": ["归结推理", "MGU 算法"]
  },
  "evidence_count": 18,
  "updated_at": "2026-06-12T21:30:00"
}
```

## 5. 个性化资源生成

### POST /api/resources/generate

Request：

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai_ch3",
  "topic": "确定性推理",
  "resource_types": ["course_doc", "mindmap", "exercise", "reading", "video_script", "code_practice"]
}
```

Response：

```json
{
  "job_id": "res_job_001",
  "status": "completed",
  "resources": [
    {
      "resource_id": "res_001",
      "type": "course_doc",
      "title": "确定性推理讲解文档"
    },
    {
      "resource_id": "res_002",
      "type": "mindmap",
      "title": "归结推理思维导图"
    }
  ]
}
```

链路：

```text
ResourceAPI -> ResourceService -> ResourceGenerationWorkflow
Agent: Resource Agent
Tools: Retrieval, Mindmap, CodeRunner 可选
写入: learning_resources, agent_run_logs
```

## 6. 学习路径

### POST /api/learning-paths/generate

Request：

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai_ch3",
  "target": "两周内掌握确定性推理"
}
```

Response：

```json
{
  "path_id": "path_001",
  "version": 1,
  "steps": [
    {
      "order": 1,
      "objective": "理解推理分类",
      "recommended_resource_ids": ["res_001"],
      "exercise_ids": ["ex_001"],
      "evaluation_point": "完成基础概念题"
    }
  ]
}
```

链路：

```text
LearningPathAPI -> LearningPathService -> LearningPathWorkflow
Agent: Planner Agent
写入: learning_paths, learning_steps
```

## 7. 知识图谱

### POST /api/knowledge-graphs/generate

Request：

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai_ch3",
  "sources": ["materials", "conversations"]
}
```

Response：

```json
{
  "graph_id": "kg_001",
  "node_count": 120,
  "edge_count": 96,
  "graph": {
    "nodes": [
      {
        "id": "归结推理",
        "label": "归结推理",
        "type": "METHOD"
      }
    ],
    "edges": [
      {
        "source": "归结推理",
        "target": "确定性推理",
        "relation": "part_of"
      }
    ]
  }
}
```

链路：

```text
KGAPI -> KGService -> KnowledgeGraphWorkflow
Agent: KG Agent
Tools: Retrieval, Graph
写入: knowledge_graphs, graph_nodes, graph_edges, graph JSON
```

## 8. 练习题

### POST /api/exercises/generate

Request：

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai_ch3",
  "topic": "归结推理",
  "types": ["choice", "short_answer"],
  "difficulty": "medium"
}
```

Response：

```json
{
  "exercise_set_id": "exset_001",
  "exercises": [
    {
      "exercise_id": "ex_001",
      "type": "choice",
      "question": "归结推理的核心目标是？",
      "options": ["生成空子句", "排序节点", "训练模型", "压缩文本"]
    }
  ]
}
```

## 9. 提交练习答案

### POST /api/exercises/submit

Request：

```json
{
  "student_id": "stu_001",
  "exercise_id": "ex_001",
  "answer": "生成空子句"
}
```

Response：

```json
{
  "attempt_id": "att_001",
  "score": 1.0,
  "feedback": "回答正确",
  "mistake_tags": []
}
```

链路：

```text
ExerciseAPI -> ExerciseService -> AssessmentWorkflow
Agent: Evaluator Agent
Tool: Exercise Grading Tool
写入: exercise_attempts, assessment_results
```

## 10. 学习评估

### POST /api/assessments/run

Request：

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai_ch3"
}
```

Response：

```json
{
  "assessment_id": "assess_001",
  "mastery_score": 0.72,
  "weak_points": ["MGU 算法", "子句化"],
  "next_actions": ["补充归结推理练习", "复习子句集转换"],
  "path_adjusted": true
}
```

## 11. 推荐资源

### GET /api/recommendations?student_id=stu_001&task_id=task_ai_ch3

Response：

```json
{
  "recommendations": [
    {
      "resource_id": "res_002",
      "reason": "学生偏好图解，且当前薄弱点是归结推理流程",
      "priority": 1
    }
  ]
}
```

## 12. Agent 运行日志

### GET /api/agent-runs?task_id=task_ai_ch3

Response：

```json
{
  "runs": [
    {
      "run_id": "run_001",
      "workflow": "ChatProfileWorkflow",
      "agent_name": "IntentAgent",
      "status": "success",
      "latency_ms": 640,
      "model": "deepseek-chat"
    }
  ]
}
```

