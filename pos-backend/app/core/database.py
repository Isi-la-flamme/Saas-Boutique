from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
from app.core.connection_monitor import connection_monitor
import os

# Créer le dossier data/ pour SQLite
os.makedirs("data", exist_ok=True)

# Engine PostgreSQL (online)
online_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Engine SQLite (offline)
offline_engine = create_engine(
    settings.OFFLINE_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.OFFLINE_DATABASE_URL else {},
    echo=settings.DEBUG
)

def get_active_engine():
    """Détermine quel engine utiliser selon le fichier .env ou l'état de la connexion"""
    if getattr(settings, "USE_OFFLINE_DB", False):
        return offline_engine
    
    if settings.ENVIRONMENT == "development":
        if connection_monitor.is_online:
            return online_engine
        else:
            return offline_engine
            
    if connection_monitor.is_online:
        return online_engine
    else:
        return offline_engine

# --- UN VRAI ENGINE DIRECT ---
# Plus de proxy complexe : un vrai objet Engine SQLAlchemy standard qui supporte toutes les méthodes (inspect, create_all, etc.)
engine = get_active_engine()

# Session Local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    """Dépendance FastAPI pour obtenir une session DB adaptée au contexte"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()