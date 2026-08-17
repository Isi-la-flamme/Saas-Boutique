from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings
import os
import time

# Création du dossier local pour SQLite (uniquement au cas où le mode offline serait requis plus tard)
os.makedirs("data", exist_ok=True)

# 1. Définition des deux moteurs
online_engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True, 
    echo=settings.DEBUG
)

offline_engine = create_engine(
    settings.OFFLINE_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.OFFLINE_DATABASE_URL else {},
    echo=settings.DEBUG
)

Base = declarative_base()

def get_active_engine():
    """
    Tente de joindre PostgreSQL avec plusieurs essais (retry) pour laisser 
    le temps au conteneur distant de démarrer dans Docker.
    """
    if getattr(settings, "USE_OFFLINE_DB", False):
        print("📴 Mode hors-ligne forcé via configuration -> SQLite")
        return offline_engine
    
    max_retries = 5
    delay = 2  # Secondes d'attente entre chaque essai

    for attempt in range(1, max_retries + 1):
        try:
            with online_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("🌐 PostgreSQL connecté avec succès !")
            return online_engine
        except Exception as e:
            if attempt < max_retries:
                print(f"⏳ Tentative {attempt}/{max_retries} : PostgreSQL en cours de démarrage, nouvelle tentative dans {delay}s...")
                time.sleep(delay)
            else:
                print(f"⚠️ PostgreSQL définitivement injoignable après {max_retries} essais ({e}) -> Basculement sur SQLite.")
                return offline_engine

def get_db() -> Session:
    """
    Dépendance FastAPI dynamique pour chaque requête.
    """
    current_engine = get_active_engine()
    DynamicSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=current_engine)
    
    db = DynamicSessionLocal()
    try:
        yield db
    finally:
        db.close()