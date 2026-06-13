# 多智能体个性化学习助手后端

可运行后端，包含 FastAPI、SQLite、本地文件存储、PDF 解析、RAG 检索、多智能体工作流、DeepSeek 适配器和 Agent 运行日志。

## 启动

```powershell
cd D:\KESHE\agent\backend
pip install -r requirements.txt
Copy-Item .env.example .env
# 编辑 backend\.env，填写 DEEPSEEK_API_KEY
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## API

- 健康检查：`http://127.0.0.1:8000/api/health`
- LLM 检查：`http://127.0.0.1:8000/api/health/llm`
- Swagger：`http://127.0.0.1:8000/docs`

## API Key

填写位置：

```env
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

没有 API Key 时后端仍能启动；需要真实模型能力的接口会使用本地降级结果，`/api/health/llm` 会提示未配置。
