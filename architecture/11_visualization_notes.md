# 11. 可视化设计准备

本文件用于后续生成架构图、智能体协作图、工作流图和数据流图。

## 系统模块节点

```text
React Frontend
FastAPI API
Service Layer
LangGraph Workflow
Agent Layer
Tool Node
Repository Layer
Storage Layer
LLMAdapter
```

## Agent 节点

```text
Intent Agent
Profile Agent
Tutor Agent
Resource Agent
Planner Agent
KG Agent
Evaluator Agent
```

## Tool 节点

```text
LLMAdapter
Retrieval Tool
PDF Parser Tool
Chunk Tool
Embedding Tool
File Storage Tool
Graph Tool
Mindmap Tool
Exercise Grading Tool
Code Runner Tool
Search Tool
Agent Log Tool
```

## 数据存储节点

```text
SQLite
Local File Store
FAISS / Chroma Vector Store
Graph JSON Store
AgentRunLog
```

## 外部服务节点

```text
DeepSeek API
OpenAI-compatible API
Embedding Model
Optional Search API
```

## 主要调用边

| 边 | 含义 |
|---|---|
| Frontend -> API | 用户操作请求 |
| API -> Service | 调用业务用例 |
| Service -> Workflow | 启动 LangGraph 工作流 |
| Workflow -> Agent | 执行智能节点 |
| Workflow -> Tool Node | 执行业务关键工具 |
| Agent -> LLMAdapter | 调用大模型 |
| Agent -> Tool | 调用生成辅助工具 |
| Service -> Repository | 读写结构化数据 |
| Repository -> Storage | 访问具体存储 |
| Tool -> VectorStore | 检索或写向量 |
| KG Agent -> Graph Tool | 构建知识图谱 |

## 颜色建议

```text
前端：蓝色
API/Service：绿色
Workflow：紫色
Agent：橙色
Tool：黄色
LLM：红色
Storage：灰色
外部服务：粉色
```

## 适合画的图

### 总体架构图

展示：

```text
Frontend
API
Service
Workflow
Agent
Tool
LLM
Storage
```

### 智能体协作图

展示：

```text
Intent -> Tutor/Profile/Resource/Planner/KG/Evaluator
Evaluator -> Profile/Planner
KG -> Planner
Resource -> Planner
```

### 功能调用链路图

以具体功能为单位：

```text
用户点击生成图谱
-> API
-> KGService
-> KnowledgeGraphWorkflow
-> Retrieval Tool
-> KG Agent
-> Graph Tool
-> Storage
-> Frontend GraphCanvas
```

### 数据流图

展示：

```text
PDF -> Parser -> Chunk -> VectorStore -> Retrieval -> Agent -> Resource/Graph/Path
```

### LangGraph 工作流图

展示：

```text
Start
-> Agent Node
-> Tool Node
-> Condition
-> Service Node
-> End
```

## Image Prompt 准备模板

```text
生成一张清晰的系统架构图，主题是“多智能体个性化学习助手”。
图中包含 React 前端、FastAPI API、Service 层、LangGraph Workflow、7 个核心 Agent、Tools、LLMAdapter、SQLite、本地文件、向量库、知识图谱存储。
使用分层布局，从左到右展示用户请求流。
颜色区分：前端蓝色，服务绿色，工作流紫色，Agent 橙色，Tool 黄色，LLM 红色，存储灰色。
图风格要求：现代软件架构图，清晰、专业、可读性强。
```

