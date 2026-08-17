from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.connection_monitor import connection_monitor, ConnectionStatus
import os


class DatabaseRouter:
    """
    Routeur de base de données.
    Bascule automatiquement entre PostgreSQL (online) et SQLite (offline).
    """
    
    def __init__(self):
        self._online_engine = None
        self._offline_engine = None
    
    def _get_online_engine(self):
        """Retourne l'engine PostgreSQL"""
        if self._online_engine is None:
            print(f"🔗 Connexion à PostgreSQL: {settings.DATABASE_URL}")
            self._online_engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                echo=settings.DEBUG
            )
        return self._online_engine
    
    def _get_offline_engine(self):
        """Retourne l'engine SQLite"""
        if self._offline_engine is None:
            os.makedirs("data", exist_ok=True)
            print(f"🔗 Connexion à SQLite: {settings.OFFLINE_DATABASE_URL}")
            self._offline_engine = create_engine(
                settings.OFFLINE_DATABASE_URL,
                connect_args={"check_same_thread": False} if "sqlite" in settings.OFFLINE_DATABASE_URL else {},
                echo=settings.DEBUG
            )
        return self._offline_engine
    
    @property
    def engine(self):
        """Retourne l'engine correspondant à l'état de la connexion ou à la configuration"""
        # 1. Si le mode hors-ligne est explicitement demandé dans le .env
        if hasattr(settings, "USE_OFFLINE_DB") and settings.USE_OFFLINE_DB:
            return self._get_offline_engine()

        # 2. Si le moniteur est explicitement OFFLINE, on bascule sur SQLite.
        # Sinon (au démarrage, en cours de test, ou ONLINE), on privilégie PostgreSQL.
        if connection_monitor.status == ConnectionStatus.OFFLINE:
            return self._get_offline_engine()
        
        return self._get_online_engine()

    
    @property
    def is_online(self) -> bool:
        return connection_monitor.is_online
    
    @property
    def is_offline(self) -> bool:
        return connection_monitor.is_offline
    
    def get_session(self) -> Session:
        """Retourne une session DB pour l'engine actif"""
        return sessionmaker(bind=self.engine, autocommit=False, autoflush=False)()

    def get_local_session(self) -> Session:
       """Retourne TOUJOURS une session sur la base SQLite locale (pour l'outbox/sync)."""
       engine = self._get_offline_engine()
       return sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    
    def get_db(self):
        """Dépendance FastAPI pour obtenir une session DB"""
        db = self.get_session()
        try:
            yield db
        finally:
            db.close()


# Instance globale
db_router = DatabaseRouter()