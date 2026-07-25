from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)


class CustomerResponse(CustomerBase):
    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
