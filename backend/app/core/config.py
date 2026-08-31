import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Resume-Based Interview & Skill Gap Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Debug
    ENV: str = "development"
    DEBUG: bool = True
    
    # Security & Auth
    SECRET_KEY: str = "ai-interview-super-secret-key-change-in-production-2026-secure-token-vault-9988"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database (Defaults to SQLite for instant local dev, PostgreSQL for production)
    DATABASE_URL: str = "sqlite:///./talentpulse.db"
    
    # Redis & Celery
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Storage Configuration (local private storage or S3)
    STORAGE_TYPE: str = "local"  # 'local' or 's3'
    STORAGE_LOCAL_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../storage"))
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc", ".txt"]
    
    # AI Gateway Settings
    AI_PROVIDER: str = "mock"  # 'mock', 'openai', 'anthropic', 'gemini', 'groq', 'deepseek', 'ollama'
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4o"
    AI_FALLBACK_PROVIDER: str = "mock"
    AI_TEMPERATURE: float = 0.2
    AI_MAX_TOKENS: int = 2000
    AI_REQUEST_TIMEOUT_SECONDS: int = 30
    
    # Specific Provider Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Admin defaults
    ADMIN_EMAIL: str = "admin@talentpulse.ai"
    ADMIN_PASSWORD: str = "Admin@12345"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()
