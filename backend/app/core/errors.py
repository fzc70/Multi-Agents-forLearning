from fastapi import HTTPException


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail={"message": message})


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=404, detail={"message": message})


def llm_not_configured() -> HTTPException:
    return HTTPException(status_code=503, detail={"message": "DeepSeek API Key 未配置，请在 backend/.env 中填写 DEEPSEEK_API_KEY"})
