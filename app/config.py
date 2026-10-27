"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration settings."""

    app_name: str = "EventCraft AI"
    app_env: str = "production"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    allowed_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    rate_limit_per_min: int = 60
    max_text_length: int = 1000
    host: str = "127.0.0.1"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_cors_origins(self) -> list[str]:
        """Return list of allowed CORS origins."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
