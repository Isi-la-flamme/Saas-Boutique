from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Customer(Base):
    """Client appartenant à une seule boutique (tenant)."""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sync_version = Column(Integer, default=0)
    sync_source = Column(String(20), default="local")

    def __repr__(self):
        return f"<Customer {self.id}: {self.name}>"
