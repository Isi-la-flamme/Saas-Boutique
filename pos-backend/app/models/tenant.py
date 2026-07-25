from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Tenant(Base):
    """Modèle Tenant"""
    
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), index=True, nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sync_version = Column(Integer, default=0)
    sync_source = Column(String(20), default="local")
    
    def __repr__(self):
        return f"<Tenant {self.id}: {self.name}>"
    
    def __str__(self):
        return self.__repr__()