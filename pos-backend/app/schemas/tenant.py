from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TenantBase(BaseModel):
    """Base Tenant schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class TenantCreate(TenantBase):
    """Création d'un tenant"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    pass


class TenantUpdate(BaseModel):
    """Mise à jour d'un tenant"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    """Réponse Tenant"""
    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    sync_version: int
    sync_source: str
    
    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """Liste des tenants"""
    items: list[TenantResponse]
    total: int
    
    class Config:
        from_attributes = True