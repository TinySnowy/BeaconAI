import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # App info
    APP_NAME: str = "Beacon AI API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Database settings
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "True").lower() in ("true", "1", "t")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "beaconai")
    
    # Database URI
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.USE_SQLITE:
            # Use SQLite for testing
            return "sqlite+aiosqlite:///./beaconai.db"
        else:
            # Use PostgreSQL for production
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:8000",  # FastAPI backend for development
    ]
    
    # JWT settings (for future authentication)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()

# Create settings instance
settings = get_settings() 