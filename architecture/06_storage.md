# 06. 存储设计

## 存储组成

初期使用：

```text
SQLite：结构化数据
本地文件：PDF、生成资源、图谱 JSON
FAISS / Chroma：向量检索
NetworkX JSON：知识图谱数据
```

后续迁移：

```text
SQLite -> PostgreSQL
本地文件 -> MinIO / S3
本地向量库 -> Chroma Server / Milvus
```

## SQLite 表

```text
students
learning_tasks
student_profiles
profile_dimensions
materials
material_chunks
conversations
messages
memory_records
learning_resources
exercises
exercise_attempts
learning_paths
learning_steps
knowledge_graphs
graph_nodes
graph_edges
assessment_results
recommendations
workflow_runs
agent_run_logs
```

## 本地文件结构

```text
data/
  materials/
    {task_id}/
      raw/
        {material_id}.pdf
      text/
        {material_id}.txt
      chunks/
        {material_id}_chunks.json

  resources/
    {task_id}/
      course_doc/
      mindmap/
      exercise/
      reading/
      video_script/
      code_practice/

  graphs/
    {task_id}/
      {graph_id}.json
      {graph_id}.html

  exports/
```

## PDF 存储

原文件：

```text
data/materials/{task_id}/raw/{material_id}.pdf
```

抽取文本：

```text
data/materials/{task_id}/text/{material_id}.txt
```

切片 JSON：

```text
data/materials/{task_id}/chunks/{material_id}_chunks.json
```

每个 chunk 需要保留：

```json
{
  "chunk_id": "chunk_001",
  "material_id": "mat_001",
  "page_start": 73,
  "page_end": 74,
  "text": "归结推理...",
  "vector_id": "vec_001"
}
```

## 向量库 Collection

建议：

```text
materials_{task_id}
memory_{student_id}
resources_{task_id}
```

检索优先级：

```text
当前任务 PDF > 当前任务会话摘要 > 学生长期记忆 > 已生成资源
```

## 图谱存储

SQLite 保存元信息：

```text
knowledge_graphs
graph_nodes
graph_edges
```

完整图谱 JSON 保存到：

```text
data/graphs/{task_id}/{graph_id}.json
```

前端从 API 获取：

```json
{
  "nodes": [],
  "edges": []
}
```

再用 `vis-network` 渲染。

## AgentRunLog 存储

每次 Agent 执行都写入：

```text
agent_run_logs
```

必须记录：

```text
workflow_run_id
agent_name
input_json
output_json
model
prompt_version
status
latency_ms
tokens
error_message
```

## 画像版本存储

每次 Profile Agent 产生有效 `ProfilePatch` 后：

```text
student_profiles.version + 1
profile_dimensions 更新 value/confidence/evidence
```

Evidence 必须保存：

```json
{
  "source_type": "message",
  "source_id": "msg_001",
  "quote": "我不理解归结推理"
}
```

