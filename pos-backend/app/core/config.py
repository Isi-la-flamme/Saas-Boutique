# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "POS Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/pos.db"
    OFFLINE_DATABASE_URL: str = "sqlite:///./data/pos_offline.db"
    
    # Sync
    SYNC_QUEUE_MAX_SIZE: int = 255
    SYNC_INTERVAL_SECONDS: int = 5
    HEALTH_CHECK_URL: str = "https://api.yourapp.com/health"
    
    # JWT
    SECRET_KEY: str  # Champ obligatoire (doit être dans .env)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Super Admin (NOUVEAU)
    SUPERUSER_EMAIL: str
    SUPERUSER_USERNAME: str
    SUPERUSER_PASSWORD: str
    SUPERUSER_FULL_NAME: str = "Super Admin"  # Valeur par défaut
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # extra = "ignore"  # À décommenter si tu veux ignorer d'autres champs non déclarés

settings = Settings()