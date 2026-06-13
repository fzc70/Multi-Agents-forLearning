# 05. Tools 设计

Tool 是确定性能力，不是智能体。Agent 可以调用 Tool，Workflow 也可以通过 Tool Node 调用 Tool，Service 也可以在业务步骤中调用 Tool。

## Tool 调用原则

```text
业务关键型 Tool：优先由 Workflow 的 Tool Node 或 Service 调用
生成辅助型 Tool：可以由 Agent 调用
```

例如：

- Retrieval Tool 推荐由 Workflow 的 Retrieval Node 调用，避免 Tutor Agent 随意检索。
- PDF Parser / Chunk / Embedding 由 MaterialIngestionWorkflow 调用。
- Mindmap Tool 可由 Resource Agent 调用。
- Code Runner Tool 可由 Resource Agent 或 Evaluator Agent 调用。

## Tool 清单

| Tool | 功能 | 输入 | 输出 | 调用者 | 确定性 | 外部服务 |
|---|---|---|---|---|---|---|
| LLMAdapter | 统一调用 DeepSeek / OpenAI-compatible | prompt, model, schema | raw / parsed JSON | Agent | 否 | 是 |
| Retrieval Tool | 从资料、记忆、资源中检索上下文 | task_id, query, top_k | context chunks | Workflow Node | 是 | 否/向量库 |
| PDF Parser Tool | 解析 PDF 文本和页码 | file_path | pages text | Service/Workflow | 是 | 否 |
| Chunk Tool | 文本切片，保留来源 | text, page info | chunks | Workflow | 是 | 否 |
| Embedding Tool | 生成向量并入库 | chunks | vector ids | Workflow | 半确定 | 可本地/外部 |
| File Storage Tool | 保存 PDF、资源、图谱文件 | bytes/json/text | file path | Service | 是 | 否 |
| Graph Tool | 基于 nodes/edges 构建图谱 | nodes, edges | graph json/html | KG Agent/Workflow | 是 | 否 |
| Mindmap Tool | 转换思维导图结构 | tree json | mindmap json | Resource Agent | 是 | 否 |
| Exercise Grading Tool | 规则判分、客观题评分 | answer, key | score | Evaluator/Workflow | 是 | 否 |
| Code Runner Tool | 运行代码案例或测试代码 | code, language | stdout/errors | Resource/Evaluator | 是 | 否 |
| Search Tool | 获取拓展阅读候选 | query | search results | Resource Agent | 否 | 是 |
| Agent Log Tool | 记录 Agent 输入输出和耗时 | run payload | run_id | Workflow/Service | 是 | 否 |

## Retrieval Tool 示例

Input：

```json
{
  "student_id": "stu_001",
  "task_id": "task_ai_ch3",
  "query": "归结推理",
  "sources": ["materials", "memory", "resources"],
  "top_k": 5
}
```

Output：

```json
{
  "chunks": [
    {
      "chunk_id": "chunk_001",
      "source_type": "material",
      "source_id": "mat_001",
      "page": 73,
      "text": "归结原理是在子句集基础上讨论问题...",
      "score": 0.86
    }
  ]
}
```

## Graph Tool 示例

Input：

```json
{
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
```

Output：

```json
{
  "node_count": 1,
  "edge_count": 1,
  "graph_json": {
    "nodes": [],
    "edges": []
  }
}
```

## Tool 与 Agent 的边界

```text
Agent 决定“要生成什么、如何解释、如何分析”
Tool 执行“检索、解析、切片、评分、构图、保存”等明确动作
Service 决定“结果保存在哪里、如何返回给前端”
```

