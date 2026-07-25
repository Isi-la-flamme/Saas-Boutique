from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
import os

# Créer le dossier data/
os.makedirs("data", exist_ok=True)

# Engine PostgreSQL (online)
engine = create_engine(
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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

def get_db() -> Session:
    """Dépendance FastAPI pour obtenir une session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()