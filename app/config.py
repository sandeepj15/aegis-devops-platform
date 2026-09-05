from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Aegis API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_MESSAGE: str = "Hello from Aegis DevOps Platform!"
    HOST: str = "0.0.0.0"  # nosec B104 - Required for container interface binding
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Kubernetes Downward API metadata
    POD_NAME: str = "local-pod"
    POD_NAMESPACE: str = "aegis"
    POD_IP: str = "127.0.0.1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
