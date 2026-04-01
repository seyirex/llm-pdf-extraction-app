"""Application settings with environment variable support."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )

    # LLM
    gemini_api_key: str = Field(
        default="",
        validation_alias="GEMINI_API_KEY",
        description="Google Gemini API key",
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        validation_alias="GEMINI_MODEL",
        description="Gemini model name used for extraction",
    )

    # Redis / Celery
    redis_url: str = Field(
        default="redis://llm-redis:6379/0",
        validation_alias="REDIS_URL",
        description="Redis connection URL for Celery broker/backend",
    )
    redis_port: int = Field(
        default=6379,
        validation_alias="REDIS_PORT",
        description="Redis TCP port",
    )
    celery_concurrency: int = Field(
        default=2,
        validation_alias="CELERY_CONCURRENCY",
        description="Celery worker concurrency",
    )
    celery_log_level: str = Field(
        default="info",
        validation_alias="CELERY_LOG_LEVEL",
        description="Celery worker log level",
    )
    celery_task_time_limit: int = Field(
        default=3600,
        validation_alias="CELERY_TASK_TIME_LIMIT",
        description="Celery hard task time limit in seconds",
    )
    celery_task_soft_time_limit: int = Field(
        default=3300,
        validation_alias="CELERY_TASK_SOFT_TIME_LIMIT",
        description="Celery soft task time limit in seconds",
    )

    # API runtime
    host: str = Field(
        default="0.0.0.0",
        validation_alias="APP_HOST",
        description="API server host",
    )
    port: int = Field(
        default=8083,
        validation_alias="APP_PORT",
        description="API server port",
    )
    debug: bool = Field(
        default=False,
        validation_alias="DEBUG",
        description="Enable development autoreload",
    )
    log_level: str = Field(
        default="INFO",
        validation_alias="LOG_LEVEL",
        description="Application log level",
    )
    cors_origins: str = Field(
        default="*",
        validation_alias="CORS_ORIGINS",
        description="Comma-separated CORS origins",
    )

    # App paths/limits
    upload_dir: str = Field(
        default="/tmp/uploads",
        validation_alias="UPLOAD_DIR",
        description="Directory for uploaded PDF files",
    )
    output_dir: str = Field(
        default="/tmp/outputs",
        validation_alias="OUTPUT_DIR",
        description="Directory for generated TXT files",
    )
    max_upload_size_mb: int = Field(
        default=10,
        validation_alias="MAX_UPLOAD_SIZE_MB",
        description="Maximum upload file size in megabytes",
    )

    # Optional API key auth
    api_key_auth_enabled: bool = Field(
        default=False,
        validation_alias="API_KEY_AUTH_ENABLED",
        description="Enable API key authentication for API endpoints",
    )
    api_key: str = Field(
        default="",
        validation_alias="API_KEY",
        description="Expected API key value when auth is enabled",
    )
    api_key_header_name: str = Field(
        default="x-api-key",
        validation_alias="API_KEY_HEADER_NAME",
        description="Header name to read API key from",
    )

    # Redis behavior (used by container/runtime configuration)
    redis_appendonly: str = Field(
        default="yes",
        validation_alias="REDIS_APPENDONLY",
        description="Enable Redis append-only persistence",
    )
    redis_maxmemory: str = Field(
        default="256mb",
        validation_alias="REDIS_MAXMEMORY",
        description="Redis max memory setting",
    )
    redis_maxmemory_policy: str = Field(
        default="allkeys-lru",
        validation_alias="REDIS_MAXMEMORY_POLICY",
        description="Redis memory eviction policy",
    )


settings = Settings()
