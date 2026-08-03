from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.core.database_router import db_router

# Base déclarative unique pour vos modèles
Base = declarative_base()

# Proxy dynamique pour l'engine et les sessions basé sur le routeur
class ProxyEngine:
    """Redirige dynamiquement vers l'engine actif (PostgreSQL ou SQLite)"""
    @property
    def _current_engine(self):
        return db_router.engine

    def connect(self, *args, **kwargs):
        return self._current_engine.connect(*args, **kwargs)

    def begin(self, *args, **kwargs):
        return self._current_engine.begin(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._current_engine, name)

    def __sa_inspect__(self):
        from sqlalchemy import inspect
        return inspect(self._current_engine)

# Engine global intelligent
engine = ProxyEngine()

def get_db() -> Session:
    """
    Dépendance FastAPI pour obtenir une session DB adaptée au contexte.
    Utilise automatiquement PostgreSQL si connecté, sinon SQLite en local.
    """
    db = db_router.get_session()
    try:
        yield db
    finally:
        db.close()