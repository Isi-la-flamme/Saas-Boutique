# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "POS Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://saas_user:saas_password@postgres-database:5432/saas_db"    
    OFFLINE_DATABASE_URL: str = "sqlite:///./data/pos_offline.db"
    SUPERUSER_TENANT_NAME: str = "SaaS Platform"
    SUPERUSER_TENANT_ID: str = "tenant_platform"
    
    # Bascule automatique ou manuelle vers le mode hors-ligne
    USE_OFFLINE_DB: bool = False  # Mettre à true dans .env si on est hors-ligne
    
    # Sync
    SYNC_QUEUE_MAX_SIZE: int = 255
    SYNC_INTERVAL_SECONDS: int = 5
    HEALTH_CHECK_URL: str = "http://backend:8000/docs"
    # JWT
    SECRET_KEY: str = "Pass2Test@@"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Super Admin
    SUPERUSER_EMAIL: str = "admin@saas.com"
    SUPERUSER_USERNAME: str = "superadmin"
    SUPERUSER_PASSWORD: str = "SuperAdmin123!"
    SUPERUSER_FULL_NAME: str = "Super Admin"
    
    @property
    def ACTIVE_DATABASE_URL(self) -> str:
        """Renvoie l'URL SQLite locale si le mode hors-ligne est activé ou si PostgreSQL est injoignable, sinon PostgreSQL."""
        if self.USE_OFFLINE_DB:
            return self.OFFLINE_DATABASE_URL
        return self.DATABASE_URL

    class Config:
        # Le même fichier est utilisé par Docker, le backend local et Vite.
        env_file = str(ROOT_ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
