import asyncio
from enum import Enum
from typing import List, Callable, Awaitable
from sqlalchemy import create_engine, text
from app.core.config import settings


class ConnectionStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class ConnectionMonitor:
    """
    Monitor indépendant qui teste directement l'URL PostgreSQL configurée.
    """
    
    def __init__(self):
        self._listeners: List[Callable[[ConnectionStatus], Awaitable[None]]] = []
        self._is_running = False
        self._task = None
        self.status = ConnectionStatus.OFFLINE
        
        # Crée un engine dédié uniquement au test de santé, avec un timeout court (2 secondes)
        # On s'assure d'utiliser l'URL PostgreSQL principale (settings.DATABASE_URL ou équivalent)
        pg_url = getattr(settings, "POSTGRES_DATABASE_URL", settings.DATABASE_URL)
        self._test_engine = create_engine(
            pg_url, 
            connect_args={"connect_timeout": 2},
            pool_pre_ping=True
        )
    
    async def start(self):
        if self._is_running:
            return
        self._is_running = True
        await self.check()
        self._task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self):
        while self._is_running:
            await asyncio.sleep(settings.SYNC_INTERVAL_SECONDS)
            await self.check()
    
    async def check(self) -> ConnectionStatus:
        new_status = ConnectionStatus.OFFLINE
        
        try:
            def ping_postgres():
                with self._test_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return True

            is_ok = await asyncio.to_thread(ping_postgres)
            if is_ok:
                new_status = ConnectionStatus.ONLINE
        except Exception:
            new_status = ConnectionStatus.OFFLINE
        
        if new_status != self.status:
            print(f"🔄 Bascule de l'état réseau/base : {self.status.value} -> {new_status.value}")
            self.status = new_status
            await self._notify()
            
        return self.status
    
    async def _notify(self):
        for listener in self._listeners:
            try:
                await listener(self.status)
            except Exception:
                pass
    
    def add_listener(self, listener: Callable[[ConnectionStatus], Awaitable[None]]):
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[ConnectionStatus], Awaitable[None]]):
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    @property
    def is_online(self) -> bool:
        return self.status == ConnectionStatus.ONLINE
    
    @property
    def is_offline(self) -> bool:
        return self.status == ConnectionStatus.OFFLINE


# Instance globale
connection_monitor = ConnectionMonitor()