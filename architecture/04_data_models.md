# 04. 核心数据模型

## 设计原则

- 画像、路径、评估、资源生成结果都要可追踪。
- 学生画像必须保存 evidence。
- Agent 运行必须保存 AgentRunLog。
- 资源和路径要绑定 `profile_version`，便于解释为什么生成当前内容。

## 模型清单

### StudentProfile

用途：学生画像主实体。

字段：

```text
id
student_id
version
summary
created_at
updated_at
```

关系：

```text
StudentProfile 1 -> N ProfileDimension
```

需要版本：是。

### ProfileDimension

用途：画像维度。

字段：

```text
id
profile_id
dimension_name
value_json
confidence
evidence_json
updated_at
```

维度至少包含：

```text
major
knowledge_level
learning_goal
cognitive_style
learning_preference
weak_points
learning_history
resource_preference
exercise_performance
```

必须 evidence：是。

### LearningTask

字段：

```text
id
student_id
title
course
goal
status
created_at
updated_at
```

关系：

```text
Task 1 -> N Material
Task 1 -> N Conversation
Task 1 -> N LearningResource
Task 1 -> N LearningPath
Task 1 -> N KnowledgeGraph
```

### Material

字段：

```text
id
task_id
filename
file_path
text_path
status
page_count
chunk_count
created_at
```

### MaterialChunk

字段：

```text
id
material_id
task_id
chunk_index
page_start
page_end
text
vector_id
created_at
```

用途：向量检索和引用来源。

### Conversation

字段：

```text
id
student_id
task_id
title
summary
created_at
updated_at
```

### Message

字段：

```text
id
conversation_id
role
content
intent
metadata_json
created_at
```

### MemoryRecord

字段：

```text
id
student_id
task_id
type
content
source_type
source_id
importance
created_at
```

类型：

```text
conversation_summary
weak_point
preference
learning_fact
```

### LearningResource

字段：

```text
id
student_id
task_id
type
title
content_json
content_path
generated_by_agent
profile_version
source_refs_json
created_at
```

类型：

```text
course_doc
mindmap
exercise
reading
video_script
code_practice
```

### Exercise

字段：

```text
id
task_id
resource_id
type
question
options_json
answer_json
explanation
difficulty
tags_json
created_at
```

### ExerciseAttempt

字段：

```text
id
exercise_id
student_id
answer_json
score
feedback
mistake_tags_json
created_at
```

### LearningPath

字段：

```text
id
student_id
task_id
version
title
status
profile_version
assessment_id
created_at
updated_at
```

需要版本：是。

### LearningStep

字段：

```text
id
path_id
order_index
objective
resource_ids_json
exercise_ids_json
evaluation_point
status
```

### KnowledgeGraph

字段：

```text
id
task_id
graph_path
node_count
edge_count
source_material_ids_json
source_conversation_ids_json
created_at
```

### GraphNode

字段：

```text
id
graph_id
node_key
label
type
weight
metadata_json
```

### GraphEdge

字段：

```text
id
graph_id
source_key
target_key
relation
confidence
context
```

### AssessmentResult

字段：

```text
id
student_id
task_id
mastery_score
weak_points_json
mistake_patterns_json
resource_fit_score
next_actions_json
evidence_json
created_at
```

### Recommendation

字段：

```text
id
student_id
task_id
resource_id
reason
priority
matched_dimensions_json
created_at
```

### AgentRunLog

字段：

```text
id
workflow_run_id
agent_name
status
model
prompt_version
input_json
output_json
error_message
latency_ms
tokens_in
tokens_out
created_at
```

用途：

- 调试 Agent 结果。
- 追踪图谱、画像、资源、评估的生成依据。
- 支持后续质量分析。

