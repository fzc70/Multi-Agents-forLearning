from app.schemas.base import ApiModel


class HealthResponse(ApiModel):
    status: str
    app_name: str
    llm_provider: str
    model: str
    api_key_configured: bool
