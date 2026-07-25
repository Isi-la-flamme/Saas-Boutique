from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    """Modèle Product"""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sync_version = Column(Integer, default=0)
    sync_source = Column(String(20), default="local")
    
    def __repr__(self):
        return f"<Product {self.id}: {self.name}>"