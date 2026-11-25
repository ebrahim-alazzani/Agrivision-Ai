"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "AgriVision AI"
    app_version: str = "0.1.0"
    debug: bool = False
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"

    # Database
    database_url: str = "postgresql+asyncpg://agrivision:agrivision@localhost:5432/agrivision"
    database_url_sync: str = "postgresql://agrivision:agrivision@localhost:5432/agrivision"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # S3 / MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_name: str = "agrivision-media"
    s3_region: str = "us-east-1"

    # Security
    secret_key: str = "change-me-to-a-random-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Weather
    weather_api_key: str = ""
    weather_api_url: str = "https://api.openweathermap.org/data/2.5"

    # Upload limits
    max_upload_size_mb: int = 50
    allowed_image_types: str = "image/jpeg,image/png,image/webp"
    allowed_video_types: str = "video/mp4,video/avi"

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def allowed_image_types_list(self) -> List[str]:
        return [t.strip() for t in self.allowed_image_types.split(",")]

    @property
    def allowed_video_types_list(self) -> List[str]:
        return [t.strip() for t in self.allowed_video_types.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
