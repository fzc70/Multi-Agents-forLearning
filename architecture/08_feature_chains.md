# 08. 功能完整链路

本文件说明每个核心功能如何从前端操作一路流转到 Agent、Tool、LLM、Storage，再返回前端。

通用链路：

```text
前端操作
-> API Request
-> Service
-> Workflow
-> Agent Node / Tool Node / Service Node
-> LLM / Tool / Storage
-> Workflow State
-> Service 保存结果
-> API Response
-> 前端展示
```

## 1. 首次对话生成学生画像

前端操作：

```text
ChatPage 输入：“我是计算机专业，想学人工智能，但逻辑基础一般”
```

API：

```http
POST /api/chat
```

Request：

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai",
  "conversation_id": null,
  "message": "我是计算机专业，想学人工智能，但逻辑基础一般"
}
```

链路：

```text
ChatService
-> ChatProfileWorkflow
-> Intent Agent 判断为 profile_build + tutoring
-> Profile Agent 抽取画像 patch
-> Tutor Agent 生成学习引导回复
-> Service 保存 Message/ProfileDimension/AgentRunLog
-> API 返回 answer + profile_updated
```

Response：

```json
{
  "answer": "我会按人工智能入门路线帮你学习，先补足逻辑基础...",
  "profile_updated": true,
  "updated_dimensions": ["major", "learning_goal", "knowledge_level"]
}
```

前端展示：

```text
聊天区显示回答
右侧画像卡片更新：专业背景、学习目标、知识基础
```

## 2. 后续对话更新画像

用户输入：

```text
“我还是不太会做归结推理题”
```

链路：

```text
Intent Agent -> need_profile_update=true
Profile Agent -> weak_points append “归结推理”
Tutor Agent -> 生成针对性讲解
Service -> 保存新画像版本和 evidence
```

Evidence：

```json
{
  "source_type": "message",
  "source_id": "msg_010",
  "quote": "我还是不太会做归结推理题"
}
```

## 3. 上传 PDF 并入库

前端：

```text
MaterialsPage 点击上传 PDF
```

API：

```http
POST /api/materials/upload
```

链路：

```text
MaterialService
-> MaterialIngestionWorkflow
-> File Storage Tool 保存 PDF
-> PDF Parser Tool 抽文本
-> Chunk Tool 切片
-> Embedding Tool 入向量库
-> MaterialRepository 保存 material/chunks
```

Response：

```json
{
  "material_id": "mat_001",
  "status": "indexed",
  "chunk_count": 42
}
```

## 4. 基于 PDF + 对话生成知识图谱

前端：

```text
KnowledgeGraphPage 点击“生成图谱”
```

API：

```http
POST /api/knowledge-graphs/generate
```

链路：

```text
KGService
-> KnowledgeGraphWorkflow
-> Service Node 加载 MaterialChunk
-> Service Node 加载 Conversation Summary
-> Retrieval Tool Node 筛选相关片段
-> KG Agent 抽取 nodes/edges
-> Graph Tool 构建图谱
-> GraphStore 保存 graph.json
-> API 返回 graph
```

Response：

```json
{
  "graph_id": "kg_001",
  "node_count": 120,
  "edge_count": 96,
  "graph": {
    "nodes": [],
    "edges": []
  }
}
```

前端展示：

```text
GraphCanvas 用 vis-network 渲染 nodes/edges
```

## 5. 生成课程讲解文档

API：

```http
POST /api/resources/generate
```

Request：

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai_ch3",
  "topic": "归结推理",
  "resource_types": ["course_doc"]
}
```

链路：

```text
ResourceService
-> ResourceGenerationWorkflow
-> Retrieval Tool 获取资料片段
-> Resource Agent(resource_type=course_doc)
-> LLM 生成结构化文档
-> Service 保存 LearningResource
```

## 6. 生成思维导图

与资源生成链路相同，区别：

```text
resource_type = mindmap
Resource Agent 输出 tree JSON
Mindmap Tool 转换为前端可渲染结构
```

## 7. 生成练习题

```text
Resource Agent(resource_type=exercise)
输入：topic + weak_points + difficulty
输出：题目、答案、解析、标签
保存：exercises
```

## 8. 生成拓展阅读

```text
Resource Agent(resource_type=reading)
可调用 Search Tool
输出：阅读材料、适合原因、难度、阅读目标
```

## 9. 生成视频/动画脚本

```text
Resource Agent(resource_type=video_script)
输出：分镜、旁白、画面元素、时长建议
```

## 10. 生成代码实操案例

```text
Resource Agent(resource_type=code_practice)
可调用 Code Runner Tool 验证代码
输出：代码、运行说明、练习任务
```

## 11. 生成学习路径

链路：

```text
LearningPathService
-> LearningPathWorkflow
-> Service Node 加载画像/资源/评估
-> Planner Agent 生成步骤
-> Service 校验和保存 LearningPath/LearningStep
```

## 12. 推荐个性化资源

推荐不单独做 Agent，默认由 Planner Agent 输出推荐策略，Service 落库为 Recommendation。

```text
Planner Agent 输出每个 step 的 recommended_resource_ids 和 reason
RecommendationRepository 保存
前端 RecommendationPanel 展示
```

## 13. 智能答疑

链路：

```text
ChatPage 提问
-> ChatService
-> ChatProfileWorkflow
-> Intent Agent
-> Retrieval Tool Node
-> Tutor Agent
-> Profile Agent
-> Service 保存
-> 前端显示答案、引用、画像变化
```

## 14. 提交练习答案

链路：

```text
ExerciseService
-> AssessmentWorkflow
-> Exercise Grading Tool
-> Evaluator Agent
-> Profile Agent
-> Planner Agent 可选
-> 保存 ExerciseAttempt/Assessment/ProfilePatch
```

## 15. 生成学习效果评估

```text
AssessmentService
-> AssessmentWorkflow
-> Service Node 加载 attempts/messages/resources usage
-> Evaluator Agent
-> Profile Agent 生成画像更新
-> Planner Agent 给路径调整建议
-> 保存 AssessmentResult
```

## 16. 根据评估结果调整学习路径

```text
AssessmentResult
-> LearningPathWorkflow
-> Planner Agent
-> 生成新 path version
-> 前端展示“路径已调整”
```

