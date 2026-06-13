# 10. 工程规范和防混乱规则

## 模块边界

```text
api 只调用 service
service 可调用 repository 和 workflow
workflow 编排 agent/tool/service node
agent 只调用 llm/tools
repository 只访问 storage/db
storage 不含业务逻辑
frontend page 只调用 hooks/api client
```

禁止：

```text
API 直接调用 LLM
API 直接调用 Agent
Agent 直接写数据库
Agent 直接保存文件
Service 写 Prompt
Repository 调用 Service
React 页面拼复杂业务规则
```

## Agent 设计规则

每个 Agent 必须包含：

```text
name
description
input_schema
output_schema
prompt_template
run()
validate_output()
log_run()
```

Agent 必须单一职责：

```text
Intent Agent 只做意图
Profile Agent 只做画像 patch
Tutor Agent 只做讲解答疑
Resource Agent 只做资源生成
Planner Agent 只做路径
KG Agent 只做图谱抽取
Evaluator Agent 只做评估
```

## API Schema 规则

- 所有请求响应使用 Pydantic。
- 所有错误统一格式。
- 长任务返回 `job_id`。
- 查询任务状态使用 `GET /api/jobs/{job_id}`。

## Service 编排规则

Service 负责：

- 加载必要数据。
- 启动 Workflow。
- 保存 Workflow 输出。
- 处理事务。
- 返回 API DTO。

Service 不负责：

- 写 Prompt。
- 直接调用 LLM。
- 处理 Agent 内部逻辑。

## Repository 规则

Repository 负责：

- CRUD。
- 查询封装。
- 屏蔽 SQLite / PostgreSQL 差异。

Repository 不负责：

- 业务判断。
- 调用 Agent。
- 调用 LLM。

## Prompt 管理规则

- 每个 Agent 独立 Prompt 文件。
- Prompt 必须带版本。
- Prompt 输入变量必须显式。
- Prompt 输出必须声明 JSON Schema。
- Prompt 修改要记录 changelog。

## 日志规范

必须有：

```text
request_id
workflow_run_id
agent_run_id
student_id
task_id
```

关键日志：

- API 请求日志
- Workflow 状态迁移日志
- AgentRunLog
- Tool 调用日志
- LLM 错误和重试日志

## 错误处理

错误分类：

```text
VALIDATION_ERROR
NOT_FOUND
AGENT_OUTPUT_SCHEMA_ERROR
LLM_CALL_FAILED
TOOL_FAILED
STORAGE_FAILED
WORKFLOW_FAILED
```

## 测试策略

Agent 单测：

```text
mock LLM
固定输入
校验输出 schema
校验失败重试
```

Workflow 测试：

```text
mock Agent 和 Tool
测试条件分支
测试失败回退
```

Service 测试：

```text
mock repository/workflow
验证读写和事务
```

API 测试：

```text
FastAPI TestClient
校验请求响应
校验错误格式
```

前端测试：

```text
组件测试
hook 测试
API mock
```

端到端测试：

```text
上传 PDF -> 生成图谱 -> 生成资源 -> 生成学习路径 -> 提交练习 -> 评估
```

## 文件命名

```text
snake_case.py
PascalCase.tsx
camelCase.ts
agent_name_agent.py
xxx_service.py
xxx_repo.py
xxx_workflow.py
```

## 防混乱强约束

- 不允许超级 Agent。
- 不允许无 Schema 的 LLM 输出进入流程。
- 不允许没有 evidence 的画像更新。
- 不允许没有 AgentRunLog 的 Agent 调用。
- 不允许业务逻辑散落在工具函数里。
- 新增功能必须先补 API / Service / Workflow / Schema 设计。

