# 09. LLM 交互设计

## 目标

统一管理所有 Agent 对大模型的调用，避免 API、Service、Agent 到处直接写模型调用逻辑。

## 标准调用链路

```text
Service
-> Workflow
-> Agent
-> PromptBuilder
-> LLMAdapter
-> JSONParser
-> SchemaValidator
-> AgentOutput
-> WorkflowState
-> ServiceResponse
```

## LLMAdapter

职责：

- 统一 DeepSeek / OpenAI-compatible API。
- 统一超时、重试、模型配置。
- 统一流式/非流式调用。
- 统一记录 token、耗时、错误。

配置示例：

```json
{
  "provider": "deepseek",
  "model": "deepseek-chat",
  "temperature": 0.2,
  "timeout": 60,
  "max_retries": 2,
  "response_format": "json_schema"
}
```

## Prompt 管理

建议结构：

```text
backend/app/llm/prompts/
  intent_agent.md
  profile_agent.md
  tutor_agent.md
  resource_agent_course_doc.md
  resource_agent_mindmap.md
  resource_agent_exercise.md
  resource_agent_reading.md
  resource_agent_video_script.md
  resource_agent_code_practice.md
  planner_agent.md
  kg_agent.md
  evaluator_agent.md
```

规则：

- 每个 Agent 独立 Prompt。
- Resource Agent 根据 `resource_type` 选择不同 Prompt。
- Prompt 必须版本化。
- Prompt 中 JSON 示例的大括号必须转义。
- Prompt 输入变量必须明确。

## 结构化输出

所有 Agent 输出必须：

```text
LLM raw output
-> JSON parse
-> Pydantic schema validate
-> 通过后进入 Workflow State
```

禁止：

```text
LLM 随意文本直接进入数据库
LLM 输出缺字段仍继续业务流程
Agent 返回自然语言当作结构化数据
```

## 输出不合法处理

策略：

```text
1. JSON parse 失败 -> repair prompt
2. Schema validate 失败 -> repair prompt
3. 最多重试 2 次
4. 仍失败 -> 返回结构化错误
5. 写 AgentRunLog
```

错误示例：

```json
{
  "status": "failed",
  "error_code": "AGENT_OUTPUT_SCHEMA_ERROR",
  "agent_name": "KGAgent",
  "message": "LLM 输出缺少 edges 字段"
}
```

## AgentRunLog

每次 Agent 调用必须记录：

```json
{
  "workflow_run_id": "wf_001",
  "agent_name": "ProfileAgent",
  "prompt_version": "v1",
  "model": "deepseek-chat",
  "input_json": {},
  "output_json": {},
  "status": "success",
  "latency_ms": 1800,
  "tokens_in": 1200,
  "tokens_out": 500
}
```

## 流式输出

适合流式：

- Chat 答疑
- Tutor Agent 长回答
- 课程讲解文档预览

不适合流式：

- Profile Agent
- Intent Agent
- KG Agent
- Evaluator Agent
- Planner Agent

原因：这些 Agent 要先通过完整 JSON Schema 校验。

## 后台异步任务

应异步：

- PDF 解析和向量入库
- 知识图谱生成
- 多资源批量生成
- 学习效果评估
- 学习路径重算

返回：

```json
{
  "job_id": "job_001",
  "status": "running"
}
```

