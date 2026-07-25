from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SaleStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    PARTIAL = "partial"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    CREDIT = "credit"
    DEFERRED = "deferred"


class SaleItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemResponse(SaleItemBase):
    id: int
    sale_id: int
    total_price: float
    created_at: datetime
    product_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    customer_id: Optional[int] = None
    status: SaleStatus = SaleStatus.COMPLETED
    payment_status: PaymentStatus = PaymentStatus.UNPAID
    payment_method: PaymentMethod = PaymentMethod.DEFERRED
    amount_paid: float = Field(0.0, ge=0)


class SaleCreate(SaleBase):
    items: List[SaleItemCreate]


class SaleUpdate(BaseModel):
    status: Optional[SaleStatus] = None
    payment_status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    amount_paid: Optional[float] = Field(None, ge=0)


class SaleResponse(SaleBase):
    id: int
    tenant_id: str
    total: float
    remaining_amount: float
    created_at: datetime
    updated_at: datetime
    sync_version: int
    sync_source: str
    items: List[SaleItemResponse] = []
    customer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SaleListResponse(BaseModel):
    items: list[SaleResponse]
    total: int
