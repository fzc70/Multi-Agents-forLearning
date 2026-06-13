# 多智能体个性化学习助手架构文档

本目录是从零重构系统的最终架构设计文档。目标是把系统拆成低耦合、可测试、可扩展的前后端分离架构，重点说明 Agent、Workflow、Tool、API、数据模型和功能链路。

## 文件索引

- [00_overview.md](00_overview.md)：系统总体分层、依赖方向、总体架构图
- [01_agents.md](01_agents.md)：精简后的 7 个核心 Agent 设计和协作方式
- [02_workflows.md](02_workflows.md)：LangGraph 工作流设计
- [03_api_design.md](03_api_design.md)：REST API 设计和请求/返回示例
- [04_data_models.md](04_data_models.md)：核心领域模型和表结构方向
- [05_tools.md](05_tools.md)：Tools 能力清单和调用边界
- [06_storage.md](06_storage.md)：SQLite、本地文件、向量库、图谱存储设计
- [07_frontend_architecture.md](07_frontend_architecture.md)：React 前端模块架构
- [08_feature_chains.md](08_feature_chains.md)：核心功能从前端到 Agent 再回前端的完整链路
- [09_llm_interaction.md](09_llm_interaction.md)：LLMAdapter、Prompt、结构化输出、日志与重试
- [10_engineering_rules.md](10_engineering_rules.md)：工程规范、防混乱规则、测试策略
- [11_visualization_notes.md](11_visualization_notes.md)：后续生成架构图的可视化元素清单

## 核心原则

```text
API 只接请求
Service 负责编排业务
Workflow 编排 Agent 和 Tool Node
Agent 只做单一智能任务
Tool 做确定性能力
Repository 负责数据访问
Storage 封装具体存储
LLMAdapter 统一模型调用
```

强约束：

- 不允许超级 Agent。
- 不允许 API 直接调用 LLM。
- 不允许 React 页面组件直接拼复杂业务逻辑。
- 不允许 Agent 直接写数据库。
- 不允许无 Schema 的 LLM 输出进入业务流程。
- 每次画像更新必须有 evidence。
- 每次 Agent 执行必须写 AgentRunLog。
