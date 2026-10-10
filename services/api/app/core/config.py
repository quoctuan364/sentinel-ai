import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentinel AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "sentinel-super-secret-jwt-signing-key-for-dev-change-in-prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALLOW_DEV_FALLBACK_AUTH: bool = False  # Strict security: require explicit JWT by default
    
    # Database
    # Default to sqlite local db for immediate zero-config runs, overridden by POSTGRES_URL in prod/docker
    DATABASE_URL: str = "sqlite+aiosqlite:///./sentinel.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # GitHub App Integration
    GITHUB_APP_ID: Optional[str] = None
    GITHUB_APP_PRIVATE_KEY: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: str = "sentinel-webhook-secret-token"
    
    # AI Provider Settings
    AI_ENABLED: bool = True
    AI_PROVIDER: str = "mock"  # "mock" or "openai"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_MONTHLY_BUDGET_CENTS_DEFAULT: int = 5000  # $50
    
    # Security scanner limits
    MAX_DIFF_FILE_COUNT: int = 100
    MAX_DIFF_LINE_COUNT: int = 15000
    MAX_FILE_SIZE_BYTES: int = 1024 * 1024 * 5  # 5MB
    SCAN_TIMEOUT_SECONDS: int = 180

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
