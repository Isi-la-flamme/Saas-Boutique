from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class SaleStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    PARTIAL = "partial"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    CREDIT = "credit"
    DEFERRED = "deferred"  # Paiement différé


class Sale(Base):
    """Modèle Sale (vente)"""
    
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), index=True, nullable=False)
    # Une vente peut être anonyme. Lorsque renseigné, le client doit appartenir au tenant de la vente.
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    total = Column(Float, default=0.0)
    status = Column(Enum(SaleStatus), default=SaleStatus.PENDING)
    
    # Nouveaux champs pour le paiement
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.DEFERRED)
    amount_paid = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sync_version = Column(Integer, default=0)
    sync_source = Column(String(20), default="local")
    
    # Relation
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<Sale {self.id}: {self.total}F CFA - {self.payment_status}>"


class SaleItem(Base):
    """Modèle SaleItem (ligne de vente)"""
    
    __tablename__ = "sale_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")  # Ajout de la relation
    
    def __repr__(self):
        return f"<SaleItem {self.id}: qty={self.quantity} price={self.unit_price}F CFA>"
