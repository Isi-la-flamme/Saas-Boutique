from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base


class SyncMixin:
    """
    Mixin pour toutes les tables qui doivent être syncées.
    Ajoute les colonnes communes pour le sync et le multi-tenant.
    """
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sync_version = Column(Integer, default=0)
    sync_source = Column(String(20), default="local")  # "local" ou "cloud"