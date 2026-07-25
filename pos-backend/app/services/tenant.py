from sqlalchemy.orm import Session
from typing import Optional
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.core import db_router, sync_engine
import uuid


class TenantService:
    """Service Tenant"""
    
    @staticmethod
    def _get_db():
        """Retourne une session DB via le router"""
        return db_router.get_session()
    
    @staticmethod
    def create(tenant_data: TenantCreate) -> TenantResponse:
        """Crée un nouveau tenant"""
        db = TenantService._get_db()
        try:
            tenant_id = f"tenant_{uuid.uuid4().hex[:8]}"
            
            tenant = Tenant(
                tenant_id=tenant_id,
                name=tenant_data.name,
                description=tenant_data.description,
                is_active=tenant_data.is_active,
                sync_source="local"
            )
            
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            
            sync_engine.add_operation(
                table="tenants",
                action="create",
                data={
                    "id": tenant.id,
                    "tenant_id": tenant.tenant_id,
                    "name": tenant.name,
                    "description": tenant.description,
                    "is_active": tenant.is_active,
                    "sync_version": tenant.sync_version
                },
                tenant_id=tenant.tenant_id
            )
            
            return TenantResponse.model_validate(tenant)
        finally:
            db.close()
    
    @staticmethod
    def get(tenant_id: str) -> Optional[TenantResponse]:
        """Récupère un tenant par son tenant_id"""
        db = TenantService._get_db()
        try:
            tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
            if tenant:
                return TenantResponse.model_validate(tenant)
            return None
        finally:
            db.close()
    
    @staticmethod
    def list(skip: int = 0, limit: int = 100) -> dict:
        """Liste tous les tenants"""
        db = TenantService._get_db()
        try:
            query = db.query(Tenant)
            total = query.count()
            tenants = query.offset(skip).limit(limit).all()
            
            return {
                "items": [TenantResponse.model_validate(t) for t in tenants],
                "total": total
            }
        finally:
            db.close()
    
    @staticmethod
    def update(tenant_id: str, tenant_data: TenantUpdate) -> Optional[TenantResponse]:
        """Met à jour un tenant"""
        db = TenantService._get_db()
        try:
            tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
            if not tenant:
                return None
            
            if tenant_data.name is not None:
                tenant.name = tenant_data.name
            if tenant_data.description is not None:
                tenant.description = tenant_data.description
            if tenant_data.is_active is not None:
                tenant.is_active = tenant_data.is_active
            
            tenant.sync_version += 1
            tenant.sync_source = "local"
            
            db.commit()
            db.refresh(tenant)
            
            sync_engine.add_operation(
                table="tenants",
                action="update",
                data={
                    "id": tenant.id,
                    "tenant_id": tenant.tenant_id,
                    "name": tenant.name,
                    "description": tenant.description,
                    "is_active": tenant.is_active,
                    "sync_version": tenant.sync_version
                },
                tenant_id=tenant.tenant_id
            )
            
            return TenantResponse.model_validate(tenant)
        finally:
            db.close()
    
    @staticmethod
    def delete(tenant_id: str) -> bool:
        """Supprime un tenant"""
        db = TenantService._get_db()
        try:
            tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
            if not tenant:
                return False
            
            db.delete(tenant)
            db.commit()
            
            sync_engine.add_operation(
                table="tenants",
                action="delete",
                data={"tenant_id": tenant_id},
                tenant_id=tenant_id
            )
            
            return True
        finally:
            db.close()


tenant_service = TenantService()