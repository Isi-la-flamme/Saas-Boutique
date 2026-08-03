# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "POS Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/pos"
    OFFLINE_DATABASE_URL: str = "sqlite:///./data/pos_offline.db"
    
    # Bascule automatique ou manuelle vers le mode hors-ligne
    USE_OFFLINE_DB: bool = True  # Mettre à true dans .env si on est hors-ligne
    
    # Sync
    SYNC_QUEUE_MAX_SIZE: int = 255
    SYNC_INTERVAL_SECONDS: int = 5
    HEALTH_CHECK_URL: str = "https://api.yourapp.com/health"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Super Admin
    SUPERUSER_EMAIL: str
    SUPERUSER_USERNAME: str
    SUPERUSER_PASSWORD: str
    SUPERUSER_FULL_NAME: str = "Super Admin"
    
    @property
    def ACTIVE_DATABASE_URL(self) -> str:
        """Renvoie l'URL SQLite locale si le mode hors-ligne est activé ou si PostgreSQL est injoignable, sinon PostgreSQL."""
        if self.USE_OFFLINE_DB:
            return self.OFFLINE_DATABASE_URL
        return self.DATABASE_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()