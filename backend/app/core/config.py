from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Interview Platform"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str
    DATABASE_URL_TEST: Optional[str] = None

    # Redis
    REDIS_URL: str

    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    # AI Provider
    AI_PROVIDER: str = "mock"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    ANTHROPIC_MAX_TOKENS: int = 2000

    # Storage
    STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_EXTENSIONS: List[str] = ["pdf", "doc", "docx"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Interview Settings
    MAX_INTERVIEW_DURATION_MINUTES: int = 120
    MIN_QUESTIONS_PER_INTERVIEW: int = 5
    MAX_QUESTIONS_PER_INTERVIEW: int = 30
    DEFAULT_INTERVIEW_DIFFICULTY: str = "intermediate"

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Admin
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "change-this-admin-password"

    # S3 Storage (Optional)
    USE_S3_STORAGE: bool = False
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
