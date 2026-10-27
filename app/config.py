"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration settings."""

    app_name: str = "EventCraft AI"
    app_env: str = "production"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    max_text_length: int = 1000
    host: str = "127.0.0.1"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
