import json
import asyncio
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.connection_monitor import connection_monitor, ConnectionStatus
from app.core.database_router import db_router
from app.models.sync_outbox import SyncOutboxModel  # Modèle de persistance locale
from app.models.tenant import Tenant
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem


class SyncEngine:
    """
    Moteur de synchronisation avec persistance locale (Outbox Pattern).
    Queue les opérations offline en base SQLite locale et les replay quand la connexion revient.
    Protégé contre les crashs et les exécutions concurrentes.
    """
    
    def __init__(self, max_queue_size: int = None):
        self.max_queue_size = max_queue_size or settings.SYNC_QUEUE_MAX_SIZE
        self.is_syncing = False
        self._is_running = False
        self._task = None
        self._needs_reconciliation = True
        self._lock = asyncio.Lock()  # Verrou pour éviter les exécutions concurrentes de sync()
        
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
        """Boucle de sync périodique"""
        while self._is_running:
            if connection_monitor.is_online and (self.queue_size > 0 or self._needs_reconciliation):
                await self.sync()
            await asyncio.sleep(settings.SYNC_INTERVAL_SECONDS)
    
    async def _on_connection_change(self, status: ConnectionStatus):
        """Quand la connexion revient, on sync immédiatement"""
        if status == ConnectionStatus.ONLINE:
            self._needs_reconciliation = True
            await self.sync()

    @staticmethod
    def _has_business_data(db: Session) -> bool:
        """Ignore le tenant/admin système pour déterminer quelle base a commencé."""
        return any(
            db.query(model).count() > 0
            for model in (Product, Customer, Sale)
        )

    @staticmethod
    def _record_values(record, *, exclude=()):
        return {
            column.name: getattr(record, column.name)
            for column in record.__table__.columns
            if column.name not in exclude
        }

    def _copy_snapshot(self, source: Session, destination: Session):
        """Copie un instantané sans suppression, parents avant enfants."""
        # Tenant et utilisateur ont des identifiants métier stables, pas des
        # clés entières : cela évite de générer deux comptes admin différents.
        for tenant in source.query(Tenant).all():
            target = destination.query(Tenant).filter(Tenant.tenant_id == tenant.tenant_id).first()
            values = self._record_values(tenant, exclude=("id",))
            if target:
                for key, value in values.items():
                    setattr(target, key, value)
            else:
                destination.add(Tenant(**values))

        for user in source.query(User).all():
            target = destination.query(User).filter(User.email == user.email).first()
            values = self._record_values(user, exclude=("id",))
            if target:
                for key, value in values.items():
                    setattr(target, key, value)
            else:
                destination.add(User(**values))

        destination.flush()
        for model in (Product, Customer, Sale, SaleItem):
            for record in source.query(model).all():
                destination.merge(model(**self._record_values(record)))
        destination.commit()

    @staticmethod
    def _remove_bootstrap_admin(destination: Session, source: Session):
        """Retire uniquement l'admin temporaire d'une base initialement vide."""
        source_emails = {email for (email,) in source.query(User.email).all()}
        placeholder = destination.query(User).filter(User.email == settings.SUPERUSER_EMAIL).first()
        if placeholder and placeholder.email not in source_emails:
            destination.delete(placeholder)
            destination.flush()

            platform_tenant = destination.query(Tenant).filter(
                Tenant.tenant_id == settings.SUPERUSER_TENANT_ID
            ).first()
            if platform_tenant:
                has_users = destination.query(User).filter(User.tenant_id == platform_tenant.tenant_id).first()
                if not has_users:
                    destination.delete(platform_tenant)

    def _reconcile_databases(self):
        """Initialise la base vide à partir de celle qui contient les données."""
        local = db_router.get_local_session()
        cloud = db_router.get_online_session()
        try:
            local_has_data = self._has_business_data(local)
            cloud_has_data = self._has_business_data(cloud)

            # SQLite est la source quand elle contient déjà des données ou
            # qu'aucune des deux bases n'a encore de données métier. Sinon,
            # un démarrage en ligne récupère d'abord les données cloud.
            if local_has_data or not cloud_has_data:
                # PostgreSQL peut ne contenir que l'admin généré lors d'un
                # démarrage précédent. SQLite est alors la vraie source.
                if not cloud_has_data:
                    self._remove_bootstrap_admin(cloud, local)
                self._copy_snapshot(local, cloud)
                print("Réconciliation initiale : SQLite -> PostgreSQL")
            else:
                self._copy_snapshot(cloud, local)
                print("Réconciliation initiale : PostgreSQL -> SQLite")
        except Exception:
            cloud.rollback()
            local.rollback()
            raise
        finally:
            cloud.close()
            local.close()
    
    def add_operation(self, table: str, action: str, data: Dict[str, Any], tenant_id: str):
        """
        Ajoute une opération directement dans la table outbox de la base SQLite locale.
        Si online, on déclenche la synchronisation immédiatement.
        """
        db = db_router.get_local_session()
        try:
            # Gestion de la taille max de la queue : suppression de la plus ancienne si saturation
            current_count = db.query(SyncOutboxModel).count()
            if current_count >= self.max_queue_size:
                oldest = db.query(SyncOutboxModel).order_by(SyncOutboxModel.created_at.asc()).first()
                if oldest:
                    db.delete(oldest)
                    db.commit()

            # Création de l'entrée persistance
            outbox_entry = SyncOutboxModel(
                table_name=table,
                action=action,
                data=json.dumps(data),
                tenant_id=tenant_id,
                sync_version=data.get("sync_version", 0),
                created_at=datetime.utcnow()
            )
            db.add(outbox_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Erreur lors de l'écriture dans l'outbox locale: {e}")
        finally:
            db.close()
        
        # Si online, on sync tout de suite en arrière-plan
        if connection_monitor.is_online:
            asyncio.create_task(self.sync())
    
    async def sync(self):
        """
        Dépile et synchronise toutes les opérations de l'outbox locale vers le cloud de manière exclusive.
        """
        if self.is_syncing:
            return
        
        async with self._lock:
            if self.is_syncing:
                return
                
            self.is_syncing = True
            db = db_router.get_local_session()
            try:
                # L'application peut avoir démarré hors ligne : dans ce cas,
                # le schéma local a été créé mais PostgreSQL n'a encore aucune
                # table. On le prépare avant de rejouer la première opération.
                from app.core.database import Base
                cloud_engine = db_router.get_online_engine()
                Base.metadata.create_all(bind=cloud_engine)

                # create_all ne complète pas une table déjà existante. Cette
                # colonne a été ajoutée après les premiers déploiements et
                # doit donc être appliquée aussi lorsque le cloud revient.
                sales_columns = {column["name"] for column in inspect(cloud_engine).get_columns("sales")}
                if "customer_id" not in sales_columns:
                    with cloud_engine.begin() as connection:
                        connection.execute(text("ALTER TABLE sales ADD COLUMN customer_id INTEGER"))

                # Le seed est identique dans les deux bases. Puis, selon la
                # base qui possède les données métier, l'autre reçoit un
                # instantané avant le rejeu de l'outbox.
                from app.core.seed import seed_database
                seed_database(engine=cloud_engine)
                self._reconcile_databases()
                self._needs_reconciliation = False

                # Récupérer toutes les opérations en attente par ordre chronologique
                pending_ops = db.query(SyncOutboxModel).order_by(SyncOutboxModel.created_at.asc()).all()
                
                if not pending_ops:
                    return

                for op in pending_ops:
                    operation_data = {
                        "table": op.table_name,
                        "action": op.action,
                        "data": json.loads(op.data),
                        "tenant_id": op.tenant_id,
                        "sync_version": op.sync_version
                    }
                    
                    # Rejeu vers la base/serveur distant
                    await self._replay_operation(operation_data)
                    
                    # Si le rejeu réussit, on supprime l'opération de la table locale
                    db.delete(op)
                    db.commit()
                    
            except Exception as e:
                db.rollback()
                print(f"Sync error (Outbox): {e}")
            finally:
                db.close()
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

        elif table == "users":
            from app.services.user import UserService
            await UserService.replay_sync(tenant_id=tenant_id, action=action, data=data)
            
        else:
            print(f"Table de synchronisation non gérée : {table}")
    
    @property
    def queue_size(self) -> int:
        """Nombre d'opérations en attente de sync dans la base locale"""
        db = db_router.get_local_session()
        try:
            return db.query(SyncOutboxModel).count()
        finally:
            db.close()
    
    @property
    def is_full(self) -> bool:
        """Queue pleine ?"""
        return self.queue_size >= self.max_queue_size


# Instance globale
sync_engine = SyncEngine()
