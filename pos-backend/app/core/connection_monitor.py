import httpx
import asyncio
from enum import Enum
from typing import List, Callable, Awaitable
from app.core.config import settings


class ConnectionStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class ConnectionMonitor:
    """
    Monitor de connexion réseau.
    Vérifie périodiquement si l'API est accessible.
    """
    
    def __init__(self, health_check_url: str = None):
        self.health_check_url = health_check_url or settings.HEALTH_CHECK_URL
        # Si le mode hors-ligne est forcé dans les settings, on démarre directement en OFFLINE
        initial_status = ConnectionStatus.OFFLINE if getattr(settings, "USE_OFFLINE_DB", False) else ConnectionStatus.OFFLINE
        self.status = initial_status
        self._listeners: List[Callable[[ConnectionStatus], Awaitable[None]]] = []
        self._is_running = False
        self._task = None
    
    async def start(self):
        """Démarre le monitoring en arrière-plan"""
        if self._is_running:
            return
        
        # Si on force l'utilisation de la base hors-ligne en local, inutile de spammer des requêtes réseau inutiles
        if getattr(settings, "USE_OFFLINE_DB", False):
            print("📴 Mode hors-ligne forcé via la configuration (Monitoring réseau ignoré).")
            return
            
        self._is_running = True
        self._task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        """Arrête le monitoring"""
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self):
        """Boucle de monitoring"""
        while self._is_running:
            await self.check()
            await asyncio.sleep(settings.SYNC_INTERVAL_SECONDS)
    
    async def check(self) -> ConnectionStatus:
        """
        Vérifie l'état de la connexion.
        Retourne le nouveau statut.
        """
        if getattr(settings, "USE_OFFLINE_DB", False):
            return ConnectionStatus.OFFLINE

        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(self.health_check_url)
                new_status = ConnectionStatus.ONLINE if resp.status_code == 200 else ConnectionStatus.OFFLINE
        except Exception:
            new_status = ConnectionStatus.OFFLINE
        
        # Si changement, notifier les listeners
        if new_status != self.status:
            self.status = new_status
            await self._notify()
        
        return self.status
    
    async def _notify(self):
        """Notifie tous les listeners du changement de statut"""
        for listener in self._listeners:
            try:
                await listener(self.status)
            except Exception:
                pass
    
    def add_listener(self, listener: Callable[[ConnectionStatus], Awaitable[None]]):
        """Ajoute un listener qui sera notifié à chaque changement"""
        self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[ConnectionStatus], Awaitable[None]]):
        """Retire un listener"""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    @property
    def is_online(self) -> bool:
        if getattr(settings, "USE_OFFLINE_DB", False):
            return False
        return self.status == ConnectionStatus.ONLINE
    
    @property
    def is_offline(self) -> bool:
        if getattr(settings, "USE_OFFLINE_DB", False):
            return True
        return self.status == ConnectionStatus.OFFLINE


# Instance globale
connection_monitor = ConnectionMonitor()