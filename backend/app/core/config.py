from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "multi-agent-learning-backend"
    env: str = "dev"

    database_url: str = "sqlite:///./data/app.db"
    data_dir: str = "./data"

    llm_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    llm_temperature: float = 0.2
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 2
    llm_max_tokens: int = 4096

    cors_origins: str = Field(default="http://127.0.0.1:5173,http://localhost:5173")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def data_path(self) -> Path:
        """返回并创建应用数据目录。"""
        return Path(self.data_dir).resolve()

    @property
    def sqlite_path(self) -> Path:
        """返回 SQLite 数据库文件路径。"""
        prefix = "sqlite:///"
        if self.database_url.startswith(prefix):
            return Path(self.database_url.removeprefix(prefix)).resolve()
        return Path("./data/app.db").resolve()

    @property
    def cors_origin_list(self) -> list[str]:
        """将跨域来源配置解析为列表。"""
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    """返回缓存后的应用配置。"""
    return Settings()
