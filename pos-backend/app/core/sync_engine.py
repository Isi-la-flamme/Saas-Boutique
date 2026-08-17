import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque
from app.core.config import settings
from app.core.connection_monitor import connection_monitor, ConnectionStatus
from app.core.database_router import db_router


class SyncEngine:
    """
    Moteur de synchronisation.
    Queue les opérations offline et les replay quand la connexion revient.
    """
    
    def __init__(self, max_queue_size: int = None):
        self.max_queue_size = max_queue_size or settings.SYNC_QUEUE_MAX_SIZE
        self.queue: deque = deque(maxlen=self.max_queue_size)
        self.is_syncing = False
        self._is_running = False
        self._task = None
        
        # S'abonner aux changements de connexion
        connection_monitor.add_listener(self._on_connection_change)
    
    async def start(self):
        """Démarre le sync engine"""
        if self._is_running:
            return
        
        self._is_running = True
        self._task = asyncio.create_task(self._sync_loop())
    
    async def stop(self):
        """Arrête le sync engine"""
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _sync_loop(self):
        """Boucle de sync"""
        while self._is_running:
            # Si online et queue non vide, on sync
            if connection_monitor.is_online and self.queue:
                await self.sync()
            await asyncio.sleep(settings.SYNC_INTERVAL_SECONDS)
    
    async def _on_connection_change(self, status: ConnectionStatus):
        """Quand la connexion revient, on sync immédiatement"""
        if status == ConnectionStatus.ONLINE and self.queue:
            await self.sync()
    
    def add_operation(self, table: str, action: str, data: Dict[str, Any], tenant_id: str):
        """
        Ajoute une opération à la queue de sync.
        Si online, on sync immédiatement.
        """
        operation = {
            "table": table,
            "action": action,
            "data": data,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "sync_version": data.get("sync_version", 0)
        }
        
        # Si queue pleine, on retire le plus ancien
        if len(self.queue) >= self.max_queue_size:
            self.queue.popleft()
        
        self.queue.append(operation)
        
        # Si online, on sync tout de suite
        if connection_monitor.is_online:
            asyncio.create_task(self.sync())
    
    async def sync(self):
        """
        Synchronise toutes les opérations en queue vers le cloud.
        """
        if self.is_syncing or not self.queue:
            return
        
        self.is_syncing = True
        try:
            # Copier la queue
            operations = list(self.queue)
            self.queue.clear()
            
            # Rejouer chaque opération
            for op in operations:
                await self._replay_operation(op)
                
        except Exception as e:
            # En cas d'erreur, remettre les opérations dans la queue
            self.queue.extendleft(reversed(operations))
            print(f"Sync error: {e}")
        finally:
            self.is_syncing = False
    
    async def _replay_operation(self, operation: Dict[str, Any]):
            """
            Rejoue une opération sur la DB online en appelant les services appropriés.
            """
            table = operation["table"]
            action = operation["action"]
            data = operation["data"]
            tenant_id = operation["tenant_id"]

            print(f"Replay [Tenant: {tenant_id}] -> {table}.{action}")

            # Dispatcher selon la table cible
            if table == "sales":
                from app.services.sale import SaleService
                await SaleService.replay_sync(tenant_id=tenant_id, action=action, data=data)
                
            elif table == "products":
                from app.services.product import ProductService
                await ProductService.replay_sync(tenant_id=tenant_id, action=action, data=data)
                
            elif table == "customers":
                from app.services.customer import CustomerService
                await CustomerService.replay_sync(tenant_id=tenant_id, action=action, data=data)
                
            elif table == "tenants":
                from app.services.tenant import TenantService
                await TenantService.replay_sync(tenant_id=tenant_id, action=action, data=data)
                
            else:
                print(f"Table de synchronisation non gérée : {table}")
        
    @property
    def queue_size(self) -> int:
        """Nombre d'opérations en attente de sync"""
        return len(self.queue)
    
    @property
    def is_full(self) -> bool:
        """Queue pleine ?"""
        return len(self.queue) >= self.max_queue_size


# Instance globale
sync_engine = SyncEngine()